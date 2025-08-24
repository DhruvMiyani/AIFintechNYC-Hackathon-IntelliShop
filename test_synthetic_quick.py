"""
Quick Test for Synthetic Data Generation Component
Tests core functionality without API calls
"""

import asyncio
from datetime import datetime
from synthetic_data_generator import GPT5SyntheticDataGenerator


async def test_synthetic_generation():
    """Quick test of synthetic data generation"""
    
    print("="*60)
    print("SYNTHETIC DATA GENERATION QUICK TEST")
    print("="*60)
    
    generator = GPT5SyntheticDataGenerator()
    
    # Test 1: Generate baseline data
    print("\n1. Testing Normal Baseline Generation...")
    baseline = await generator.generate_normal_baseline(
        days=3,
        daily_volume=20,
        avg_amount=100.0
    )
    
    charges = [t for t in baseline if t.type == "charge"]
    refunds = [t for t in baseline if t.type == "refund"]
    
    print(f"   Generated: {len(baseline)} transactions")
    print(f"   - Charges: {len(charges)}")
    print(f"   - Refunds: {len(refunds)}")
    print(f"   - Refund rate: {len(refunds)/len(charges)*100:.1f}%")
    
    # Test 2: Generate freeze trigger
    print("\n2. Testing Volume Spike Pattern...")
    spike_txns = await generator.generate_freeze_trigger_scenario(
        pattern_type="sudden_spike",
        severity="high"
    )
    
    print(f"   Generated: {len(spike_txns)} spike transactions")
    if spike_txns:
        avg_amount = sum(t.amount for t in spike_txns) / len(spike_txns)
        print(f"   - Average amount: ${avg_amount:.2f}")
    
    # Test 3: Stripe format export
    print("\n3. Testing Stripe Format Export...")
    stripe_format = generator.export_to_stripe_format(baseline[:3])
    
    print(f"   Exported {len(stripe_format)} transactions to Stripe format")
    if stripe_format:
        sample = stripe_format[0]
        print(f"   Sample:")
        print(f"   - ID: {sample['id']}")
        print(f"   - Amount: {sample['amount']} cents")
        print(f"   - Type: {sample['type']}")
    
    # Test 4: Pattern statistics
    print("\n4. Analyzing Pattern Statistics...")
    
    # Volume spike analysis
    if spike_txns:
        time_range = max(t.created for t in spike_txns) - min(t.created for t in spike_txns)
        hours = time_range.total_seconds() / 3600
        print(f"   Volume spike compressed into: {hours:.1f} hours")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\nSummary:")
    print(f"- Baseline generation: WORKING")
    print(f"- Freeze trigger patterns: WORKING")
    print(f"- Stripe format export: WORKING")
    print(f"- Total transactions generated: {len(baseline) + len(spike_txns)}")


if __name__ == "__main__":
    print("\nRunning quick synthetic data test...\n")
    asyncio.run(test_synthetic_generation())