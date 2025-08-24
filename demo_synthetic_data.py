"""
GPT-5 Synthetic Data Generation Demo
Shows GPT-5's capabilities for generating realistic Stripe transaction patterns
"""

import asyncio
import httpx
import json
from datetime import datetime


async def run_synthetic_data_demo():
    """Demonstrate GPT-5's synthetic data generation capabilities."""
    
    base_url = "http://localhost:8000"
    
    print("\n" + "="*70)
    print("GPT-5 SYNTHETIC STRIPE DATA GENERATION DEMO")
    print("Solving: Realistic transaction patterns for testing & analysis")
    print("="*70)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Demo 1: Normal baseline data generation
        print("\n" + "-"*50)
        print("DEMO 1: Normal Business Baseline (GPT-5 Structured Generation)")
        print("-"*50)
        
        request = {
            "pattern_type": "normal",
            "days": 30,
            "daily_volume": 50,
            "reasoning_effort": "minimal"  # Fast generation for baseline
        }
        
        response = await client.post(f"{base_url}/data/generate", json=request)
        result = response.json()
        
        print(f"✅ Generated {result['transaction_count']} normal transactions")
        print(f"   Period: {result['period_days']} days")
        print(f"   Daily average: {result['daily_average']:.1f} transactions")
        print(f"   Average amount: ${result['summary']['avg_amount']:.2f}")
        print(f"   Refund rate: {result['summary']['refund_rate']:.1f}% (normal)")
        print(f"   GPT-5 reasoning effort: {request['reasoning_effort']}")
        
        # Demo 2: Volume spike scenario (freeze trigger)
        print("\n" + "-"*50)
        print("DEMO 2: Volume Spike Scenario (High GPT-5 Reasoning)")
        print("This pattern typically triggers Stripe account freeze")
        print("-"*50)
        
        request = {
            "pattern_type": "sudden_spike",
            "reasoning_effort": "high"  # Complex pattern needs deep reasoning
        }
        
        response = await client.post(f"{base_url}/data/generate", json=request)
        result = response.json()
        
        print(f"🚨 Generated volume spike: {result['transaction_count']} transactions")
        print(f"   Risk level: {result['freeze_likelihood']}")
        print(f"   Charges: {result['risk_indicators']['charges']}")
        print(f"   Sample large amounts: ", end="")
        for txn in result['sample_transactions'][:3]:
            print(f"${txn['amount']/100:.0f}", end=" ")
        print("")
        print(f"   GPT-5 analysis: Pattern recognition + Risk modeling")
        print("   ⚠️  This would trigger Stripe freeze within 24 hours")
        
        # Demo 3: High refund rate scenario
        print("\n" + "-"*50)
        print("DEMO 3: High Refund Rate Scenario")
        print("Refund rate >5% triggers Stripe review")
        print("-"*50)
        
        request = {
            "pattern_type": "high_refund_rate",
            "reasoning_effort": "high"
        }
        
        response = await client.post(f"{base_url}/data/generate", json=request)
        result = response.json()
        
        print(f"🔄 Generated refund surge pattern")
        print(f"   Total transactions: {result['transaction_count']}")
        print(f"   Charges: {result['risk_indicators']['charges']}")
        print(f"   Refunds: {result['risk_indicators']['refunds']}")
        print(f"   Refund rate: {result['risk_indicators']['refund_rate']:.1f}% (HIGH)")
        print("   Normal refund rate: ~2%")
        print("   ⚠️  This triggers immediate Stripe investigation")
        
        # Demo 4: Chargeback pattern (most serious)
        print("\n" + "-"*50)
        print("DEMO 4: Chargeback Surge (Critical Risk)")
        print("Chargeback rate >1% triggers immediate freeze + 180-day hold")
        print("-"*50)
        
        request = {
            "pattern_type": "chargeback_surge",
            "reasoning_effort": "high"
        }
        
        response = await client.post(f"{base_url}/data/generate", json=request)
        result = response.json()
        
        print(f"💥 Generated chargeback pattern")
        print(f"   Total transactions: {result['transaction_count']}")
        print(f"   Charges: {result['risk_indicators']['charges']}")
        print(f"   Chargebacks: {result['risk_indicators']['adjustments']}")
        print(f"   Chargeback rate: {result['risk_indicators']['chargeback_rate']:.1f}%")
        print("   Stripe threshold: 1.0%")
        print("   🚫 CRITICAL: Immediate account freeze + fund hold")
        
        # Demo 5: Complete dataset with all scenarios
        print("\n" + "-"*50)
        print("DEMO 5: Complete Dataset Generation")
        print("GPT-5 generates comprehensive test data")
        print("-"*50)
        
        response = await client.get(f"{base_url}/data/demo/complete-dataset")
        result = response.json()
        
        print(f"📊 Complete dataset generated:")
        print(f"   Total transactions: {result['total_transactions']:,}")
        print(f"   Baseline period: {result['baseline_stats']['period']}")
        print(f"   Baseline average: ${result['baseline_stats']['avg_amount']:.2f}")
        print("")
        print("   Freeze scenarios included:")
        
        for scenario, data in result['scenario_breakdown'].items():
            risk_emoji = "🚨" if data['freeze_risk'] == 'high' else "⚠️"
            print(f"   {risk_emoji} {scenario}: {data['transaction_count']} transactions")
            if data['refund_rate'] > 0:
                print(f"      → Refund rate: {data['refund_rate']:.1f}%")
            if data['chargeback_rate'] > 0:
                print(f"      → Chargeback rate: {data['chargeback_rate']:.1f}%")
        
        print("\n" + "="*50)
        print("GPT-5 CAPABILITIES DEMONSTRATED")
        print("="*50)
        
        capabilities = result['gpt5_capabilities_demonstrated']
        for i, capability in enumerate(capabilities, 1):
            print(f"{i}. {capability}")
        
        # Demo 6: Risk analysis of generated data
        print("\n" + "-"*50)
        print("DEMO 6: GPT-5 Risk Analysis")
        print("Analyzing the chargeback scenario for freeze risk")
        print("-"*50)
        
        # Get some sample transactions for analysis
        sample_transactions = result['stripe_format_sample']
        
        analysis_request = {
            "transactions": sample_transactions,
            "analysis_type": "freeze_risk",
            "reasoning_effort": "high"
        }
        
        response = await client.post(f"{base_url}/data/analyze", json=analysis_request)
        analysis = response.json()
        
        print(f"🧠 GPT-5 Risk Analysis Results:")
        print(f"   Risk level: {analysis['risk_level'].upper()}")
        print(f"   Risk score: {analysis['risk_score']:.1f}/100")
        print(f"   Freeze probability: {analysis['freeze_probability']*100:.0f}%")
        print(f"   Analysis time: {analysis['analysis_time_ms']:.0f}ms")
        
        if analysis['detected_patterns']:
            print("   Detected patterns:")
            for pattern in analysis['detected_patterns']:
                print(f"   → {pattern}")
        
        if analysis['recommendations']:
            print("   Recommendations:")
            for rec in analysis['recommendations'][:2]:  # Show first 2
                print(f"   → {rec}")
        
        print("\n" + "="*50)
        print("HACKATHON SCORING HIGHLIGHTS")
        print("="*50)
        
        print("✅ GPT-5 in Development:")
        print("   • Code generation for data structures")
        print("   • Schema-compliant synthetic data creation")
        print("   • Automated pattern generation")
        
        print("\n✅ GPT-5 in Project:")
        print("   • Runtime risk analysis with reasoning")
        print("   • reasoning_effort control (minimal/high)")
        print("   • verbosity control for different outputs")
        print("   • Context-aware pattern recognition")
        print("   • Long context analysis (2K+ transactions)")
        
        print("\n💡 Business Value:")
        print("   • Test payment systems without real money")
        print("   • Understand Stripe freeze triggers")
        print("   • Proactively avoid account issues")
        print("   • Train ML models on realistic data")


if __name__ == "__main__":
    print("\nStarting GPT-5 Synthetic Data Demo...")
    print("Make sure the server is running: ./start_server.sh")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        asyncio.run(run_synthetic_data_demo())
        print("\n\n🎉 Demo completed! Check out the API docs at http://localhost:8000/docs")
    except KeyboardInterrupt:
        print("\n\nDemo stopped.")
    except httpx.ConnectError:
        print("\n❌ Could not connect to server. Please run: ./start_server.sh")