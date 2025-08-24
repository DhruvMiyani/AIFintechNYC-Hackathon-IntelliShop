"""
GPT-5 Powered Payment Processor Registry
Real-time health monitoring and intelligent processor selection
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ProcessorStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    FROZEN = "frozen"
    MAINTENANCE = "maintenance"


@dataclass
class ProcessorHealthMetrics:
    success_rate: float  # 0.0 to 1.0
    avg_response_time: float  # milliseconds
    failure_count_24h: int
    last_failure_time: Optional[datetime]
    uptime_percentage: float
    freeze_risk_score: float  # 0-10 scale


@dataclass
class PaymentProcessor:
    id: str
    name: str
    type: str  # "card", "crypto", "bank_transfer", "wallet"
    status: ProcessorStatus
    capabilities: List[str]
    fee_structure: Dict[str, float]
    limits: Dict[str, Any]
    health: ProcessorHealthMetrics
    last_updated: datetime = field(default_factory=datetime.utcnow)
    api_endpoint: str = ""
    fallback_priority: int = 1  # 1=primary, 2=secondary, etc.


class ProcessorRegistry:
    """
    Intelligent processor registry that GPT-5 can query for routing decisions.
    Maintains real-time health status and failure patterns.
    """
    
    def __init__(self):
        self.processors: Dict[str, PaymentProcessor] = {}
        self.health_history: Dict[str, List[ProcessorHealthMetrics]] = {}
        self._initialize_processors()
        
    def _initialize_processors(self):
        """Initialize demo processors with realistic configurations."""
        
        # Stripe (Primary)
        self.processors["stripe"] = PaymentProcessor(
            id="stripe",
            name="Stripe",
            type="card",
            status=ProcessorStatus.HEALTHY,
            capabilities=["cards", "ach", "subscriptions", "payouts"],
            fee_structure={"percentage": 0.029, "fixed": 0.30},
            limits={"daily_volume": 1000000, "single_transaction": 99999},
            health=ProcessorHealthMetrics(
                success_rate=0.987,
                avg_response_time=245,
                failure_count_24h=3,
                last_failure_time=datetime.utcnow() - timedelta(hours=6),
                uptime_percentage=99.94,
                freeze_risk_score=2.1
            ),
            api_endpoint="https://api.stripe.com/v1",
            fallback_priority=1
        )
        
        # PayPal (Secondary)
        self.processors["paypal"] = PaymentProcessor(
            id="paypal",
            name="PayPal",
            type="wallet",
            status=ProcessorStatus.HEALTHY,
            capabilities=["paypal", "cards", "bank_transfer"],
            fee_structure={"percentage": 0.035, "fixed": 0.49},
            limits={"daily_volume": 750000, "single_transaction": 60000},
            health=ProcessorHealthMetrics(
                success_rate=0.983,
                avg_response_time=312,
                failure_count_24h=7,
                last_failure_time=datetime.utcnow() - timedelta(hours=2),
                uptime_percentage=99.82,
                freeze_risk_score=1.7
            ),
            api_endpoint="https://api.paypal.com/v2",
            fallback_priority=2
        )
        
        # Visa Direct (Tertiary)
        self.processors["visa"] = PaymentProcessor(
            id="visa",
            name="Visa Direct",
            type="bank_transfer", 
            status=ProcessorStatus.HEALTHY,
            capabilities=["push_payments", "cards"],
            fee_structure={"percentage": 0.025, "fixed": 0.50},
            limits={"daily_volume": 500000, "single_transaction": 25000},
            health=ProcessorHealthMetrics(
                success_rate=0.995,
                avg_response_time=189,
                failure_count_24h=1,
                last_failure_time=datetime.utcnow() - timedelta(days=2),
                uptime_percentage=99.97,
                freeze_risk_score=0.8
            ),
            api_endpoint="https://sandbox.api.visa.com",
            fallback_priority=3
        )
    
    async def get_processor_for_gpt5_analysis(self, transaction_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get processor information formatted for GPT-5 decision making.
        Includes real-time health metrics and risk assessments.
        """
        
        processors_data = {}
        
        for proc_id, processor in self.processors.items():
            # Calculate real-time risk factors
            risk_factors = await self._assess_processor_risk(processor, transaction_context)
            
            processors_data[proc_id] = {
                "id": processor.id,
                "name": processor.name,
                "status": processor.status.value,
                "health_metrics": {
                    "success_rate": f"{processor.health.success_rate*100:.1f}%",
                    "response_time": f"{processor.health.avg_response_time}ms",
                    "uptime": f"{processor.health.uptime_percentage:.2f}%",
                    "recent_failures": processor.health.failure_count_24h,
                    "freeze_risk": f"{processor.health.freeze_risk_score}/10"
                },
                "fees": processor.fee_structure,
                "capabilities": processor.capabilities,
                "limits": processor.limits,
                "risk_assessment": risk_factors,
                "fallback_priority": processor.fallback_priority,
                "recommendation": self._get_processor_recommendation(processor, transaction_context)
            }
        
        return {
            "available_processors": processors_data,
            "last_updated": datetime.utcnow().isoformat(),
            "analysis_context": transaction_context
        }
    
    async def _assess_processor_risk(self, processor: PaymentProcessor, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess real-time risk factors for processor selection."""
        
        transaction_amount = context.get("amount", 0)
        merchant_risk_level = context.get("merchant_risk", "low")
        
        risk_factors = []
        risk_score = 0.0
        
        # Volume risk
        if processor.status == ProcessorStatus.FROZEN:
            risk_factors.append("ACCOUNT_FROZEN")
            risk_score += 10.0
        elif processor.health.success_rate < 0.95:
            risk_factors.append("LOW_SUCCESS_RATE")
            risk_score += 3.0
        
        # Recent failures
        if processor.health.failure_count_24h > 10:
            risk_factors.append("HIGH_FAILURE_COUNT")
            risk_score += 2.0
        
        # Transaction size vs limits
        if transaction_amount > processor.limits.get("single_transaction", 999999):
            risk_factors.append("EXCEEDS_LIMITS")
            risk_score += 5.0
        
        # Response time degradation
        if processor.health.avg_response_time > 500:
            risk_factors.append("SLOW_RESPONSE")
            risk_score += 1.0
        
        return {
            "risk_factors": risk_factors,
            "risk_score": min(risk_score, 10.0),
            "is_recommended": risk_score < 3.0,
            "concerns": self._generate_risk_concerns(risk_factors)
        }
    
    def _generate_risk_concerns(self, risk_factors: List[str]) -> List[str]:
        """Generate human-readable risk concerns for GPT-5."""
        
        concern_map = {
            "ACCOUNT_FROZEN": "Processor account is currently frozen - cannot process payments",
            "LOW_SUCCESS_RATE": "Below normal success rate - higher chance of payment failures", 
            "HIGH_FAILURE_COUNT": "Unusual number of recent failures - may indicate system issues",
            "EXCEEDS_LIMITS": "Transaction amount exceeds processor limits",
            "SLOW_RESPONSE": "Response times are degraded - may cause timeout issues"
        }
        
        return [concern_map.get(factor, factor) for factor in risk_factors]
    
    def _get_processor_recommendation(self, processor: PaymentProcessor, context: Dict[str, Any]) -> str:
        """Get recommendation text for GPT-5 analysis."""
        
        if processor.status == ProcessorStatus.FROZEN:
            return "NOT_RECOMMENDED - Account frozen, use alternative processor"
        elif processor.health.success_rate > 0.99 and processor.health.freeze_risk_score < 2.0:
            return "HIGHLY_RECOMMENDED - Excellent health metrics and low risk"
        elif processor.health.success_rate > 0.95:
            return "RECOMMENDED - Good performance metrics"
        else:
            return "CAUTION - Consider alternative if available"
    
    async def simulate_processor_failure(self, processor_id: str, failure_type: str = "timeout"):
        """Simulate processor failure for demo purposes."""
        
        if processor_id not in self.processors:
            return
        
        processor = self.processors[processor_id]
        
        # Update health metrics based on failure type
        if failure_type == "freeze":
            processor.status = ProcessorStatus.FROZEN
            processor.health.freeze_risk_score = 10.0
            print(f"🚨 {processor.name} account FROZEN - switching to fallback")
        elif failure_type == "degraded":
            processor.status = ProcessorStatus.DEGRADED
            processor.health.success_rate = max(0.85, processor.health.success_rate - 0.1)
            processor.health.avg_response_time += 200
            print(f"⚠️  {processor.name} performance DEGRADED")
        elif failure_type == "timeout":
            processor.health.failure_count_24h += 5
            processor.health.avg_response_time += 100
            processor.health.last_failure_time = datetime.utcnow()
            print(f"⏱️  {processor.name} experiencing TIMEOUTS")
        
        processor.last_updated = datetime.utcnow()
    
    async def restore_processor(self, processor_id: str):
        """Restore processor to healthy state."""
        
        if processor_id not in self.processors:
            return
        
        processor = self.processors[processor_id]
        processor.status = ProcessorStatus.HEALTHY
        processor.health.freeze_risk_score = random.uniform(0.5, 2.0)
        processor.health.success_rate = random.uniform(0.98, 0.995)
        processor.health.avg_response_time = random.randint(150, 300)
        processor.health.failure_count_24h = random.randint(0, 5)
        processor.last_updated = datetime.utcnow()
        
        print(f"✅ {processor.name} RESTORED to healthy status")
    
    async def update_health_metrics(self):
        """Continuously update processor health metrics (background task)."""
        
        while True:
            for processor in self.processors.values():
                if processor.status == ProcessorStatus.HEALTHY:
                    # Slight random variations in healthy processors
                    processor.health.success_rate += random.uniform(-0.001, 0.001)
                    processor.health.avg_response_time += random.randint(-10, 10)
                    
                    # Keep within realistic bounds
                    processor.health.success_rate = max(0.95, min(0.999, processor.health.success_rate))
                    processor.health.avg_response_time = max(100, min(1000, processor.health.avg_response_time))
                
                processor.last_updated = datetime.utcnow()
            
            await asyncio.sleep(30)  # Update every 30 seconds
    
    def get_fallback_chain(self, failed_processor: str, context: Dict[str, Any]) -> List[str]:
        """Get ordered list of fallback processors for GPT-5."""
        
        available = [
            proc for proc_id, proc in self.processors.items() 
            if proc_id != failed_processor and proc.status != ProcessorStatus.FROZEN
        ]
        
        # Sort by fallback priority and health
        available.sort(key=lambda p: (
            p.fallback_priority,
            -p.health.success_rate,  # Higher success rate = lower sort value
            p.health.avg_response_time
        ))
        
        return [proc.id for proc in available]
    
    def export_for_gpt5_prompt(self, context: Dict[str, Any]) -> str:
        """Export processor data as formatted text for GPT-5 prompts."""
        
        output = "AVAILABLE PAYMENT PROCESSORS:\n\n"
        
        for proc_id, processor in self.processors.items():
            status_icon = {
                ProcessorStatus.HEALTHY: "✅",
                ProcessorStatus.DEGRADED: "⚠️",
                ProcessorStatus.FROZEN: "🚨", 
                ProcessorStatus.MAINTENANCE: "🔧"
            }.get(processor.status, "❓")
            
            output += f"{status_icon} {processor.name} ({proc_id}):\n"
            output += f"  Status: {processor.status.value}\n"
            output += f"  Success Rate: {processor.health.success_rate*100:.1f}%\n"
            output += f"  Response Time: {processor.health.avg_response_time}ms\n"
            output += f"  Recent Failures: {processor.health.failure_count_24h}/24h\n"
            output += f"  Freeze Risk: {processor.health.freeze_risk_score}/10\n"
            output += f"  Fees: {processor.fee_structure['percentage']*100:.1f}% + ${processor.fee_structure['fixed']}\n"
            output += f"  Priority: {processor.fallback_priority} (1=primary)\n\n"
        
        return output


# Demo usage
async def demo_processor_registry():
    """Demonstrate processor registry for GPT-5 integration."""
    
    registry = ProcessorRegistry()
    
    # Simulate transaction context
    transaction_context = {
        "amount": 450.00,
        "currency": "USD",
        "merchant_id": "acme_corp",
        "merchant_risk": "low",
        "urgency": "normal"
    }
    
    print("📊 Initial Processor Health Status:")
    data = await registry.get_processor_for_gpt5_analysis(transaction_context)
    print(registry.export_for_gpt5_prompt(transaction_context))
    
    # Simulate Stripe freeze
    print("\n🚨 SIMULATING STRIPE ACCOUNT FREEZE...")
    await registry.simulate_processor_failure("stripe", "freeze")
    
    print("\n📊 Updated Status After Stripe Freeze:")
    print(registry.export_for_gpt5_prompt(transaction_context))
    
    print("\n🔄 Fallback Chain:")
    fallback_chain = registry.get_fallback_chain("stripe", transaction_context)
    print(f"Recommended fallback order: {' → '.join(fallback_chain)}")
    
    # Restore for demo
    await asyncio.sleep(2)
    await registry.restore_processor("stripe")
    print("\n✅ Stripe restored for continued demo")


if __name__ == "__main__":
    asyncio.run(demo_processor_registry())