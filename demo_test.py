"""
Test GPT-5 components without API key for hackathon demo
"""

import asyncio
from processor_registry import ProcessorRegistry
from synthetic_data_generator import GPT5SyntheticDataGenerator

async def test_processor_registry():
    """Test processor registry functionality."""
    
    print("🧪 TESTING: Processor Registry")
    print("=" * 40)
    
    registry = ProcessorRegistry()
    
    # Test normal status
    context = {
        "amount": 450.00,
        "currency": "USD",
        "merchant_id": "test_merchant"
    }
    
    data = await registry.get_processor_for_gpt5_analysis(context)
    print("✅ Initial processor status:")
    print(registry.export_for_gpt5_prompt(context))
    
    # Test freeze simulation
    await registry.simulate_processor_failure("stripe", "freeze")
    print("🚨 After Stripe freeze:")
    print(registry.export_for_gpt5_prompt(context))
    
    # Test fallback chain
    fallbacks = registry.get_fallback_chain("stripe", context)
    print(f"🔄 Fallback chain: {' → '.join(fallbacks)}")
    
    return True

async def test_synthetic_data():
    """Test synthetic data generation."""
    
    print("\n🧪 TESTING: Synthetic Data Generator")
    print("=" * 40)
    
    # Mock generator without OpenAI API
    generator = GPT5SyntheticDataGenerator()
    generator.gpt5_client = None  # Disable API calls
    
    # Test basic transaction generation  
    baseline = await generator.generate_normal_baseline(days=5, daily_volume=10)
    print(f"✅ Generated {len(baseline)} baseline transactions")
    
    # Test risk scenario
    risk_txns = await generator._generate_volume_spike(baseline[0].created if baseline else None)
    print(f"⚠️ Generated {len(risk_txns)} volume spike transactions")
    
    # Test real-time feed simulation (1 minute demo)
    print("🔴 Testing real-time feed (30 seconds)...")
    count = 0
    async for batch in generator.generate_real_time_stripe_feed(duration_minutes=0.5, events_per_minute=10):
        count += len(batch["events"])
        print(f"   Batch: {len(batch['events'])} events, Risk score: {batch['risk_indicators']['risk_score']:.1f}")
        if batch["gpt5_analysis_needed"]:
            print("   🧠 GPT-5 analysis triggered!")
        
        if count > 25:  # Limit for demo
            break
    
    print(f"✅ Real-time feed generated {count} events")
    return True

async def test_integration():
    """Test component integration."""
    
    print("\n🧪 TESTING: Component Integration")  
    print("=" * 40)
    
    # Test processor registry + synthetic data
    registry = ProcessorRegistry()
    generator = GPT5SyntheticDataGenerator()
    generator.gpt5_client = None
    
    # Generate some risk data
    risk_batch = await generator._inject_risk_scenario()
    print(f"⚠️ Generated {len(risk_batch)} risk events")
    
    # Check if it would trigger GPT-5 analysis
    needs_analysis = generator._should_trigger_gpt5_analysis(risk_batch)
    print(f"🧠 GPT-5 analysis needed: {needs_analysis}")
    
    if needs_analysis:
        # Simulate processor selection logic
        context = {"amount": 1500, "risk_events": len(risk_batch)}
        processor_data = await registry.get_processor_for_gpt5_analysis(context)
        
        # Find best processor
        best_proc = min(
            processor_data["available_processors"].items(),
            key=lambda x: x[1]["health_metrics"]["freeze_risk"].split("/")[0]
        )
        
        print(f"📊 Best processor: {best_proc[0]} (risk: {best_proc[1]['health_metrics']['freeze_risk']})")
    
    return True

async def main():
    """Run all tests."""
    
    print("🚀 GPT-5 PAYMENT ORCHESTRATION - COMPONENT TESTS")
    print("=" * 60)
    
    try:
        # Test individual components
        await test_processor_registry()
        await test_synthetic_data()
        await test_integration()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("🎯 Ready for GPT-5 API integration")
        print("📋 Components working:")
        print("   • Processor Registry with Health Monitoring")
        print("   • Real-time Synthetic Data Generation")
        print("   • GPT-5 Analysis Triggering Logic")
        print("   • Fallback Chain Generation")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())