"""
Claude Synthetic Transaction Data Generator
Generates realistic Stripe transaction patterns that can trigger account freezes
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass, field
import uuid


@dataclass
class TransactionPattern:
    pattern_type: str
    description: str
    risk_level: str
    typical_triggers: List[str]


@dataclass 
class SyntheticTransaction:
    id: str
    type: str  # charge, refund, payout, adjustment
    amount: float
    currency: str = "usd"
    created: datetime = field(default_factory=datetime.utcnow)
    status: str = "succeeded"
    customer_id: Optional[str] = None
    card_brand: Optional[str] = None
    failure_code: Optional[str] = None
    failure_message: Optional[str] = None
    fee: float = 0.0
    net: float = 0.0
    source_id: Optional[str] = None
    description: Optional[str] = None


class ClaudeSyntheticDataGenerator:
    """
    Uses Claude's structured data generation capabilities to create realistic
    Stripe transaction patterns that demonstrate common freeze triggers.
    """
    
    def __init__(self, openai_api_key: str = None):
        try:
            from claude_client import ClaudeClient
            self.claude_client = ClaudeClient()
        except Exception as e:
            print(f"⚠️  Claude client not available: {e}")
            self.claude_client = None
        
        self.transaction_history = []
        
        # Common patterns that trigger Stripe freezes
        self.freeze_patterns = {
            "sudden_spike": TransactionPattern(
                pattern_type="sudden_spike",
                description="Dramatic increase in transaction volume/amount",
                risk_level="high",
                typical_triggers=["10x volume increase", "unusually large amounts", "rapid succession"]
            ),
            "high_refund_rate": TransactionPattern(
                pattern_type="high_refund_rate", 
                description="Excessive refunds (>5% of transactions)",
                risk_level="critical",
                typical_triggers=["refund rate >5%", "frequent reversals", "customer complaints"]
            ),
            "chargeback_surge": TransactionPattern(
                pattern_type="chargeback_surge",
                description="Chargebacks exceeding 1% threshold", 
                risk_level="critical",
                typical_triggers=["chargeback rate >1%", "dispute pattern", "fraud indicators"]
            ),
            "pattern_deviation": TransactionPattern(
                pattern_type="pattern_deviation",
                description="Inconsistent with historical business profile",
                risk_level="medium", 
                typical_triggers=["location changes", "currency shifts", "ticket size variance"]
            )
        }
    
    async def generate_normal_baseline(
        self,
        days: int = 30,
        daily_volume: int = 50,
        avg_amount: float = 85.0
    ) -> List[SyntheticTransaction]:
        """
        Generate normal transaction baseline using Claude's structured generation.
        This represents typical business activity before freeze triggers.
        """
        
        claude_context = {
            "task": "generate_baseline_transactions",
            "parameters": {
                "days": days,
                "daily_volume": daily_volume,
                "avg_amount": avg_amount,
                "business_type": "B2B SaaS",
                "customer_profile": "small_to_medium_businesses"
            },
            "schema": {
                "transaction_fields": ["amount", "currency", "customer_type", "card_brand", "status"],
                "patterns": ["consistent_timing", "predictable_amounts", "low_refund_rate"]
            }
        }
        
        # Real Claude API call for data generation
        if self.claude_client:
            generation_plan = await self.claude_client.generate_synthetic_data(
                pattern_type="normal",
                context=claude_context,
                reasoning_effort="minimal",  # Fast generation for baseline data
                verbosity="low"  # Concise structured output
            )
        else:
            generation_plan = {"pattern_type": "normal", "generation_plan": "Mock data generation"}
        
        # Generate actual transaction objects
        baseline_transactions = []
        start_date = datetime.utcnow() - timedelta(days=days)
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            
            # Normal daily variation: ±20%
            daily_count = int(daily_volume * random.uniform(0.8, 1.2))
            
            for i in range(daily_count):
                # Normal amount distribution
                amount = max(10, random.gauss(avg_amount, avg_amount * 0.3))
                
                transaction = SyntheticTransaction(
                    id=f"ch_{uuid.uuid4().hex[:24]}",
                    type="charge",
                    amount=round(amount, 2),
                    created=current_date + timedelta(
                        hours=random.randint(9, 17),
                        minutes=random.randint(0, 59)
                    ),
                    status="succeeded",
                    customer_id=f"cus_{uuid.uuid4().hex[:14]}",
                    card_brand=random.choice(["visa", "mastercard", "amex"]),
                    fee=round(amount * 0.029 + 0.30, 2),  # Standard Stripe fees
                    net=round(amount - (amount * 0.029 + 0.30), 2),
                    description="Monthly subscription charge"
                )
                
                baseline_transactions.append(transaction)
                
                # Add occasional refunds (normal rate ~2%)
                if random.random() < 0.02:
                    refund = SyntheticTransaction(
                        id=f"re_{uuid.uuid4().hex[:24]}",
                        type="refund", 
                        amount=-transaction.amount,
                        created=transaction.created + timedelta(hours=random.randint(1, 48)),
                        status="succeeded",
                        source_id=transaction.id,
                        description="Customer requested refund"
                    )
                    baseline_transactions.append(refund)
        
        self.transaction_history.extend(baseline_transactions)
        return baseline_transactions
    
    async def generate_freeze_trigger_scenario(
        self,
        pattern_type: str,
        severity: str = "high"
    ) -> List[SyntheticTransaction]:
        """
        Generate transaction patterns that typically trigger Stripe account freezes.
        Uses Claude's comprehensive analysis to create realistic risk scenarios.
        """
        
        if pattern_type not in self.freeze_patterns:
            raise ValueError(f"Unknown pattern type: {pattern_type}")
        
        pattern = self.freeze_patterns[pattern_type]
        
        claude_context = {
            "task": "generate_freeze_trigger_pattern",
            "pattern": pattern.pattern_type,
            "severity": severity,
            "risk_factors": pattern.typical_triggers,
            "historical_baseline": self._get_baseline_stats(),
            "freeze_thresholds": {
                "refund_rate": 0.05,  # 5% triggers review
                "chargeback_rate": 0.01,  # 1% triggers freeze
                "volume_spike": 10.0,  # 10x normal volume
                "amount_spike": 5.0   # 5x normal transaction size
            }
        }
        
        # Use Claude comprehensive analysis for complex pattern generation
        scenario_plan = await self._simulate_claude_reasoning(
            context=claude_context,
            reasoning_effort="high",  # Deep analysis of risk patterns
            verbosity="high"  # Detailed explanation of pattern logic
        )
        
        # Generate the actual problematic transactions
        trigger_transactions = []
        base_time = datetime.utcnow()
        
        if pattern_type == "sudden_spike":
            trigger_transactions = await self._generate_volume_spike(base_time)
        elif pattern_type == "high_refund_rate":
            trigger_transactions = await self._generate_refund_surge(base_time)
        elif pattern_type == "chargeback_surge":
            trigger_transactions = await self._generate_chargeback_pattern(base_time)
        elif pattern_type == "pattern_deviation":
            trigger_transactions = await self._generate_pattern_deviation(base_time)
        
        self.transaction_history.extend(trigger_transactions)
        return trigger_transactions
    
    async def _generate_volume_spike(self, base_time: datetime) -> List[SyntheticTransaction]:
        """Generate sudden volume spike that triggers freeze."""
        
        transactions = []
        normal_daily = len([t for t in self.transaction_history if t.created.date() == (base_time - timedelta(days=1)).date()])
        spike_volume = max(normal_daily * 12, 500)  # 12x spike or minimum 500
        
        # Compress spike into 2-3 hours (highly suspicious)
        for i in range(spike_volume):
            amount = random.uniform(200, 2000)  # Unusually large amounts
            
            transaction = SyntheticTransaction(
                id=f"ch_{uuid.uuid4().hex[:24]}",
                type="charge",
                amount=round(amount, 2),
                created=base_time + timedelta(minutes=random.randint(0, 180)),  # Within 3 hours
                status="succeeded",
                customer_id=f"cus_{uuid.uuid4().hex[:14]}",
                card_brand=random.choice(["visa", "mastercard"]),
                fee=round(amount * 0.029 + 0.30, 2),
                net=round(amount - (amount * 0.029 + 0.30), 2),
                description="Large purchase - promotional event"
            )
            transactions.append(transaction)
        
        return transactions
    
    async def _generate_refund_surge(self, base_time: datetime) -> List[SyntheticTransaction]:
        """Generate high refund rate scenario (>5% triggers review)."""
        
        transactions = []
        
        # Generate charges first
        charge_count = 100
        for i in range(charge_count):
            amount = random.uniform(50, 300)
            
            charge = SyntheticTransaction(
                id=f"ch_{uuid.uuid4().hex[:24]}",
                type="charge",
                amount=round(amount, 2),
                created=base_time - timedelta(days=random.randint(1, 5)),
                status="succeeded",
                customer_id=f"cus_{uuid.uuid4().hex[:14]}",
                card_brand=random.choice(["visa", "mastercard", "amex"]),
                fee=round(amount * 0.029 + 0.30, 2),
                net=round(amount - (amount * 0.029 + 0.30), 2),
                description="Product purchase"
            )
            transactions.append(charge)
            
            # Generate excessive refunds (15% rate - way above normal 2%)
            if random.random() < 0.15:
                refund = SyntheticTransaction(
                    id=f"re_{uuid.uuid4().hex[:24]}",
                    type="refund",
                    amount=-charge.amount,
                    created=charge.created + timedelta(hours=random.randint(2, 48)),
                    status="succeeded",
                    source_id=charge.id,
                    description=random.choice([
                        "Product not as described",
                        "Customer complaint", 
                        "Defective item",
                        "Unauthorized purchase",
                        "Billing dispute"
                    ])
                )
                transactions.append(refund)
        
        return transactions
    
    async def _generate_chargeback_pattern(self, base_time: datetime) -> List[SyntheticTransaction]:
        """Generate chargeback surge (>1% triggers immediate freeze)."""
        
        transactions = []
        charge_count = 200
        
        for i in range(charge_count):
            amount = random.uniform(100, 800)
            
            charge = SyntheticTransaction(
                id=f"ch_{uuid.uuid4().hex[:24]}",
                type="charge", 
                amount=round(amount, 2),
                created=base_time - timedelta(days=random.randint(7, 30)),  # Chargebacks take time
                status="succeeded",
                customer_id=f"cus_{uuid.uuid4().hex[:14]}",
                card_brand=random.choice(["visa", "mastercard"]),
                fee=round(amount * 0.029 + 0.30, 2),
                net=round(amount - (amount * 0.029 + 0.30), 2),
                description="High-risk transaction"
            )
            transactions.append(charge)
            
            # Generate chargebacks (3% rate - 3x the 1% freeze threshold)
            if random.random() < 0.03:
                chargeback = SyntheticTransaction(
                    id=f"cb_{uuid.uuid4().hex[:24]}",
                    type="adjustment",  # Chargebacks appear as adjustments
                    amount=-(charge.amount + 15.00),  # Amount + $15 chargeback fee
                    created=charge.created + timedelta(days=random.randint(10, 60)),
                    status="succeeded",
                    source_id=charge.id,
                    description=random.choice([
                        "Chargeback: Fraudulent transaction",
                        "Chargeback: Authorization dispute", 
                        "Chargeback: Processing error",
                        "Chargeback: Duplicate processing"
                    ])
                )
                transactions.append(chargeback)
        
        return transactions
    
    async def _generate_pattern_deviation(self, base_time: datetime) -> List[SyntheticTransaction]:
        """Generate transactions that deviate from normal business pattern."""
        
        transactions = []
        
        # Sudden change in transaction characteristics
        for i in range(200):
            # Unusual characteristics that deviate from baseline
            amount = random.uniform(2000, 10000)  # 10x normal ticket size
            
            transaction = SyntheticTransaction(
                id=f"ch_{uuid.uuid4().hex[:24]}",
                type="charge",
                amount=round(amount, 2),
                created=base_time + timedelta(hours=random.randint(0, 24)),
                status="succeeded",
                customer_id=f"cus_{uuid.uuid4().hex[:14]}",
                card_brand=random.choice(["visa", "mastercard"]),
                fee=round(amount * 0.029 + 0.30, 2),
                net=round(amount - (amount * 0.029 + 0.30), 2),
                description=random.choice([
                    "Enterprise license - annual",
                    "Bulk hardware purchase", 
                    "Consulting services - large project",
                    "Multi-year service contract"
                ])
            )
            transactions.append(transaction)
        
        return transactions
    
    async def _simulate_claude_generation(
        self,
        context: Dict[str, Any],
        reasoning_effort: str = "medium",
        verbosity: str = "medium"
    ) -> Dict[str, Any]:
        """
        Simulate Claude API call for structured data generation.
        In production, replace with actual OpenAI API call.
        """
        
        # Simulate processing time based on reasoning effort
        processing_times = {"minimal": 0.1, "low": 0.3, "medium": 0.5, "high": 1.0}
        await asyncio.sleep(processing_times.get(reasoning_effort, 0.5))
        
        return {
            "generated_schema": context.get("schema", {}),
            "reasoning_tokens": {"minimal": 10, "low": 50, "medium": 150, "high": 500}.get(reasoning_effort, 150),
            "verbosity_level": verbosity,
            "context_analyzed": True
        }
    
    async def _simulate_claude_reasoning(
        self,
        context: Dict[str, Any], 
        reasoning_effort: str = "high",
        verbosity: str = "high"
    ) -> Dict[str, Any]:
        """
        Simulate Claude's analysis process for complex pattern analysis.
        """
        
        await asyncio.sleep(0.8)  # High reasoning effort takes more time
        
        pattern_type = context["pattern"]
        reasoning_chain = []
        
        if pattern_type == "sudden_spike":
            reasoning_chain = [
                "Analyzing historical transaction volume baseline",
                "Current spike represents 12x normal daily volume", 
                "Timing compressed into 3-hour window is highly unusual",
                "Large transaction amounts (200-2000) deviate from $85 baseline",
                "Pattern matches typical promotional fraud or account compromise",
                "Recommendation: Generate realistic but suspicious spike pattern"
            ]
        elif pattern_type == "high_refund_rate":
            reasoning_chain = [
                "Normal refund rate in baseline: ~2%",
                "Target refund rate for freeze trigger: 15% (7.5x normal)",
                "Refund reasons should vary to appear organic",
                "Timing should cluster within 24-48 hours of original charges",
                "Pattern suggests product quality issues or customer dissatisfaction",
                "Will trigger automated risk review at Stripe"
            ]
        
        return {
            "reasoning_chain": reasoning_chain,
            "pattern_analysis": context["pattern"],
            "risk_assessment": "high_probability_freeze",
            "estimated_freeze_timeline": "24-72 hours after pattern detection"
        }
    
    def _get_baseline_stats(self) -> Dict[str, float]:
        """Calculate baseline statistics from historical transactions."""
        
        if not self.transaction_history:
            return {"avg_amount": 85.0, "daily_volume": 50, "refund_rate": 0.02}
        
        charges = [t for t in self.transaction_history if t.type == "charge"]
        refunds = [t for t in self.transaction_history if t.type == "refund"]
        
        return {
            "avg_amount": sum(t.amount for t in charges) / len(charges) if charges else 85.0,
            "daily_volume": len(charges) / 30,  # Assuming 30-day baseline
            "refund_rate": len(refunds) / len(charges) if charges else 0.02
        }
    
    def export_to_stripe_format(self, transactions: List[SyntheticTransaction]) -> List[Dict[str, Any]]:
        """Export transactions in Stripe balance_transactions table format."""
        
        stripe_format = []
        for txn in transactions:
            stripe_format.append({
                "id": f"txn_{txn.id[3:]}",  # Convert ch_ to txn_
                "object": "balance_transaction",
                "amount": int(txn.amount * 100),  # Stripe uses cents
                "currency": txn.currency,
                "created": int(txn.created.timestamp()),
                "fee": int(txn.fee * 100) if txn.fee else 0,
                "net": int(txn.net * 100) if txn.net else 0,
                "status": txn.status,
                "type": txn.type,
                "source_id": txn.source_id or txn.id,
                "description": txn.description
            })
        
        return stripe_format
    
    async def generate_real_time_stripe_feed(
        self, 
        duration_minutes: int = 60,
        events_per_minute: int = 5
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate real-time Stripe transaction stream for Claude to analyze.
        Simulates live balance_transactions feed with varied risk patterns.
        """
        print(f"🔴 LIVE: Claude real-time Stripe feed starting ({duration_minutes}m)")
        
        start_time = datetime.utcnow()
        event_count = 0
        
        while (datetime.utcnow() - start_time).total_seconds() < duration_minutes * 60:
            # Generate batch of events
            batch = []
            for _ in range(events_per_minute):
                event = await self._generate_live_transaction_event()
                batch.append(event)
                event_count += 1
            
            # Occasionally inject risk scenarios
            if event_count % 50 == 0:
                risk_batch = await self._inject_risk_scenario()
                batch.extend(risk_batch)
                print(f"⚠️  RISK INJECTION: {len(risk_batch)} suspicious events")
            
            # Yield events with Claude context
            yield {
                "timestamp": datetime.utcnow().isoformat(),
                "events": batch,
                "risk_indicators": self._calculate_risk_indicators(batch),
                "claude_analysis_needed": self._should_trigger_claude_analysis(batch),
                "cumulative_events": event_count
            }
            
            # Wait for next batch (simulate real-time)
            await asyncio.sleep(60 / events_per_minute)
    
    async def _generate_live_transaction_event(self) -> Dict[str, Any]:
        """Generate single realistic Stripe balance_transaction."""
        
        amount = random.uniform(25, 400)
        txn_id = f"txn_{uuid.uuid4().hex[:17]}"
        
        # Weighted transaction types
        txn_type = random.choices(
            ["charge", "refund", "payout", "adjustment"],
            weights=[0.85, 0.10, 0.03, 0.02]
        )[0]
        
        if txn_type == "refund":
            amount = -amount
        elif txn_type == "adjustment":
            amount = random.choice([-15.00, -25.00])  # Chargeback fees
        
        return {
            "id": txn_id,
            "object": "balance_transaction", 
            "amount": int(amount * 100),  # Stripe uses cents
            "currency": "usd",
            "created": int(datetime.utcnow().timestamp()),
            "fee": int((abs(amount) * 0.029 + 0.30) * 100),
            "net": int((amount - (abs(amount) * 0.029 + 0.30)) * 100),
            "type": txn_type,
            "status": "available",
            "source": f"ch_{uuid.uuid4().hex[:24]}" if txn_type == "charge" else None,
            "description": self._generate_realistic_description(txn_type)
        }
    
    async def _inject_risk_scenario(self) -> List[Dict[str, Any]]:
        """Inject risk pattern that should trigger Claude analysis."""
        
        scenario_type = random.choice(["volume_spike", "refund_cluster", "large_amounts"])
        risk_events = []
        
        if scenario_type == "volume_spike":
            # Generate 20+ transactions in quick succession
            for _ in range(random.randint(20, 35)):
                event = await self._generate_live_transaction_event()
                event["risk_flag"] = "volume_anomaly"
                risk_events.append(event)
                
        elif scenario_type == "refund_cluster":
            # Generate cluster of refunds
            for _ in range(random.randint(8, 15)):
                refund_event = {
                    "id": f"txn_{uuid.uuid4().hex[:17]}",
                    "type": "refund",
                    "amount": -random.randint(5000, 25000),  # $50-250 refunds
                    "created": int(datetime.utcnow().timestamp()),
                    "risk_flag": "refund_cluster",
                    "description": "Customer complaint refund"
                }
                risk_events.append(refund_event)
                
        elif scenario_type == "large_amounts":
            # Unusually large transactions
            for _ in range(random.randint(3, 8)):
                large_event = await self._generate_live_transaction_event()
                large_event["amount"] = random.randint(100000, 500000)  # $1000-5000
                large_event["risk_flag"] = "amount_anomaly"
                risk_events.append(large_event)
        
        return risk_events
    
    def _calculate_risk_indicators(self, batch: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate risk metrics for current batch."""
        
        charges = [e for e in batch if e.get("type") == "charge"]
        refunds = [e for e in batch if e.get("type") == "refund"]
        
        total_volume = len(batch)
        refund_rate = len(refunds) / max(len(charges), 1)
        avg_amount = sum(abs(e.get("amount", 0)) for e in batch) / max(total_volume, 1) / 100
        
        # Risk flags
        has_risk_flags = any(e.get("risk_flag") for e in batch)
        
        return {
            "transaction_velocity": total_volume,
            "refund_rate": refund_rate,
            "average_amount": avg_amount,
            "risk_flags_present": has_risk_flags,
            "risk_score": min((total_volume * 0.1) + (refund_rate * 50) + (1 if has_risk_flags else 0), 10.0)
        }
    
    def _should_trigger_claude_analysis(self, batch: List[Dict[str, Any]]) -> bool:
        """Determine if batch needs Claude intelligent analysis."""
        
        indicators = self._calculate_risk_indicators(batch)
        
        # Trigger Claude analysis if:
        return (
            indicators["transaction_velocity"] > 15 or  # High volume
            indicators["refund_rate"] > 0.08 or         # >8% refunds
            indicators["risk_flags_present"] or         # Risk flags
            indicators["average_amount"] > 800          # Large amounts
        )
    
    def _generate_realistic_description(self, txn_type: str) -> str:
        """Generate realistic transaction descriptions."""
        
        descriptions = {
            "charge": [
                "Monthly subscription billing",
                "One-time service payment", 
                "Product purchase - digital",
                "Consulting services",
                "License fee - annual"
            ],
            "refund": [
                "Customer service refund",
                "Billing dispute resolution",
                "Product return processing",
                "Service cancellation",
                "Duplicate charge reversal"
            ],
            "payout": [
                "Automatic payout to bank",
                "Manual payout request", 
                "Daily settlement"
            ],
            "adjustment": [
                "Chargeback fee",
                "Processing adjustment",
                "Account correction"
            ]
        }
        
        return random.choice(descriptions.get(txn_type, ["Transaction"]))

    async def generate_demo_dataset(self) -> Dict[str, Any]:
        """Generate complete demo dataset showing normal vs freeze-trigger patterns."""
        
        print("🤖 Claude generating synthetic Stripe transaction data...")
        
        # Generate baseline (normal business)
        baseline = await self.generate_normal_baseline(days=30, daily_volume=45, avg_amount=85.0)
        print(f"✅ Generated {len(baseline)} baseline transactions")
        
        # Generate freeze trigger scenarios
        scenarios = {}
        
        # Scenario 1: Volume spike
        spike_txns = await self.generate_freeze_trigger_scenario("sudden_spike")
        scenarios["volume_spike"] = spike_txns
        print(f"⚠️ Generated volume spike: {len(spike_txns)} transactions in 3 hours")
        
        # Scenario 2: High refund rate  
        refund_txns = await self.generate_freeze_trigger_scenario("high_refund_rate")
        scenarios["refund_surge"] = refund_txns
        refund_count = len([t for t in refund_txns if t.type == "refund"])
        charge_count = len([t for t in refund_txns if t.type == "charge"])
        print(f"⚠️ Generated refund surge: {refund_count}/{charge_count} = {refund_count/charge_count*100:.1f}% refund rate")
        
        # Scenario 3: Chargeback pattern
        chargeback_txns = await self.generate_freeze_trigger_scenario("chargeback_surge") 
        scenarios["chargeback_pattern"] = chargeback_txns
        cb_count = len([t for t in chargeback_txns if t.type == "adjustment"])
        cb_charge_count = len([t for t in chargeback_txns if t.type == "charge"])
        print(f"⚠️ Generated chargeback surge: {cb_count}/{cb_charge_count} = {cb_count/cb_charge_count*100:.1f}% chargeback rate")
        
        return {
            "baseline": baseline,
            "freeze_scenarios": scenarios,
            "summary": {
                "total_transactions": len(self.transaction_history),
                "baseline_period": "30 days", 
                "freeze_triggers": list(scenarios.keys()),
                "claude_features_used": [
                    "structured_data_generation",
                    "reasoning_effort_control", 
                    "verbosity_control",
                    "context_aware_patterns"
                ]
            }
        }