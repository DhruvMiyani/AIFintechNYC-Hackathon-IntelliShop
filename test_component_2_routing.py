"""
Component 2 Test Module: Intelligent Payment Routing
Modular testing following separation of concerns
"""

import asyncio
import httpx
from typing import Dict, Any, List


class PaymentRoutingTester:
    """Isolated tester for payment routing component"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    async def test_normal_payment(self) -> Dict[str, Any]:
        """Test normal payment processing"""
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/payments/process",
                json={"amount": 50.00, "currency": "USD", "description": "Test payment"}
            )
            
            data = response.json()
            return {
                "test_name": "normal_payment",
                "success": data.get("success", False),
                "processor": data.get("processor_used"),
                "time_ms": data.get("processing_time_ms", 0),
                "status_code": response.status_code
            }
    
    async def test_stripe_frozen_fallback(self) -> Dict[str, Any]:
        """Test automatic fallback when Stripe is frozen"""
        async with httpx.AsyncClient(timeout=60) as client:
            # Freeze Stripe
            await client.post(f"{self.base_url}/processors/stripe/freeze")
            
            # Process payment
            response = await client.post(
                f"{self.base_url}/payments/process",
                json={"amount": 200.00, "currency": "USD"}
            )
            
            data = response.json()
            
            # Unfreeze Stripe
            await client.post(f"{self.base_url}/processors/stripe/unfreeze")
            
            return {
                "test_name": "stripe_frozen_fallback",
                "success": data.get("success", False),
                "processor": data.get("processor_used"),
                "avoided_stripe": data.get("processor_used") != "stripe",
                "reasoning": data.get("reasoning", "")[:100]
            }
    
    async def test_high_value_routing(self) -> Dict[str, Any]:
        """Test high-value transaction routing"""
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/payments/process",
                json={"amount": 15000.00, "currency": "USD", "description": "High-value B2B"}
            )
            
            data = response.json()
            return {
                "test_name": "high_value_routing",
                "success": data.get("success", False),
                "amount": data.get("amount"),
                "processor": data.get("processor_used"),
                "fees": data.get("fees", 0)
            }
    
    async def run_all_tests(self) -> List[Dict[str, Any]]:
        """Execute all routing tests"""
        print("Testing Component 2: Intelligent Payment Routing...")
        
        tests = [
            self.test_normal_payment(),
            self.test_stripe_frozen_fallback(),
            self.test_high_value_routing()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                self.results.append({
                    "test_name": "error",
                    "success": False,
                    "error": str(result)
                })
            else:
                self.results.append(result)
        
        return self.results


async def validate_component_2():
    """Main validation function for Component 2"""
    tester = PaymentRoutingTester()
    results = await tester.run_all_tests()
    
    passed = sum(1 for r in results if r.get("success", False))
    total = len(results)
    
    print(f"\nComponent 2 Results: {passed}/{total} tests passed")
    
    for result in results:
        status = "PASS" if result.get("success") else "FAIL"
        print(f"[{status}] {result.get('test_name', 'unknown')}")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(validate_component_2())
    print(f"\nComponent 2 Status: {'VALIDATED' if success else 'NEEDS REVIEW'}")