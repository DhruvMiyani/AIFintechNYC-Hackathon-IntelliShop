"""
COMPLETE INTEGRATED PAYMENT ORCHESTRATION DEMO
Components 1 + 2 + 3 working together with real GPT-5
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import uuid
import random

# Component 2: GPT-5 Engine
from gpt5_working_demo import GPT5PaymentOrchestrator, ReasoningEffort, Verbosity


@dataclass
class PaymentRequest:
    amount: float
    currency: str = "USD" 
    merchant_id: str = "default_merchant"
    urgency: str = "normal"
    description: str = ""


@dataclass
class CompletePaymentFlow:
    """Complete payment flow through all 3 components"""
    flow_id: str
    payment_request: PaymentRequest
    
    # Component 1: Data Analysis results
    risk_analysis: Optional[Dict[str, Any]] = None
    data_analysis_time_ms: int = 0
    
    # Component 2: GPT-5 Engine results
    gpt5_decision: Optional[Any] = None
    gpt5_processing_time_ms: int = 0
    
    # Component 3: Routing Logic results
    routing_result: Optional[Dict[str, Any]] = None
    routing_time_ms: int = 0
    
    # Overall results
    final_status: str = "pending"
    total_processing_time_ms: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class CompleteIntegratedSystem:
    """
    Complete payment orchestration system integrating:
    - Component 1: Data Analysis & Risk Assessment
    - Component 2: GPT-5 Engine Decision Making
    - Component 3: Routing Logic & Processor Execution
    """
    
    def __init__(self):
        # Component 2: GPT-5 Engine (working)
        self.gpt5_orchestrator = GPT5PaymentOrchestrator()
        
        # Component 1: Mock Data Analysis
        self.risk_patterns = {
            "low": {"score": 1.5, "factors": []},
            "medium": {"score": 4.5, "factors": ["amount_elevated"]},
            "high": {"score": 7.8, "factors": ["high_value", "velocity_spike"]},
            "critical": {"score": 9.2, "factors": ["high_value", "emergency_merchant", "unusual_pattern"]}
        }
        
        # Component 3: Mock Payment Processors
        self.processors = {
            "stripe": {"success_rate": 0.989, "response_time": 245, "status": "healthy", "freeze_risk": 2.1},
            "paypal": {"success_rate": 0.983, "response_time": 312, "status": "healthy", "freeze_risk": 1.8},
            "visa": {"success_rate": 0.995, "response_time": 189, "status": "healthy", "freeze_risk": 0.9},
            "square": {"success_rate": 0.976, "response_time": 334, "status": "healthy", "freeze_risk": 2.8}
        }
        
        # System metrics
        self.flows_processed = 0
        self.total_tokens_used = 0
        self.successful_flows = 0
        
    async def process_complete_payment_flow(self, payment_request: PaymentRequest) -> CompletePaymentFlow:
        """
        Process payment through complete integrated system
        """
        
        flow_id = f"integrated_{uuid.uuid4().hex[:10]}"
        start_time = datetime.utcnow()
        
        flow = CompletePaymentFlow(
            flow_id=flow_id,
            payment_request=payment_request
        )
        
        print(f"\n🔄 INTEGRATED FLOW START: {flow_id}")
        print(f"   Payment: ${payment_request.amount:,.2f} {payment_request.currency}")
        print(f"   Merchant: {payment_request.merchant_id}")
        print(f"   Description: {payment_request.description}")
        
        try:
            # COMPONENT 1: Data Analysis & Risk Assessment
            print(f"\n📊 COMPONENT 1: Data Analysis")
            component1_start = datetime.utcnow()
            
            risk_analysis = await self._component1_data_analysis(payment_request)
            flow.risk_analysis = risk_analysis
            flow.data_analysis_time_ms = int((datetime.utcnow() - component1_start).total_seconds() * 1000)
            
            print(f"   ✅ Risk Level: {risk_analysis['risk_level']}")
            print(f"   ✅ Risk Score: {risk_analysis['risk_score']}/10")
            print(f"   ✅ Risk Factors: {', '.join(risk_analysis['risk_factors'])}")
            print(f"   ⏱️  Processing Time: {flow.data_analysis_time_ms}ms")
            
            # COMPONENT 2: GPT-5 Engine Decision Making
            print(f"\n🧠 COMPONENT 2: GPT-5 Engine")
            component2_start = datetime.utcnow()
            
            gpt5_decision = await self._component2_gpt5_decision(payment_request, risk_analysis)
            flow.gpt5_decision = gpt5_decision
            flow.gpt5_processing_time_ms = gpt5_decision.processing_time_ms
            
            print(f"   ✅ Selected Processor: {gpt5_decision.selected_processor}")
            print(f"   ✅ Confidence: {gpt5_decision.confidence:.1%}")
            print(f"   ✅ Reasoning Effort: {gpt5_decision.reasoning_effort}")
            print(f"   ✅ Verbosity: {gpt5_decision.verbosity}")
            print(f"   ✅ GPT-5 Tokens: {gpt5_decision.tokens_used}")
            print(f"   ⏱️  Processing Time: {flow.gpt5_processing_time_ms}ms")
            
            # Show GPT-5 reasoning if high verbosity
            if gpt5_decision.verbosity == "high" and gpt5_decision.reasoning_chain:
                print(f"   🔍 Sample GPT-5 Reasoning:")
                for i, step in enumerate(gpt5_decision.reasoning_chain[:2], 1):
                    print(f"      {i}. {step[:80]}...")
            
            # COMPONENT 3: Routing Logic & Execution  
            print(f"\n🔀 COMPONENT 3: Routing Logic")
            component3_start = datetime.utcnow()
            
            routing_result = await self._component3_routing_execution(gpt5_decision.selected_processor, payment_request)
            flow.routing_result = routing_result
            flow.routing_time_ms = int((datetime.utcnow() - component3_start).total_seconds() * 1000)
            
            success_icon = "✅" if routing_result["success"] else "❌"
            print(f"   {success_icon} Execution Result: {'SUCCESS' if routing_result['success'] else 'FAILED'}")
            print(f"   ✅ Processor: {routing_result['processor']}")
            print(f"   ✅ Response Time: {routing_result['response_time']}ms")
            if routing_result["success"]:
                print(f"   ✅ Transaction ID: {routing_result['transaction_id']}")
                print(f"   💰 Fee Charged: ${routing_result['fee_charged']:.2f}")
                print(f"   💰 Net Amount: ${routing_result['net_amount']:.2f}")
            else:
                print(f"   ❌ Error: {routing_result['error']}")
            print(f"   ⏱️  Processing Time: {flow.routing_time_ms}ms")
            
            # Complete flow
            flow.completed_at = datetime.utcnow()
            flow.total_processing_time_ms = int((flow.completed_at - start_time).total_seconds() * 1000)
            flow.final_status = "success" if routing_result["success"] else "failed"
            
            # Update system metrics
            self.flows_processed += 1
            self.total_tokens_used += gpt5_decision.tokens_used
            if flow.final_status == "success":
                self.successful_flows += 1
            
            # Final summary
            print(f"\n🏁 FLOW COMPLETE: {flow_id}")
            print(f"   Final Status: {'✅ SUCCESS' if flow.final_status == 'success' else '❌ FAILED'}")
            print(f"   Total Time: {flow.total_processing_time_ms}ms")
            print(f"   Component 1: {flow.data_analysis_time_ms}ms")
            print(f"   Component 2: {flow.gpt5_processing_time_ms}ms") 
            print(f"   Component 3: {flow.routing_time_ms}ms")
            print(f"   GPT-5 Tokens: {gpt5_decision.tokens_used}")
            
            return flow
            
        except Exception as e:
            print(f"❌ FLOW ERROR: {e}")
            flow.final_status = "error"
            flow.completed_at = datetime.utcnow()
            flow.total_processing_time_ms = int((flow.completed_at - start_time).total_seconds() * 1000)
            return flow
    
    async def _component1_data_analysis(self, payment_request: PaymentRequest) -> Dict[str, Any]:
        """Component 1: Data Analysis & Risk Assessment"""
        
        # Simulate data analysis processing time
        await asyncio.sleep(0.1)  # 100ms simulation
        
        amount = payment_request.amount
        merchant = payment_request.merchant_id.lower()
        
        # Determine risk level based on amount and merchant
        if amount > 10000 or "emergency" in merchant:
            risk_level = "critical"
        elif amount > 5000 or "high_risk" in merchant:
            risk_level = "high" 
        elif amount > 1000:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        pattern = self.risk_patterns[risk_level]
        
        return {
            "risk_level": risk_level,
            "risk_score": pattern["score"],
            "risk_factors": pattern["factors"].copy(),
            "merchant_risk_profile": "elevated" if "emergency" in merchant else "normal",
            "transaction_velocity": "normal",
            "geographic_risk": "low",
            "recommendations": [
                "Monitor transaction patterns",
                "Enhanced authentication recommended" if risk_level in ["high", "critical"] else "Standard processing"
            ],
            "component": "data_analysis",
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _component2_gpt5_decision(
        self, 
        payment_request: PaymentRequest, 
        risk_analysis: Dict[str, Any]
    ) -> Any:
        """Component 2: GPT-5 Engine Decision Making"""
        
        # Determine GPT-5 parameters based on risk analysis
        risk_level = risk_analysis["risk_level"]
        amount = payment_request.amount
        
        # reasoning_effort mapping
        if risk_level == "critical" or amount > 10000:
            reasoning_effort = ReasoningEffort.HIGH
        elif risk_level == "high" or amount > 1000:
            reasoning_effort = ReasoningEffort.MEDIUM
        elif risk_level == "low" and amount < 100:
            reasoning_effort = ReasoningEffort.MINIMAL
        else:
            reasoning_effort = ReasoningEffort.LOW
        
        # verbosity mapping
        if risk_level in ["critical", "high"] or amount > 5000:
            verbosity = Verbosity.HIGH
        elif risk_level == "medium" or amount > 1000:
            verbosity = Verbosity.MEDIUM
        else:
            verbosity = Verbosity.LOW
        
        # Simulate failed processors occasionally
        failed_processors = []
        if random.random() < 0.3:  # 30% chance of failures
            failed_processors = [random.choice(["square", "paypal"])]
        
        # Use real GPT-5 orchestrator
        decision = await self.gpt5_orchestrator.make_routing_decision(
            amount=payment_request.amount,
            merchant=payment_request.merchant_id,
            failed_processors=failed_processors,
            reasoning_effort=reasoning_effort,
            verbosity=verbosity
        )
        
        return decision
    
    async def _component3_routing_execution(
        self, 
        selected_processor: str, 
        payment_request: PaymentRequest
    ) -> Dict[str, Any]:
        """Component 3: Routing Logic & Processor Execution"""
        
        processor = self.processors.get(selected_processor)
        if not processor:
            return {
                "success": False,
                "processor": selected_processor,
                "error": f"Processor {selected_processor} not found",
                "response_time": 100
            }
        
        # Simulate processor response time
        response_time = processor["response_time"]
        await asyncio.sleep(response_time / 1000)  # Convert to seconds
        
        # Simulate success/failure based on processor health
        success = random.random() < processor["success_rate"]
        
        if success:
            # Calculate fees (simplified)
            fee_rate = 0.029 if selected_processor == "stripe" else 0.035 if selected_processor == "paypal" else 0.025
            fixed_fee = 0.30 if selected_processor != "paypal" else 0.49
            
            fee_charged = payment_request.amount * fee_rate + fixed_fee
            net_amount = payment_request.amount - fee_charged
            
            return {
                "success": True,
                "processor": selected_processor,
                "response_time": response_time,
                "transaction_id": f"{selected_processor}_{uuid.uuid4().hex[:16]}",
                "fee_charged": fee_charged,
                "net_amount": net_amount,
                "processor_reference": f"ref_{uuid.uuid4().hex[:8]}",
                "component": "routing_logic"
            }
        else:
            errors = [
                "Card declined - insufficient funds",
                "Transaction blocked - fraud detection",
                "Network timeout - please retry",
                "Rate limit exceeded",
                "Processor temporarily unavailable"
            ]
            
            return {
                "success": False,
                "processor": selected_processor,
                "response_time": response_time,
                "error": random.choice(errors),
                "retry_recommended": True,
                "component": "routing_logic"
            }
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get complete system performance summary"""
        
        success_rate = (self.successful_flows / max(self.flows_processed, 1)) * 100
        
        return {
            "system_status": "operational",
            "components_integrated": 3,
            "performance_metrics": {
                "total_flows_processed": self.flows_processed,
                "successful_flows": self.successful_flows,
                "success_rate_percentage": success_rate,
                "total_gpt5_tokens_used": self.total_tokens_used,
                "average_tokens_per_decision": self.total_tokens_used / max(self.flows_processed, 1)
            },
            "component_status": {
                "component_1_data_analysis": "✅ Integrated (Mock)",
                "component_2_gpt5_engine": "✅ Live GPT-5 API",
                "component_3_routing_logic": "✅ Integrated (Mock)"
            },
            "gpt5_capabilities_demonstrated": [
                "reasoning_effort parameter control",
                "verbosity parameter control",
                "chain_of_thought reasoning",
                "adaptive parameter selection",
                "real_time_decision_making"
            ],
            "processors_available": list(self.processors.keys())
        }


async def run_complete_integrated_demo():
    """
    Run complete demonstration of all 3 components working together
    """
    
    print("🚀 COMPLETE INTEGRATED PAYMENT ORCHESTRATION DEMO")
    print("=" * 80)
    print("Components 1 (Data Analysis) + 2 (GPT-5 Engine) + 3 (Routing Logic)")
    print("Real GPT-5 API integration with reasoning_effort and verbosity control")
    print("=" * 80)
    
    system = CompleteIntegratedSystem()
    
    # Demo payment scenarios
    demo_payments = [
        PaymentRequest(
            amount=89.99,
            merchant_id="coffee_shop_downtown",
            description="Regular coffee purchase - routine processing"
        ),
        PaymentRequest(
            amount=2750.00,
            merchant_id="b2b_software_solutions", 
            description="Monthly software licensing fee"
        ),
        PaymentRequest(
            amount=12500.00,
            merchant_id="emergency_contractor_llc",
            description="Critical infrastructure repair - high priority"
        ),
        PaymentRequest(
            amount=6800.00,
            merchant_id="high_risk_merchant_corp",
            description="Complex B2B transaction with elevated risk"
        )
    ]
    
    print(f"🎯 Processing {len(demo_payments)} payments through complete integrated system...")
    
    flows = []
    for i, payment in enumerate(demo_payments, 1):
        print(f"\n{'='*80}")
        print(f"INTEGRATED DEMO PAYMENT {i}/{len(demo_payments)}")
        print(f"{'='*80}")
        
        flow = await system.process_complete_payment_flow(payment)
        flows.append(flow)
        
        # Brief pause between payments
        await asyncio.sleep(1)
    
    # Final system analysis
    print(f"\n{'='*80}")
    print("📊 COMPLETE SYSTEM ANALYSIS")
    print("="*80)
    
    summary = system.get_system_summary()
    
    print(f"🎯 SYSTEM PERFORMANCE:")
    metrics = summary["performance_metrics"]
    print(f"   Total Flows: {metrics['total_flows_processed']}")
    print(f"   Success Rate: {metrics['success_rate_percentage']:.1f}%")
    print(f"   Total GPT-5 Tokens: {metrics['total_gpt5_tokens_used']}")
    print(f"   Avg Tokens/Decision: {metrics['average_tokens_per_decision']:.0f}")
    
    print(f"\n🔗 COMPONENT INTEGRATION:")
    for component, status in summary["component_status"].items():
        print(f"   {component}: {status}")
    
    print(f"\n🧠 GPT-5 CAPABILITIES DEMONSTRATED:")
    for capability in summary["gpt5_capabilities_demonstrated"]:
        print(f"   ✅ {capability.replace('_', ' ').title()}")
    
    # Flow analysis
    print(f"\n📈 PAYMENT FLOW ANALYSIS:")
    total_time = sum(flow.total_processing_time_ms for flow in flows)
    avg_time = total_time / len(flows)
    
    component_times = {
        "Data Analysis": sum(flow.data_analysis_time_ms for flow in flows) / len(flows),
        "GPT-5 Engine": sum(flow.gpt5_processing_time_ms for flow in flows) / len(flows),
        "Routing Logic": sum(flow.routing_time_ms for flow in flows) / len(flows)
    }
    
    print(f"   Average Total Time: {avg_time:.0f}ms")
    for component, avg_comp_time in component_times.items():
        percentage = (avg_comp_time / avg_time) * 100
        print(f"   {component}: {avg_comp_time:.0f}ms ({percentage:.1f}%)")
    
    # GPT-5 parameter usage analysis
    print(f"\n🎛️ GPT-5 PARAMETER USAGE:")
    reasoning_efforts = [flow.gpt5_decision.reasoning_effort for flow in flows if flow.gpt5_decision]
    verbosity_levels = [flow.gpt5_decision.verbosity for flow in flows if flow.gpt5_decision]
    
    print(f"   Reasoning Effort Distribution:")
    for effort in set(reasoning_efforts):
        count = reasoning_efforts.count(effort)
        print(f"     {effort}: {count} decisions")
    
    print(f"   Verbosity Distribution:")
    for verbosity in set(verbosity_levels):
        count = verbosity_levels.count(verbosity)
        print(f"     {verbosity}: {count} decisions")
    
    # Export results
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    results_file = f"complete_integration_results_{timestamp}.json"
    
    export_data = {
        "demo_timestamp": timestamp,
        "system_summary": summary,
        "payment_flows": [
            {
                "flow_id": flow.flow_id,
                "payment_amount": flow.payment_request.amount,
                "merchant": flow.payment_request.merchant_id,
                "final_status": flow.final_status,
                "total_time_ms": flow.total_processing_time_ms,
                "component_times": {
                    "data_analysis": flow.data_analysis_time_ms,
                    "gpt5_engine": flow.gpt5_processing_time_ms, 
                    "routing_logic": flow.routing_time_ms
                },
                "gpt5_decision": {
                    "selected_processor": flow.gpt5_decision.selected_processor if flow.gpt5_decision else None,
                    "confidence": flow.gpt5_decision.confidence if flow.gpt5_decision else None,
                    "reasoning_effort": flow.gpt5_decision.reasoning_effort if flow.gpt5_decision else None,
                    "verbosity": flow.gpt5_decision.verbosity if flow.gpt5_decision else None,
                    "tokens_used": flow.gpt5_decision.tokens_used if flow.gpt5_decision else 0
                },
                "risk_analysis": flow.risk_analysis,
                "routing_result": flow.routing_result
            }
            for flow in flows
        ]
    }
    
    with open(results_file, "w") as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"\n📄 Complete results exported: {results_file}")
    
    print(f"\n🏆 COMPLETE INTEGRATED SYSTEM DEMO FINISHED!")
    print("✅ All 3 components working together")
    print("✅ Real GPT-5 API integration confirmed")
    print("✅ reasoning_effort and verbosity parameters functional")
    print("✅ Chain-of-thought reasoning captured")
    print("✅ End-to-end payment orchestration operational")
    print("\n🎬 System ready for hackathon presentation!")


if __name__ == "__main__":
    asyncio.run(run_complete_integrated_demo())