"""
Enhanced Brave Search Integration Test
Demonstrates fraud trends, service status, and social sentiment insights
"""

import asyncio
import json
from datetime import datetime
from brave_search_insights import (
    PaymentInsightsOrchestrator, 
    BraveSearchClient,
    InsightType
)


async def test_enhanced_insights():
    """Test the enhanced Brave Search insights functionality."""
    
    print("🚀 Testing Enhanced Brave Search Integration")
    print("=" * 60)
    
    # Initialize the orchestrator
    orchestrator = PaymentInsightsOrchestrator()
    
    # Test processors
    processors = ["stripe", "paypal", "visa"]
    regions = ["US", "EU"]
    
    print(f"\n📊 Fetching comprehensive insights for {len(processors)} processors...")
    
    try:
        # Fetch all insights
        all_insights = await orchestrator.fetch_all_insights(processors, regions)
        
        print(f"✅ Successfully fetched insights for {len(all_insights)} processors")
        
        # Analyze each processor's insights
        for processor_id, processor_insights in all_insights.items():
            print(f"\n🔍 {processor_id.upper()} Processor Analysis:")
            print("-" * 40)
            
            if "error" in processor_insights:
                print(f"❌ Error: {processor_insights['error']}")
                continue
            
            # Display insight counts by type
            for insight_type, insights in processor_insights.items():
                if insight_type != "composite_scores":
                    count = len(insights) if isinstance(insights, list) else 0
                    print(f"  {insight_type}: {count} insights")
            
            # Display composite scores
            composite_scores = processor_insights.get("composite_scores", {})
            if composite_scores:
                print(f"\n  📈 Composite Scores:")
                for metric, score in composite_scores.items():
                    print(f"    {metric}: {score:.3f}")
        
        # Test routing adjustments
        print(f"\n🎯 Testing Routing Adjustments...")
        routing_adjustments = orchestrator.get_routing_adjustments(all_insights)
        
        for processor_id, adjustments in routing_adjustments.items():
            print(f"\n  {processor_id.upper()} Routing Adjustments:")
            print(f"    Fee Adjustment: {adjustments['fee_adjustment']:+.2f}%")
            print(f"    Reliability Bonus: {adjustments['reliability_bonus']:+.2f}")
            print(f"    Priority Boost: {adjustments['priority_boost']:+.2f}")
            print(f"    Risk Penalty: {adjustments['risk_penalty']:+.2f}")
            
            if adjustments['reasons']:
                print(f"    Reasons:")
                for reason in adjustments['reasons']:
                    print(f"      • {reason}")
        
        # Test specific insight types
        print(f"\n🔍 Testing Specific Insight Types...")
        
        # Test fraud trends
        print(f"\n  🚨 Fraud Trends Analysis:")
        for processor_id in processors[:2]:  # Test first 2 processors
            fraud_insights = await orchestrator.search_client.search_fraud_trends(processor_id, "US")
            if fraud_insights:
                print(f"    {processor_id}: {len(fraud_insights)} fraud insights")
                for insight in fraud_insights[:2]:  # Show first 2
                    print(f"      - {insight.fraud_type} ({insight.risk_level} risk)")
            else:
                print(f"    {processor_id}: No fraud insights found")
        
        # Test service status
        print(f"\n  ⚡ Service Status Analysis:")
        for processor_id in processors[:2]:
            status_insights = await orchestrator.search_client.search_service_status(processor_id)
            if status_insights:
                print(f"    {processor_id}: {len(status_insights)} status insights")
                for insight in status_insights[:2]:
                    print(f"      - {insight.service_status} ({insight.uptime_percentage:.1f}% uptime)")
            else:
                print(f"    {processor_id}: No service status insights found")
        
        # Test social sentiment
        print(f"\n  📱 Social Sentiment Analysis:")
        for processor_id in processors[:2]:
            sentiment_insights = await orchestrator.search_client.search_social_sentiment(processor_id)
            if sentiment_insights:
                print(f"    {processor_id}: {len(sentiment_insights)} sentiment insights")
                for insight in sentiment_insights[:2]:
                    print(f"      - {insight.platform}: {insight.sentiment_score:+.2f} sentiment")
            else:
                print(f"    {processor_id}: No social sentiment insights found")
        
        # Test cache functionality
        print(f"\n💾 Testing Cache Functionality...")
        cache_size_before = len(orchestrator.insights_cache)
        orchestrator.cleanup_cache()
        cache_size_after = len(orchestrator.insights_cache)
        print(f"  Cache cleanup: {cache_size_before} → {cache_size_after} entries")
        
        # Test periodic updates
        print(f"\n🔄 Testing Periodic Updates...")
        await orchestrator.start_periodic_insights_updates(update_interval_hours=1)
        print(f"  Started periodic updates (1 hour interval)")
        
        # Force refresh
        print(f"\n🔄 Testing Force Refresh...")
        forced_insights = await orchestrator.force_insights_refresh(processors[:2])
        print(f"  Force refresh completed for {len(forced_insights)} processors")
        
        # Stop periodic updates
        await orchestrator.stop_periodic_insights_updates()
        print(f"  Stopped periodic updates")
        
        print(f"\n✅ Enhanced Brave Search Integration Test Complete!")
        
        # Summary statistics
        total_insights = sum(
            len([insight for insight_type, insights in processor_insights.items() 
                 if insight_type != "composite_scores" and isinstance(insights, list)])
            for processor_insights in all_insights.values()
        )
        
        print(f"\n📊 Summary:")
        print(f"  Processors analyzed: {len(all_insights)}")
        print(f"  Total insights collected: {total_insights}")
        print(f"  Insight types: {len(InsightType)}")
        print(f"  Routing adjustments generated: {len(routing_adjustments)}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_insight_parsing():
    """Test the new insight parsing functionality."""
    
    print(f"\n🧪 Testing Insight Parsing...")
    print("-" * 40)
    
    # Mock search results for testing
    mock_results = {
        "fraud_trend": {
            "title": "Stripe Reports Critical Security Breach in Q4 2024",
            "description": "Major security incident affecting payment processing. Chargeback fraud on the rise. Global impact reported.",
            "source_url": "https://example.com/stripe-breach"
        },
        "service_status": {
            "title": "PayPal Service Degraded - API Response Times Increased",
            "description": "PayPal experiencing 95.2% uptime due to maintenance. Expected resolution in 2 hours.",
            "source_url": "https://example.com/paypal-status"
        },
        "social_sentiment": {
            "title": "Visa Merchant Reviews - Twitter Sentiment Analysis",
            "description": "Positive feedback from merchants. Great reliability and good customer service.",
            "source_url": "https://example.com/visa-sentiment"
        }
    }
    
    # Test parsing
    from brave_search_insights import InsightParser
    parser = InsightParser()
    
    # Test fraud trend parsing
    fraud_insight = parser.parse_fraud_trend(mock_results["fraud_trend"], "stripe", "US")
    if fraud_insight:
        print(f"✅ Fraud Trend Parsed:")
        print(f"  Type: {fraud_insight.fraud_type}")
        print(f"  Risk Level: {fraud_insight.risk_level}")
        print(f"  Trend: {fraud_insight.trend_direction}")
        print(f"  Regions: {fraud_insight.affected_regions}")
    
    # Test service status parsing
    status_insight = parser.parse_service_status(mock_results["service_status"], "paypal")
    if status_insight:
        print(f"✅ Service Status Parsed:")
        print(f"  Status: {status_insight.service_status}")
        print(f"  Uptime: {status_insight.uptime_percentage}%")
        print(f"  Duration: {status_insight.incident_duration_minutes} minutes")
    
    # Test social sentiment parsing
    sentiment_insight = parser.parse_social_sentiment(mock_results["social_sentiment"], "visa", "Twitter")
    if sentiment_insight:
        print(f"✅ Social Sentiment Parsed:")
        print(f"  Platform: {sentiment_insight.platform}")
        print(f"  Sentiment: {sentiment_insight.sentiment_score:+.2f}")
        print(f"  Mentions: {sentiment_insight.mention_count}")


if __name__ == "__main__":
    print("🚀 Starting Enhanced Brave Search Integration Tests")
    print("=" * 60)
    
    # Run tests
    asyncio.run(test_enhanced_insights())
    asyncio.run(test_insight_parsing())
    
    print(f"\n🎉 All tests completed!")