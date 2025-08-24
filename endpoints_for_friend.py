"""
FastAPI Endpoints for Market Analysis Dashboard and Competitive Analysis Dashboard
Share these endpoints with your friend for independent development
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

app = FastAPI(title="Payment Processor Analytics API", version="1.0.0")

# Data Models
class ProcessorMetrics(BaseModel):
    id: str
    name: str
    success_rate: float
    avg_response_time: int
    fee_percentage: float
    uptime_percentage: float
    transaction_volume: int
    market_share: float

class MarketTrend(BaseModel):
    date: str
    metric: str
    value: float
    processor_id: str

class CompetitiveInsight(BaseModel):
    processor_id: str
    ranking: int
    market_position: str
    competitive_advantage: str
    strengths: List[str]
    weaknesses: List[str]
    confidence_score: float

# Endpoints

@app.get("/api/market-analysis/overview")
async def get_market_overview():
    """
    Market Analysis Dashboard - Overview metrics
    Returns: Overall market metrics, growth trends, key insights
    """
    return {
        "market_size": 89.7,  # Billion USD
        "growth_rate": 12.3,  # YoY %
        "total_processors": 156,
        "active_merchants": 2_450_000,
        "total_transactions_today": 847_293,
        "key_trends": [
            {"trend": "Digital Wallet Adoption", "impact": "High", "change": "+23%"},
            {"trend": "Cross-border Payments", "impact": "Medium", "change": "+18%"},
            {"trend": "Crypto Integration", "impact": "High", "change": "+45%"}
        ],
        "market_health_score": 87.5,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/market-analysis/processors")
async def get_processor_metrics():
    """
    Market Analysis Dashboard - Processor performance metrics
    Returns: Real-time metrics for all payment processors
    """
    processors = [
        {
            "id": "stripe",
            "name": "Stripe",
            "success_rate": 99.4,
            "avg_response_time": 245,
            "fee_percentage": 2.9,
            "uptime_percentage": 99.9,
            "transaction_volume": 1_234_567,
            "market_share": 23.4,
            "status": "operational",
            "last_incident": None
        },
        {
            "id": "paypal",
            "name": "PayPal",
            "success_rate": 98.7,
            "avg_response_time": 312,
            "fee_percentage": 3.49,
            "uptime_percentage": 99.7,
            "transaction_volume": 987_654,
            "market_share": 19.8,
            "status": "operational",
            "last_incident": "2024-08-20T10:30:00Z"
        },
        {
            "id": "crossmint",
            "name": "Crossmint",
            "success_rate": 99.2,
            "avg_response_time": 156,
            "fee_percentage": 1.5,
            "uptime_percentage": 99.8,
            "transaction_volume": 234_567,
            "market_share": 8.7,
            "status": "operational",
            "last_incident": None
        },
        {
            "id": "visa",
            "name": "Visa Direct",
            "success_rate": 99.8,
            "avg_response_time": 189,
            "fee_percentage": 2.5,
            "uptime_percentage": 99.95,
            "transaction_volume": 2_345_678,
            "market_share": 31.2,
            "status": "operational",
            "last_incident": None
        },
        {
            "id": "square",
            "name": "Square",
            "success_rate": 98.9,
            "avg_response_time": 278,
            "fee_percentage": 2.6,
            "uptime_percentage": 99.6,
            "transaction_volume": 456_789,
            "market_share": 12.1,
            "status": "maintenance",
            "last_incident": "2024-08-23T14:15:00Z"
        }
    ]
    
    return {
        "processors": processors,
        "total_count": len(processors),
        "timestamp": datetime.now().isoformat(),
        "refresh_interval": 30  # seconds
    }

@app.get("/api/market-analysis/trends/{timeframe}")
async def get_market_trends(timeframe: str = "24h"):
    """
    Market Analysis Dashboard - Historical trends
    Timeframes: 1h, 24h, 7d, 30d
    Returns: Time-series data for key metrics
    """
    # Generate sample trend data
    trends = {
        "transaction_volume": [
            {"timestamp": "2024-08-24T10:00:00Z", "value": 123456},
            {"timestamp": "2024-08-24T11:00:00Z", "value": 145678},
            {"timestamp": "2024-08-24T12:00:00Z", "value": 167890},
            {"timestamp": "2024-08-24T13:00:00Z", "value": 189012},
            {"timestamp": "2024-08-24T14:00:00Z", "value": 201234}
        ],
        "success_rates": [
            {"timestamp": "2024-08-24T10:00:00Z", "stripe": 99.4, "paypal": 98.7, "crossmint": 99.2},
            {"timestamp": "2024-08-24T11:00:00Z", "stripe": 99.3, "paypal": 98.9, "crossmint": 99.1},
            {"timestamp": "2024-08-24T12:00:00Z", "stripe": 99.5, "paypal": 98.6, "crossmint": 99.3},
            {"timestamp": "2024-08-24T13:00:00Z", "stripe": 99.4, "paypal": 98.8, "crossmint": 99.0},
            {"timestamp": "2024-08-24T14:00:00Z", "stripe": 99.6, "paypal": 98.7, "crossmint": 99.2}
        ],
        "response_times": [
            {"timestamp": "2024-08-24T10:00:00Z", "stripe": 245, "paypal": 312, "crossmint": 156},
            {"timestamp": "2024-08-24T11:00:00Z", "stripe": 238, "paypal": 298, "crossmint": 162},
            {"timestamp": "2024-08-24T12:00:00Z", "stripe": 251, "paypal": 325, "crossmint": 149},
            {"timestamp": "2024-08-24T13:00:00Z", "stripe": 242, "paypal": 308, "crossmint": 154},
            {"timestamp": "2024-08-24T14:00:00Z", "stripe": 245, "paypal": 312, "crossmint": 156}
        ]
    }
    
    return {
        "timeframe": timeframe,
        "trends": trends,
        "timestamp": datetime.now().isoformat(),
        "data_points": len(trends["transaction_volume"])
    }

@app.get("/api/competitive-analysis/rankings")
async def get_competitive_rankings():
    """
    Competitive Analysis Dashboard - Processor rankings
    Returns: Ranked list of processors with competitive insights
    """
    rankings = [
        {
            "rank": 1,
            "processor_id": "visa",
            "name": "Visa Direct",
            "overall_score": 94.2,
            "market_share": 31.2,
            "competitive_advantage": "Global acceptance and established trust network",
            "strengths": ["Global reach", "Brand trust", "Regulatory compliance", "Network effects"],
            "weaknesses": ["Higher fees", "Legacy technology", "Slow innovation"],
            "growth_rate": 8.3,
            "confidence_score": 0.92
        },
        {
            "rank": 2,
            "processor_id": "stripe",
            "name": "Stripe",
            "overall_score": 91.8,
            "market_share": 23.4,
            "competitive_advantage": "Developer-friendly API and innovative features",
            "strengths": ["Developer experience", "Innovation", "Documentation", "Ecosystem"],
            "weaknesses": ["Limited offline presence", "Compliance complexity", "Support inconsistency"],
            "growth_rate": 15.7,
            "confidence_score": 0.89
        },
        {
            "rank": 3,
            "processor_id": "paypal",
            "name": "PayPal",
            "overall_score": 87.5,
            "market_share": 19.8,
            "competitive_advantage": "Consumer trust and ease of use",
            "strengths": ["Consumer trust", "Ease of use", "Buyer protection", "Global presence"],
            "weaknesses": ["High fees", "Account holds", "Limited B2B features"],
            "growth_rate": 6.2,
            "confidence_score": 0.85
        },
        {
            "rank": 4,
            "processor_id": "square",
            "name": "Square",
            "overall_score": 83.1,
            "market_share": 12.1,
            "competitive_advantage": "Integrated POS and small business focus",
            "strengths": ["POS integration", "Small business focus", "Hardware ecosystem", "Simplicity"],
            "weaknesses": ["Limited enterprise features", "Geographic restrictions", "Pricing transparency"],
            "growth_rate": 11.4,
            "confidence_score": 0.78
        },
        {
            "rank": 5,
            "processor_id": "crossmint",
            "name": "Crossmint",
            "overall_score": 89.3,
            "market_share": 8.7,
            "competitive_advantage": "Lowest fees and crypto-native features",
            "strengths": ["Lowest fees", "Crypto integration", "Fast settlement", "Modern API"],
            "weaknesses": ["Newer brand", "Limited enterprise adoption", "Regulatory uncertainty"],
            "growth_rate": 45.8,
            "confidence_score": 0.81
        }
    ]
    
    return {
        "rankings": rankings,
        "total_processors": len(rankings),
        "analysis_date": datetime.now().isoformat(),
        "methodology": "Composite score based on market share, performance, innovation, and growth"
    }

@app.get("/api/competitive-analysis/comparison/{processor1}/{processor2}")
async def compare_processors(processor1: str, processor2: str):
    """
    Competitive Analysis Dashboard - Direct processor comparison
    Returns: Head-to-head comparison of two processors
    """
    
    # Sample comparison data
    comparison_data = {
        "processors": [processor1, processor2],
        "metrics": {
            "fees": {
                processor1: {"transaction_fee": 2.9, "monthly_fee": 0, "setup_fee": 0},
                processor2: {"transaction_fee": 1.5, "monthly_fee": 0, "setup_fee": 0}
            },
            "performance": {
                processor1: {"success_rate": 99.4, "avg_response_time": 245, "uptime": 99.9},
                processor2: {"success_rate": 99.2, "avg_response_time": 156, "uptime": 99.8}
            },
            "features": {
                processor1: {"international": True, "subscriptions": True, "marketplace": True, "crypto": False},
                processor2: {"international": True, "subscriptions": True, "marketplace": False, "crypto": True}
            },
            "market_position": {
                processor1: {"market_share": 23.4, "growth_rate": 15.7, "ranking": 2},
                processor2: {"market_share": 8.7, "growth_rate": 45.8, "ranking": 5}
            }
        },
        "recommendation": {
            "winner": processor2 if processor2 == "crossmint" else processor1,
            "reason": "Lower fees and better performance metrics",
            "confidence": 0.82,
            "use_cases": {
                processor1: ["Large enterprises", "International transactions", "Complex workflows"],
                processor2: ["Cost-conscious merchants", "Crypto payments", "Fast settlement"]
            }
        },
        "timestamp": datetime.now().isoformat()
    }
    
    return comparison_data

@app.get("/api/competitive-analysis/market-insights")
async def get_market_insights():
    """
    Competitive Analysis Dashboard - Strategic market insights
    Returns: Market intelligence, trends, and strategic recommendations
    """
    return {
        "market_dynamics": {
            "consolidation_trend": "Medium",
            "new_entrant_threat": "High", 
            "technology_disruption": "High",
            "regulatory_pressure": "Medium"
        },
        "key_insights": [
            {
                "category": "Technology",
                "insight": "Crypto payment integration becoming table stakes",
                "impact": "High",
                "timeline": "6-12 months",
                "affected_processors": ["all"]
            },
            {
                "category": "Pricing",
                "insight": "Fee compression accelerating due to new entrants",
                "impact": "High", 
                "timeline": "3-6 months",
                "affected_processors": ["stripe", "paypal", "square"]
            },
            {
                "category": "Market",
                "insight": "SMB segment driving growth in payment processing",
                "impact": "Medium",
                "timeline": "12-18 months", 
                "affected_processors": ["square", "crossmint"]
            }
        ],
        "opportunities": [
            {
                "opportunity": "Crypto payment integration",
                "market_size": 2.3,  # Billion USD
                "growth_rate": 67.8,  # %
                "leaders": ["crossmint", "coinbase"],
                "barriers": ["Regulatory uncertainty", "Technical complexity"]
            },
            {
                "opportunity": "Cross-border B2B payments", 
                "market_size": 12.7,  # Billion USD
                "growth_rate": 23.4,  # %
                "leaders": ["visa", "stripe"],
                "barriers": ["Regulatory compliance", "Network effects"]
            }
        ],
        "threats": [
            {
                "threat": "Big Tech entry (Apple, Google Pay expansion)",
                "probability": "High",
                "impact": "High",
                "timeline": "6-12 months"
            },
            {
                "threat": "Central Bank Digital Currencies (CBDCs)",
                "probability": "Medium",
                "impact": "High", 
                "timeline": "24-36 months"
            }
        ],
        "timestamp": datetime.now().isoformat(),
        "next_update": "2024-08-25T14:00:00Z"
    }

@app.get("/api/competitive-analysis/live-alerts")
async def get_live_alerts():
    """
    Competitive Analysis Dashboard - Real-time market alerts
    Returns: Live alerts about processor changes, outages, news
    """
    return {
        "alerts": [
            {
                "id": "alert_001",
                "type": "performance",
                "severity": "medium", 
                "processor": "square",
                "title": "Square experiencing elevated response times",
                "description": "Response times increased 15% over the last hour",
                "timestamp": "2024-08-24T14:30:00Z",
                "status": "active"
            },
            {
                "id": "alert_002", 
                "type": "pricing",
                "severity": "high",
                "processor": "crossmint",
                "title": "Crossmint announces volume discount program",
                "description": "New tiered pricing for merchants processing >$100K/month",
                "timestamp": "2024-08-24T13:15:00Z",
                "status": "new"
            },
            {
                "id": "alert_003",
                "type": "market",
                "severity": "low",
                "processor": "all",
                "title": "Industry report: Payment volumes up 12% YoY",
                "description": "McKinsey Global Payments Report shows continued growth",
                "timestamp": "2024-08-24T11:00:00Z", 
                "status": "acknowledged"
            }
        ],
        "alert_count": {
            "active": 1,
            "new": 1, 
            "acknowledged": 1,
            "total": 3
        },
        "timestamp": datetime.now().isoformat()
    }

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "endpoints_available": 8
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)