#!/usr/bin/env python3
"""
Enhanced Claude Routing Engine with Stripe Freeze Detection & Re-routing
Automatically switches processors when Stripe account is frozen or at risk
"""

import sqlite3
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ProcessorStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    FROZEN = "frozen"
    UNAVAILABLE = "unavailable"

class ProcessorType(Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    SQUARE = "square"
    VISA = "visa"
    ADYEN = "adyen"
    CROSSMINT = "crossmint"

@dataclass
class ProcessorHealth:
    processor: ProcessorType
    status: ProcessorStatus
    freeze_risk: float  # 0.0 to 1.0
    chargeback_rate: float
    refund_rate: float
    volume_spike: float  # Multiplier from baseline
    geographic_risk: float  # 0.0 to 1.0
    last_update: datetime
    freeze_reasons: List[str]
    recommended_action: str

@dataclass
class RoutingDecision:
    selected_processor: ProcessorType
    confidence: float
    reasoning: str
    fallback_chain: List[ProcessorType]
    risk_assessment: str
    processing_time_ms: int
    claude_analysis: Dict[str, Any]
    freeze_avoidance: bool = False

class EnhancedClaudeRoutingEngine:
    """
    Advanced routing engine with Stripe freeze detection and intelligent re-routing
    """
    
    def __init__(self, db_path: str = "stripe_transactions.db"):
        self.db_path = db_path
        
        # Stripe freeze thresholds (based on real Stripe policies)
        self.stripe_thresholds = {
            "chargeback_rate_freeze": 0.01,      # 1% immediate freeze
            "chargeback_rate_warning": 0.005,    # 0.5% warning
            "refund_rate_freeze": 0.10,          # 10% freeze threshold  
            "refund_rate_warning": 0.05,         # 5% warning threshold
            "volume_spike_freeze": 20.0,          # 20x spike = immediate review
            "volume_spike_warning": 10.0,         # 10x spike = warning
            "geographic_risk_threshold": 0.7,     # 70% new countries
            "enterprise_transaction_threshold": 100000   # $1000+ enterprise transactions
        }
        
        # Processor capabilities and preferences
        self.processor_capabilities = {
            ProcessorType.STRIPE: {
                "max_amount": 999999,
                "best_for": ["b2b", "subscription", "saas"],
                "geographic_strength": ["US", "EU", "AU"],
                "freeze_resistance": 0.3
            },
            ProcessorType.PAYPAL: {
                "max_amount": 100000,
                "best_for": ["consumer", "marketplace", "ecommerce"],
                "geographic_strength": ["US", "EU", "GLOBAL"],
                "freeze_resistance": 0.6
            },
            ProcessorType.SQUARE: {
                "max_amount": 50000,
                "best_for": ["retail", "pos", "small_business"],
                "geographic_strength": ["US", "CA", "AU"],
                "freeze_resistance": 0.7
            },
            ProcessorType.VISA: {
                "max_amount": 2000000,
                "best_for": ["enterprise", "high_value", "international"],
                "geographic_strength": ["GLOBAL"],
                "freeze_resistance": 0.9
            },
            ProcessorType.ADYEN: {
                "max_amount": 1000000,
                "best_for": ["international", "enterprise", "high_volume"],
                "geographic_strength": ["EU", "ASIA", "GLOBAL"],
                "freeze_resistance": 0.8
            },
            ProcessorType.CROSSMINT: {
                "max_amount": 500000,
                "best_for": ["crypto", "web3", "defi", "nft", "international"],
                "geographic_strength": ["GLOBAL", "CRYPTO"],
                "freeze_resistance": 0.95,
                "supported_chains": ["solana", "ethereum", "polygon"],
                "supported_currencies": ["usdc", "sol", "eth", "matic"],
                "features": ["wallet_creation", "cross_chain", "email_based"]
            }
        }
    
    async def assess_processor_health(self, time_window_hours: int = 24) -> Dict[ProcessorType, ProcessorHealth]:
        """
        Assess health of all processors based on recent transaction data
        """
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent transactions
        cutoff_time = int((datetime.utcnow() - timedelta(hours=time_window_hours)).timestamp())
        
        cursor.execute('''
            SELECT 
                type,
                COUNT(*) as count,
                AVG(amount) as avg_amount,
                SUM(amount) as total_amount
            FROM balance_transactions 
            WHERE created >= ?
            GROUP BY type
        ''', (cutoff_time,))
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = {
                "count": row[1],
                "avg_amount": row[2],
                "total_amount": row[3]
            }
        
        # Calculate risk metrics
        charges = stats.get("charge", {"count": 0})["count"]
        refunds = stats.get("refund", {"count": 0})["count"]
        adjustments = stats.get("adjustment", {"count": 0})["count"]
        
        chargeback_rate = (adjustments / max(charges, 1))
        refund_rate = (refunds / max(charges, 1))
        
        # Get baseline volume for spike detection
        baseline_window = int((datetime.utcnow() - timedelta(days=30)).timestamp())
        cursor.execute('''
            SELECT COUNT(*) / 30.0 as daily_avg
            FROM balance_transactions 
            WHERE created >= ? AND created < ? AND type = 'charge'
        ''', (baseline_window, cutoff_time))
        
        baseline_daily = cursor.fetchone()[0] or 10
        current_daily = charges / (time_window_hours / 24)
        volume_spike = current_daily / baseline_daily if baseline_daily > 0 else 1
        
        conn.close()
        
        # Assess Stripe health specifically
        stripe_health = self._assess_stripe_health(chargeback_rate, refund_rate, volume_spike)
        
        # Create health assessment for all processors
        processor_healths = {}
        
        for processor in ProcessorType:
            if processor == ProcessorType.STRIPE:
                health = stripe_health
            else:
                # Other processors are assumed healthy unless Stripe issues affect ecosystem
                health = self._assess_alternative_processor_health(processor, stripe_health.status)
            
            processor_healths[processor] = health
        
        return processor_healths
    
    def _assess_stripe_health(self, chargeback_rate: float, refund_rate: float, volume_spike: float) -> ProcessorHealth:
        """Assess Stripe-specific health and freeze risk"""
        
        freeze_reasons = []
        freeze_risk = 0.0
        status = ProcessorStatus.HEALTHY
        recommended_action = "Continue normal operations"
        
        # Chargeback analysis
        if chargeback_rate >= self.stripe_thresholds["chargeback_rate_freeze"]:
            freeze_reasons.append(f"CRITICAL: Chargeback rate {chargeback_rate:.1%} exceeds 1% freeze threshold")
            freeze_risk = max(freeze_risk, 0.95)
            status = ProcessorStatus.FROZEN
            recommended_action = "IMMEDIATE: Switch to alternative processors - Stripe account freeze imminent"
            
        elif chargeback_rate >= self.stripe_thresholds["chargeback_rate_warning"]:
            freeze_reasons.append(f"WARNING: Chargeback rate {chargeback_rate:.1%} approaching 1% threshold")
            freeze_risk = max(freeze_risk, 0.6)
            status = ProcessorStatus.WARNING
            recommended_action = "Prepare alternative processors - monitor closely"
        
        # Refund analysis
        if refund_rate >= self.stripe_thresholds["refund_rate_freeze"]:
            freeze_reasons.append(f"CRITICAL: Refund rate {refund_rate:.1%} exceeds 10% freeze threshold")
            freeze_risk = max(freeze_risk, 0.85)
            if status == ProcessorStatus.HEALTHY:
                status = ProcessorStatus.WARNING  # Refunds less critical than chargebacks
            recommended_action = "Route high-risk transactions to alternatives"
            
        elif refund_rate >= self.stripe_thresholds["refund_rate_warning"]:
            freeze_reasons.append(f"WARNING: Refund rate {refund_rate:.1%} exceeds 5% warning threshold")
            freeze_risk = max(freeze_risk, 0.4)
            if status == ProcessorStatus.HEALTHY:
                status = ProcessorStatus.WARNING
        
        # Volume spike analysis
        if volume_spike >= self.stripe_thresholds["volume_spike_freeze"]:
            freeze_reasons.append(f"CRITICAL: Volume spike {volume_spike:.1f}x exceeds 20x freeze threshold")
            freeze_risk = max(freeze_risk, 0.8)
            if status != ProcessorStatus.FROZEN:
                status = ProcessorStatus.WARNING
            recommended_action = "Diversify payment processing immediately"
            
        elif volume_spike >= self.stripe_thresholds["volume_spike_warning"]:
            freeze_reasons.append(f"WARNING: Volume spike {volume_spike:.1f}x exceeds 10x warning threshold")
            freeze_risk = max(freeze_risk, 0.3)
            if status == ProcessorStatus.HEALTHY:
                status = ProcessorStatus.WARNING
        
        return ProcessorHealth(
            processor=ProcessorType.STRIPE,
            status=status,
            freeze_risk=freeze_risk,
            chargeback_rate=chargeback_rate,
            refund_rate=refund_rate,
            volume_spike=volume_spike,
            geographic_risk=0.0,  # Would need geographic data
            last_update=datetime.utcnow(),
            freeze_reasons=freeze_reasons,
            recommended_action=recommended_action
        )
    
    def _assess_alternative_processor_health(self, processor: ProcessorType, stripe_status: ProcessorStatus) -> ProcessorHealth:
        """Assess health of alternative processors"""
        
        # Alternative processors become more attractive when Stripe has issues
        if stripe_status == ProcessorStatus.FROZEN:
            freeze_risk = 0.1  # Very low risk
            status = ProcessorStatus.HEALTHY
            recommended_action = f"PRIMARY OPTION: Use {processor.value} while Stripe is frozen"
        elif stripe_status == ProcessorStatus.WARNING:
            freeze_risk = 0.2
            status = ProcessorStatus.HEALTHY  
            recommended_action = f"BACKUP READY: Prepare {processor.value} for potential Stripe issues"
        else:
            freeze_risk = 0.15
            status = ProcessorStatus.HEALTHY
            recommended_action = f"Available as routing option"
        
        return ProcessorHealth(
            processor=processor,
            status=status,
            freeze_risk=freeze_risk,
            chargeback_rate=0.005,  # Assumed low
            refund_rate=0.03,       # Assumed normal
            volume_spike=1.0,       # Assumed normal
            geographic_risk=0.2,    # Assumed low
            last_update=datetime.utcnow(),
            freeze_reasons=[],
            recommended_action=recommended_action
        )
    
    async def make_intelligent_routing_decision(
        self,
        amount: float,
        currency: str,
        description: str,
        customer_country: str = "US",
        complexity: str = "balanced"
    ) -> RoutingDecision:
        """
        Make intelligent routing decision considering Stripe freeze risk
        """
        
        print(f"🤖 Claude Enhanced Routing Analysis Starting...")
        
        # Assess processor health
        processor_healths = await self.assess_processor_health()
        stripe_health = processor_healths[ProcessorType.STRIPE]
        
        print(f"🏥 Stripe Health Assessment: {stripe_health.status.value.upper()} (Risk: {stripe_health.freeze_risk:.0%})")
        
        # Start with default processor selection based on transaction
        default_processor = self._get_default_processor(amount, description)
        
        # Check if default processor is available
        selected_processor = default_processor
        freeze_avoidance = False
        
        # CRITICAL: If Stripe is frozen or high risk, route around it
        if default_processor == ProcessorType.STRIPE and stripe_health.status == ProcessorStatus.FROZEN:
            selected_processor = self._select_stripe_alternative(amount, description, processor_healths)
            freeze_avoidance = True
            print(f"🚨 STRIPE FREEZE DETECTED: Routing to {selected_processor.value.upper()}")
            
        elif default_processor == ProcessorType.STRIPE and stripe_health.freeze_risk > 0.7:
            selected_processor = self._select_stripe_alternative(amount, description, processor_healths)
            freeze_avoidance = True
            print(f"⚠️ HIGH STRIPE RISK: Proactively routing to {selected_processor.value.upper()}")
        
        # Generate Claude reasoning
        reasoning = await self._generate_routing_reasoning(
            amount, description, selected_processor, stripe_health, freeze_avoidance, complexity
        )
        
        # Build fallback chain
        fallback_chain = self._build_fallback_chain(selected_processor, processor_healths)
        
        # Calculate processing time based on complexity
        processing_times = {"simple": 400, "balanced": 800, "comprehensive": 1500}
        processing_time = processing_times.get(complexity, 800) + random.randint(0, 200)
        
        return RoutingDecision(
            selected_processor=selected_processor,
            confidence=0.92 if freeze_avoidance else 0.95,
            reasoning=reasoning,
            fallback_chain=fallback_chain,
            risk_assessment=stripe_health.status.value,
            processing_time_ms=processing_time,
            claude_analysis={
                "stripe_health": {
                    "status": stripe_health.status.value,
                    "freeze_risk": stripe_health.freeze_risk,
                    "chargeback_rate": stripe_health.chargeback_rate,
                    "refund_rate": stripe_health.refund_rate,
                    "volume_spike": stripe_health.volume_spike,
                    "freeze_reasons": stripe_health.freeze_reasons
                },
                "freeze_avoidance_active": freeze_avoidance,
                "complexity": complexity
            },
            freeze_avoidance=freeze_avoidance
        )
    
    def _get_default_processor(self, amount: float, description: str) -> ProcessorType:
        """Get default processor based on transaction characteristics (NOT individual amount risk)
        
        IMPORTANT: Individual amounts like $50, $100, $500 are NOT high-risk.
        Risk comes from VOLUME PATTERNS: refund rates, chargeback rates, velocity.
        """
        
        # Enterprise-level transactions (truly large amounts) for enhanced security
        if amount > 100000:  # $1000+ for enterprise-level security and compliance
            return ProcessorType.VISA
        elif any(keyword in description.lower() for keyword in ["crypto", "web3", "defi", "nft", "token", "blockchain", "wallet"]):
            return ProcessorType.CROSSMINT
        elif any(keyword in description.lower() for keyword in ["b2b", "enterprise", "business", "subscription"]):
            return ProcessorType.STRIPE
        elif any(keyword in description.lower() for keyword in ["marketplace", "ecommerce", "consumer"]):
            return ProcessorType.PAYPAL
        elif any(keyword in description.lower() for keyword in ["retail", "pos", "store"]):
            return ProcessorType.SQUARE
        elif any(keyword in description.lower() for keyword in ["international", "global", "cross-border"]):
            return ProcessorType.ADYEN
        else:
            return ProcessorType.STRIPE  # Default fallback
    
    def _select_stripe_alternative(self, amount: float, description: str, processor_healths: Dict[ProcessorType, ProcessorHealth]) -> ProcessorType:
        """Select best alternative when Stripe is unavailable"""
        
        # Score alternatives based on transaction fit and health
        scores = {}
        
        for processor, health in processor_healths.items():
            if processor == ProcessorType.STRIPE:
                continue
            
            score = 0
            capabilities = self.processor_capabilities[processor]
            
            # Amount compatibility
            if amount <= capabilities["max_amount"]:
                score += 30
            else:
                score -= 50  # Penalize if can't handle amount
            
            # Business type fit
            if any(keyword in description.lower() for keyword in capabilities["best_for"]):
                score += 25
            
            # Health score
            score += (1 - health.freeze_risk) * 20
            
            # Freeze resistance
            score += capabilities["freeze_resistance"] * 15
            
            scores[processor] = score
        
        # Return processor with highest score
        best_processor = max(scores, key=scores.get)
        return best_processor
    
    async def _generate_routing_reasoning(
        self, 
        amount: float, 
        description: str, 
        selected_processor: ProcessorType,
        stripe_health: ProcessorHealth,
        freeze_avoidance: bool,
        complexity: str
    ) -> str:
        """Generate detailed Claude reasoning for routing decision"""
        
        await asyncio.sleep(0.3)  # Simulate Claude processing
        
        reasoning = f"Enhanced Claude Routing Analysis (complexity={complexity}):\n\n"
        
        if freeze_avoidance:
            reasoning += "🚨 STRIPE FREEZE AVOIDANCE ACTIVATED:\n"
            reasoning += f"Stripe Status: {stripe_health.status.value.upper()} (Freeze Risk: {stripe_health.freeze_risk:.0%})\n"
            if stripe_health.freeze_reasons:
                reasoning += "Critical Issues Detected:\n"
                for reason in stripe_health.freeze_reasons[:3]:
                    reasoning += f"• {reason}\n"
            reasoning += f"\nRerouting to {selected_processor.value.upper()} for transaction safety.\n\n"
        
        reasoning += f"Transaction Analysis:\n"
        reasoning += f"• Amount: ${amount:,.2f} (Individual amount is NOT a risk factor)\n"
        reasoning += f"• Context: {description}\n"
        reasoning += f"• Selected Processor: {selected_processor.value.upper()}\n"
        reasoning += f"• Risk Type: {'ACCOUNT-LEVEL VOLUME' if freeze_avoidance else 'TRANSACTION CHARACTERISTICS'}\n\n"
        
        reasoning += f"Processor Selection Logic:\n"
        capabilities = self.processor_capabilities[selected_processor]
        reasoning += f"• Best for: {', '.join(capabilities['best_for'])}\n"
        reasoning += f"• Max amount: ${capabilities['max_amount']:,}\n"
        reasoning += f"• Freeze resistance: {capabilities['freeze_resistance']:.0%}\n"
        
        # Clarify risk type
        if freeze_avoidance:
            reasoning += f"\n✅ VOLUME-BASED ROUTING:\n"
            reasoning += f"• Routing based on ACCOUNT-LEVEL risk metrics\n"
            reasoning += f"• Chargeback rate: {stripe_health.chargeback_rate:.1%} (threshold: 1%)\n"
            reasoning += f"• Refund rate: {stripe_health.refund_rate:.1%} (threshold: 5%)\n"
            reasoning += f"• Volume spike: {stripe_health.volume_spike:.1f}x normal\n"
        else:
            reasoning += f"\n✅ CHARACTERISTIC-BASED ROUTING:\n"
            reasoning += f"• Routing based on transaction type and business needs\n"
            reasoning += f"• No account-level volume risks detected\n"
            reasoning += f"• Individual transaction amount ({amount:.2f}) is not a risk factor\n"
        
        if complexity == "comprehensive":
            reasoning += f"\n🔍 COMPREHENSIVE RISK ANALYSIS:\n"
            reasoning += f"Stripe Account Volume Metrics:\n"
            reasoning += f"• Chargeback rate: {stripe_health.chargeback_rate:.1%} (freeze at 1%)\n"
            reasoning += f"• Refund rate: {stripe_health.refund_rate:.1%} (freeze at 10%)\n"
            reasoning += f"• Volume spike: {stripe_health.volume_spike:.1f}x baseline\n"
            reasoning += f"• Overall freeze risk: {stripe_health.freeze_risk:.0%}\n"
            reasoning += f"• Recommended action: {stripe_health.recommended_action}\n"
            reasoning += f"\n⚠️ REMINDER: Risk assessment is based on VOLUME PATTERNS,\n"
            reasoning += f"not individual transaction amounts. A $50 transaction is\n"
            reasoning += f"routed due to account-level metrics, not the $50 amount.\n"
        
        return reasoning
    
    def _build_fallback_chain(self, selected: ProcessorType, healths: Dict[ProcessorType, ProcessorHealth]) -> List[ProcessorType]:
        """Build intelligent fallback chain excluding frozen processors"""
        
        available_processors = [p for p, h in healths.items() if p != selected and h.status != ProcessorStatus.FROZEN]
        
        # Sort by health and capability
        fallback_chain = sorted(available_processors, key=lambda p: (
            -healths[p].freeze_risk,  # Lower freeze risk first
            -self.processor_capabilities[p]["freeze_resistance"]  # Higher resistance first
        ))
        
        return fallback_chain[:3]  # Top 3 alternatives

# Example usage and testing
async def main():
    """Test the enhanced routing engine"""
    
    engine = EnhancedClaudeRoutingEngine()
    
    test_transactions = [
        {
            "amount": 25000,
            "currency": "USD", 
            "description": "Enterprise software license",
            "complexity": "comprehensive"
        },
        {
            "amount": 150,
            "currency": "USD",
            "description": "B2B monthly subscription", 
            "complexity": "balanced"
        },
        {
            "amount": 75,
            "currency": "USD",
            "description": "Consumer purchase",
            "complexity": "simple"
        },
        {
            "amount": 200,
            "currency": "USDC",
            "description": "NFT marketplace purchase with crypto wallet",
            "complexity": "balanced"
        },
        {
            "amount": 500,
            "currency": "USDC",
            "description": "DeFi protocol payment via blockchain",
            "complexity": "comprehensive"
        }
    ]
    
    print("🚀 ENHANCED CLAUDE ROUTING ENGINE TEST")
    print("═" * 50)
    
    for i, txn in enumerate(test_transactions, 1):
        print(f"\n💳 TEST TRANSACTION #{i}")
        print(f"Amount: ${txn['amount']:,.2f} | Description: {txn['description']}")
        print("-" * 40)
        
        decision = await engine.make_intelligent_routing_decision(
            amount=txn['amount'],
            currency=txn['currency'],
            description=txn['description'],
            complexity=txn['complexity']
        )
        
        print(f"🎯 ROUTING DECISION:")
        print(f"Selected Processor: {decision.selected_processor.value.upper()}")
        print(f"Confidence: {decision.confidence:.0%}")
        print(f"Freeze Avoidance: {'YES' if decision.freeze_avoidance else 'NO'}")
        print(f"Processing Time: {decision.processing_time_ms}ms")
        
        stripe_health = decision.claude_analysis['stripe_health']
        print(f"\n📊 Stripe Health: {stripe_health['status'].upper()} (Risk: {stripe_health['freeze_risk']:.0%})")
        
        if stripe_health['freeze_reasons']:
            print("⚠️ Freeze Reasons:")
            for reason in stripe_health['freeze_reasons'][:2]:
                print(f"   • {reason}")
        
        print(f"\n🔄 Fallback Chain: {' → '.join([p.value.upper() for p in decision.fallback_chain])}")

if __name__ == "__main__":
    asyncio.run(main())