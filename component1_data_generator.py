"""
GPT-5 Enhanced Stripe Data Generator with Real-time Pattern Recognition
Generates Stripe-compliant synthetic transaction data using GPT-5's advanced capabilities
"""

import asyncio
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib

from gpt5_client import GPT5Client


class TransactionType(Enum):
    CHARGE = "charge"
    REFUND = "refund"
    PAYOUT = "payout"
    ADJUSTMENT = "adjustment"
    APPLICATION_FEE = "application_fee"
    TRANSFER = "transfer"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class StripeTransaction:
    """Stripe balance_transaction compliant format"""
    id: str
    object: str = "balance_transaction"
    amount: int = 0  # In cents
    available_on: int = 0
    created: int = 0
    currency: str = "usd"
    description: Optional[str] = None
    exchange_rate: Optional[float] = None
    fee: int = 0
    fee_details: List[Dict] = field(default_factory=list)
    net: int = 0
    reporting_category: str = "charge"
    source: Optional[str] = None
    status: str = "available"
    type: str = "charge"
    
    # Additional metadata for risk analysis
    metadata: Dict[str, Any] = field(default_factory=dict)


class GPT5StripeDataGenerator:
    """
    Advanced Stripe data generator powered by GPT-5's reasoning and pattern generation
    """
    
    def __init__(self):
        self.gpt5_client = GPT5Client()
        self.transaction_cache = []
        self.risk_patterns = []
        self.current_baseline = {}
        
        # Stripe-specific thresholds
        self.STRIPE_THRESHOLDS = {
            "refund_rate_warning": 0.03,  # 3% triggers review
            "refund_rate_freeze": 0.05,   # 5% triggers investigation
            "chargeback_rate_freeze": 0.01,  # 1% immediate freeze
            "volume_spike_review": 5.0,    # 5x normal triggers review
            "volume_spike_freeze": 10.0,   # 10x triggers freeze
            "large_transaction_threshold": 10000,  # $10K+ requires review
            "rapid_succession_threshold": 100,  # 100 txns in 1 hour
        }
        
        # Card brands and their typical characteristics
        self.CARD_BRANDS = {
            "visa": {"fee_rate": 0.0215, "international_rate": 0.01},
            "mastercard": {"fee_rate": 0.0215, "international_rate": 0.01},
            "amex": {"fee_rate": 0.035, "international_rate": 0.015},
            "discover": {"fee_rate": 0.02, "international_rate": 0.01},
        }
    
    async def generate_intelligent_dataset(
        self,
        scenario: str = "normal",
        duration_days: int = 30,
        base_volume: int = 50
    ) -> Dict[str, Any]:
        """
        Generate complete dataset using GPT-5's intelligent pattern generation
        """
        
        print(f"Initializing GPT-5 for {scenario} scenario generation...")
        
        # Step 1: Use GPT-5 to design the data generation strategy
        strategy = await self._design_generation_strategy(scenario, duration_days, base_volume)
        
        # Step 2: Generate baseline if needed
        if scenario != "existing_freeze":
            baseline = await self._generate_baseline_period(strategy)
            self.current_baseline = self._calculate_baseline_metrics(baseline)
        
        # Step 3: Generate scenario-specific patterns
        scenario_data = await self._generate_scenario_patterns(scenario, strategy)
        
        # Step 4: Analyze the generated data with GPT-5
        risk_analysis = await self._analyze_generated_patterns(scenario_data)
        
        return {
            "scenario": scenario,
            "baseline": self.current_baseline,
            "transactions": scenario_data,
            "risk_analysis": risk_analysis,
            "gpt5_strategy": strategy,
            "statistics": self._calculate_statistics(scenario_data),
            "export_format": "stripe_balance_transactions"
        }
    
    async def _design_generation_strategy(
        self,
        scenario: str,
        duration_days: int,
        base_volume: int
    ) -> Dict[str, Any]:
        """
        Use GPT-5 to design the data generation strategy
        """
        
        context = {
            "scenario": scenario,
            "duration_days": duration_days,
            "base_volume": base_volume,
            "business_type": "B2B SaaS Platform",
            "stripe_thresholds": self.STRIPE_THRESHOLDS,
            "objective": "Generate realistic Stripe transaction patterns"
        }
        
        # Use GPT-5 with high reasoning effort for strategy design
        strategy = await self.gpt5_client.generate_synthetic_data(
            pattern_type=scenario,
            context=context,
            reasoning_effort="high",  # Deep analysis for strategy
            verbosity="medium"  # Balanced output
        )
        
        # Parse GPT-5's strategy into actionable parameters
        return self._parse_generation_strategy(strategy, scenario, duration_days, base_volume)
    
    def _parse_generation_strategy(
        self,
        gpt5_response: Dict[str, Any],
        scenario: str,
        duration_days: int,
        base_volume: int
    ) -> Dict[str, Any]:
        """
        Parse GPT-5's strategy response into generation parameters
        """
        
        # Default strategy if GPT-5 response parsing fails
        default_strategy = {
            "normal": {
                "daily_variance": 0.2,
                "refund_rate": 0.015,
                "failure_rate": 0.02,
                "avg_amount": 85.0,
                "amount_variance": 0.3,
                "peak_hours": [9, 10, 11, 14, 15, 16],
                "weekend_factor": 0.3
            },
            "sudden_spike": {
                "spike_multiplier": 12.0,
                "spike_duration_hours": 3,
                "spike_amount_multiplier": 3.0,
                "concurrent_transactions": True,
                "new_customer_ratio": 0.8
            },
            "high_refund_rate": {
                "target_refund_rate": 0.08,  # 8% to exceed 5% threshold
                "refund_delay_hours": [2, 48],
                "refund_reasons": [
                    "Product not as described",
                    "Quality issues",
                    "Unauthorized purchase",
                    "Duplicate charge",
                    "Service dissatisfaction"
                ],
                "clustered_refunds": True
            },
            "chargeback_surge": {
                "target_chargeback_rate": 0.025,  # 2.5% to exceed 1% threshold
                "chargeback_delay_days": [15, 60],
                "chargeback_reasons": [
                    "Fraudulent transaction",
                    "Product not received",
                    "Credit not processed",
                    "Duplicate processing",
                    "Product unacceptable"
                ],
                "chargeback_fee": 15.00
            }
        }
        
        base_strategy = default_strategy.get(scenario, default_strategy["normal"])
        
        # Enhance with GPT-5 suggestions if available
        if "generation_plan" in gpt5_response:
            # Extract specific parameters from GPT-5's response
            base_strategy["gpt5_enhanced"] = True
            base_strategy["reasoning_chain"] = gpt5_response.get("gpt5_reasoning", "")
        
        base_strategy.update({
            "scenario": scenario,
            "duration_days": duration_days,
            "base_volume": base_volume,
            "start_date": datetime.utcnow() - timedelta(days=duration_days)
        })
        
        return base_strategy
    
    async def _generate_baseline_period(self, strategy: Dict[str, Any]) -> List[StripeTransaction]:
        """
        Generate normal baseline transactions
        """
        
        transactions = []
        start_date = strategy["start_date"]
        
        for day in range(strategy.get("duration_days", 30)):
            current_date = start_date + timedelta(days=day)
            
            # Apply day-of-week patterns
            is_weekend = current_date.weekday() >= 5
            day_factor = strategy.get("weekend_factor", 0.3) if is_weekend else 1.0
            
            # Calculate daily volume with variance
            daily_volume = int(
                strategy["base_volume"] * 
                day_factor * 
                random.uniform(1 - strategy.get("daily_variance", 0.2), 
                              1 + strategy.get("daily_variance", 0.2))
            )
            
            for i in range(daily_volume):
                # Generate transaction timing (business hours concentration)
                hour = random.choice(strategy.get("peak_hours", list(range(24))))
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                
                transaction_time = current_date.replace(hour=hour, minute=minute, second=second)
                
                # Generate amount with realistic distribution
                avg_amount = strategy.get("avg_amount", 85.0)
                amount_variance = strategy.get("amount_variance", 0.3)
                amount = max(10.0, random.gauss(avg_amount, avg_amount * amount_variance))
                
                # Select card brand
                card_brand = random.choice(list(self.CARD_BRANDS.keys()))
                card_info = self.CARD_BRANDS[card_brand]
                
                # Calculate fees
                fee = amount * card_info["fee_rate"] + 0.30  # Base rate + fixed fee
                
                # Create charge transaction
                charge = StripeTransaction(
                    id=f"txn_{uuid.uuid4().hex[:24]}",
                    amount=int(amount * 100),  # Convert to cents
                    created=int(transaction_time.timestamp()),
                    available_on=int((transaction_time + timedelta(days=2)).timestamp()),
                    currency="usd",
                    description=f"Payment from customer",
                    fee=int(fee * 100),
                    fee_details=[{
                        "amount": int(fee * 100),
                        "currency": "usd",
                        "description": "Stripe processing fee",
                        "type": "stripe_fee"
                    }],
                    net=int((amount - fee) * 100),
                    source=f"ch_{uuid.uuid4().hex[:24]}",
                    type="charge",
                    metadata={
                        "card_brand": card_brand,
                        "customer_id": f"cus_{hashlib.md5(str(random.randint(1, 1000)).encode()).hexdigest()[:14]}",
                        "risk_score": random.uniform(0, 30)  # Low risk for baseline
                    }
                )
                
                transactions.append(charge)
                
                # Add occasional refunds (normal rate)
                if random.random() < strategy.get("refund_rate", 0.015):
                    refund_time = transaction_time + timedelta(
                        hours=random.randint(
                            strategy.get("refund_delay_hours", [2, 48])[0],
                            strategy.get("refund_delay_hours", [2, 48])[1]
                        )
                    )
                    
                    refund = StripeTransaction(
                        id=f"txn_{uuid.uuid4().hex[:24]}",
                        amount=-charge.amount,
                        created=int(refund_time.timestamp()),
                        available_on=int((refund_time + timedelta(days=2)).timestamp()),
                        currency="usd",
                        description="Refund for charge",
                        fee=-charge.fee,
                        fee_details=[{
                            "amount": -charge.fee,
                            "currency": "usd",
                            "description": "Stripe processing fee reversal",
                            "type": "stripe_fee"
                        }],
                        net=-charge.net,
                        source=f"re_{uuid.uuid4().hex[:24]}",
                        type="refund",
                        metadata={
                            "original_charge": charge.id,
                            "reason": "requested_by_customer",
                            "risk_score": random.uniform(0, 40)
                        }
                    )
                    
                    transactions.append(refund)
        
        return transactions
    
    async def _generate_scenario_patterns(
        self,
        scenario: str,
        strategy: Dict[str, Any]
    ) -> List[StripeTransaction]:
        """
        Generate scenario-specific transaction patterns
        """
        
        if scenario == "normal":
            return await self._generate_baseline_period(strategy)
        elif scenario == "sudden_spike":
            return await self._generate_volume_spike(strategy)
        elif scenario == "high_refund_rate":
            return await self._generate_refund_surge(strategy)
        elif scenario == "chargeback_surge":
            return await self._generate_chargeback_pattern(strategy)
        elif scenario == "pattern_deviation":
            return await self._generate_pattern_deviation(strategy)
        else:
            return await self._generate_baseline_period(strategy)
    
    async def _generate_volume_spike(self, strategy: Dict[str, Any]) -> List[StripeTransaction]:
        """
        Generate sudden volume spike pattern
        """
        
        transactions = []
        base_time = datetime.utcnow()
        
        # Normal baseline for context (last 7 days)
        baseline = await self._generate_baseline_period({
            **strategy,
            "duration_days": 7,
            "base_volume": strategy.get("base_volume", 50)
        })
        transactions.extend(baseline)
        
        # Generate the spike
        spike_multiplier = strategy.get("spike_multiplier", 12.0)
        spike_volume = int(strategy.get("base_volume", 50) * spike_multiplier)
        spike_duration_hours = strategy.get("spike_duration_hours", 3)
        
        print(f"Generating volume spike: {spike_volume} transactions in {spike_duration_hours} hours")
        
        for i in range(spike_volume):
            # Compress into short time window
            minutes_offset = random.randint(0, spike_duration_hours * 60)
            transaction_time = base_time + timedelta(minutes=minutes_offset)
            
            # Larger amounts during spike
            amount = random.uniform(200, 2000)
            
            # Higher risk scores for spike transactions
            risk_score = random.uniform(40, 80)
            
            charge = StripeTransaction(
                id=f"txn_{uuid.uuid4().hex[:24]}",
                amount=int(amount * 100),
                created=int(transaction_time.timestamp()),
                available_on=int((transaction_time + timedelta(days=2)).timestamp()),
                currency="usd",
                description="Flash sale purchase",
                fee=int(amount * 0.029 * 100 + 30),  # 2.9% + $0.30
                net=int((amount * 0.971 - 0.30) * 100),
                source=f"ch_{uuid.uuid4().hex[:24]}",
                type="charge",
                metadata={
                    "spike_indicator": True,
                    "risk_score": risk_score,
                    "pattern": "volume_spike",
                    "new_customer": random.random() < 0.8  # 80% new customers
                }
            )
            
            transactions.append(charge)
        
        return transactions
    
    async def _generate_refund_surge(self, strategy: Dict[str, Any]) -> List[StripeTransaction]:
        """
        Generate high refund rate pattern
        """
        
        transactions = []
        base_time = datetime.utcnow() - timedelta(days=5)
        
        # Generate charges that will be refunded
        charge_count = 200
        target_refund_rate = strategy.get("target_refund_rate", 0.08)
        
        for i in range(charge_count):
            charge_time = base_time + timedelta(
                days=random.randint(0, 4),
                hours=random.randint(0, 23)
            )
            
            amount = random.uniform(50, 500)
            
            charge = StripeTransaction(
                id=f"txn_{uuid.uuid4().hex[:24]}",
                amount=int(amount * 100),
                created=int(charge_time.timestamp()),
                available_on=int((charge_time + timedelta(days=2)).timestamp()),
                currency="usd",
                description="Product purchase",
                fee=int(amount * 0.029 * 100 + 30),
                net=int((amount * 0.971 - 0.30) * 100),
                source=f"ch_{uuid.uuid4().hex[:24]}",
                type="charge",
                metadata={
                    "risk_score": random.uniform(20, 60),
                    "pattern": "refund_surge_base"
                }
            )
            
            transactions.append(charge)
            
            # Generate refunds at target rate
            if random.random() < target_refund_rate:
                refund_delay = random.randint(
                    strategy.get("refund_delay_hours", [2, 48])[0],
                    strategy.get("refund_delay_hours", [2, 48])[1]
                )
                refund_time = charge_time + timedelta(hours=refund_delay)
                
                refund_reason = random.choice(strategy.get("refund_reasons", ["Customer request"]))
                
                refund = StripeTransaction(
                    id=f"txn_{uuid.uuid4().hex[:24]}",
                    amount=-charge.amount,
                    created=int(refund_time.timestamp()),
                    available_on=int((refund_time + timedelta(days=2)).timestamp()),
                    currency="usd",
                    description=f"Refund: {refund_reason}",
                    fee=-charge.fee,
                    net=-charge.net,
                    source=f"re_{uuid.uuid4().hex[:24]}",
                    type="refund",
                    metadata={
                        "original_charge": charge.id,
                        "reason": refund_reason,
                        "risk_score": random.uniform(50, 90),
                        "pattern": "refund_surge"
                    }
                )
                
                transactions.append(refund)
        
        refund_count = len([t for t in transactions if t.type == "refund"])
        actual_rate = refund_count / charge_count
        print(f"Generated refund surge: {refund_count}/{charge_count} = {actual_rate:.1%} refund rate")
        
        return transactions
    
    async def _generate_chargeback_pattern(self, strategy: Dict[str, Any]) -> List[StripeTransaction]:
        """
        Generate chargeback surge pattern
        """
        
        transactions = []
        base_time = datetime.utcnow() - timedelta(days=45)  # Chargebacks take time
        
        charge_count = 300
        target_chargeback_rate = strategy.get("target_chargeback_rate", 0.025)
        
        for i in range(charge_count):
            charge_time = base_time + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23)
            )
            
            amount = random.uniform(100, 1000)
            
            charge = StripeTransaction(
                id=f"txn_{uuid.uuid4().hex[:24]}",
                amount=int(amount * 100),
                created=int(charge_time.timestamp()),
                available_on=int((charge_time + timedelta(days=2)).timestamp()),
                currency="usd",
                description="Online purchase",
                fee=int(amount * 0.029 * 100 + 30),
                net=int((amount * 0.971 - 0.30) * 100),
                source=f"ch_{uuid.uuid4().hex[:24]}",
                type="charge",
                metadata={
                    "risk_score": random.uniform(30, 70),
                    "pattern": "chargeback_base"
                }
            )
            
            transactions.append(charge)
            
            # Generate chargebacks
            if random.random() < target_chargeback_rate:
                chargeback_delay = random.randint(
                    strategy.get("chargeback_delay_days", [15, 60])[0],
                    strategy.get("chargeback_delay_days", [15, 60])[1]
                )
                chargeback_time = charge_time + timedelta(days=chargeback_delay)
                
                chargeback_reason = random.choice(strategy.get("chargeback_reasons", ["Fraud"]))
                chargeback_fee = strategy.get("chargeback_fee", 15.00)
                
                chargeback = StripeTransaction(
                    id=f"txn_{uuid.uuid4().hex[:24]}",
                    amount=-(charge.amount + int(chargeback_fee * 100)),
                    created=int(chargeback_time.timestamp()),
                    available_on=int(chargeback_time.timestamp()),
                    currency="usd",
                    description=f"Chargeback: {chargeback_reason}",
                    fee=int(chargeback_fee * 100),
                    net=-(charge.amount + int(chargeback_fee * 100)),
                    source=f"cb_{uuid.uuid4().hex[:24]}",
                    type="adjustment",
                    metadata={
                        "original_charge": charge.id,
                        "reason": chargeback_reason,
                        "chargeback_fee": chargeback_fee,
                        "risk_score": random.uniform(80, 100),
                        "pattern": "chargeback"
                    }
                )
                
                transactions.append(chargeback)
        
        cb_count = len([t for t in transactions if t.type == "adjustment"])
        actual_rate = cb_count / charge_count
        print(f"Generated chargeback surge: {cb_count}/{charge_count} = {actual_rate:.1%} chargeback rate")
        
        return transactions
    
    async def _generate_pattern_deviation(self, strategy: Dict[str, Any]) -> List[StripeTransaction]:
        """
        Generate pattern deviation (unusual business behavior)
        """
        
        transactions = []
        base_time = datetime.utcnow()
        
        # Sudden change in transaction characteristics
        for i in range(150):
            transaction_time = base_time + timedelta(
                hours=random.randint(0, 48)
            )
            
            # Unusual amounts (10x normal)
            amount = random.uniform(1000, 10000)
            
            # Different currency occasionally
            currency = random.choice(["usd", "usd", "usd", "eur", "gbp"])
            
            charge = StripeTransaction(
                id=f"txn_{uuid.uuid4().hex[:24]}",
                amount=int(amount * 100),
                created=int(transaction_time.timestamp()),
                available_on=int((transaction_time + timedelta(days=2)).timestamp()),
                currency=currency,
                description="Enterprise license - unusual sale",
                fee=int(amount * 0.029 * 100 + 30),
                net=int((amount * 0.971 - 0.30) * 100),
                source=f"ch_{uuid.uuid4().hex[:24]}",
                type="charge",
                metadata={
                    "risk_score": random.uniform(60, 95),
                    "pattern": "deviation",
                    "unusual_amount": True,
                    "currency_change": currency != "usd"
                }
            )
            
            transactions.append(charge)
        
        return transactions
    
    async def _analyze_generated_patterns(self, transactions: List[StripeTransaction]) -> Dict[str, Any]:
        """
        Use GPT-5 to analyze the generated transaction patterns
        """
        
        # Prepare transaction data for analysis
        transaction_summary = {
            "total_count": len(transactions),
            "types": {},
            "amount_range": {},
            "time_distribution": {},
            "risk_indicators": []
        }
        
        # Calculate metrics
        charges = [t for t in transactions if t.type == "charge"]
        refunds = [t for t in transactions if t.type == "refund"]
        adjustments = [t for t in transactions if t.type == "adjustment"]
        
        if charges:
            charge_amounts = [t.amount / 100 for t in charges]
            transaction_summary["amount_range"] = {
                "min": min(charge_amounts),
                "max": max(charge_amounts),
                "avg": sum(charge_amounts) / len(charge_amounts)
            }
        
        transaction_summary["types"] = {
            "charges": len(charges),
            "refunds": len(refunds),
            "adjustments": len(adjustments)
        }
        
        # Calculate rates
        refund_rate = len(refunds) / len(charges) if charges else 0
        chargeback_rate = len(adjustments) / len(charges) if charges else 0
        
        # Identify risk indicators
        if refund_rate > self.STRIPE_THRESHOLDS["refund_rate_freeze"]:
            transaction_summary["risk_indicators"].append(f"High refund rate: {refund_rate:.1%}")
        
        if chargeback_rate > self.STRIPE_THRESHOLDS["chargeback_rate_freeze"]:
            transaction_summary["risk_indicators"].append(f"High chargeback rate: {chargeback_rate:.1%}")
        
        # Use GPT-5 for deep analysis
        risk_analysis = await self.gpt5_client.analyze_transaction_risk(
            transactions=[asdict(t) for t in transactions[:10]],  # Sample for GPT-5
            context={
                "summary": transaction_summary,
                "thresholds": self.STRIPE_THRESHOLDS,
                "business_type": "B2B SaaS"
            },
            reasoning_effort="high",
            verbosity="high"
        )
        
        return {
            "summary": transaction_summary,
            "refund_rate": refund_rate,
            "chargeback_rate": chargeback_rate,
            "freeze_probability": self._calculate_freeze_probability(refund_rate, chargeback_rate),
            "gpt5_analysis": risk_analysis,
            "recommendations": self._generate_recommendations(transaction_summary)
        }
    
    def _calculate_baseline_metrics(self, transactions: List[StripeTransaction]) -> Dict[str, Any]:
        """
        Calculate baseline metrics from transactions
        """
        
        if not transactions:
            return {}
        
        charges = [t for t in transactions if t.type == "charge"]
        
        if not charges:
            return {}
        
        amounts = [t.amount / 100 for t in charges]
        
        return {
            "daily_volume": len(charges) / 30,  # Assuming 30-day period
            "avg_amount": sum(amounts) / len(amounts),
            "min_amount": min(amounts),
            "max_amount": max(amounts),
            "total_processed": sum(amounts),
            "transaction_count": len(charges)
        }
    
    def _calculate_statistics(self, transactions: List[StripeTransaction]) -> Dict[str, Any]:
        """
        Calculate comprehensive statistics
        """
        
        stats = {
            "total_transactions": len(transactions),
            "by_type": {},
            "total_volume": 0,
            "fees_collected": 0,
            "net_amount": 0
        }
        
        for txn in transactions:
            txn_type = txn.type
            if txn_type not in stats["by_type"]:
                stats["by_type"][txn_type] = {"count": 0, "volume": 0}
            
            stats["by_type"][txn_type]["count"] += 1
            stats["by_type"][txn_type]["volume"] += abs(txn.amount / 100)
            
            if txn.type == "charge":
                stats["total_volume"] += txn.amount / 100
                stats["fees_collected"] += txn.fee / 100
                stats["net_amount"] += txn.net / 100
        
        return stats
    
    def _calculate_freeze_probability(self, refund_rate: float, chargeback_rate: float) -> float:
        """
        Calculate probability of account freeze based on rates
        """
        
        freeze_prob = 0.0
        
        # Refund rate contribution
        if refund_rate > self.STRIPE_THRESHOLDS["refund_rate_freeze"]:
            freeze_prob += 0.4 * (refund_rate / self.STRIPE_THRESHOLDS["refund_rate_freeze"])
        elif refund_rate > self.STRIPE_THRESHOLDS["refund_rate_warning"]:
            freeze_prob += 0.2 * (refund_rate / self.STRIPE_THRESHOLDS["refund_rate_warning"])
        
        # Chargeback rate contribution (more severe)
        if chargeback_rate > self.STRIPE_THRESHOLDS["chargeback_rate_freeze"]:
            freeze_prob += 0.6 * (chargeback_rate / self.STRIPE_THRESHOLDS["chargeback_rate_freeze"])
        
        return min(1.0, freeze_prob)
    
    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on patterns
        """
        
        recommendations = []
        
        if summary.get("risk_indicators"):
            recommendations.append("Immediately review transaction patterns with payment team")
            recommendations.append("Prepare documentation for Stripe risk team")
            recommendations.append("Consider implementing additional fraud detection")
        
        if "High refund rate" in str(summary.get("risk_indicators", [])):
            recommendations.append("Investigate product/service quality issues")
            recommendations.append("Improve customer communication and expectations")
        
        if "High chargeback rate" in str(summary.get("risk_indicators", [])):
            recommendations.append("Implement stronger customer authentication")
            recommendations.append("Review and improve dispute resolution process")
        
        return recommendations
    
    def export_to_jsonl(self, transactions: List[StripeTransaction], filename: str):
        """
        Export transactions to JSONL format for easy import
        """
        
        with open(filename, 'w') as f:
            for txn in transactions:
                f.write(json.dumps(asdict(txn)) + '\n')
        
        print(f"Exported {len(transactions)} transactions to {filename}")
    
    def export_to_csv(self, transactions: List[StripeTransaction], filename: str):
        """
        Export transactions to CSV format matching Stripe's export
        """
        
        import csv
        
        with open(filename, 'w', newline='') as f:
            fieldnames = [
                'id', 'created', 'available_on', 'amount', 'currency',
                'fee', 'net', 'type', 'description', 'source', 'status'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for txn in transactions:
                writer.writerow({
                    'id': txn.id,
                    'created': datetime.fromtimestamp(txn.created).isoformat(),
                    'available_on': datetime.fromtimestamp(txn.available_on).isoformat(),
                    'amount': txn.amount / 100,  # Convert from cents
                    'currency': txn.currency,
                    'fee': txn.fee / 100,
                    'net': txn.net / 100,
                    'type': txn.type,
                    'description': txn.description,
                    'source': txn.source,
                    'status': txn.status
                })
        
        print(f"Exported {len(transactions)} transactions to {filename}")


async def main():
    """
    Demo the GPT-5 enhanced Stripe data generator
    """
    
    generator = GPT5StripeDataGenerator()
    
    print("GPT-5 Enhanced Stripe Data Generator")
    print("=" * 50)
    
    # Generate different scenarios
    scenarios = [
        ("normal", "Normal business operations"),
        ("sudden_spike", "Volume spike that triggers review"),
        ("high_refund_rate", "Excessive refunds triggering freeze"),
        ("chargeback_surge", "Chargeback pattern causing immediate freeze")
    ]
    
    for scenario_type, description in scenarios:
        print(f"\nGenerating scenario: {description}")
        print("-" * 40)
        
        dataset = await generator.generate_intelligent_dataset(
            scenario=scenario_type,
            duration_days=7 if scenario_type == "normal" else 3,
            base_volume=50
        )
        
        # Display results
        stats = dataset["statistics"]
        analysis = dataset["risk_analysis"]
        
        print(f"Generated {stats['total_transactions']} transactions")
        print(f"Total volume: ${stats['total_volume']:,.2f}")
        print(f"Refund rate: {analysis['refund_rate']:.1%}")
        print(f"Chargeback rate: {analysis['chargeback_rate']:.1%}")
        print(f"Freeze probability: {analysis['freeze_probability']:.1%}")
        
        if analysis.get("recommendations"):
            print("\nRecommendations:")
            for rec in analysis["recommendations"]:
                print(f"  - {rec}")
        
        # Export data
        if scenario_type == "high_refund_rate":
            generator.export_to_jsonl(
                dataset["transactions"],
                f"stripe_data_{scenario_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
            )


if __name__ == "__main__":
    asyncio.run(main())