"""
Stripe-compatible Data Generation API for Claude Payment Orchestration
Generates realistic transaction data using proper Stripe schemas
"""

import asyncio
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from synthetic_data_generator import ClaudeSyntheticDataGenerator, SyntheticTransaction

# Initialize FastAPI app
app = FastAPI(
    title="Stripe Data Generation API",
    description="Generate realistic Stripe transaction data with Claude",
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

# Initialize data generator
try:
    data_generator = ClaudeSyntheticDataGenerator()
    print("✅ Claude Synthetic Data Generator initialized")
except Exception as e:
    print(f"⚠️ Data generator error: {e}")
    data_generator = None


class DataGenerationRequest(BaseModel):
    pattern_type: str = "normal"
    days: int = 30
    daily_volume: int = 50
    complexity: str = "balanced"


class RiskAnalysisRequest(BaseModel):
    transactions: List[Dict[str, Any]]
    analysis_type: str = "freeze_risk"
    complexity: str = "comprehensive"


@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "Stripe Data Generation API",
        "status": "operational",
        "claude_enabled": data_generator is not None,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "api": "healthy",
        "data_generator": "healthy" if data_generator else "unavailable",
        "stripe_schema": "supported"
    }


@app.post("/generate/demo-dataset")
async def generate_demo_dataset():
    """Generate complete demo dataset with all Stripe patterns"""
    
    if not data_generator:
        return await _generate_fallback_data()
    
    try:
        # Generate complete dataset
        dataset = await data_generator.generate_demo_dataset()
        
        # Process scenarios for frontend
        scenario_summary = {}
        for name, txns in dataset["freeze_scenarios"].items():
            charges = [t for t in txns if t.type == "charge"]
            refunds = [t for t in txns if t.type == "refund"]
            adjustments = [t for t in txns if t.type == "adjustment"]
            
            scenario_summary[name] = {
                "transaction_count": len(txns),
                "charges": len(charges),
                "refunds": len(refunds),
                "adjustments": len(adjustments),
                "refund_rate": (len(refunds) / len(charges) * 100) if charges else 0,
                "chargeback_rate": (len(adjustments) / len(charges) * 100) if charges else 0,
                "freeze_risk": "critical" if name in ["chargeback_pattern"] else "high" if name == "volume_spike" else "medium",
                "avg_amount": sum(t.amount for t in charges) / len(charges) if charges else 0
            }
        
        # Get baseline stats
        baseline_charges = [t for t in dataset["baseline"] if t.type == "charge"]
        baseline_refunds = [t for t in dataset["baseline"] if t.type == "refund"]
        
        return {
            "success": True,
            "baseline": {
                "transaction_count": len(dataset["baseline"]),
                "daily_average": len(baseline_charges) / 30,
                "avg_amount": sum(t.amount for t in baseline_charges) / len(baseline_charges) if baseline_charges else 0,
                "refund_rate": (len(baseline_refunds) / len(baseline_charges) * 100) if baseline_charges else 0
            },
            "scenarios": scenario_summary,
            "stripe_format_sample": data_generator.export_to_stripe_format(dataset["baseline"][:3]),
            "total_transactions": len(dataset["baseline"]) + sum(len(txns) for txns in dataset["freeze_scenarios"].values()),
            "claude_features": [
                "Realistic Stripe transaction patterns",
                "Account freeze trigger scenarios",
                "Proper balance_transaction format",
                "Risk pattern generation"
            ]
        }
        
    except Exception as e:
        print(f"Dataset generation error: {e}")
        return await _generate_fallback_data()


@app.post("/generate/pattern")
async def generate_specific_pattern(request: DataGenerationRequest):
    """Generate specific transaction pattern"""
    
    if not data_generator:
        return await _generate_simple_pattern(request.pattern_type)
    
    try:
        if request.pattern_type == "normal":
            transactions = await data_generator.generate_normal_baseline(
                days=request.days,
                daily_volume=request.daily_volume
            )
        else:
            transactions = await data_generator.generate_freeze_trigger_scenario(
                pattern_type=request.pattern_type
            )
        
        # Export to Stripe format
        stripe_data = data_generator.export_to_stripe_format(transactions)
        
        # Calculate stats
        charges = [t for t in transactions if t.type == "charge"]
        refunds = [t for t in transactions if t.type == "refund"]
        adjustments = [t for t in transactions if t.type == "adjustment"]
        
        return {
            "pattern_type": request.pattern_type,
            "transaction_count": len(transactions),
            "statistics": {
                "charges": len(charges),
                "refunds": len(refunds),
                "adjustments": len(adjustments),
                "refund_rate": (len(refunds) / len(charges) * 100) if charges else 0,
                "chargeback_rate": (len(adjustments) / len(charges) * 100) if charges else 0,
                "avg_amount": sum(t.amount for t in charges) / len(charges) if charges else 0,
                "total_volume": sum(t.amount for t in charges)
            },
            "stripe_transactions": stripe_data[:10],  # Sample
            "freeze_probability": _calculate_freeze_probability(request.pattern_type, len(refunds), len(charges), len(adjustments))
        }
        
    except Exception as e:
        print(f"Pattern generation error: {e}")
        return await _generate_simple_pattern(request.pattern_type)


@app.post("/analyze/risk")
async def analyze_transaction_risk(request: RiskAnalysisRequest):
    """Analyze transactions for Stripe freeze risk"""
    
    try:
        # Basic risk analysis
        charges = [t for t in request.transactions if t.get("type") == "charge"]
        refunds = [t for t in request.transactions if t.get("type") == "refund"]
        adjustments = [t for t in request.transactions if t.get("type") == "adjustment"]
        
        refund_rate = (len(refunds) / len(charges) * 100) if charges else 0
        chargeback_rate = (len(adjustments) / len(charges) * 100) if charges else 0
        
        # Risk scoring
        risk_score = 0
        risk_factors = []
        
        if refund_rate > 5:
            risk_score += 40
            risk_factors.append(f"High refund rate: {refund_rate:.1f}%")
        
        if chargeback_rate > 1:
            risk_score += 50
            risk_factors.append(f"High chargeback rate: {chargeback_rate:.1f}%")
        
        if len(charges) > 200:
            risk_score += 20
            risk_factors.append(f"High transaction volume: {len(charges)}")
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "critical"
            freeze_probability = 0.85
        elif risk_score >= 40:
            risk_level = "high"
            freeze_probability = 0.60
        elif risk_score >= 20:
            risk_level = "medium"
            freeze_probability = 0.25
        else:
            risk_level = "low"
            freeze_probability = 0.05
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "freeze_probability": freeze_probability,
            "detected_patterns": risk_factors,
            "recommendations": _get_risk_recommendations(risk_level),
            "claude_reasoning": f"Analyzed {len(request.transactions)} transactions. Refund rate: {refund_rate:.1f}%, Chargeback rate: {chargeback_rate:.1f}%",
            "stripe_thresholds": {
                "refund_rate_warning": "5%",
                "chargeback_rate_freeze": "1%",
                "volume_spike_review": "10x normal"
            }
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "risk_level": "unknown",
            "recommendations": ["Unable to analyze - check transaction format"]
        }


async def _generate_fallback_data():
    """Generate basic data without Claude"""
    
    fallback_transactions = []
    
    # Normal baseline (30 days)
    for day in range(30):
        daily_count = random.randint(40, 60)
        for i in range(daily_count):
            amount = random.uniform(25, 200)
            tx_id = f"txn_{uuid.uuid4().hex[:17]}"
            
            transaction = {
                "id": tx_id,
                "object": "balance_transaction",
                "amount": int(amount * 100),
                "currency": "usd",
                "created": int((datetime.utcnow() - timedelta(days=30-day)).timestamp()),
                "fee": int((amount * 0.029 + 0.30) * 100),
                "net": int((amount - (amount * 0.029 + 0.30)) * 100),
                "type": "charge",
                "status": "available",
                "description": "Monthly subscription"
            }
            fallback_transactions.append(transaction)
    
    # Risk scenarios
    risk_scenarios = {
        "volume_spike": _generate_volume_spike_fallback(),
        "refund_surge": _generate_refund_surge_fallback(),
        "chargeback_pattern": _generate_chargeback_fallback()
    }
    
    return {
        "success": True,
        "fallback_mode": True,
        "baseline": {
            "transaction_count": len(fallback_transactions),
            "daily_average": len(fallback_transactions) / 30
        },
        "scenarios": {
            name: {
                "transaction_count": len(data),
                "freeze_risk": "high"
            }
            for name, data in risk_scenarios.items()
        },
        "stripe_format_sample": fallback_transactions[:3]
    }


def _generate_volume_spike_fallback():
    """Generate volume spike without Claude"""
    spike_transactions = []
    for i in range(500):  # 10x normal
        amount = random.uniform(200, 2000)
        tx_id = f"txn_{uuid.uuid4().hex[:17]}"
        
        spike_transactions.append({
            "id": tx_id,
            "amount": int(amount * 100),
            "type": "charge",
            "created": int(datetime.utcnow().timestamp()),
            "description": "Large promotional purchase"
        })
    
    return spike_transactions


def _generate_refund_surge_fallback():
    """Generate refund surge without Claude"""
    refund_transactions = []
    
    # Charges first
    for i in range(100):
        amount = random.uniform(50, 300)
        charge = {
            "id": f"ch_{uuid.uuid4().hex[:24]}",
            "amount": int(amount * 100),
            "type": "charge",
            "created": int(datetime.utcnow().timestamp())
        }
        refund_transactions.append(charge)
        
        # 15% refund rate
        if random.random() < 0.15:
            refund = {
                "id": f"re_{uuid.uuid4().hex[:24]}",
                "amount": -int(amount * 100),
                "type": "refund",
                "created": int(datetime.utcnow().timestamp()),
                "description": "Customer complaint"
            }
            refund_transactions.append(refund)
    
    return refund_transactions


def _generate_chargeback_fallback():
    """Generate chargeback pattern without Claude"""
    chargeback_transactions = []
    
    for i in range(200):
        amount = random.uniform(100, 800)
        charge = {
            "id": f"ch_{uuid.uuid4().hex[:24]}",
            "amount": int(amount * 100),
            "type": "charge",
            "created": int(datetime.utcnow().timestamp())
        }
        chargeback_transactions.append(charge)
        
        # 3% chargeback rate
        if random.random() < 0.03:
            chargeback = {
                "id": f"cb_{uuid.uuid4().hex[:24]}",
                "amount": -int((amount + 15) * 100),  # Amount + fee
                "type": "adjustment",
                "created": int(datetime.utcnow().timestamp()),
                "description": "Chargeback fee"
            }
            chargeback_transactions.append(chargeback)
    
    return chargeback_transactions


async def _generate_simple_pattern(pattern_type: str):
    """Generate simple pattern without Claude"""
    
    if pattern_type == "volume_spike":
        data = _generate_volume_spike_fallback()
    elif pattern_type == "high_refund_rate":
        data = _generate_refund_surge_fallback()
    elif pattern_type == "chargeback_surge":
        data = _generate_chargeback_fallback()
    else:
        data = []
        for i in range(50):
            amount = random.uniform(25, 150)
            data.append({
                "id": f"txn_{uuid.uuid4().hex[:17]}",
                "amount": int(amount * 100),
                "type": "charge",
                "created": int(datetime.utcnow().timestamp())
            })
    
    return {
        "pattern_type": pattern_type,
        "transaction_count": len(data),
        "fallback_mode": True,
        "stripe_transactions": data[:10]
    }


def _calculate_freeze_probability(pattern_type: str, refund_count: int, charge_count: int, adjustment_count: int) -> float:
    """Calculate freeze probability based on pattern"""
    
    if pattern_type == "chargeback_surge":
        return 0.90
    elif pattern_type == "volume_spike":
        return 0.75
    elif pattern_type == "high_refund_rate":
        refund_rate = (refund_count / charge_count) if charge_count else 0
        return min(refund_rate * 10, 0.85)  # Higher refund rate = higher freeze prob
    else:
        return 0.10


def _get_risk_recommendations(risk_level: str) -> List[str]:
    """Get recommendations based on risk level"""
    
    if risk_level == "critical":
        return [
            "Contact Stripe immediately to explain transaction patterns",
            "Prepare all documentation (invoices, contracts, customer communications)",
            "Implement additional fraud prevention measures",
            "Consider temporarily reducing transaction volume"
        ]
    elif risk_level == "high":
        return [
            "Monitor refund and chargeback rates closely",
            "Prepare documentation for potential Stripe review",
            "Implement customer service improvements to reduce disputes"
        ]
    elif risk_level == "medium":
        return [
            "Continue monitoring transaction patterns",
            "Maintain detailed records",
            "Consider gradual scaling rather than sudden increases"
        ]
    else:
        return [
            "Current patterns are normal",
            "Continue existing practices"
        ]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)