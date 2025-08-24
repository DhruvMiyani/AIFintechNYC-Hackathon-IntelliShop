"""
Test direct Brave Search API calls to verify it's working with real data
"""
import asyncio
import os
from dotenv import load_dotenv
from brave_search_insights import BraveSearchClient, PaymentInsightsOrchestrator

load_dotenv()

async def test_brave_search_api():
    """Test the Brave Search API directly"""
    
    print("🧪 Testing Brave Search API with your API key...")
    
    # Initialize client
    client = BraveSearchClient()
    print(f"API Key configured: {bool(client.api_key)}")
    print(f"API Key (masked): {client.api_key[:10]}..." if client.api_key else "No API Key")
    
    try:
        # Test 1: Basic search
        print("\n🔍 Test 1: Basic search query...")
        response = await client.search("Stripe payment processor pricing 2024", count=3)
        if response and response.get("web", {}).get("results"):
            print(f"✅ Basic search successful! Got {len(response['web']['results'])} results")
            for i, result in enumerate(response["web"]["results"][:2]):
                print(f"  {i+1}. {result.get('title', 'No title')}")
                print(f"     URL: {result.get('url', 'No URL')}")
        else:
            print(f"❌ Basic search failed or returned no results: {response}")
            
        # Test 2: Specific search methods  
        print("\n🔍 Test 2: Testing specific search methods...")
        
        # Test promotion search
        promotions = await client.search_promotions("stripe")
        print(f"Promotions found: {len(promotions)}")
        for promo in promotions[:1]:
            print(f"  - {promo.title}")
            print(f"    Discount: {getattr(promo, 'discount_percentage', 'N/A')}%")
            
        # Test fraud trends
        fraud_trends = await client.search_fraud_trends("stripe")
        print(f"Fraud trends found: {len(fraud_trends)}")
        for trend in fraud_trends[:1]:
            print(f"  - {trend.title}")
            print(f"    Risk Level: {getattr(trend, 'risk_level', 'N/A')}")
            
        # Test service status
        service_status = await client.search_service_status("stripe")
        print(f"Service status insights found: {len(service_status)}")
        for status in service_status[:1]:
            print(f"  - {status.title}")
            print(f"    Status: {getattr(status, 'service_status', 'N/A')}")
            
        print("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_orchestrator():
    """Test the full orchestrator"""
    
    print("\n🎼 Testing PaymentInsightsOrchestrator...")
    
    try:
        orchestrator = PaymentInsightsOrchestrator()
        
        # Fetch insights for multiple processors
        insights = await orchestrator.fetch_all_insights(["stripe", "paypal"])
        
        print(f"Orchestrator results:")
        for processor, data in insights.items():
            if "error" in data:
                print(f"  {processor}: ERROR - {data['error']}")
            else:
                print(f"  {processor}: SUCCESS")
                for insight_type, insight_list in data.items():
                    if isinstance(insight_list, list):
                        print(f"    {insight_type}: {len(insight_list)} insights")
                        
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Brave Search API Tests")
    
    async def run_tests():
        api_test = await test_brave_search_api()
        orchestrator_test = await test_orchestrator()
        
        if api_test and orchestrator_test:
            print("\n🎉 All tests passed! Brave Search API is working with real data!")
        else:
            print("\n❌ Some tests failed. Check the errors above.")
    
    asyncio.run(run_tests())