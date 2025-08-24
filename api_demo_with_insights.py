"""
API Demo Server with Brave Search Insights Integration
Run this to test the integration in your browser
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
import uvicorn
import json
from datetime import datetime

# Import our enhanced modules
from claude_router import ClaudeRouter
from processors.base import PaymentRequest
from synthetic_insights_generator import SyntheticDataGenerator, BusinessType

app = FastAPI(title="Payment Orchestrator with Brave Search Insights")

# Add CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the enhanced router and synthetic data generator
router = ClaudeRouter()
synthetic_generator = SyntheticDataGenerator(seed=42)  # Fixed seed for consistent demos

class PaymentRouteRequest(BaseModel):
    amount: float
    currency: str = "USD"
    merchant_id: str
    customer_id: Optional[str] = None
    urgency: str = "normal"  # normal, high, critical
    complexity: str = "balanced"  # simple, balanced, comprehensive
    test_insights: bool = False  # Enable mock insights for demo

class ProcessorInfo(BaseModel):
    id: str
    name: str
    fee_percentage: float
    success_rate: float
    supported_regions: List[str] = ["US"]

@app.get("/")
async def root():
    return {
        "message": "Payment Orchestrator with Brave Search Insights",
        "version": "2.0.0",
        "features": [
            "Real-time processor insights",
            "Dynamic fee adjustments", 
            "Market sentiment analysis",
            "Regulatory compliance updates",
            "Enhanced Claude AI routing"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check with insights status"""
    insights_analytics = router.get_insights_analytics()
    routing_analytics = router.get_routing_analytics()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "insights_enabled": insights_analytics["insights_enabled"],
        "cache_entries": insights_analytics["cache_entries"],
        "total_decisions": routing_analytics.get("total_routing_decisions", 0),
        "insights_effectiveness": routing_analytics.get("insights_effectiveness_percentage", 0)
    }

@app.get("/processors")
async def get_processors():
    """Get available processors with current status"""
    processors = [
        ProcessorInfo(
            id="stripe",
            name="Stripe",
            fee_percentage=2.9,
            success_rate=0.95,
            supported_regions=["US", "EU", "APAC"]
        ),
        ProcessorInfo(
            id="paypal", 
            name="PayPal",
            fee_percentage=3.49,
            success_rate=0.93,
            supported_regions=["US", "EU", "APAC"]
        ),
        ProcessorInfo(
            id="visa",
            name="Visa Direct",
            fee_percentage=2.5,
            success_rate=0.97,
            supported_regions=["US"]
        )
    ]
    
    return {
        "processors": [p.dict() for p in processors],
        "total_count": len(processors),
        "health_status": router.processor_health
    }

@app.post("/route-payment")
async def route_payment(request: PaymentRouteRequest):
    """Route payment with Brave Search insights"""
    
    try:
        # Create payment request
        payment_request = PaymentRequest(
            request_id=f"demo_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            amount=request.amount,
            currency=request.currency,
            merchant_id=request.merchant_id,
            customer_id=request.customer_id
        )
        
        # Available processors
        available_processors = [
            {
                "id": "stripe",
                "name": "Stripe", 
                "fee_percentage": 2.9,
                "metrics": {"success_rate": 0.95, "avg_response_time": 200},
                "supported_regions": ["US", "EU"],
                "priority_score": 0.8
            },
            {
                "id": "paypal",
                "name": "PayPal",
                "fee_percentage": 3.49, 
                "metrics": {"success_rate": 0.93, "avg_response_time": 250},
                "supported_regions": ["US", "EU", "APAC"],
                "priority_score": 0.6
            },
            {
                "id": "visa",
                "name": "Visa Direct",
                "fee_percentage": 2.5,
                "metrics": {"success_rate": 0.97, "avg_response_time": 150},
                "supported_regions": ["US"],
                "priority_score": 0.7
            }
        ]
        
        # Context for routing decision
        context = {
            "urgency": request.urgency,
            "customer_type": "standard",
            "risk_indicators": {}
        }
        
        # Add mock insights if requested (for demo purposes)
        if request.test_insights:
            # Simulate some insights being found
            mock_insights = {
                "stripe": {
                    "fee_adjustment": -0.4,  # 0.4% discount
                    "reliability_bonus": 0.02,
                    "priority_boost": 0.3,
                    "reasons": ["Demo: 0.4% promotional discount until Dec 2024", "Positive market sentiment: 0.8"]
                },
                "paypal": {
                    "fee_adjustment": 0.0,
                    "reliability_bonus": -0.01,
                    "priority_boost": -0.1, 
                    "reasons": ["Demo: Slight reliability concerns from recent reviews"]
                },
                "visa": {
                    "fee_adjustment": 0.0,
                    "reliability_bonus": 0.01,
                    "priority_boost": 0.1,
                    "reasons": ["Demo: Good uptime and reliability ratings"]
                }
            }
            
            # Apply mock insights
            enhanced_processors = router._apply_insights_to_processors(
                available_processors, 
                mock_insights
            )
            available_processors = enhanced_processors
            context["mock_insights_applied"] = True
        
        # Make routing decision
        decision = await router.make_routing_decision(
            request=payment_request,
            available_processors=available_processors,
            context=context,
            complexity=request.complexity
        )
        
        # Find the selected processor details
        selected_processor_details = next(
            (p for p in available_processors if p["id"] == decision.selected_processor),
            available_processors[0]
        )
        
        return {
            "success": True,
            "routing_decision": {
                "selected_processor": decision.selected_processor,
                "processor_details": selected_processor_details,
                "reasoning": decision.reasoning,
                "confidence": decision.confidence,
                "decision_time_ms": decision.decision_time_ms,
                "fallback_chain": decision.fallback_chain,
                "claude_params": decision.claude_params
            },
            "request_details": {
                "amount": request.amount,
                "currency": request.currency,
                "complexity": request.complexity,
                "insights_used": request.test_insights
            },
            "processor_comparison": [
                {
                    "id": p["id"],
                    "name": p["name"],
                    "original_fee": p.get("fee_percentage", 0),
                    "effective_fee": p.get("effective_fee_percentage", p.get("fee_percentage", 0)),
                    "success_rate": p.get("adjusted_success_rate", p.get("metrics", {}).get("success_rate", 0)),
                    "priority_score": p.get("priority_score", 0.5),
                    "insights_applied": p.get("insights_applied", {}).get("reasons", [])
                }
                for p in available_processors
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing failed: {str(e)}")

@app.post("/force-insights-refresh")
async def force_insights_refresh():
    """Force refresh of insights (for testing)"""
    try:
        adjustments = await router.force_insights_refresh(["stripe", "paypal", "visa"])
        
        return {
            "success": True,
            "message": "Insights refreshed successfully",
            "adjustments": adjustments,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Insights refresh failed (may be due to API limits or missing key)"
        }

@app.get("/insights-analytics")
async def get_insights_analytics():
    """Get detailed insights analytics"""
    
    routing_analytics = router.get_routing_analytics()
    insights_analytics = router.get_insights_analytics()
    
    return {
        "routing_analytics": routing_analytics,
        "insights_analytics": insights_analytics,
        "summary": {
            "total_decisions": routing_analytics.get("total_routing_decisions", 0),
            "insights_effectiveness": routing_analytics.get("insights_effectiveness_percentage", 0),
            "cache_performance": {
                "entries": insights_analytics["cache_entries"],
                "last_fetch_ago": insights_analytics["last_fetch_seconds_ago"]
            }
        }
    }

@app.post("/start-periodic-updates")
async def start_periodic_updates(interval_hours: int = 2):
    """Start periodic insights updates"""
    try:
        await router.start_periodic_insights_updates(interval_hours)
        return {
            "success": True,
            "message": f"Periodic updates started (every {interval_hours} hours)",
            "interval_hours": interval_hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop-periodic-updates")
async def stop_periodic_updates():
    """Stop periodic insights updates"""
    try:
        await router.stop_periodic_insights_updates()
        return {
            "success": True,
            "message": "Periodic updates stopped"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/comprehensive-insights/{processor_id}")
async def get_comprehensive_insights(processor_id: str):
    """Get all types of insights for a specific processor"""
    
    try:
        # Generate synthetic insights for demonstration
        synthetic_insights = synthetic_generator.generate_synthetic_insights(
            processors=[processor_id],
            insight_count_per_type=2
        )
        
        processor_insights = synthetic_insights.get(processor_id, {})
        
        # Organize insights by type with metadata
        organized_insights = {}
        for insight_type, insights in processor_insights.items():
            organized_insights[insight_type] = {
                "count": len(insights),
                "insights": [
                    {
                        "title": insight.title,
                        "content": insight.content[:150] + "..." if len(insight.content) > 150 else insight.content,
                        "confidence_score": insight.confidence_score,
                        "impact_score": getattr(insight, 'impact_score', 0.5),
                        "timestamp": insight.timestamp.isoformat(),
                        "type_specific_data": {
                            # Add type-specific fields
                            **{k: v for k, v in insight.__dict__.items() 
                               if k not in ['insight_type', 'processor_id', 'title', 'content', 'source_url', 'confidence_score', 'timestamp']}
                        }
                    }
                    for insight in insights[:3]  # Limit to first 3 for display
                ]
            }
        
        return {
            "processor_id": processor_id,
            "total_insight_types": len(organized_insights),
            "insights_by_type": organized_insights,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e), "processor_id": processor_id}

@app.post("/synthetic-data/transactions")
async def generate_synthetic_transactions(
    count: int = 50,
    business_type: Optional[str] = None,
    time_range_hours: int = 24
):
    """Generate realistic synthetic transaction data"""
    
    try:
        transactions = synthetic_generator.generate_transactions(
            count=count,
            business_type=business_type,
            time_range_hours=time_range_hours
        )
        
        # Convert to API-friendly format
        transaction_data = []
        risk_summary = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for tx in transactions:
            # Categorize risk
            if tx.risk_score < 0.25:
                risk_category = "low"
            elif tx.risk_score < 0.65:
                risk_category = "medium"
            elif tx.risk_score < 0.85:
                risk_category = "high"
            else:
                risk_category = "critical"
            
            risk_summary[risk_category] += 1
            
            transaction_data.append({
                "request_id": tx.request_id,
                "amount": tx.amount,
                "currency": tx.currency,
                "risk_score": round(tx.risk_score, 3),
                "risk_category": risk_category,
                "fraud_indicators": tx.fraud_indicators,
                "business_type": tx.business_type,
                "geographic_region": tx.geographic_region,
                "timestamp": tx.timestamp.isoformat(),
                "metadata": tx.metadata
            })
        
        return {
            "transactions": transaction_data,
            "summary": {
                "total_count": len(transactions),
                "business_type_used": business_type or "mixed",
                "time_range_hours": time_range_hours,
                "risk_distribution": risk_summary,
                "average_amount": sum(tx.amount for tx in transactions) / len(transactions)
            }
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/competitive-analysis")
async def get_competitive_analysis():
    """Get competitive analysis across all processors"""
    
    processors = ["stripe", "paypal", "visa", "adyen", "square"]
    
    try:
        # Generate synthetic competitive insights
        competitive_data = {}
        
        for processor in processors:
            insights = synthetic_generator.generate_synthetic_insights(
                processors=[processor],
                insight_count_per_type=1
            )
            
            competitive_insights = insights[processor].get("competitive_analysis", [])
            if competitive_insights:
                insight = competitive_insights[0]
                competitive_data[processor] = {
                    "market_position": insight.market_position,
                    "competitive_advantage": insight.competitive_advantage,
                    "compared_processors": insight.compared_processors,
                    "pricing_comparison": insight.pricing_comparison,
                    "feature_comparison": insight.feature_comparison
                }
        
        return {
            "competitive_analysis": competitive_data,
            "analysis_date": datetime.utcnow().isoformat(),
            "processors_analyzed": len(competitive_data)
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/market-intelligence")
async def get_market_intelligence():
    """Get comprehensive market intelligence across all insight types"""
    
    processors = ["stripe", "paypal", "visa"]
    
    try:
        # Generate comprehensive insights
        all_insights = synthetic_generator.generate_synthetic_insights(
            processors=processors,
            insight_count_per_type=2
        )
        
        # Analyze market intelligence
        market_intelligence = {
            "fraud_trends": {},
            "service_health": {},
            "market_sentiment": {},
            "news_impact": {},
            "performance_rankings": {}
        }
        
        for processor, insights in all_insights.items():
            # Fraud risk assessment
            fraud_insights = insights.get("fraud_trends", [])
            if fraud_insights:
                high_risk_count = sum(1 for f in fraud_insights if f.risk_level in ["high", "critical"])
                market_intelligence["fraud_trends"][processor] = {
                    "total_threats": len(fraud_insights),
                    "high_risk_threats": high_risk_count,
                    "risk_level": "high" if high_risk_count > 0 else "medium"
                }
            
            # Service health
            service_insights = insights.get("service_status", [])
            if service_insights:
                operational_count = sum(1 for s in service_insights if s.service_status == "operational")
                avg_uptime = sum(s.uptime_percentage for s in service_insights) / len(service_insights)
                market_intelligence["service_health"][processor] = {
                    "operational_services": f"{operational_count}/{len(service_insights)}",
                    "average_uptime": round(avg_uptime, 2),
                    "health_status": "excellent" if avg_uptime > 99 else "good" if avg_uptime > 95 else "concerning"
                }
            
            # Market sentiment
            sentiment_insights = insights.get("social_sentiment", [])
            if sentiment_insights:
                avg_sentiment = sum(s.sentiment_score for s in sentiment_insights) / len(sentiment_insights)
                total_mentions = sum(s.mention_count for s in sentiment_insights)
                market_intelligence["market_sentiment"][processor] = {
                    "average_sentiment": round(avg_sentiment, 2),
                    "sentiment_category": "positive" if avg_sentiment > 0.3 else "neutral" if avg_sentiment > -0.3 else "negative",
                    "total_mentions": total_mentions
                }
            
            # News impact
            news_insights = insights.get("news_impact", [])
            if news_insights:
                high_impact_count = sum(1 for n in news_insights if n.impact_level in ["high", "critical"])
                avg_market_impact = sum(n.market_impact for n in news_insights) / len(news_insights)
                market_intelligence["news_impact"][processor] = {
                    "high_impact_news": high_impact_count,
                    "average_market_impact": round(avg_market_impact, 2),
                    "impact_trend": "positive" if avg_market_impact > 0.1 else "neutral" if avg_market_impact > -0.1 else "negative"
                }
            
            # Performance ranking
            perf_insights = insights.get("performance_benchmarking", [])
            if perf_insights:
                avg_score = sum(p.benchmark_score for p in perf_insights) / len(perf_insights)
                avg_percentile = sum(p.percentile_rank for p in perf_insights) / len(perf_insights)
                market_intelligence["performance_rankings"][processor] = {
                    "average_score": round(avg_score, 2),
                    "average_percentile": round(avg_percentile, 1),
                    "ranking": "top_tier" if avg_percentile > 85 else "strong" if avg_percentile > 70 else "average"
                }
        
        return {
            "market_intelligence": market_intelligence,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "processors_analyzed": processors
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/scenario-testing")
async def test_routing_scenarios():
    """Test routing decisions across different market scenarios"""
    
    try:
        # Generate different scenarios
        scenarios = {
            "normal_market": synthetic_generator.generate_processor_scenarios("normal"),
            "stripe_outage": synthetic_generator.generate_processor_scenarios("stripe_outage"),
            "promotional_period": synthetic_generator.generate_processor_scenarios("promotional_period"),
            "high_fraud_alert": synthetic_generator.generate_processor_scenarios("high_fraud_alert")
        }
        
        results = {}
        
        for scenario_name, processors in scenarios.items():
            # Generate a test transaction
            test_transactions = synthetic_generator.generate_transactions(count=1, business_type="startup_tech")
            test_request = PaymentRequest(
                request_id=test_transactions[0].request_id,
                amount=test_transactions[0].amount,
                currency=test_transactions[0].currency,
                merchant_id=test_transactions[0].merchant_id,
                customer_id=test_transactions[0].customer_id
            )
            
            # Test routing decision
            try:
                decision = await router.make_routing_decision(
                    request=test_request,
                    available_processors=processors,
                    context={"scenario": scenario_name},
                    complexity="balanced"
                )
                
                results[scenario_name] = {
                    "selected_processor": decision.selected_processor,
                    "confidence": decision.confidence,
                    "reasoning_preview": decision.reasoning[:100] + "...",
                    "decision_time_ms": decision.decision_time_ms,
                    "scenario_processors": [p["id"] for p in processors],
                    "transaction_amount": test_request.amount
                }
            except Exception as e:
                results[scenario_name] = {
                    "error": str(e),
                    "scenario_processors": [p["id"] for p in processors]
                }
        
        return {
            "scenario_results": results,
            "test_timestamp": datetime.utcnow().isoformat(),
            "scenarios_tested": len(scenarios)
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/demo-scenarios")
async def get_demo_scenarios():
    """Get enhanced demo scenarios for comprehensive testing"""
    
    scenarios = [
        {
            "name": "🎯 Simple Routing Demo",
            "description": "Low-value transaction with basic routing",
            "payload": {
                "amount": 25.0,
                "merchant_id": "demo_merchant_1",
                "complexity": "simple",
                "test_insights": False
            },
            "expected_behavior": "Fast routing without API calls, uses hardcoded processor ranking"
        },
        {
            "name": "💎 Premium Transaction Analysis",
            "description": "High-value transaction with comprehensive insights analysis", 
            "payload": {
                "amount": 5000.0,
                "merchant_id": "enterprise_merchant_2",
                "complexity": "comprehensive",
                "test_insights": True
            },
            "expected_behavior": "Full insights analysis with fraud trends, market sentiment, and competitive data"
        },
        {
            "name": "⚡ Urgent Payment Processing",
            "description": "Time-sensitive payment with balanced insights",
            "payload": {
                "amount": 1500.0,
                "merchant_id": "urgent_merchant_3",
                "urgency": "high",
                "complexity": "balanced",
                "test_insights": True
            },
            "expected_behavior": "Quick insights lookup with promotional discounts and service status"
        },
        {
            "name": "🏢 B2B Standard Payment",
            "description": "Regular business payment with standard insights",
            "payload": {
                "amount": 750.0,
                "merchant_id": "b2b_merchant",
                "complexity": "balanced",
                "test_insights": True
            },
            "expected_behavior": "Balanced analysis with cost optimization and reliability focus"
        },
        {
            "name": "🚀 Startup High-Growth Scenario",
            "description": "Startup with high transaction volume and growth",
            "payload": {
                "amount": 299.0,
                "merchant_id": "startup_saas",
                "complexity": "comprehensive",
                "test_insights": True
            },
            "expected_behavior": "Comprehensive analysis focusing on scalability and cost efficiency"
        },
        {
            "name": "🛡️ High-Risk Transaction",
            "description": "Transaction with elevated risk indicators",
            "payload": {
                "amount": 2500.0,
                "merchant_id": "high_risk_merchant",
                "urgency": "normal",
                "complexity": "comprehensive",
                "test_insights": True
            },
            "expected_behavior": "Enhanced fraud analysis and risk-aware processor selection"
        }
    ]
    
    return {
        "scenarios": scenarios,
        "total_scenarios": len(scenarios),
        "instructions": "POST each payload to /route-payment to test different capabilities",
        "new_endpoints": [
            "/comprehensive-insights/{processor_id}",
            "/synthetic-data/transactions",
            "/competitive-analysis",
            "/market-intelligence",
            "/scenario-testing"
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting Payment Orchestrator with Brave Search Insights")
    print("📍 API available at: http://localhost:8000")
    print("📖 Docs available at: http://localhost:8000/docs")
    print("🧪 Test scenarios at: http://localhost:8000/demo-scenarios")
    
    uvicorn.run(
        "api_demo_with_insights:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )