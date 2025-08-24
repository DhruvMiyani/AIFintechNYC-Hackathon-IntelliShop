"""
Debug Component 2: Intelligent Payment Routing
Enhanced error reporting for debugging
"""

import asyncio
import httpx
import traceback
from typing import Dict, Any, List


class DebugPaymentRoutingTester:
    """Debug tester for payment routing component"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    async def test_normal_payment(self) -> Dict[str, Any]:
        """Test normal payment processing with detailed error reporting"""
        print("Testing normal payment...")
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                print(f"Making request to: {self.base_url}/payments/process")
                response = await client.post(
                    f"{self.base_url}/payments/process",
                    json={"amount": 50.00, "currency": "USD", "description": "Test payment"}
                )
                
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status_code != 200:
                    print(f"Response text: {response.text}")
                    return {
                        "test_name": "normal_payment",
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}",
                        "status_code": response.status_code
                    }
                
                data = response.json()
                print(f"Response data: {data}")
                
                return {
                    "test_name": "normal_payment",
                    "success": data.get("success", False),
                    "processor": data.get("processor_used"),
                    "time_ms": data.get("processing_time_ms", 0),
                    "status_code": response.status_code
                }
                
        except Exception as e:
            print(f"Exception in test_normal_payment: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                "test_name": "normal_payment",
                "success": False,
                "error": f"Exception: {str(e)}",
                "traceback": traceback.format_exc()
            }
    
    async def test_server_health(self) -> Dict[str, Any]:
        """Test if server is responding"""
        print("Testing server health...")
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                # Test root endpoint instead of /health
                response = await client.get(f"{self.base_url}/")
                print(f"Root endpoint status: {response.status_code}")
                return {
                    "test_name": "server_health",
                    "success": response.status_code in [200, 404],  # 404 is OK if no root handler
                    "status_code": response.status_code
                }
        except Exception as e:
            print(f"Health check failed: {e}")
            return {
                "test_name": "server_health", 
                "success": False,
                "error": str(e)
            }
    
    async def test_docs_endpoint(self) -> Dict[str, Any]:
        """Test if docs endpoint is working"""
        print("Testing docs endpoint...")
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/docs")
                print(f"Docs endpoint status: {response.status_code}")
                return {
                    "test_name": "docs_endpoint",
                    "success": response.status_code == 200,
                    "status_code": response.status_code
                }
        except Exception as e:
            print(f"Docs endpoint failed: {e}")
            return {
                "test_name": "docs_endpoint",
                "success": False,
                "error": str(e)
            }
    
    async def run_debug_tests(self) -> List[Dict[str, Any]]:
        """Execute debug tests"""
        print("=" * 60)
        print("COMPONENT 2 DEBUG TEST SUITE")
        print("=" * 60)
        
        # Test server connectivity first
        health_result = await self.test_server_health()
        self.results.append(health_result)
        
        docs_result = await self.test_docs_endpoint()
        self.results.append(docs_result)
        
        # If docs endpoint works, server is running - test payment processing
        if docs_result.get("success"):
            payment_result = await self.test_normal_payment()
            self.results.append(payment_result)
        else:
            print("Server not responding, skipping payment tests")
        
        return self.results


async def debug_component_2():
    """Main debug function for Component 2"""
    tester = DebugPaymentRoutingTester()
    results = await tester.run_debug_tests()
    
    print("\n" + "=" * 60)
    print("DEBUG RESULTS")
    print("=" * 60)
    
    for result in results:
        status = "PASS" if result.get("success") else "FAIL"
        test_name = result.get("test_name", "unknown")
        print(f"[{status}] {test_name}")
        
        if not result.get("success"):
            if "error" in result:
                print(f"      Error: {result['error']}")
            if "traceback" in result:
                print(f"      Traceback: {result['traceback'][:200]}...")


if __name__ == "__main__":
    print("Running Component 2 Debug Tests...")
    asyncio.run(debug_component_2())