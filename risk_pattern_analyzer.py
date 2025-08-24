"""
Claude Powered Risk Pattern Analysis for Payment Orchestration
Analyzes transaction patterns and predicts account freeze probability using Claude's advanced reasoning
"""

import asyncio
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

from claude_client import ClaudeClient
from stripe_synthetic_data_generator import StripeTransaction, TransactionType


class RiskTier(Enum):
    MINIMAL = "minimal"
    LOW = "low"  
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskPattern:
    pattern_type: str
    severity: RiskTier
    description: str
    confidence: float
    triggers: List[str]
    freeze_probability: float
    timeline_estimate: str
    gpt5_reasoning: str


@dataclass 
class RiskAnalysis:
    overall_risk: RiskTier
    freeze_probability: float
    identified_patterns: List[RiskPattern]
    recommendations: List[str]
    gpt5_insights: Dict[str, Any]
    analysis_timestamp: datetime
    data_summary: Dict[str, Any]


class ClaudeRiskAnalyzer:
    """
    Advanced risk pattern analysis using GPT-5's reasoning capabilities
    """
    
    def __init__(self):
        self.gpt5_client = GPT5Client()
        
        # Stripe freeze thresholds (based on real Stripe policies)
        self.FREEZE_THRESHOLDS = {
            "refund_rate_warning": 0.03,      # 3% triggers monitoring
            "refund_rate_investigation": 0.05, # 5% triggers investigation  
            "refund_rate_freeze": 0.08,        # 8% likely freeze
            "chargeback_rate_freeze": 0.01,    # 1% immediate freeze
            "volume_spike_review": 5.0,        # 5x normal triggers review
            "volume_spike_freeze": 10.0,       # 10x triggers freeze
            "rapid_transactions": 100,         # 100+ txns/hour is suspicious
            "large_transaction": 10000,        # $10K+ requires documentation
            "international_rate": 0.3,         # >30% international is risky
            "velocity_threshold": 1000,        # Transaction velocity limit
        }
        
        # Pattern detection rules
        self.PATTERN_RULES = {
            "velocity_spike": {
                "window_minutes": 60,
                "threshold_multiplier": 5.0,
                "risk_tier": RiskTier.HIGH
            },
            "refund_clustering": {
                "window_hours": 24,
                "min_refunds": 10,
                "rate_threshold": 0.2
            },
            "amount_deviation": {
                "std_multiplier": 3.0,
                "risk_tier": RiskTier.MODERATE
            },
            "geographic_anomaly": {
                "new_country_threshold": 3,
                "risk_tier": RiskTier.MODERATE  
            }
        }
    
    async def analyze_transactions(
        self,
        transactions: List[StripeTransaction],
        baseline_metrics: Optional[Dict[str, Any]] = None,
        reasoning_effort: str = "high"
    ) -> RiskAnalysis:
        """
        Comprehensive risk analysis using GPT-5's advanced reasoning
        """
        
        print(f"Starting GPT-5 risk analysis on {len(transactions)} transactions...")
        
        # Step 1: Statistical analysis
        stats = self._calculate_comprehensive_statistics(transactions)
        
        # Step 2: Pattern detection
        detected_patterns = await self._detect_risk_patterns(transactions, stats)
        
        # Step 3: GPT-5 deep analysis
        gpt5_analysis = await self._perform_gpt5_analysis(
            transactions, stats, detected_patterns, reasoning_effort
        )
        
        # Step 4: Risk scoring and recommendations
        overall_risk, freeze_prob = self._calculate_overall_risk(detected_patterns, stats)
        recommendations = await self._generate_recommendations(detected_patterns, gpt5_analysis)
        
        return RiskAnalysis(
            overall_risk=overall_risk,
            freeze_probability=freeze_prob,
            identified_patterns=detected_patterns,
            recommendations=recommendations,
            gpt5_insights=gpt5_analysis,
            analysis_timestamp=datetime.utcnow(),
            data_summary=stats
        )
    
    def _calculate_comprehensive_statistics(self, transactions: List[StripeTransaction]) -> Dict[str, Any]:
        """
        Calculate comprehensive transaction statistics for risk analysis
        """
        
        if not transactions:
            return {}
        
        # Separate by transaction type
        charges = [t for t in transactions if t.type == "charge"]
        refunds = [t for t in transactions if t.type == "refund"] 
        adjustments = [t for t in transactions if t.type == "adjustment"]
        
        stats = {
            "total_transactions": len(transactions),
            "transaction_types": {
                "charges": len(charges),
                "refunds": len(refunds),
                "adjustments": len(adjustments)
            }
        }
        
        if not charges:
            return stats
        
        # Amount analysis
        charge_amounts = [t.amount / 100 for t in charges]  # Convert from cents
        stats["amount_analysis"] = {
            "min": min(charge_amounts),
            "max": max(charge_amounts),
            "mean": statistics.mean(charge_amounts),
            "median": statistics.median(charge_amounts),
            "std_dev": statistics.stdev(charge_amounts) if len(charge_amounts) > 1 else 0,
            "total_volume": sum(charge_amounts)
        }
        
        # Time distribution analysis
        charge_times = [datetime.fromtimestamp(t.created) for t in charges]
        if charge_times:
            time_span = max(charge_times) - min(charge_times)
            stats["temporal_analysis"] = {
                "time_span_days": time_span.days,
                "time_span_hours": time_span.total_seconds() / 3600,
                "transactions_per_hour": len(charges) / max(1, time_span.total_seconds() / 3600),
                "peak_detection": self._detect_time_peaks(charge_times)
            }
        
        # Risk rates calculation
        stats["risk_rates"] = {
            "refund_rate": len(refunds) / len(charges) if charges else 0,
            "chargeback_rate": len(adjustments) / len(charges) if charges else 0,
            "failure_indicators": self._detect_failure_patterns(transactions)
        }
        
        # Velocity analysis
        stats["velocity_analysis"] = self._analyze_transaction_velocity(charges)
        
        # Pattern flags
        stats["pattern_flags"] = {
            "high_refund_rate": stats["risk_rates"]["refund_rate"] > self.FREEZE_THRESHOLDS["refund_rate_investigation"],
            "high_chargeback_rate": stats["risk_rates"]["chargeback_rate"] > self.FREEZE_THRESHOLDS["chargeback_rate_freeze"],
            "volume_spike": stats["temporal_analysis"]["transactions_per_hour"] > 50 if "temporal_analysis" in stats else False,
            "amount_anomalies": stats["amount_analysis"]["std_dev"] > stats["amount_analysis"]["mean"] * 2 if stats["amount_analysis"]["std_dev"] > 0 else False
        }
        
        return stats
    
    def _detect_time_peaks(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """
        Detect unusual time clustering patterns
        """
        
        if not timestamps:
            return {}
        
        # Group by hour buckets
        hour_counts = {}
        for ts in timestamps:
            hour_bucket = ts.replace(minute=0, second=0, microsecond=0)
            hour_counts[hour_bucket] = hour_counts.get(hour_bucket, 0) + 1
        
        if not hour_counts:
            return {}
        
        counts = list(hour_counts.values())
        mean_count = statistics.mean(counts)
        max_count = max(counts)
        
        return {
            "max_hourly_transactions": max_count,
            "avg_hourly_transactions": mean_count,
            "peak_to_average_ratio": max_count / mean_count if mean_count > 0 else 0,
            "suspicious_clustering": max_count > mean_count * 5  # 5x average in single hour
        }
    
    def _detect_failure_patterns(self, transactions: List[StripeTransaction]) -> Dict[str, Any]:
        """
        Detect patterns that indicate system or business issues
        """
        
        failure_indicators = {
            "rapid_refunds": 0,
            "clustered_failures": 0,
            "unusual_descriptions": []
        }
        
        # Look for rapid refunds (within 1 hour of charge)
        charges_dict = {t.id: t for t in transactions if t.type == "charge"}
        
        for txn in transactions:
            if txn.type == "refund" and txn.metadata.get("original_charge"):
                original_id = txn.metadata["original_charge"]
                if original_id in charges_dict:
                    original = charges_dict[original_id]
                    time_diff = abs(txn.created - original.created)
                    if time_diff < 3600:  # Less than 1 hour
                        failure_indicators["rapid_refunds"] += 1
            
            # Check for unusual patterns in descriptions
            if txn.description:
                suspicious_keywords = ["fraud", "dispute", "unauthorized", "stolen", "error"]
                if any(keyword in txn.description.lower() for keyword in suspicious_keywords):
                    failure_indicators["unusual_descriptions"].append(txn.description)
        
        return failure_indicators
    
    def _analyze_transaction_velocity(self, transactions: List[StripeTransaction]) -> Dict[str, Any]:
        """
        Analyze transaction velocity for suspicious patterns
        """
        
        if not transactions:
            return {}
        
        # Sort by timestamp
        sorted_txns = sorted(transactions, key=lambda t: t.created)
        
        # Calculate intervals between transactions
        intervals = []
        for i in range(1, len(sorted_txns)):
            interval = sorted_txns[i].created - sorted_txns[i-1].created
            intervals.append(interval)
        
        if not intervals:
            return {}
        
        # Detect rapid-fire patterns
        rapid_intervals = [i for i in intervals if i < 60]  # Less than 1 minute apart
        
        return {
            "avg_interval_seconds": statistics.mean(intervals),
            "min_interval_seconds": min(intervals),
            "rapid_transactions": len(rapid_intervals),
            "velocity_score": len(rapid_intervals) / len(intervals) if intervals else 0,
            "suspicious_velocity": len(rapid_intervals) > len(intervals) * 0.3  # >30% rapid
        }
    
    async def _detect_risk_patterns(
        self,
        transactions: List[StripeTransaction],
        stats: Dict[str, Any]
    ) -> List[RiskPattern]:
        """
        Detect specific risk patterns using both statistical and GPT-5 analysis
        """
        
        detected_patterns = []
        
        # Pattern 1: High refund rate
        refund_rate = stats["risk_rates"]["refund_rate"]
        if refund_rate > self.FREEZE_THRESHOLDS["refund_rate_investigation"]:
            severity = RiskTier.CRITICAL if refund_rate > self.FREEZE_THRESHOLDS["refund_rate_freeze"] else RiskTier.HIGH
            
            pattern = RiskPattern(
                pattern_type="high_refund_rate",
                severity=severity,
                description=f"Refund rate of {refund_rate:.1%} exceeds threshold",
                confidence=0.95,
                triggers=[f"Refund rate: {refund_rate:.1%}", "Customer dissatisfaction indicators"],
                freeze_probability=min(1.0, refund_rate / self.FREEZE_THRESHOLDS["refund_rate_freeze"]),
                timeline_estimate="24-72 hours",
                gpt5_reasoning=""
            )
            detected_patterns.append(pattern)
        
        # Pattern 2: High chargeback rate
        chargeback_rate = stats["risk_rates"]["chargeback_rate"]  
        if chargeback_rate > self.FREEZE_THRESHOLDS["chargeback_rate_freeze"]:
            pattern = RiskPattern(
                pattern_type="chargeback_surge",
                severity=RiskTier.CRITICAL,
                description=f"Chargeback rate of {chargeback_rate:.1%} exceeds 1% freeze threshold",
                confidence=0.98,
                triggers=[f"Chargeback rate: {chargeback_rate:.1%}", "Immediate freeze risk"],
                freeze_probability=min(1.0, chargeback_rate / self.FREEZE_THRESHOLDS["chargeback_rate_freeze"]),
                timeline_estimate="Immediate to 24 hours",
                gpt5_reasoning=""
            )
            detected_patterns.append(pattern)
        
        # Pattern 3: Volume spike
        if "temporal_analysis" in stats:
            tph = stats["temporal_analysis"]["transactions_per_hour"]
            if tph > 50:  # Arbitrary threshold for demo
                severity = RiskTier.CRITICAL if tph > 100 else RiskTier.HIGH
                
                pattern = RiskPattern(
                    pattern_type="volume_spike",
                    severity=severity,
                    description=f"Transaction velocity of {tph:.1f} per hour is unusually high",
                    confidence=0.85,
                    triggers=[f"Velocity: {tph:.1f} txns/hour", "Potential promotional abuse"],
                    freeze_probability=min(1.0, tph / 200),  # Arbitrary scaling
                    timeline_estimate="24-48 hours",
                    gpt5_reasoning=""
                )
                detected_patterns.append(pattern)
        
        # Pattern 4: Amount deviation
        if stats["pattern_flags"]["amount_anomalies"]:
            pattern = RiskPattern(
                pattern_type="amount_deviation",
                severity=RiskTier.MODERATE,
                description="Transaction amounts show unusual deviation from normal patterns",
                confidence=0.7,
                triggers=["High amount variance", "Business model change indicators"],
                freeze_probability=0.3,
                timeline_estimate="7-14 days",
                gpt5_reasoning=""
            )
            detected_patterns.append(pattern)
        
        # Pattern 5: Rapid refunds
        rapid_refunds = stats["risk_rates"]["failure_indicators"]["rapid_refunds"]
        if rapid_refunds > 5:
            pattern = RiskPattern(
                pattern_type="rapid_refunds",
                severity=RiskTier.HIGH,
                description=f"{rapid_refunds} refunds issued within 1 hour of original charge",
                confidence=0.88,
                triggers=["Rapid refund pattern", "Potential fraud or system issues"],
                freeze_probability=0.6,
                timeline_estimate="48-72 hours",
                gpt5_reasoning=""
            )
            detected_patterns.append(pattern)
        
        # Use GPT-5 to enhance pattern analysis
        for pattern in detected_patterns:
            pattern.gpt5_reasoning = await self._enhance_pattern_with_gpt5(pattern, stats)
        
        return detected_patterns
    
    async def _enhance_pattern_with_gpt5(
        self,
        pattern: RiskPattern,
        stats: Dict[str, Any]
    ) -> str:
        """
        Use GPT-5 to provide detailed reasoning for detected patterns
        """
        
        try:
            context = {
                "pattern": asdict(pattern),
                "statistics": stats,
                "thresholds": self.FREEZE_THRESHOLDS
            }
            
            # Use GPT-5 with high reasoning effort for pattern analysis
            analysis = await self.gpt5_client.analyze_transaction_risk(
                transactions=[],  # Summary analysis, not individual transactions
                context=context,
                reasoning_effort="high",
                verbosity="high"
            )
            
            return analysis.get("risk_analysis", "GPT-5 analysis not available")
            
        except Exception as e:
            return f"Pattern analysis: {pattern.description} (GPT-5 error: {str(e)})"
    
    async def _perform_gpt5_analysis(
        self,
        transactions: List[StripeTransaction],
        stats: Dict[str, Any],
        patterns: List[RiskPattern],
        reasoning_effort: str = "high"
    ) -> Dict[str, Any]:
        """
        Comprehensive GPT-5 analysis of the entire dataset
        """
        
        # Prepare data summary for GPT-5
        analysis_context = {
            "transaction_count": len(transactions),
            "statistics_summary": {
                "total_volume": stats.get("amount_analysis", {}).get("total_volume", 0),
                "refund_rate": stats.get("risk_rates", {}).get("refund_rate", 0),
                "chargeback_rate": stats.get("risk_rates", {}).get("chargeback_rate", 0),
                "velocity": stats.get("temporal_analysis", {}).get("transactions_per_hour", 0)
            },
            "detected_patterns": [p.pattern_type for p in patterns],
            "risk_flags": stats.get("pattern_flags", {}),
            "business_context": "B2B payment orchestration platform"
        }
        
        try:
            # Use GPT-5 for comprehensive analysis
            gpt5_analysis = await self.gpt5_client.analyze_transaction_risk(
                transactions=[asdict(t) for t in transactions[:5]],  # Sample for context
                context=analysis_context,
                reasoning_effort=reasoning_effort,
                verbosity="high"
            )
            
            return {
                "gpt5_risk_assessment": gpt5_analysis,
                "confidence": "high" if reasoning_effort == "high" else "medium",
                "analysis_parameters": {
                    "reasoning_effort": reasoning_effort,
                    "sample_size": min(5, len(transactions)),
                    "full_dataset_size": len(transactions)
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "fallback_analysis": "Statistical analysis indicates elevated risk patterns",
                "confidence": "low"
            }
    
    def _calculate_overall_risk(
        self,
        patterns: List[RiskPattern],
        stats: Dict[str, Any]
    ) -> Tuple[RiskTier, float]:
        """
        Calculate overall risk tier and freeze probability
        """
        
        if not patterns:
            return RiskTier.MINIMAL, 0.0
        
        # Weight patterns by severity
        severity_weights = {
            RiskTier.MINIMAL: 0.1,
            RiskTier.LOW: 0.2,
            RiskTier.MODERATE: 0.4,
            RiskTier.HIGH: 0.7,
            RiskTier.CRITICAL: 1.0
        }
        
        # Calculate weighted risk score
        total_weight = 0
        weighted_score = 0
        freeze_probs = []
        
        for pattern in patterns:
            weight = severity_weights[pattern.severity]
            weighted_score += weight * pattern.confidence
            total_weight += weight
            freeze_probs.append(pattern.freeze_probability)
        
        avg_risk_score = weighted_score / total_weight if total_weight > 0 else 0
        max_freeze_prob = max(freeze_probs) if freeze_probs else 0
        
        # Determine overall risk tier
        if avg_risk_score >= 0.8:
            overall_risk = RiskTier.CRITICAL
        elif avg_risk_score >= 0.6:
            overall_risk = RiskTier.HIGH
        elif avg_risk_score >= 0.4:
            overall_risk = RiskTier.MODERATE
        elif avg_risk_score >= 0.2:
            overall_risk = RiskTier.LOW
        else:
            overall_risk = RiskTier.MINIMAL
        
        return overall_risk, max_freeze_prob
    
    async def _generate_recommendations(
        self,
        patterns: List[RiskPattern],
        gpt5_analysis: Dict[str, Any]
    ) -> List[str]:
        """
        Generate actionable recommendations based on detected patterns
        """
        
        recommendations = []
        
        # Pattern-specific recommendations
        for pattern in patterns:
            if pattern.pattern_type == "high_refund_rate":
                recommendations.extend([
                    "Immediately review customer satisfaction and product quality",
                    "Implement proactive customer communication before charges",
                    "Consider offering trial periods or money-back guarantees",
                    "Prepare detailed documentation for Stripe review"
                ])
            elif pattern.pattern_type == "chargeback_surge":
                recommendations.extend([
                    "URGENT: Contact Stripe immediately - account freeze imminent",
                    "Prepare 180-day cash flow contingency plan", 
                    "Implement stronger fraud detection and 3DS authentication",
                    "Review and improve dispute resolution process"
                ])
            elif pattern.pattern_type == "volume_spike":
                recommendations.extend([
                    "Document business justification for volume increase",
                    "Prepare promotional/marketing evidence for Stripe",
                    "Consider contacting Stripe proactively to explain activity",
                    "Monitor for fraud indicators in spike transactions"
                ])
        
        # General risk mitigation
        if patterns:
            recommendations.extend([
                "Set up real-time transaction monitoring alerts",
                "Establish backup payment processor relationships",
                "Create comprehensive risk management documentation",
                "Consider professional payment consulting services"
            ])
        
        # GPT-5 enhanced recommendations
        if gpt5_analysis.get("gpt5_risk_assessment", {}).get("recommendations"):
            gpt5_recs = gpt5_analysis["gpt5_risk_assessment"]["recommendations"]
            if isinstance(gpt5_recs, list):
                recommendations.extend(gpt5_recs)
        
        return list(set(recommendations))  # Remove duplicates
    
    def export_risk_report(self, analysis: RiskAnalysis, filename: str):
        """
        Export comprehensive risk analysis report
        """
        
        report = {
            "risk_analysis": {
                "overall_risk": analysis.overall_risk.value,
                "freeze_probability": analysis.freeze_probability,
                "analysis_timestamp": analysis.analysis_timestamp.isoformat(),
                "data_summary": analysis.data_summary
            },
            "identified_patterns": [asdict(p) for p in analysis.identified_patterns],
            "recommendations": analysis.recommendations,
            "gpt5_insights": analysis.gpt5_insights
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Risk analysis report exported to {filename}")
    
    def print_risk_summary(self, analysis: RiskAnalysis):
        """
        Print a formatted risk analysis summary
        """
        
        print("\n" + "="*60)
        print("GPT-5 POWERED RISK ANALYSIS REPORT")
        print("="*60)
        
        print(f"\nOVERALL RISK LEVEL: {analysis.overall_risk.value.upper()}")
        print(f"FREEZE PROBABILITY: {analysis.freeze_probability:.1%}")
        print(f"ANALYSIS TIMESTAMP: {analysis.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        if analysis.identified_patterns:
            print(f"\nIDENTIFIED RISK PATTERNS ({len(analysis.identified_patterns)}):")
            print("-" * 40)
            
            for pattern in analysis.identified_patterns:
                print(f"\n{pattern.pattern_type.upper()} [{pattern.severity.value.upper()}]")
                print(f"  Description: {pattern.description}")
                print(f"  Confidence: {pattern.confidence:.1%}")
                print(f"  Freeze Risk: {pattern.freeze_probability:.1%}")
                print(f"  Timeline: {pattern.timeline_estimate}")
                
                if pattern.triggers:
                    print(f"  Triggers: {', '.join(pattern.triggers)}")
        
        if analysis.recommendations:
            print(f"\nRECOMMENDATIONS ({len(analysis.recommendations)}):")
            print("-" * 30)
            for i, rec in enumerate(analysis.recommendations, 1):
                print(f"{i:2d}. {rec}")
        
        # GPT-5 insights summary
        if analysis.gpt5_insights.get("confidence"):
            print(f"\nGPT-5 ANALYSIS CONFIDENCE: {analysis.gpt5_insights['confidence'].upper()}")
        
        print("\n" + "="*60)


async def main():
    """
    Demo the GPT-5 risk analysis system
    """
    
    # Import the data generator to create test data
    from gpt5_stripe_data_generator import GPT5StripeDataGenerator
    
    print("GPT-5 Risk Pattern Analysis Demo")
    print("="*50)
    
    # Generate test datasets
    generator = GPT5StripeDataGenerator()
    analyzer = ClaudeRiskAnalyzer()
    
    scenarios = [
        "high_refund_rate",
        "chargeback_surge", 
        "sudden_spike"
    ]
    
    for scenario in scenarios:
        print(f"\nAnalyzing {scenario} scenario...")
        print("-" * 30)
        
        # Generate test data
        dataset = await generator.generate_intelligent_dataset(
            scenario=scenario,
            duration_days=7,
            base_volume=100
        )
        
        # Perform risk analysis
        analysis = await analyzer.analyze_transactions(
            transactions=dataset["transactions"],
            reasoning_effort="high"
        )
        
        # Display results
        analyzer.print_risk_summary(analysis)
        
        # Export detailed report
        filename = f"risk_analysis_{scenario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        analyzer.export_risk_report(analysis, filename)


if __name__ == "__main__":
    asyncio.run(main())