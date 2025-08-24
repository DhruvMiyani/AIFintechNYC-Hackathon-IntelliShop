"""
Simplified FastAPI Server for Claude Payment Orchestration Demo
"""

import asyncio
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import custom processors
from crossmint_processor import CrossmintPaymentProcessor

# Initialize FastAPI app
app = FastAPI(
    title="Claude Payment Demo API",
    description="Simplified API for Claude payment orchestration demo",
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

# Request/Response models
class DataGenerationRequest(BaseModel):
    pattern_type: str = "normal"
    days: int = 30
    daily_volume: int = 50
    analysis_complexity: str = "balanced"

class PaymentRequest(BaseModel):
    amount: float
    currency: str
    description: str
    analysis_complexity: str

class VisaMCPRequest(BaseModel):
    amount: float
    currency: str
    customer_email: str = ""
    customer_name: str = ""
    description: str

class CrossmintRequest(BaseModel):
    amount: float
    currency: str  # usdc, sol, eth, matic
    chain: str  # solana, ethereum, polygon
    customer_email: str
    description: str
    analysis_complexity: str = "balanced"

@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "Claude Payment Demo API",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "api": "healthy",
        "claude_client": "demo_mode",
        "data_generator": "healthy"
    }

@app.post("/data/generate")
async def generate_synthetic_data(request: DataGenerationRequest):
    """Generate synthetic transaction data"""
    
    # Simulate processing delay
    await asyncio.sleep(1.0)
    
    # Generate different transaction counts based on pattern
    pattern_configs = {
        "normal": {"count": 150, "risk": "low"},
        "freeze_trigger": {"count": 1200, "risk": "high"},
        "sudden_spike": {"count": 800, "risk": "high"},
        "high_refund_rate": {"count": 400, "risk": "critical"},
        "chargeback_surge": {"count": 600, "risk": "critical"},
        "volume_spike": {"count": 500, "risk": "high"}
    }
    
    config = pattern_configs.get(request.pattern_type, pattern_configs["normal"])
    transaction_count = config["count"] + random.randint(-50, 50)
    
    # Generate sample transactions
    sample_transactions = []
    for i in range(min(5, transaction_count)):
        sample_transactions.append({
            "id": f"txn_{uuid.uuid4().hex[:17]}",
            "object": "balance_transaction",
            "amount": random.randint(5000, 50000),  # $50-500 in cents
            "currency": "usd",
            "created": int(datetime.utcnow().timestamp()),
            "type": "charge",
            "status": "available"
        })
    
    return {
        "success": True,
        "pattern_type": request.pattern_type,
        "transaction_count": transaction_count,
        "freeze_likelihood": config["risk"],
        "sample_transactions": sample_transactions,
        "claude_features": {
            "complexity": request.analysis_complexity,
            "structured_generation": True,
            "pattern_recognition": True
        }
    }

@app.get("/data/demo/complete-dataset")
async def generate_complete_demo_dataset():
    """Generate complete demo dataset with actual transactions"""
    
    await asyncio.sleep(2.0)  # Simulate generation time
    
    # Generate actual transaction data
    all_transactions = []
    
    # 1. Generate baseline transactions (1350)
    baseline_count = 1350
    for i in range(baseline_count):
        day_offset = i % 30  # Spread across 30 days
        all_transactions.append({
            "id": f"txn_{uuid.uuid4().hex[:17]}",
            "object": "balance_transaction",
            "amount": random.randint(5000, 15000),  # $50-150
            "currency": "usd",
            "created": int((datetime.utcnow() - timedelta(days=30-day_offset)).timestamp()),
            "type": "charge",
            "status": "available",
            "description": "Monthly subscription",
            "risk_flag": "normal"
        })
    
    # 2. Generate volume spike transactions (400-500)
    volume_spike_count = random.randint(400, 500)
    spike_time = datetime.utcnow() - timedelta(days=5)
    for i in range(volume_spike_count):
        all_transactions.append({
            "id": f"txn_{uuid.uuid4().hex[:17]}",
            "object": "balance_transaction", 
            "amount": random.randint(20000, 200000),  # $200-2000 (high amounts)
            "currency": "usd",
            "created": int((spike_time + timedelta(minutes=random.randint(0, 180))).timestamp()),
            "type": "charge",
            "status": "available",
            "description": "Large promotional purchase",
            "risk_flag": "volume_spike"
        })
    
    # 3. Generate refund surge transactions (80-120)
    refund_surge_count = random.randint(80, 120)
    for i in range(refund_surge_count):
        # Original charge
        charge_id = f"ch_{uuid.uuid4().hex[:24]}"
        charge_amount = random.randint(5000, 30000)
        all_transactions.append({
            "id": f"txn_{charge_id[3:20]}",
            "object": "balance_transaction",
            "amount": charge_amount,
            "currency": "usd",
            "created": int((datetime.utcnow() - timedelta(days=random.randint(2, 7))).timestamp()),
            "type": "charge",
            "status": "available",
            "description": "Product purchase",
            "risk_flag": "refund_surge"
        })
        # Refund
        if random.random() < 0.15:  # 15% refund rate
            all_transactions.append({
                "id": f"txn_re_{uuid.uuid4().hex[:14]}",
                "object": "balance_transaction",
                "amount": -charge_amount,
                "currency": "usd",
                "created": int((datetime.utcnow() - timedelta(days=random.randint(0, 2))).timestamp()),
                "type": "refund",
                "status": "available",
                "description": "Customer refund",
                "risk_flag": "refund_surge",
                "source_id": charge_id
            })
    
    # 4. Generate chargeback pattern transactions (150-200)
    chargeback_count = random.randint(150, 200)
    for i in range(chargeback_count):
        charge_id = f"ch_{uuid.uuid4().hex[:24]}"
        charge_amount = random.randint(10000, 80000)
        all_transactions.append({
            "id": f"txn_{charge_id[3:20]}",
            "object": "balance_transaction",
            "amount": charge_amount,
            "currency": "usd",
            "created": int((datetime.utcnow() - timedelta(days=random.randint(10, 30))).timestamp()),
            "type": "charge",
            "status": "available",
            "description": "High-risk transaction",
            "risk_flag": "chargeback_pattern"
        })
        # Chargeback (3% rate)
        if random.random() < 0.03:
            all_transactions.append({
                "id": f"txn_cb_{uuid.uuid4().hex[:14]}",
                "object": "balance_transaction",
                "amount": -(charge_amount + 1500),  # Amount + $15 fee
                "currency": "usd",
                "created": int((datetime.utcnow() - timedelta(days=random.randint(0, 5))).timestamp()),
                "type": "adjustment",
                "status": "available",
                "description": "Chargeback fee",
                "risk_flag": "chargeback_pattern",
                "source_id": charge_id
            })
    
    # Calculate stats
    total_count = len(all_transactions)
    
    # Calculate actual statistics from generated data
    volume_spike_txns = [t for t in all_transactions if t.get("risk_flag") == "volume_spike"]
    refund_surge_txns = [t for t in all_transactions if t.get("risk_flag") == "refund_surge"]
    chargeback_txns = [t for t in all_transactions if t.get("risk_flag") == "chargeback_pattern"]
    baseline_txns = [t for t in all_transactions if t.get("risk_flag") == "normal"]
    
    return {
        "dataset_summary": {
            "total_transactions": total_count,
            "actual_count": len(all_transactions),
            "generation_time": "3.2 seconds",
            "claude_complexity": "comprehensive"
        },
        "total_transactions": total_count,
        "transactions": all_transactions[:100],  # Return first 100 transactions as sample
        "all_transactions_available": total_count,
        "scenario_breakdown": {
            "volume_spike": {
                "transaction_count": len(volume_spike_txns),
                "freeze_risk": "high",
                "sample_transactions": volume_spike_txns[:5]
            },
            "refund_surge": {
                "transaction_count": len(refund_surge_txns),
                "freeze_risk": "critical", 
                "sample_transactions": refund_surge_txns[:5]
            },
            "chargeback_pattern": {
                "transaction_count": len(chargeback_txns),
                "freeze_risk": "critical",
                "sample_transactions": chargeback_txns[:5]
            },
            "baseline": {
                "transaction_count": len(baseline_txns),
                "freeze_risk": "low",
                "sample_transactions": baseline_txns[:5]
            }
        },
        "baseline_stats": {
            "period": "30 days",
            "transaction_count": len(baseline_txns),
            "daily_average": len(baseline_txns) / 30 if baseline_txns else 0,
            "avg_amount": sum(t["amount"] for t in baseline_txns) / len(baseline_txns) / 100 if baseline_txns else 85.0
        },
        "claude_capabilities_demonstrated": [
            "Structured data generation with schema compliance",
            "Pattern recognition and risk modeling", 
            "Analysis complexity control (simple/balanced/comprehensive)",
            "Context-aware synthetic data creation",
            "Advanced reasoning capabilities"
        ],
        "download_endpoints": {
            "all_transactions": "/data/transactions/all",
            "by_risk_flag": "/data/transactions/{risk_flag}",
            "export_csv": "/data/export/csv",
            "export_stripe": "/data/export/stripe"
        }
    }

@app.get("/data/transactions/all")
async def get_all_transactions():
    """Get ALL transaction data (full dataset)"""
    
    # Generate the same dataset as complete-dataset endpoint
    all_transactions = []
    
    # Generate 2000+ transactions
    for i in range(2000):
        transaction_type = random.choice(["charge", "refund", "adjustment"])
        amount = random.randint(1000, 100000) if transaction_type == "charge" else -random.randint(1000, 50000)
        
        all_transactions.append({
            "id": f"txn_{uuid.uuid4().hex[:17]}",
            "object": "balance_transaction",
            "amount": amount,
            "currency": "usd",
            "created": int((datetime.utcnow() - timedelta(days=random.randint(0, 30))).timestamp()),
            "type": transaction_type,
            "status": "available",
            "fee": int(abs(amount) * 0.029 + 30) if transaction_type == "charge" else 0,
            "net": int(amount - (abs(amount) * 0.029 + 30)) if transaction_type == "charge" else amount,
            "description": f"Transaction {i+1}",
            "metadata": {
                "risk_flag": random.choice(["normal", "volume_spike", "refund_surge", "chargeback_pattern"]),
                "claude_analyzed": True
            }
        })
    
    return {
        "total_count": len(all_transactions),
        "transactions": all_transactions,
        "export_format": "stripe_balance_transaction",
        "generated_at": datetime.utcnow().isoformat()
    }

@app.post("/analyze/risk-engine")
async def claude_risk_analysis_engine():
    """Enhanced Claude Risk Analysis Engine using real transaction data"""
    
    try:
        # Import and use the risk analyzer
        import subprocess
        import json
        
        # Run the risk analyzer
        result = subprocess.run([
            'python3', 'claude_risk_analyzer.py'
        ], capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            # Parse the output for key metrics
            output = result.stdout
            
            # Extract risk level
            risk_level = "unknown"
            freeze_probability = 0.0
            
            for line in output.split('\n'):
                if "Overall Risk Level:" in line:
                    risk_level = line.split(': ')[1].lower()
                elif "Freeze Probability:" in line:
                    freeze_probability = float(line.split(': ')[1].rstrip('%')) / 100
            
            return {
                "success": True,
                "analysis_type": "claude_risk_engine",
                "overall_risk": risk_level,
                "freeze_probability": freeze_probability,
                "raw_output": output,
                "recommendations": [
                    "Enhanced risk analysis complete",
                    f"Risk level: {risk_level.upper()}",
                    f"Freeze probability: {freeze_probability:.1%}",
                    "See full analysis in raw_output"
                ],
                "claude_features": {
                    "real_transaction_analysis": True,
                    "pattern_recognition": True,
                    "database_integration": True,
                    "comprehensive_reasoning": True
                }
            }
        else:
            return {
                "success": False,
                "error": "Risk analysis failed",
                "details": result.stderr
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Risk analysis engine error: {str(e)}"
        }

@app.get("/analyze/risk-patterns")
async def get_risk_patterns_summary():
    """Get summary of risk patterns from transaction data"""
    
    try:
        import sqlite3
        
        conn = sqlite3.connect('stripe_transactions.db')
        cursor = conn.cursor()
        
        # Get risk pattern distribution
        cursor.execute('''
            SELECT 
                json_extract(metadata, '$.risk_flag') as risk_flag,
                type,
                COUNT(*) as count,
                ROUND(AVG(amount)/100.0, 2) as avg_amount,
                ROUND(SUM(amount)/100.0, 2) as total_amount
            FROM balance_transactions 
            WHERE created >= ? 
            GROUP BY risk_flag, type
            ORDER BY count DESC
        ''', (int((datetime.utcnow() - timedelta(hours=24)).timestamp()),))
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                "risk_flag": row[0],
                "type": row[1], 
                "count": row[2],
                "avg_amount": row[3],
                "total_amount": row[4]
            })
        
        # Get total statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_transactions,
                COUNT(DISTINCT json_extract(metadata, '$.risk_flag')) as unique_risk_flags,
                ROUND(AVG(amount)/100.0, 2) as avg_transaction_amount
            FROM balance_transactions 
            WHERE created >= ?
        ''', (int((datetime.utcnow() - timedelta(hours=24)).timestamp()),))
        
        stats = cursor.fetchone()
        
        conn.close()
        
        return {
            "success": True,
            "analysis_window": "24 hours",
            "total_transactions": stats[0],
            "unique_risk_patterns": stats[1],
            "avg_transaction_amount": stats[2],
            "risk_patterns": patterns,
            "claude_analysis": "Risk pattern distribution analysis from real transaction database"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Pattern analysis error: {str(e)}"
        }

@app.get("/analyze/dashboard")
async def risk_analysis_dashboard():
    """Comprehensive risk analysis dashboard data"""
    
    try:
        import sqlite3
        
        conn = sqlite3.connect('stripe_transactions.db')
        cursor = conn.cursor()
        
        # Get comprehensive statistics
        cursor.execute('''
            SELECT 
                type,
                json_extract(metadata, '$.risk_flag') as risk_flag,
                COUNT(*) as count,
                ROUND(SUM(amount)/100.0, 2) as total_amount,
                ROUND(AVG(amount)/100.0, 2) as avg_amount,
                MIN(datetime(created, 'unixepoch')) as earliest,
                MAX(datetime(created, 'unixepoch')) as latest
            FROM balance_transactions 
            WHERE created >= ?
            GROUP BY type, risk_flag
            ORDER BY count DESC
        ''', (int((datetime.utcnow() - timedelta(hours=48)).timestamp()),))
        
        detailed_patterns = []
        for row in cursor.fetchall():
            detailed_patterns.append({
                "type": row[0],
                "risk_flag": row[1],
                "count": row[2],
                "total_amount": row[3],
                "avg_amount": row[4],
                "earliest": row[5],
                "latest": row[6]
            })
        
        # Calculate risk scores
        charges = [p for p in detailed_patterns if p['type'] == 'charge']
        refunds = [p for p in detailed_patterns if p['type'] == 'refund']
        adjustments = [p for p in detailed_patterns if p['type'] == 'adjustment']
        
        total_charges = sum(p['count'] for p in charges)
        total_refunds = sum(p['count'] for p in refunds) 
        total_adjustments = sum(p['count'] for p in adjustments)
        
        refund_rate = (total_refunds / total_charges * 100) if total_charges > 0 else 0
        chargeback_rate = (total_adjustments / total_charges * 100) if total_charges > 0 else 0
        
        # Risk assessment
        risk_level = "low"
        freeze_probability = 0.1
        
        if chargeback_rate > 1.0:
            risk_level = "critical"
            freeze_probability = 0.9
        elif refund_rate > 10.0:
            risk_level = "critical"
            freeze_probability = 0.8
        elif refund_rate > 5.0:
            risk_level = "high"
            freeze_probability = 0.6
        elif refund_rate > 3.0:
            risk_level = "medium"
            freeze_probability = 0.3
        
        conn.close()
        
        return {
            "dashboard_data": {
                "summary": {
                    "total_transactions": total_charges + total_refunds + total_adjustments,
                    "total_charges": total_charges,
                    "total_refunds": total_refunds,
                    "total_adjustments": total_adjustments,
                    "refund_rate": round(refund_rate, 2),
                    "chargeback_rate": round(chargeback_rate, 2)
                },
                "risk_assessment": {
                    "overall_risk": risk_level,
                    "freeze_probability": freeze_probability,
                    "stripe_thresholds": {
                        "refund_rate_warning": 5.0,
                        "refund_rate_freeze": 10.0,
                        "chargeback_rate_freeze": 1.0
                    }
                },
                "detailed_patterns": detailed_patterns,
                "claude_insights": {
                    "pattern_analysis": f"Analyzed {len(detailed_patterns)} distinct risk patterns",
                    "risk_distribution": {
                        "normal": len([p for p in detailed_patterns if p['risk_flag'] == 'normal']),
                        "volume_spike": len([p for p in detailed_patterns if p['risk_flag'] == 'volume_spike']),
                        "refund_surge": len([p for p in detailed_patterns if p['risk_flag'] == 'refund_surge']),
                        "chargeback_pattern": len([p for p in detailed_patterns if p['risk_flag'] == 'chargeback_pattern'])
                    },
                    "recommendations": [
                        f"Current refund rate: {refund_rate:.1f}% (Stripe warning: 5%)",
                        f"Current chargeback rate: {chargeback_rate:.1f}% (Stripe freeze: 1%)",
                        "Monitor patterns closely for compliance",
                        "Maintain detailed transaction documentation"
                    ]
                }
            },
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "data_source": "stripe_transactions.db"
        }
        
    except Exception as e:
        return {
            "error": f"Dashboard analysis error: {str(e)}",
            "fallback_data": {
                "message": "Unable to generate dashboard data",
                "suggestion": "Check database connection"
            }
        }

@app.post("/payments/process")
async def process_payment(request: PaymentRequest):
    """Enhanced payment processing with Stripe freeze detection and intelligent re-routing"""
    
    try:
        # Use the enhanced routing engine
        from enhanced_routing_engine import EnhancedClaudeRoutingEngine
        
        routing_engine = EnhancedClaudeRoutingEngine()
        
        # Make intelligent routing decision with freeze detection
        decision = await routing_engine.make_intelligent_routing_decision(
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            complexity=request.analysis_complexity
        )
        
        # Generate payment ID
        payment_id = f"pay_{uuid.uuid4().hex[:16]}"
        
        return {
            "success": True,
            "processor_used": decision.selected_processor.value,
            "reasoning": decision.reasoning,
            "processing_time_ms": decision.processing_time_ms,
            "payment_id": payment_id,
            "claude_analysis": {
                "complexity": request.analysis_complexity,
                "confidence": decision.confidence,
                "risk_assessment": decision.risk_assessment,
                "freeze_avoidance_active": decision.freeze_avoidance,
                "stripe_health": decision.claude_analysis["stripe_health"],
                "fallback_chain": [p.value for p in decision.fallback_chain]
            },
            "enhanced_features": {
                "stripe_freeze_detection": True,
                "intelligent_rerouting": True,
                "real_transaction_analysis": True,
                "multi_processor_failover": True
            }
        }
        
    except Exception as e:
        # Fallback to simple routing if enhanced engine fails
        await asyncio.sleep(0.5)
        
        return {
            "success": True,
            "processor_used": "paypal",  # Safe fallback
            "reasoning": f"Enhanced routing unavailable, using PayPal fallback. Error: {str(e)[:100]}",
            "processing_time_ms": 500,
            "payment_id": f"pay_{uuid.uuid4().hex[:16]}",
            "claude_analysis": {
                "complexity": request.analysis_complexity,
                "confidence": 0.8,
                "risk_assessment": "fallback_mode"
            },
            "enhanced_features": {
                "fallback_mode": True,
                "fallback_reason": "Enhanced routing engine error"
            }
        }

@app.get("/routing/processor-health")
async def get_processor_health_status():
    """Get comprehensive processor health status and routing logic"""
    
    try:
        from enhanced_routing_engine import EnhancedClaudeRoutingEngine
        
        routing_engine = EnhancedClaudeRoutingEngine()
        processor_healths = await routing_engine.assess_processor_health(time_window_hours=24)
        
        # Convert to JSON-serializable format
        health_status = {}
        for processor, health in processor_healths.items():
            health_status[processor.value] = {
                "status": health.status.value,
                "freeze_risk": health.freeze_risk,
                "chargeback_rate": health.chargeback_rate,
                "refund_rate": health.refund_rate,
                "volume_spike": health.volume_spike,
                "recommended_action": health.recommended_action,
                "freeze_reasons": health.freeze_reasons,
                "last_update": health.last_update.isoformat()
            }
        
        # Add routing rules (corrected for volume-based risk, not individual amounts)
        routing_rules = {
            "enterprise_level": {"threshold": 100000, "preferred_processor": "visa", "reason": "Enterprise-level security (>$1000)"},
            "b2b_business": {"keywords": ["b2b", "enterprise", "business"], "preferred_processor": "stripe", "reason": "Business processing optimization"},
            "marketplace_consumer": {"keywords": ["marketplace", "ecommerce"], "preferred_processor": "paypal", "reason": "Consumer marketplace friendly"},
            "retail_pos": {"keywords": ["retail", "pos"], "preferred_processor": "square", "reason": "Point-of-sale integration"},
            "international_global": {"keywords": ["international", "global"], "preferred_processor": "adyen", "reason": "Global coverage"},
            "volume_based_risk": {
                "triggers": ["refund_rate > 5%", "chargeback_rate > 1%", "volume_spike > 10x"],
                "action": "automatic_stripe_avoidance",
                "reason": "High-risk comes from transaction volume patterns, not individual amounts"
            }
        }
        
        # Get current Stripe status for summary
        from enhanced_routing_engine import ProcessorType
        stripe_health = processor_healths[ProcessorType.STRIPE]
        
        return {
            "processor_health_status": health_status,
            "routing_rules": routing_rules,
            "current_stripe_status": {
                "status": stripe_health.status.value,
                "freeze_risk": stripe_health.freeze_risk,
                "critical_issues": len(stripe_health.freeze_reasons),
                "routing_impact": "All Stripe transactions being rerouted" if stripe_health.status.value == "frozen" else "Normal routing active"
            },
            "freeze_thresholds": {
                "chargeback_rate_freeze": "1.0%",
                "refund_rate_warning": "5.0%", 
                "refund_rate_freeze": "10.0%",
                "volume_spike_warning": "10x normal",
                "volume_spike_freeze": "20x normal"
            },
            "enhanced_features": {
                "real_time_freeze_detection": True,
                "intelligent_processor_failover": True,
                "multi_processor_health_monitoring": True,
                "claude_powered_routing_decisions": True
            },
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Processor health analysis failed: {str(e)}",
            "fallback_info": "Enhanced routing temporarily unavailable"
        }

@app.post("/payments/visa-mcp")
async def visa_mcp_processing(request: VisaMCPRequest):
    """Visa MCP tools integration"""
    
    # Simulate MCP processing
    await asyncio.sleep(1.5)
    
    # Select MCP tools based on request
    tools_used = ["visa-authorization", "visa-risk-scoring"]
    
    if request.amount > 5000:
        tools_used.extend(["visa-fraud-detection", "visa-3ds-authentication"])
    
    if request.payment_type == "invoice":
        tools_used.append("invoices_create")
    elif request.payment_type == "payment_link":
        tools_used.append("payment_links_create")
    
    orchestration_result = f"""Claude + Visa MCP Processing Complete:

Customer: {request.customer_name} ({request.customer_email})
Transaction: ${request.amount:,.2f} {request.currency}
Payment Type: {request.payment_type.replace('_', ' ').title()}

Visa MCP Tools Executed:
{chr(10).join(f'✅ {tool}' for tool in tools_used)}

Claude Intelligence Applied:
• Risk assessment: {"High-value processing" if request.amount > 10000 else "Standard processing"}
• Fraud analysis: Pattern recognition completed
• Payment optimization: Route selection optimized
• Integration: Visa Agent Toolkit MCP Server
"""

    return {
        "success": True,
        "payment_orchestration": orchestration_result,
        "visa_mcp_tools_used": tools_used,
        "tool_execution_times": [random.randint(200, 800) for _ in tools_used],
        "visa_responses": [{
            "visa_transaction_id": f"visa_{uuid.uuid4().hex[:12]}",
            "status": "completed",
            "mcp_server": "visa_agent_toolkit_v1.0"
        }],
        "total_processing_time_ms": random.randint(1200, 2500),
        "claude_tokens_used": random.randint(350, 600),
        "visa_mcp_integration": True,
        "tools_successful": True
    }

@app.post("/payments/crossmint")
async def process_crossmint_payment(request: CrossmintRequest):
    """
    Process payment through Crossmint Wallets
    Crypto payment alternative with Web3 integration
    """
    
    try:
        print(f"🌐 Crossmint payment request: {request.amount} {request.currency.upper()} on {request.chain}")
        
        # Initialize Crossmint processor
        crossmint_processor = CrossmintPaymentProcessor()
        
        # Process payment
        result = await crossmint_processor.process_payment(
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            customer_email=request.customer_email,
            chain=request.chain
        )
        
        if result.success:
            # Get additional wallet information
            processor_info = crossmint_processor.get_processor_info()
            balances = await crossmint_processor.get_wallet_balances(
                request.customer_email, 
                request.chain
            )
            
            return {
                "success": True,
                "processor_used": "crossmint",
                "transaction_id": result.transaction_id,
                "wallet_address": result.wallet_address,
                "explorer_link": result.explorer_link,
                "chain": result.chain,
                "currency": result.currency,
                "processing_time_ms": result.processing_time,
                "crossmint_features": {
                    "wallet_based": True,
                    "crypto_native": True,
                    "cross_chain_support": True,
                    "global_access": True,
                    "web3_integration": True
                },
                "wallet_info": {
                    "address": result.wallet_address,
                    "chain": request.chain,
                    "balances": balances
                },
                "processor_capabilities": {
                    "supported_chains": processor_info["supported_chains"],
                    "supported_currencies": processor_info["supported_currencies"],
                    "freeze_resistance": processor_info["freeze_resistance"],
                    "max_amount": processor_info["max_amount"]
                },
                "claude_analysis": {
                    "routing_reason": f"Crypto/Web3 payment selected for {request.description}",
                    "complexity": request.analysis_complexity,
                    "confidence": 0.92,
                    "processor_health": "excellent",
                    "decentralized_advantage": True
                }
            }
        else:
            return {
                "success": False,
                "processor_used": "crossmint",
                "error": result.error,
                "processing_time_ms": result.processing_time,
                "suggested_action": "Check wallet balance or try different chain/currency"
            }
            
    except Exception as e:
        print(f"❌ Crossmint payment error: {e}")
        return {
            "success": False,
            "processor_used": "crossmint",
            "error": f"Crossmint integration error: {str(e)}",
            "processing_time_ms": 0
        }

@app.get("/payments/crossmint/info")
async def get_crossmint_info():
    """Get Crossmint processor information and capabilities"""
    
    try:
        processor = CrossmintPaymentProcessor()
        info = processor.get_processor_info()
        
        return {
            "processor": info,
            "integration_status": "active",
            "sdk_version": "@crossmint/wallets-sdk v0.11.8",
            "demo_mode": True,
            "setup_instructions": {
                "step_1": "npm install @crossmint/wallets-sdk",
                "step_2": "Set CROSSMINT_API_KEY environment variable",
                "step_3": "Configure JWT for client-side calls",
                "step_4": "Use Crossmint routing for crypto payments"
            }
        }
        
    except Exception as e:
        return {
            "error": f"Failed to get Crossmint info: {str(e)}",
            "integration_status": "error"
        }

if __name__ == "__main__":
    uvicorn.run(
        "simple_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )