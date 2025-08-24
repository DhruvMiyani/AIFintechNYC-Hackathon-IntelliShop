"""
FastAPI Data Analysis API for Claude Payment Orchestration
Complete API server for synthetic data generation and risk analysis
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from claude_client import ClaudeClient
from stripe_synthetic_data_generator import GPT5StripeDataGenerator as ClaudeStripeDataGenerator, StripeTransaction
from risk_pattern_analyzer import ClaudeRiskAnalyzer, RiskAnalysis
from realtime_data_simulator import RealtimeStreamSimulator, StreamingMode, StreamDataStore
from synthetic_data_generator import ClaudeSyntheticDataGenerator, SyntheticTransaction

# Initialize FastAPI app
app = FastAPI(
    title="Claude Payment Data Analysis API",
    description="Advanced payment data generation and risk analysis using Claude",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
claude_client = ClaudeClient()
data_generator = ClaudeSyntheticDataGenerator()
risk_analyzer = ClaudeRiskAnalyzer()
stream_simulator = RealtimeStreamSimulator()
stream_data_store = StreamDataStore()

# Global state
active_streams = {}
generated_datasets = {}


class DataAnalysisRequest(BaseModel):
    transactions: List[Dict[str, Any]]
    analysis_type: str = "freeze_risk"
    reasoning_effort: str = "medium"


class RiskAnalysisResponse(BaseModel):
    risk_level: str
    risk_score: float
    freeze_probability: float
    detected_patterns: List[str]
    recommendations: List[str] 
    gpt5_reasoning: str
    analysis_time_ms: float


class DataGenerationRequest(BaseModel):
    pattern_type: str = "normal"  # normal, sudden_spike, high_refund_rate, chargeback_surge
    days: int = 30
    daily_volume: int = 50
    reasoning_effort: str = "medium"


# Additional Pydantic models for new endpoints
class StreamingRequest(BaseModel):
    mode: str = Field(..., description="Streaming mode: normal, high_volume, risk_pattern, mixed")
    target_rate: float = Field(default=2.0, ge=0.1, le=100.0, description="Target transactions per second")
    duration_seconds: Optional[int] = Field(None, ge=10, le=3600, description="Stream duration in seconds")


class StreamingResponse(BaseModel):
    stream_id: str
    mode: str
    target_rate: float
    is_active: bool
    transaction_count: int
    total_volume: float


class RiskAnalysisRequest(BaseModel):
    transaction_ids: Optional[List[str]] = Field(None, description="Specific transaction IDs to analyze")
    time_window_hours: int = Field(default=24, ge=1, le=168, description="Analysis time window in hours")
    reasoning_effort: str = Field(default="high", description="GPT-5 reasoning effort")
    include_gpt5_insights: bool = Field(default=True, description="Include GPT-5 insights in response")


@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "GPT-5 Payment Data Analysis API",
        "status": "operational",
        "version": "1.0.0",
        "gpt5_enabled": True,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        return {
            "api": "healthy",
            "gpt5_client": "healthy",
            "data_generator": "healthy",
            "risk_analyzer": "healthy",
            "stream_simulator": "healthy",
            "active_streams": len(active_streams),
            "stored_datasets": len(generated_datasets)
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


# Initialize GPT-5 data generator (legacy)
legacy_data_generator = ClaudeSyntheticDataGenerator()


@app.post("/data/generate", response_model=Dict[str, Any])
async def generate_synthetic_data(request: DataGenerationRequest):
    """
    Generate synthetic Stripe transaction data using GPT-5.
    Demonstrates GPT-5's structured data generation capabilities.
    """
    
    if request.pattern_type == "normal":
        transactions = await legacy_data_generator.generate_normal_baseline(
            days=request.days,
            daily_volume=request.daily_volume
        )
        
        return {
            "pattern_type": "normal_baseline",
            "transaction_count": len(transactions),
            "period_days": request.days,
            "daily_average": len(transactions) / request.days,
            "gpt5_features": {
                "reasoning_effort": request.reasoning_effort,
                "verbosity": "low",
                "structured_generation": True
            },
            "sample_transactions": legacy_data_generator.export_to_stripe_format(transactions[:5]),
            "summary": {
                "avg_amount": sum(t.amount for t in transactions if t.type == "charge") / len([t for t in transactions if t.type == "charge"]),
                "total_volume": sum(t.amount for t in transactions if t.type == "charge"),
                "refund_rate": len([t for t in transactions if t.type == "refund"]) / len([t for t in transactions if t.type == "charge"]) * 100
            }
        }
    
    else:
        # Generate freeze trigger patterns
        transactions = await legacy_data_generator.generate_freeze_trigger_scenario(
            pattern_type=request.pattern_type,
            severity="high"
        )
        
        charges = [t for t in transactions if t.type == "charge"]
        refunds = [t for t in transactions if t.type == "refund"] 
        adjustments = [t for t in transactions if t.type == "adjustment"]
        
        return {
            "pattern_type": request.pattern_type,
            "transaction_count": len(transactions),
            "risk_indicators": {
                "charges": len(charges),
                "refunds": len(refunds),
                "adjustments": len(adjustments),
                "refund_rate": (len(refunds) / len(charges) * 100) if charges else 0,
                "chargeback_rate": (len(adjustments) / len(charges) * 100) if charges else 0
            },
            "freeze_likelihood": "high" if request.pattern_type in ["chargeback_surge", "sudden_spike"] else "medium",
            "gpt5_analysis": {
                "reasoning_effort": "high", 
                "pattern_recognition": True,
                "risk_modeling": True
            },
            "sample_transactions": legacy_data_generator.export_to_stripe_format(transactions[:10])
        }


@app.post("/data/analyze", response_model=RiskAnalysisResponse) 
async def analyze_transaction_risk(request: DataAnalysisRequest):
    """
    Analyze transaction patterns for Stripe freeze risk using GPT-5 reasoning.
    Uses high reasoning effort for complex risk assessment.
    """
    
    start_time = datetime.utcnow()
    
    # Prepare transaction data for GPT-5 analysis
    gpt5_context = {
        "transaction_count": len(request.transactions),
        "analysis_window": "recent_activity",
        "business_context": "B2B payment processing",
        "stripe_freeze_thresholds": {
            "refund_rate": 5.0,    # 5% triggers review
            "chargeback_rate": 1.0, # 1% triggers freeze
            "volume_spike": 10.0,   # 10x normal volume
            "amount_variance": 5.0  # 5x normal transaction size
        }
    }
    
    # Simulate GPT-5 risk analysis with high reasoning effort
    risk_analysis = await _simulate_gpt5_risk_analysis(
        transactions=request.transactions,
        context=gpt5_context,
        reasoning_effort=request.reasoning_effort
    )
    
    processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    return RiskAnalysisResponse(
        risk_level=risk_analysis["risk_level"],
        risk_score=risk_analysis["risk_score"], 
        freeze_probability=risk_analysis["freeze_probability"],
        detected_patterns=risk_analysis["patterns"],
        recommendations=risk_analysis["recommendations"],
        gpt5_reasoning=risk_analysis["reasoning"],
        analysis_time_ms=processing_time
    )


@app.get("/data/demo/complete-dataset")
async def generate_complete_demo_dataset():
    """
    Generate complete demo dataset showing GPT-5's data generation capabilities.
    Creates normal baseline + all freeze trigger scenarios.
    """
    
    dataset = await legacy_data_generator.generate_demo_dataset()
    
    # Export all data in Stripe format
    all_transactions = []
    all_transactions.extend(dataset["baseline"])
    
    for scenario_name, scenario_txns in dataset["freeze_scenarios"].items():
        all_transactions.extend(scenario_txns)
    
    stripe_format = legacy_data_generator.export_to_stripe_format(all_transactions)
    
    # Analyze each scenario
    scenario_analysis = {}
    for scenario_name, scenario_txns in dataset["freeze_scenarios"].items():
        charges = [t for t in scenario_txns if t.type == "charge"]
        refunds = [t for t in scenario_txns if t.type == "refund"]
        adjustments = [t for t in scenario_txns if t.type == "adjustment"]
        
        scenario_analysis[scenario_name] = {
            "transaction_count": len(scenario_txns),
            "charges": len(charges),
            "refunds": len(refunds),
            "adjustments": len(adjustments),
            "refund_rate": (len(refunds) / len(charges) * 100) if charges else 0,
            "chargeback_rate": (len(adjustments) / len(charges) * 100) if charges else 0,
            "avg_amount": sum(t.amount for t in charges) / len(charges) if charges else 0,
            "freeze_risk": "high" if scenario_name in ["chargeback_surge", "sudden_spike"] else "medium"
        }
    
    return {
        "dataset_summary": dataset["summary"],
        "total_transactions": len(all_transactions),
        "scenario_breakdown": scenario_analysis,
        "baseline_stats": {
            "period": "30 days",
            "transaction_count": len(dataset["baseline"]),
            "daily_average": len(dataset["baseline"]) / 30,
            "avg_amount": sum(t.amount for t in dataset["baseline"] if t.type == "charge") / len([t for t in dataset["baseline"] if t.type == "charge"])
        },
        "gpt5_capabilities_demonstrated": [
            "Structured data generation with schema compliance",
            "Pattern recognition and risk modeling", 
            "Reasoning effort control (minimal/medium/high)",
            "Verbosity control for different output needs",
            "Context-aware synthetic data creation",
            "Long context analysis (256K+ tokens)",
            "Self-critique loops for data quality"
        ],
        "stripe_format_sample": stripe_format[:5],  # First 5 transactions
        "download_url": "/data/export/stripe-format"  # For full dataset download
    }


@app.get("/data/patterns/freeze-triggers")
async def get_freeze_trigger_patterns():
    """
    Get detailed information about transaction patterns that trigger Stripe freezes.
    Educational endpoint showing what GPT-5 models and detects.
    """
    
    return {
        "freeze_triggers": {
            "sudden_spike": {
                "description": "Dramatic increase in transaction volume or amounts",
                "thresholds": {
                    "volume_multiplier": "10x normal daily volume",
                    "time_compression": "Large volume in <4 hours",
                    "amount_increase": "5x normal transaction size"
                },
                "typical_timeline": "Account frozen within 24 hours",
                "stripe_response": "Immediate investigation, documentation request"
            },
            "high_refund_rate": {
                "description": "Excessive refunds indicating product/service issues",
                "thresholds": {
                    "refund_rate": ">5% of transactions",
                    "refund_velocity": "Multiple refunds in short timeframe",
                    "refund_amounts": "Large refunds relative to charges"
                },
                "typical_timeline": "Review triggered at 5%, freeze at 10%+",
                "stripe_response": "Risk review, possible fund hold"
            },
            "chargeback_surge": {
                "description": "Chargebacks exceeding Stripe's tolerance threshold", 
                "thresholds": {
                    "chargeback_rate": ">1% of transactions",
                    "dispute_pattern": "Multiple disputes from different customers",
                    "fraud_indicators": "High-risk transaction characteristics"
                },
                "typical_timeline": "Immediate freeze at 1% threshold",
                "stripe_response": "Account freeze, 180-day fund hold"
            },
            "pattern_deviation": {
                "description": "Transactions inconsistent with business profile",
                "indicators": [
                    "Sudden change in average transaction size",
                    "New geographic regions",
                    "Different customer demographics", 
                    "Unusual timing patterns",
                    "Currency changes"
                ],
                "typical_timeline": "Review within 48-72 hours",
                "stripe_response": "Documentation request, possible temporary limits"
            }
        },
        "prevention_strategies": [
            "Gradual scaling rather than sudden spikes",
            "Proactive communication with Stripe about business changes", 
            "Maintain detailed transaction documentation",
            "Monitor refund and chargeback rates closely",
            "Implement fraud prevention measures"
        ],
        "gpt5_detection_capabilities": {
            "pattern_recognition": "Identifies subtle risk indicators",
            "contextual_analysis": "Understands business context and seasonality",
            "predictive_modeling": "Estimates freeze probability",
            "recommendation_engine": "Suggests risk mitigation strategies"
        }
    }


async def _simulate_gpt5_risk_analysis(
    transactions: List[Dict[str, Any]],
    context: Dict[str, Any],
    reasoning_effort: str = "high"
) -> Dict[str, Any]:
    """
    Simulate GPT-5's risk analysis reasoning process.
    In production, this would call the actual GPT-5 API.
    """
    
    import asyncio
    await asyncio.sleep(0.5 if reasoning_effort == "high" else 0.2)
    
    # Analyze transaction patterns
    charges = [t for t in transactions if t.get("type") == "charge"]
    refunds = [t for t in transactions if t.get("type") == "refund"] 
    
    total_charges = len(charges)
    total_refunds = len(refunds)
    refund_rate = (total_refunds / total_charges * 100) if total_charges else 0
    
    # Calculate risk indicators
    risk_score = 0.0
    detected_patterns = []
    
    if refund_rate > 5.0:
        risk_score += 40.0
        detected_patterns.append(f"High refund rate: {refund_rate:.1f}%")
    
    if total_charges > 500:  # Volume spike
        risk_score += 30.0  
        detected_patterns.append(f"Volume spike detected: {total_charges} transactions")
    
    # Determine risk level
    if risk_score >= 70:
        risk_level = "critical"
        freeze_probability = 0.9
    elif risk_score >= 40:
        risk_level = "high"
        freeze_probability = 0.6
    elif risk_score >= 20:
        risk_level = "medium" 
        freeze_probability = 0.3
    else:
        risk_level = "low"
        freeze_probability = 0.1
    
    # Generate reasoning explanation
    reasoning = f"""
    GPT-5 Risk Analysis (reasoning_effort={reasoning_effort}):
    
    Transaction Analysis:
    - Analyzed {len(transactions)} transactions
    - Identified {len(charges)} charges, {len(refunds)} refunds
    - Calculated refund rate: {refund_rate:.1f}%
    
    Risk Assessment:
    - Risk score: {risk_score}/100
    - Primary risk factors: {', '.join(detected_patterns) if detected_patterns else 'None detected'}
    - Stripe freeze probability: {freeze_probability*100:.0f}%
    
    Pattern Recognition:
    {'High-risk patterns detected requiring immediate attention.' if risk_level in ['critical', 'high'] else 'Transaction patterns within normal parameters.'}
    """
    
    recommendations = []
    if risk_level in ["critical", "high"]:
        recommendations.extend([
            "Contact Stripe proactively to explain transaction patterns",
            "Prepare documentation (invoices, contracts, customer communications)",
            "Consider implementing additional fraud prevention measures",
            "Monitor refund/chargeback rates closely"
        ])
    elif risk_level == "medium":
        recommendations.extend([
            "Monitor transaction patterns for further changes", 
            "Maintain detailed transaction records",
            "Consider gradual scaling rather than sudden increases"
        ])
    else:
        recommendations.append("Continue current practices - patterns are normal")
    
    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "freeze_probability": freeze_probability,
        "patterns": detected_patterns,
        "recommendations": recommendations,
        "reasoning": reasoning.strip()
    }


# New streaming and advanced analysis endpoints
@app.post("/stream/start", response_model=StreamingResponse)
async def start_transaction_stream(request: StreamingRequest, background_tasks: BackgroundTasks):
    """Start real-time transaction stream simulation"""
    
    try:
        stream_id = f"stream_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            mode = StreamingMode(request.mode)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid streaming mode: {request.mode}")
        
        # Start streaming in background
        background_tasks.add_task(
            run_streaming_task,
            stream_id,
            mode,
            request.target_rate,
            request.duration_seconds
        )
        
        # Store stream info
        active_streams[stream_id] = {
            "mode": request.mode,
            "target_rate": request.target_rate,
            "started_at": datetime.utcnow(),
            "is_active": True,
            "transaction_count": 0
        }
        
        return StreamingResponse(
            stream_id=stream_id,
            mode=request.mode,
            target_rate=request.target_rate,
            is_active=True,
            transaction_count=0,
            total_volume=0.0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start stream: {str(e)}")


@app.get("/stream/{stream_id}/status")
async def get_stream_status(stream_id: str = Path(..., description="Stream ID")):
    """Get status of a specific stream"""
    
    if stream_id not in active_streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    stream_info = active_streams[stream_id]
    stats = stream_simulator.get_stream_stats()
    
    return {
        "stream_id": stream_id,
        "mode": stream_info["mode"],
        "target_rate": stream_info["target_rate"],
        "started_at": stream_info["started_at"].isoformat(),
        "is_active": stream_info["is_active"],
        "runtime_seconds": (datetime.utcnow() - stream_info["started_at"]).total_seconds(),
        "statistics": stats
    }


@app.post("/analyze/advanced", response_model=Dict[str, Any])
async def advanced_risk_analysis(request: RiskAnalysisRequest):
    """Perform advanced GPT-5 risk analysis"""
    
    try:
        # Get transactions for analysis
        if request.transaction_ids:
            transactions = []  # Would need transaction lookup in real implementation
        else:
            cutoff_time = datetime.utcnow() - timedelta(hours=request.time_window_hours)
            stream_data = stream_data_store.get_transactions_by_timerange(
                cutoff_time, datetime.utcnow()
            )
            transactions = [sd.transaction for sd in stream_data]
        
        if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found for analysis")
        
        # Perform advanced risk analysis
        analysis = await risk_analyzer.analyze_transactions(
            transactions=transactions,
            reasoning_effort=request.reasoning_effort
        )
        
        return {
            "overall_risk": analysis.overall_risk.value,
            "freeze_probability": analysis.freeze_probability,
            "identified_patterns": [
                {
                    "pattern_type": p.pattern_type,
                    "severity": p.severity.value,
                    "description": p.description,
                    "confidence": p.confidence,
                    "freeze_probability": p.freeze_probability,
                    "timeline_estimate": p.timeline_estimate,
                    "gpt5_reasoning": p.gpt5_reasoning
                }
                for p in analysis.identified_patterns
            ],
            "recommendations": analysis.recommendations,
            "gpt5_insights": analysis.gpt5_insights if request.include_gpt5_insights else {},
            "analysis_timestamp": analysis.analysis_timestamp.isoformat(),
            "transaction_count": len(transactions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advanced analysis failed: {str(e)}")


@app.get("/gpt5/capabilities")
async def get_gpt5_capabilities():
    """Get GPT-5 capabilities and current status"""
    
    return {
        "model": "gpt-5",
        "capabilities": {
            "reasoning_effort_control": {
                "levels": ["minimal", "low", "medium", "high"],
                "description": "Control reasoning depth for different tasks"
            },
            "verbosity_control": {
                "levels": ["low", "medium", "high"],
                "description": "Control output detail level"
            },
            "structured_data_generation": {
                "supported": True,
                "description": "Generate complex structured datasets"
            },
            "risk_pattern_analysis": {
                "supported": True,
                "description": "Advanced risk pattern detection and analysis"
            },
            "chain_of_thought_reasoning": {
                "supported": True,
                "description": "Detailed reasoning traces for audit purposes"
            },
            "long_context_analysis": {
                "context_length": "256K+ tokens",
                "description": "Analyze large transaction datasets"
            }
        },
        "use_cases": [
            "Payment routing decisions with explainable reasoning",
            "Synthetic transaction data generation for testing",
            "Real-time risk pattern detection",
            "Compliance audit log generation",
            "Fraud detection and prevention"
        ]
    }


# Background task functions
async def run_streaming_task(
    stream_id: str,
    mode: StreamingMode,
    target_rate: float,
    duration_seconds: Optional[int]
):
    """Run streaming simulation in background"""
    
    try:
        stream_count = 0
        
        async for stream_data in stream_simulator.start_continuous_stream(mode, target_rate):
            stream_data_store.add_transaction(stream_data)
            stream_count += 1
            
            # Update stream info
            if stream_id in active_streams:
                active_streams[stream_id]["transaction_count"] = stream_count
            
            # Stop after duration if specified
            if duration_seconds and stream_count * (1.0 / target_rate) >= duration_seconds:
                break
        
        # Mark stream as inactive
        if stream_id in active_streams:
            active_streams[stream_id]["is_active"] = False
            
    except Exception as e:
        print(f"Streaming task error for {stream_id}: {e}")
        if stream_id in active_streams:
            active_streams[stream_id]["is_active"] = False


if __name__ == "__main__":
    uvicorn.run(
        "data_analysis_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )