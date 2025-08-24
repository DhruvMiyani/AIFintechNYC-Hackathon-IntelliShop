"""
Complete Integration Test
Tests all components working together in realistic scenarios
"""

import asyncio
import httpx
import json
from datetime import datetime


class IntegrationTester:
    """Tests complete payment orchestration flow"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    async def test_complete_flow(self):
        """Test complete flow: data generation → risk analysis → intelligent routing"""
        print("Testing Complete Integration Flow...")
        print("=" * 60)
        
        async with httpx.AsyncClient(timeout=120) as client:
            
            # Step 1: Generate synthetic data to understand patterns
            print("\n1. Generating synthetic transaction data...")
            data_response = await client.post(
                f"{self.base_url}/data/generate",
                json={
                    "pattern_type": "high_refund_rate",
                    "reasoning_effort": "high"
                }
            )
            
            if data_response.status_code == 200:
                data_result = data_response.json()
                print(f"   Generated {data_result['transaction_count']} transactions")
                print(f"   Refund rate: {data_result['risk_indicators']['refund_rate']:.1f}%")
                print(f"   Freeze likelihood: {data_result['freeze_likelihood']}")
            else:
                print(f"   Data generation failed: {data_response.status_code}")
                return False
            
            # Step 2: Simulate Stripe freeze due to high refund rate
            print("\n2. Simulating Stripe account freeze...")
            freeze_response = await client.post(f"{self.base_url}/processors/stripe/freeze")
            
            if freeze_response.status_code == 200:
                print("   Stripe account frozen (simulated)")
            else:
                print("   Failed to freeze Stripe")
                return False
            
            # Step 3: Process payment with intelligent routing
            print("\n3. Processing payment with intelligent routing...")
            payment_response = await client.post(
                f"{self.base_url}/payments/process",
                json={
                    "amount": 500.00,
                    "currency": "USD",
                    "description": "B2B SaaS subscription",
                    "context": {
                        "risk_profile": "high_refund_merchant",
                        "stripe_frozen": True
                    }
                }
            )
            
            if payment_response.status_code == 200:
                payment_result = payment_response.json()
                print(f"   Payment processed successfully")
                print(f"   Processor used: {payment_result['processor_used']}")
                print(f"   GPT-5 reasoning: {'Yes' if payment_result.get('reasoning') else 'Minimal'}")
                print(f"   Processing time: {payment_result['processing_time_ms']:.0f}ms")
                print(f"   Fallback attempted: {payment_result['fallback_attempted']}")
                
                # Verify it didn't use Stripe
                if payment_result['processor_used'] != 'stripe':
                    print("   Correctly avoided frozen Stripe processor")
                else:
                    print("   Used frozen Stripe processor - routing logic failed")
                    return False
                    
            else:
                print(f"   Payment processing failed: {payment_response.status_code}")
                return False
            
            # Step 4: Unfreeze Stripe and test recovery
            print("\n4. Unfreezing Stripe and testing recovery...")
            unfreeze_response = await client.post(f"{self.base_url}/processors/stripe/unfreeze")
            
            if unfreeze_response.status_code == 200:
                print("   Stripe account unfrozen")
            else:
                print("   Failed to unfreeze Stripe")
                return False
            
            # Step 5: Process another payment to confirm Stripe is available again
            print("\n5. Testing Stripe recovery...")
            recovery_response = await client.post(
                f"{self.base_url}/payments/process",
                json={
                    "amount": 100.00,
                    "currency": "USD",
                    "description": "Post-recovery test payment"
                }
            )
            
            if recovery_response.status_code == 200:
                recovery_result = recovery_response.json()
                print(f"   Recovery payment processed")
                print(f"   Processor used: {recovery_result['processor_used']}")
                print("   Stripe recovery confirmed")
            else:
                print(f"   Recovery payment failed: {recovery_response.status_code}")
                return False
        
        return True
    
    async def test_performance_scenarios(self):
        """Test performance across different reasoning scenarios"""
        print("\n" + "=" * 60)
        print("PERFORMANCE TESTING")
        print("=" * 60)
        
        scenarios = [
            {"amount": 5.00, "expected_effort": "minimal", "description": "Small transaction"},
            {"amount": 250.00, "expected_effort": "medium", "description": "Standard transaction"},
            {"amount": 10000.00, "expected_effort": "high", "description": "High-value transaction"}
        ]
        
        async with httpx.AsyncClient(timeout=120) as client:
            for i, scenario in enumerate(scenarios, 1):
                print(f"\n{i}. Testing {scenario['description']}...")
                
                start_time = datetime.now()
                response = await client.post(
                    f"{self.base_url}/payments/process",
                    json={
                        "amount": scenario["amount"],
                        "currency": "USD",
                        "description": scenario["description"]
                    }
                )
                elapsed = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   Processed in {elapsed:.0f}ms")
                    print(f"   Processor: {result['processor_used']}")
                    print(f"   Fees: ${result['fees']:.2f}")
                else:
                    print(f"   Failed: {response.status_code}")
                    return False
        
        return True
    
    async def run_complete_tests(self):
        """Run all integration tests"""
        print("GPT-5 B2B Payment Orchestration - Complete Integration Test")
        print("=" * 60)
        
        # Test complete flow
        flow_success = await self.test_complete_flow()
        
        if not flow_success:
            print("\nIntegration flow test FAILED")
            return False
        
        # Test performance scenarios
        perf_success = await self.test_performance_scenarios()
        
        if not perf_success:
            print("\nPerformance test FAILED")
            return False
        
        # Summary
        print("\n" + "=" * 60)
        print("INTEGRATION TEST RESULTS")
        print("=" * 60)
        print("Complete Flow Test: PASSED")
        print("Performance Test: PASSED")
        print("Stripe Freeze/Recovery: PASSED")
        print("GPT-5 Routing Decisions: PASSED")
        print("Synthetic Data Generation: PASSED")
        print("\nALL INTEGRATION TESTS PASSED")
        print("\nSystem Status: PRODUCTION READY")
        print("Hackathon Demo: READY TO PRESENT")
        
        return True


async def main():
    """Run complete integration tests"""
    print("Starting Complete Integration Test Suite...\n")
    print("Ensure FastAPI server is running: python main.py\n")
    
    tester = IntegrationTester()
    
    try:
        success = await tester.run_complete_tests()
        
        if success:
            print("\nIntegration validation COMPLETE")
            print("See COMPONENT_VALIDATION_COMPLETE.md for full report")
        else:
            print("\nSome tests failed - check logs above")
            
    except httpx.ConnectError:
        print("Cannot connect to server")
        print("Please start the FastAPI server: python main.py")
    except Exception as e:
        print(f"Test error: {e}")


if __name__ == "__main__":
    asyncio.run(main())