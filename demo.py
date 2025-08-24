"""
Demo script showing GPT-5 intelligent payment routing in action
"""

import asyncio
import httpx
import json
from datetime import datetime


async def run_demo():
    """Run demo scenarios showing intelligent routing."""
    
    base_url = "http://localhost:8000"
    
    print("\n" + "="*60)
    print("GPT-5 PAYMENT ORCHESTRATION DEMO")
    print("Solving: Automatic fallback when processors fail")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        
        # Check system status
        print("\n1. Checking system status...")
        response = await client.get(f"{base_url}/")
        print(f"System: {response.json()['status']}")
        print(f"Active processors: {response.json()['active_processors']}")
        
        # Scenario 1: Normal payment
        print("\n" + "-"*40)
        print("SCENARIO 1: Normal Payment ($50)")
        print("-"*40)
        
        payment = {
            "amount": 50.00,
            "currency": "USD",
            "description": "Standard B2B payment"
        }
        
        response = await client.post(f"{base_url}/payments/process", json=payment)
        result = response.json()
        
        print(f"✓ Payment {'successful' if result['success'] else 'failed'}")
        print(f"  Processor used: {result['processor_used']}")
        print(f"  GPT-5 reasoning (minimal effort): {result['reasoning'][:100]}...")
        print(f"  Processing time: {result['processing_time_ms']:.0f}ms")
        
        # Scenario 2: Stripe account frozen
        print("\n" + "-"*40)
        print("SCENARIO 2: Stripe Account Frozen")
        print("-"*40)
        print("Simulating Stripe account freeze (common issue)...")
        
        # Freeze Stripe
        await client.post(f"{base_url}/processors/stripe/freeze")
        print("❌ Stripe account frozen!")
        
        # Try payment
        payment = {
            "amount": 250.00,
            "currency": "USD",
            "description": "Payment during Stripe freeze"
        }
        
        response = await client.post(f"{base_url}/payments/process", json=payment)
        result = response.json()
        
        print(f"\n✓ Payment {'successful' if result['success'] else 'failed'}")
        print(f"  Processor used: {result['processor_used']} (automatic fallback)")
        print(f"  GPT-5 reasoning (high effort): {result['reasoning']}")
        print(f"  Fallback attempted: {result['fallback_attempted']}")
        
        # Unfreeze Stripe
        await client.post(f"{base_url}/processors/stripe/unfreeze")
        print("\n✓ Stripe account restored")
        
        # Scenario 3: High-value transaction
        print("\n" + "-"*40)
        print("SCENARIO 3: High-Value Transaction ($25,000)")
        print("-"*40)
        
        payment = {
            "amount": 25000.00,
            "currency": "USD",
            "description": "Large B2B payment",
            "metadata": {
                "invoice_id": "INV-2024-LARGE",
                "customer_tier": "enterprise"
            }
        }
        
        response = await client.post(f"{base_url}/payments/process", json=payment)
        result = response.json()
        
        print(f"✓ Payment {'successful' if result['success'] else 'failed'}")
        print(f"  Processor used: {result['processor_used']}")
        print(f"  GPT-5 reasoning (high effort): {result['reasoning']}")
        print(f"  Fees: ${result.get('fees', 0):.2f}")
        
        # Scenario 4: Multiple processor failures
        print("\n" + "-"*40)
        print("SCENARIO 4: Cascading Failures")
        print("-"*40)
        
        # Freeze multiple processors
        await client.post(f"{base_url}/processors/stripe/freeze")
        print("❌ Stripe frozen")
        
        payment = {
            "amount": 500.00,
            "currency": "USD",
            "description": "Payment with multiple failures"
        }
        
        response = await client.post(f"{base_url}/payments/process", json=payment)
        result = response.json()
        
        print(f"\n✓ Payment {'successful' if result['success'] else 'failed'}")
        print(f"  Final processor: {result['processor_used']}")
        print(f"  GPT-5 handled fallback chain")
        print(f"  Reasoning: {result['reasoning']}")
        
        # Restore processors
        await client.post(f"{base_url}/processors/stripe/unfreeze")
        
        # Show analytics
        print("\n" + "-"*40)
        print("ROUTING ANALYTICS")
        print("-"*40)
        
        response = await client.get(f"{base_url}/analytics/routing")
        analytics = response.json()
        
        print(f"Total routing decisions: {analytics.get('total_routing_decisions', 0)}")
        print(f"Reasoning effort distribution: {analytics.get('reasoning_effort_distribution', {})}")
        print(f"Average decision times:")
        for effort, time in analytics.get('average_decision_time_ms', {}).get('by_effort', {}).items():
            print(f"  {effort}: {time:.0f}ms")
        
        # Show processor health
        print("\n" + "-"*40)
        print("PROCESSOR HEALTH STATUS")
        print("-"*40)
        
        response = await client.get(f"{base_url}/processors/health")
        health_data = response.json()
        
        for processor in health_data:
            print(f"\n{processor['processor_id'].upper()}:")
            print(f"  Status: {processor['status']}")
            print(f"  Success rate: {processor['recent_performance']['success_rate']:.1f}%")
            print(f"  Uptime: {processor['recent_performance']['uptime_percentage']:.1f}%")
            print(f"  Avg latency: {processor['recent_performance']['average_latency_ms']:.0f}ms")
            print(f"  Fee: {processor['capabilities']['fee_percentage']}%")


async def simulate_real_world():
    """Simulate real-world payment flow with various scenarios."""
    
    base_url = "http://localhost:8000"
    
    print("\n" + "="*60)
    print("REAL-WORLD SIMULATION")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        
        # Simulate a day of payments with various scenarios
        scenarios = [
            {"amount": 10, "description": "Small payment - minimal reasoning"},
            {"amount": 99, "description": "Standard payment"},
            {"amount": 500, "description": "Medium payment"},
            {"amount": 5000, "description": "Large payment - high reasoning"},
            {"amount": 25, "description": "Micro payment"},
            {"amount": 1500, "description": "Business invoice"},
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\nPayment {i}: ${scenario['amount']} - {scenario['description']}")
            
            payment = {
                "amount": scenario["amount"],
                "currency": "USD",
                "description": scenario["description"]
            }
            
            response = await client.post(f"{base_url}/payments/process", json=payment)
            result = response.json()
            
            print(f"  → Processor: {result['processor_used']}")
            print(f"  → Time: {result['processing_time_ms']:.0f}ms")
            print(f"  → Success: {'✓' if result['success'] else '✗'}")
            
            await asyncio.sleep(0.5)  # Simulate time between payments


if __name__ == "__main__":
    print("\nStarting GPT-5 Payment Router Demo...")
    print("Make sure the server is running: python main.py")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        asyncio.run(run_demo())
        print("\n\nWould you like to see the real-world simulation? (y/n): ", end="")
        if input().lower() == 'y':
            asyncio.run(simulate_real_world())
    except KeyboardInterrupt:
        print("\n\nDemo stopped.")
    except httpx.ConnectError:
        print("\n❌ Could not connect to server. Please run: python main.py")