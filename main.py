"""
FastAPI Payment Router with Claude Intelligent Fallback
Main API for receiving payments and handling processor failures
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import uuid

from processors.base import PaymentRequest, PaymentStatus, ProcessorStatus
from processors.stripe import StripeProcessor
from processors.paypal import PayPalProcessor
from processors.visa import VisaProcessor
from claude_router import ClaudeRouter, FailureType
from data_analysis_api import router as data_router


app = FastAPI(
    title="Claude Payment Orchestration",
    description="Intelligent payment routing with automatic fallback when processors fail",
    version="1.0.0"
)

# Include data analysis API
app.include_router(data_router)


# Initialize processors
processors = {
    "stripe": StripeProcessor(),
    "paypal": PayPalProcessor(), 
    "visa": VisaProcessor()
}

# Initialize Claude router
claude_router = ClaudeRouter()


# Request/Response models
class PaymentRequestModel(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field(default="USD", description="Currency code")
    customer_email: Optional[str] = Field(None, description="Customer email")
    description: Optional[str] = Field(None, description="Payment description")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    preferred_processor: Optional[str] = Field(None, description="Preferred processor if available")


class PaymentResponseModel(BaseModel):
    success: bool
    payment_id: str
    processor_used: str
    amount: float
    currency: str
    status: str
    reasoning: Optional[str] = None
    fallback_attempted: bool = False
    processing_time_ms: float
    fees: Optional[float] = None
    error: Optional[str] = None


class ProcessorHealthResponse(BaseModel):
    processor_id: str
    status: str
    health: Dict[str, Any]
    capabilities: Dict[str, Any]
    recent_performance: Dict[str, Any]


@app.get("/")
async def root():
    return {
        "service": "Claude Payment Orchestration",
        "status": "operational",
        "problem_solved": "Automatic fallback when payment processors fail or accounts are frozen",
        "active_processors": list(processors.keys())
    }


@app.post("/payments/process", response_model=PaymentResponseModel)
async def process_payment(payment: PaymentRequestModel):
    """
    Process a payment with intelligent routing and automatic fallback.
    
    Key features:
    - Uses Claude to select best processor based on context
    - Automatically falls back if primary processor fails
    - Handles account freezes (e.g., Stripe account under review)
    - Provides reasoning for routing decisions
    """
    
    start_time = datetime.utcnow()
    payment_id = str(uuid.uuid4())
    
    # Create payment request
    request = PaymentRequest(
        request_id=payment_id,
        amount=payment.amount,
        currency=payment.currency,
        merchant_id="demo_merchant",
        metadata=payment.metadata
    )
    
    # Determine context for routing
    context = {
        "high_risk": payment.amount > 5000,
        "urgency": "high" if payment.amount > 1000 else "normal",
        "account_frozen": processors["stripe"].status == ProcessorStatus.FAILED,  # Simulate Stripe freeze
        "customer_type": "premium" if payment.amount > 500 else "standard"
    }
    
    # Get available processors (exclude failed/frozen processors)
    available_processors = [
        {
            "id": pid,
            "fee_percentage": proc.config.get("fee_percentage", 2.9),
            "metrics": {
                "success_rate": proc.get_metrics().success_rate,
                "uptime": proc.get_metrics().uptime_percentage,
                "avg_latency": proc.get_metrics().average_latency_ms
            },
            "capabilities": proc.get_capabilities()
        }
        for pid, proc in processors.items()
        if proc.status == ProcessorStatus.ACTIVE  # Only include active processors
    ]
    
    # Use Claude to make routing decision
    complexity = "simple" if payment.amount < 10 else "balanced"
    if context.get("account_frozen") or payment.amount > 5000:
        complexity = "comprehensive"
    
    routing_decision = await claude_router.make_routing_decision(
        request=request,
        available_processors=available_processors,
        context=context,
        complexity=complexity
    )
    
    # Try primary processor
    selected_processor = processors.get(routing_decision.selected_processor)
    if not selected_processor:
        print("DEBUG: Selected processor not found, falling back to stripe")
        selected_processor = processors["stripe"]  # Default fallback
    
    response = await selected_processor.process_payment(request)
    
    # If failed, try fallback chain
    fallback_attempted = False
    if response.status in [PaymentStatus.FAILED, PaymentStatus.TIMEOUT]:
        fallback_attempted = True
        
        # Record failure
        claude_router.record_failure(
            processor_id=routing_decision.selected_processor,
            failure_type=FailureType.DECLINED if response.status == PaymentStatus.FAILED else FailureType.NETWORK_ERROR,
            error_code=response.error_code or "UNKNOWN",
            error_message=response.error_message or "Payment failed"
        )
        
        # Try fallback processors
        for fallback_id in routing_decision.fallback_chain:
            fallback_processor = processors.get(fallback_id)
            if fallback_processor and fallback_processor.status == ProcessorStatus.ACTIVE:
                response = await fallback_processor.process_payment(request)
                if response.status == PaymentStatus.SUCCESS:
                    claude_router.record_success(fallback_id)
                    routing_decision.selected_processor = fallback_id
                    break
    else:
        claude_router.record_success(routing_decision.selected_processor)
    
    processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    return PaymentResponseModel(
        success=response.status == PaymentStatus.SUCCESS,
        payment_id=payment_id,
        processor_used=routing_decision.selected_processor,
        amount=payment.amount,
        currency=payment.currency,
        status=response.status.value,
        reasoning=routing_decision.reasoning,
        fallback_attempted=fallback_attempted,
        processing_time_ms=processing_time,
        fees=response.fees,
        error=response.error_message
    )


@app.post("/processors/{processor_id}/freeze")
async def freeze_processor(processor_id: str):
    """
    Simulate a processor freeze (e.g., Stripe account under review).
    This triggers the intelligent fallback system.
    """
    
    if processor_id not in processors:
        raise HTTPException(status_code=404, detail=f"Processor {processor_id} not found")
    
    processors[processor_id].status = ProcessorStatus.FAILED
    
    # Record in Claude router
    claude_router.record_failure(
        processor_id=processor_id,
        failure_type=FailureType.ACCOUNT_FROZEN,
        error_code="ACCOUNT_FROZEN",
        error_message=f"{processor_id} account is frozen/under review",
        permanent=True
    )
    
    return {
        "message": f"Processor {processor_id} frozen",
        "status": "All payments will now be routed to alternative processors",
        "claude_router_updated": True
    }


@app.post("/processors/{processor_id}/unfreeze")
async def unfreeze_processor(processor_id: str):
    """Restore a frozen processor."""
    
    if processor_id not in processors:
        raise HTTPException(status_code=404, detail=f"Processor {processor_id} not found")
    
    processors[processor_id].status = ProcessorStatus.ACTIVE
    
    # Update Claude router health
    claude_router.processor_health[processor_id]["frozen"] = False
    claude_router.processor_health[processor_id]["failure_count"] = 0
    
    return {
        "message": f"Processor {processor_id} restored",
        "status": "Processor is now available for routing"
    }


@app.get("/processors/health", response_model=List[ProcessorHealthResponse])
async def get_processors_health():
    """Get health status of all processors."""
    
    health_data = []
    for processor_id, processor in processors.items():
        metrics = processor.get_metrics()
        capabilities = processor.get_capabilities()
        
        health_data.append(ProcessorHealthResponse(
            processor_id=processor_id,
            status=processor.status.value,
            health={
                "frozen": claude_router.processor_health.get(processor_id, {}).get("frozen", False),
                "failure_count": claude_router.processor_health.get(processor_id, {}).get("failure_count", 0),
                "last_success": claude_router.processor_health.get(processor_id, {}).get("last_success")
            },
            capabilities=capabilities,
            recent_performance={
                "success_rate": metrics.success_rate,
                "uptime_percentage": metrics.uptime_percentage,
                "average_latency_ms": metrics.average_latency_ms,
                "last_failure": metrics.last_failure.isoformat() if metrics.last_failure else None
            }
        ))
    
    return health_data


@app.get("/analytics/routing")
async def get_routing_analytics():
    """Get analytics on Claude routing decisions."""
    
    return claude_router.get_routing_analytics()


@app.post("/demo/simulate_stripe_freeze")
async def demo_simulate_stripe_freeze():
    """
    Demo endpoint: Simulate Stripe account freeze scenario.
    Shows how the system automatically falls back to PayPal/Visa.
    """
    
    # Freeze Stripe
    processors["stripe"].status = ProcessorStatus.FAILED
    claude_router.record_failure(
        processor_id="stripe",
        failure_type=FailureType.ACCOUNT_FROZEN,
        error_code="ACCOUNT_FROZEN",
        error_message="Stripe account under review - all payments blocked",
        permanent=True
    )
    
    # Process a test payment
    test_payment = PaymentRequestModel(
        amount=99.99,
        currency="USD",
        description="Test payment during Stripe freeze"
    )
    
    result = await process_payment(test_payment)
    
    # Restore Stripe
    processors["stripe"].status = ProcessorStatus.ACTIVE
    claude_router.processor_health["stripe"]["frozen"] = False
    
    return {
        "scenario": "Stripe account frozen",
        "test_payment": {
            "amount": test_payment.amount,
            "currency": test_payment.currency
        },
        "result": {
            "success": result.success,
            "processor_used": result.processor_used,
            "reasoning": result.reasoning,
            "fallback_attempted": result.fallback_attempted
        },
        "demonstration": "System automatically routed to alternative processor when Stripe was unavailable"
    }


@app.post("/demo/simulate_high_risk")
async def demo_simulate_high_risk():
    """
    Demo endpoint: Simulate high-risk transaction requiring deep reasoning.
    """
    
    # High-risk, high-value payment
    test_payment = PaymentRequestModel(
        amount=15000.00,
        currency="USD",
        description="High-value B2B payment",
        metadata={"invoice_id": "INV-2024-001", "risk_score": 75}
    )
    
    result = await process_payment(test_payment)
    
    return {
        "scenario": "High-risk, high-value transaction",
        "test_payment": {
            "amount": test_payment.amount,
            "risk_indicators": "High amount, elevated risk score"
        },
        "claude_analysis": {
            "complexity_used": "comprehensive",
            "reasoning": result.reasoning,
            "processor_selected": result.processor_used
        },
        "demonstration": "Claude used comprehensive analysis to evaluate risk and select optimal processor"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)