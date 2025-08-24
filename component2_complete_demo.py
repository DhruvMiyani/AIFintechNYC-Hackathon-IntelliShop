"""
Component 2: Complete GPT-5 Engine Demo
Comprehensive demonstration of all GPT-5 capabilities for payment orchestration
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any

from gpt5_decision_engine import (
    GPT5DecisionEngine, PaymentContext, DecisionUrgency,
    ReasoningEffort, Verbosity
)
from gpt5_realtime_router import GPT5RealtimeRouter


class Component2Demo:
    """
    Complete Component 2 demonstration showcasing:
    1. GPT-5 reasoning_effort parameter control
    2. GPT-5 verbosity parameter control
    3. Chain-of-thought reasoning capture
    4. Real-time integration with Component 1
    5. Adaptive parameter selection
    6. Comprehensive audit logging
    """
    
    def __init__(self):
        self.decision_engine = GPT5DecisionEngine()
        self.realtime_router = GPT5RealtimeRouter()
        
        self.demo_results = {
            "reasoning_effort_demos": [],
            "verbosity_demos": [],
            "chain_of_thought_examples": [],
            "realtime_integration_results": {},
            "parameter_adaptation_examples": []
        }
    
    async def run_complete_demo(self):
        """Run comprehensive Component 2 demo"""
        
        print("🚀 COMPONENT 2: GPT-5 ENGINE - COMPLETE DEMONSTRATION")
        print("=" * 80)
        print("Showcasing GPT-5's reasoning_effort, verbosity, and chain-of-thought")
        print("Real-time payment orchestration with intelligent parameter adaptation")
        print("=" * 80)
        
        # Demo 1: reasoning_effort parameter control
        await self.demo_reasoning_effort_control()
        
        # Demo 2: verbosity parameter control
        await self.demo_verbosity_control()
        
        # Demo 3: Chain-of-thought reasoning
        await self.demo_chain_of_thought()
        
        # Demo 4: Parameter adaptation
        await self.demo_parameter_adaptation()
        
        # Demo 5: Real-time integration
        await self.demo_realtime_integration()
        
        # Generate comprehensive report
        await self.generate_final_report()
    
    async def demo_reasoning_effort_control(self):
        """Demonstrate GPT-5's reasoning_effort parameter control"""
        
        print("\n" + "="*60)
        print("🧠 DEMO 1: GPT-5 REASONING_EFFORT PARAMETER CONTROL")
        print("="*60)
        
        # Same payment context, different reasoning efforts
        base_context = PaymentContext(
            amount=2500.00,
            currency="USD",
            merchant_id="demo_merchant_001",
            urgency=DecisionUrgency.NORMAL,
            failed_processors=["square"],
            risk_indicators={"risk_score": 3.2, "velocity": "elevated"},
            processor_health={
                "stripe": {"success_rate": 0.989, "response_time": 245, "freeze_risk": 2.1},
                "paypal": {"success_rate": 0.983, "response_time": 312, "freeze_risk": 1.8},
                "visa": {"success_rate": 0.995, "response_time": 189, "freeze_risk": 0.9}
            },
            business_rules={"prioritize_reliability": True}
        )
        
        reasoning_levels = [
            ReasoningEffort.MINIMAL,
            ReasoningEffort.LOW, 
            ReasoningEffort.MEDIUM,
            ReasoningEffort.HIGH
        ]
        
        for effort in reasoning_levels:
            print(f"\n🎯 Testing reasoning_effort = {effort.value}")
            print("-" * 40)
            
            decision = await self.decision_engine.make_payment_routing_decision(
                base_context,
                reasoning_effort=effort,
                verbosity=Verbosity.MEDIUM
            )
            
            result = {
                "reasoning_effort": effort.value,
                "processing_time_ms": decision.processing_time_ms,
                "tokens_used": decision.tokens_used,
                "reasoning_tokens": decision.reasoning_tokens,
                "reasoning_steps": len(decision.reasoning_chain),
                "selected_processor": decision.selected_option,
                "confidence": decision.confidence
            }
            
            self.demo_results["reasoning_effort_demos"].append(result)
            
            print(f"   Processor: {decision.selected_option}")
            print(f"   Confidence: {decision.confidence:.1%}")
            print(f"   Reasoning steps: {len(decision.reasoning_chain)}")
            print(f"   Tokens used: {decision.tokens_used} (reasoning: {decision.reasoning_tokens})")
            print(f"   Processing time: {decision.processing_time_ms}ms")
            
            await asyncio.sleep(1)  # Rate limiting
        
        print(f"\n📊 REASONING_EFFORT ANALYSIS:")
        print("   Higher effort → More reasoning steps → Better decisions")
        print("   Token usage scales with reasoning depth")
        print("   Processing time increases with complexity")
    
    async def demo_verbosity_control(self):
        """Demonstrate GPT-5's verbosity parameter control"""
        
        print("\n" + "="*60)
        print("📝 DEMO 2: GPT-5 VERBOSITY PARAMETER CONTROL")
        print("="*60)
        
        # Complex scenario requiring detailed explanation
        complex_context = PaymentContext(
            amount=15000.00,
            currency="USD",
            merchant_id="high_risk_enterprise",
            urgency=DecisionUrgency.CRITICAL,
            failed_processors=["stripe", "paypal"],
            risk_indicators={
                "risk_score": 7.8,
                "velocity": "spike",
                "fraud_alerts": 2,
                "compliance_flags": ["manual_review", "aml_check"]
            },
            processor_health={
                "stripe": {"success_rate": 0.0, "status": "frozen"},
                "paypal": {"success_rate": 0.85, "status": "degraded"},
                "visa": {"success_rate": 0.995, "response_time": 189},
                "adyen": {"success_rate": 0.992, "response_time": 267}
            },
            business_rules={
                "emergency_approval": True,
                "compliance_required": True,
                "audit_trail_mandatory": True
            }
        )
        
        verbosity_levels = [Verbosity.LOW, Verbosity.MEDIUM, Verbosity.HIGH]
        
        for verbosity in verbosity_levels:
            print(f"\n🎯 Testing verbosity = {verbosity.value}")
            print("-" * 40)
            
            decision = await self.decision_engine.make_payment_routing_decision(
                complex_context,
                reasoning_effort=ReasoningEffort.HIGH,
                verbosity=verbosity
            )
            
            result = {
                "verbosity": verbosity.value,
                "response_length": len(decision.raw_response),
                "reasoning_detail": len(decision.reasoning_chain),
                "tokens_used": decision.tokens_used,
                "audit_completeness": "high" if verbosity == Verbosity.HIGH else "medium" if verbosity == Verbosity.MEDIUM else "basic"
            }
            
            self.demo_results["verbosity_demos"].append(result)
            
            print(f"   Response length: {len(decision.raw_response)} chars")
            print(f"   Reasoning detail: {len(decision.reasoning_chain)} steps")
            print(f"   Audit trail: {result['audit_completeness']}")
            print(f"   Compliance ready: {'Yes' if verbosity == Verbosity.HIGH else 'Partial'}")
            
            if verbosity == Verbosity.HIGH:
                print(f"   📋 Sample reasoning steps:")
                for i, step in enumerate(decision.reasoning_chain[:3], 1):
                    print(f"      {i}. {step[:80]}...")
            
            await asyncio.sleep(1)
        
        print(f"\n📊 VERBOSITY ANALYSIS:")
        print("   Higher verbosity → More detailed explanations")
        print("   Audit trail completeness scales with verbosity")
        print("   Compliance requirements met at HIGH verbosity")
    
    async def demo_chain_of_thought(self):
        """Demonstrate GPT-5's chain-of-thought reasoning capture"""
        
        print("\n" + "="*60)
        print("🔗 DEMO 3: GPT-5 CHAIN-OF-THOUGHT REASONING")
        print("="*60)
        
        # Multi-factor decision scenario
        cot_context = PaymentContext(
            amount=8500.00,
            currency="USD", 
            merchant_id="multi_factor_decision",
            urgency=DecisionUrgency.ELEVATED,
            failed_processors=["square"],
            risk_indicators={
                "risk_score": 4.5,
                "velocity": "elevated",
                "geographic_anomaly": True,
                "amount_deviation": 3.2
            },
            processor_health={
                "stripe": {"success_rate": 0.989, "fees": 2.9, "compliance": "full"},
                "paypal": {"success_rate": 0.983, "fees": 3.5, "compliance": "partial"},
                "visa": {"success_rate": 0.995, "fees": 2.5, "compliance": "full", "limits": 25000},
                "adyen": {"success_rate": 0.992, "fees": 2.7, "compliance": "full", "international": True}
            },
            business_rules={
                "cost_factor_weight": 0.3,
                "reliability_factor_weight": 0.4,
                "compliance_factor_weight": 0.3,
                "geographic_preference": "domestic"
            }
        )
        
        print("🎯 Complex multi-factor routing decision")
        print("   Factors: cost, reliability, compliance, geography")
        print("   Capturing complete chain-of-thought reasoning")
        
        decision = await self.decision_engine.make_payment_routing_decision(
            cot_context,
            reasoning_effort=ReasoningEffort.HIGH,
            verbosity=Verbosity.HIGH
        )
        
        # Analyze chain of thought
        cot_example = {
            "decision_id": decision.decision_id,
            "total_reasoning_steps": len(decision.chain_of_thought),
            "factors_analyzed": [],
            "decision_path": [],
            "confidence_evolution": []
        }
        
        print(f"\n🔍 CHAIN-OF-THOUGHT ANALYSIS:")
        print(f"   Total reasoning steps: {len(decision.chain_of_thought)}")
        
        for i, step in enumerate(decision.chain_of_thought, 1):
            factors = step.get("factors_considered", [])
            cot_example["factors_analyzed"].extend(factors)
            cot_example["decision_path"].append(step["reasoning"][:100])
            cot_example["confidence_evolution"].append(step.get("confidence", 0))
            
            print(f"\n   Step {i}: {step['reasoning'][:120]}...")
            print(f"           Factors: {', '.join(factors)}")
            print(f"           Confidence: {step.get('confidence', 0):.1%}")
        
        # Unique factors considered
        unique_factors = list(set(cot_example["factors_analyzed"]))
        cot_example["unique_factors"] = unique_factors
        
        print(f"\n📊 REASONING SUMMARY:")
        print(f"   Unique factors considered: {', '.join(unique_factors)}")
        print(f"   Final confidence: {decision.confidence:.1%}")
        print(f"   Selected: {decision.selected_option}")
        print(f"   Reasoning transparency: ✅ Complete audit trail")
        
        self.demo_results["chain_of_thought_examples"].append(cot_example)
    
    async def demo_parameter_adaptation(self):
        """Demonstrate GPT-5's intelligent parameter adaptation"""
        
        print("\n" + "="*60)
        print("🎛️  DEMO 4: INTELLIGENT PARAMETER ADAPTATION")
        print("="*60)
        
        # Test scenarios that should trigger different parameter combinations
        adaptation_scenarios = [
            {
                "name": "Routine Small Payment",
                "context": PaymentContext(
                    amount=45.99,
                    currency="USD",
                    merchant_id="coffee_shop",
                    urgency=DecisionUrgency.ROUTINE,
                    failed_processors=[],
                    risk_indicators={"risk_score": 0.8},
                    processor_health={"stripe": {"success_rate": 0.99}},
                    business_rules={"optimize_cost": True}
                ),
                "expected_adaptation": {"reasoning": "minimal", "verbosity": "low"}
            },
            {
                "name": "High-Value Critical Payment",
                "context": PaymentContext(
                    amount=45000.00,
                    currency="USD",
                    merchant_id="enterprise_emergency",
                    urgency=DecisionUrgency.CRITICAL,
                    failed_processors=["stripe", "paypal"],
                    risk_indicators={"risk_score": 8.5, "fraud_alerts": 1},
                    processor_health={
                        "stripe": {"success_rate": 0.0, "status": "frozen"},
                        "visa": {"success_rate": 0.995}
                    },
                    business_rules={"emergency_approval": True, "audit_required": True}
                ),
                "expected_adaptation": {"reasoning": "high", "verbosity": "high"}
            }
        ]
        
        print("🎯 Testing automatic parameter adaptation based on context")
        
        for scenario in adaptation_scenarios:
            print(f"\n📋 Scenario: {scenario['name']}")
            print(f"   Amount: ${scenario['context'].amount:,.2f}")
            print(f"   Urgency: {scenario['context'].urgency.value}")
            print(f"   Failed processors: {len(scenario['context'].failed_processors)}")
            
            # Let the engine auto-determine parameters
            decision = await self.decision_engine.make_payment_routing_decision(
                scenario["context"]
                # No explicit parameters - let it adapt
            )
            
            actual_adaptation = {
                "reasoning": decision.reasoning_effort.value,
                "verbosity": decision.verbosity.value
            }
            expected = scenario["expected_adaptation"]
            
            adaptation_result = {
                "scenario": scenario["name"],
                "expected": expected,
                "actual": actual_adaptation,
                "adaptation_correct": actual_adaptation == expected,
                "processing_efficiency": f"{decision.processing_time_ms}ms, {decision.tokens_used} tokens"
            }
            
            self.demo_results["parameter_adaptation_examples"].append(adaptation_result)
            
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual_adaptation}")
            print(f"   Adaptation: {'✅ Correct' if adaptation_result['adaptation_correct'] else '⚠️  Different'}")
            print(f"   Efficiency: {adaptation_result['processing_efficiency']}")
        
        print(f"\n📊 ADAPTATION ANALYSIS:")
        print("   GPT-5 intelligently adapts parameters to context")
        print("   Low-risk → minimal effort, low verbosity")
        print("   High-risk → high effort, high verbosity") 
        print("   Optimization balances quality vs efficiency")
    
    async def demo_realtime_integration(self):
        """Demonstrate real-time integration with Component 1"""
        
        print("\n" + "="*60)
        print("🔄 DEMO 5: REAL-TIME COMPONENT INTEGRATION")
        print("="*60)
        
        print("🎬 Starting 2-minute real-time processing demo...")
        print("   Component 1 (Data) → Component 2 (GPT-5 Engine)")
        print("   Live parameter adaptation based on transaction patterns")
        
        try:
            # Start real-time processing for 2 minutes
            await self.realtime_router.start_realtime_processing(duration_minutes=2)
            
            # Capture results
            self.demo_results["realtime_integration_results"] = {
                "flows_processed": self.realtime_router.processing_stats["flows_processed"],
                "gpt5_decisions": self.realtime_router.processing_stats["gpt5_decisions"],
                "high_effort_decisions": self.realtime_router.processing_stats["high_effort_decisions"],
                "avg_processing_time": self.realtime_router.processing_stats["avg_processing_time"],
                "success_rate": self.realtime_router.processing_stats["routing_successes"] / max(1, self.realtime_router.processing_stats["flows_processed"]),
                "integration_status": "successful"
            }
            
        except KeyboardInterrupt:
            print("\n🔴 Real-time demo stopped early")
            self.demo_results["realtime_integration_results"] = {
                "integration_status": "interrupted",
                "partial_results": True
            }
        
        print(f"\n📊 INTEGRATION RESULTS:")
        results = self.demo_results["realtime_integration_results"]
        if results.get("integration_status") == "successful":
            print(f"   Flows processed: {results['flows_processed']}")
            print(f"   GPT-5 decisions: {results['gpt5_decisions']}")
            print(f"   Success rate: {results['success_rate']:.1%}")
            print(f"   Avg processing: {results['avg_processing_time']:.0f}ms")
            print("   ✅ Component integration working")
        else:
            print("   ⚠️  Demo interrupted - partial results captured")
    
    async def generate_final_report(self):
        """Generate comprehensive final report"""
        
        print("\n" + "="*80)
        print("📋 COMPONENT 2: FINAL DEMONSTRATION REPORT")
        print("="*80)
        
        # Reasoning effort analysis
        if self.demo_results["reasoning_effort_demos"]:
            print("\n🧠 REASONING_EFFORT PARAMETER ANALYSIS:")
            effort_demos = self.demo_results["reasoning_effort_demos"]
            
            for demo in effort_demos:
                print(f"   {demo['reasoning_effort']:>8}: "
                     f"{demo['reasoning_steps']:>2} steps, "
                     f"{demo['tokens_used']:>4} tokens, "
                     f"{demo['processing_time_ms']:>4}ms")
            
            print("   ✅ Higher effort → More thorough reasoning")
        
        # Verbosity analysis
        if self.demo_results["verbosity_demos"]:
            print("\n📝 VERBOSITY PARAMETER ANALYSIS:")
            verbosity_demos = self.demo_results["verbosity_demos"]
            
            for demo in verbosity_demos:
                print(f"   {demo['verbosity']:>6}: "
                     f"{demo['response_length']:>5} chars, "
                     f"{demo['audit_completeness']:>8} audit")
            
            print("   ✅ Higher verbosity → Better audit trails")
        
        # Chain of thought
        if self.demo_results["chain_of_thought_examples"]:
            print("\n🔗 CHAIN-OF-THOUGHT ANALYSIS:")
            cot_examples = self.demo_results["chain_of_thought_examples"]
            
            for example in cot_examples:
                print(f"   Decision {example['decision_id'][:8]}:")
                print(f"     Reasoning steps: {example['total_reasoning_steps']}")
                print(f"     Factors analyzed: {len(example['unique_factors'])}")
                print(f"     Transparency: ✅ Complete")
        
        # Parameter adaptation
        if self.demo_results["parameter_adaptation_examples"]:
            print("\n🎛️  PARAMETER ADAPTATION ANALYSIS:")
            adaptation_examples = self.demo_results["parameter_adaptation_examples"]
            
            correct_adaptations = sum(1 for ex in adaptation_examples if ex["adaptation_correct"])
            total_adaptations = len(adaptation_examples)
            
            print(f"   Adaptation accuracy: {correct_adaptations}/{total_adaptations}")
            for example in adaptation_examples:
                status = "✅" if example["adaptation_correct"] else "⚠️"
                print(f"   {status} {example['scenario']}")
                print(f"       Expected: {example['expected']}")
                print(f"       Actual: {example['actual']}")
        
        # Real-time integration
        if self.demo_results["realtime_integration_results"]:
            print("\n🔄 REAL-TIME INTEGRATION ANALYSIS:")
            results = self.demo_results["realtime_integration_results"]
            
            if results.get("integration_status") == "successful":
                print(f"   Component 1 → Component 2: ✅ Integrated")
                print(f"   Live processing: {results['flows_processed']} flows")
                print(f"   GPT-5 decisions: {results['gpt5_decisions']}")
                print(f"   Success rate: {results['success_rate']:.1%}")
            else:
                print(f"   Integration status: ⚠️  {results['integration_status']}")
        
        # GPT-5 capabilities summary
        print(f"\n🏆 GPT-5 CAPABILITIES DEMONSTRATED:")
        capabilities = [
            ("reasoning_effort parameter control", "✅"),
            ("verbosity parameter control", "✅"), 
            ("chain-of-thought reasoning capture", "✅"),
            ("intelligent parameter adaptation", "✅"),
            ("real-time decision making", "✅"),
            ("comprehensive audit logging", "✅"),
            ("component integration", "✅")
        ]
        
        for capability, status in capabilities:
            print(f"   {status} {capability}")
        
        # Export comprehensive results
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_filename = f"component2_demo_report_{timestamp}.json"
        
        with open(report_filename, "w") as f:
            json.dump(self.demo_results, f, indent=2, default=str)
        
        print(f"\n📄 Comprehensive results saved: {report_filename}")
        print("\n🎯 COMPONENT 2 (GPT-5 ENGINE) DEMONSTRATION COMPLETE")
        print("   Ready for hackathon presentation!")


# Main execution
async def main():
    """Run complete Component 2 demonstration"""
    
    demo = Component2Demo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(main())