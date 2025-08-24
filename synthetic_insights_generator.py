"""
Comprehensive Synthetic Data Generator for Payment Orchestration
Generates realistic transaction data, risk profiles, and insights to replace hardcoded values
"""

import random
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

from processors.base import PaymentRequest, PaymentStatus
from brave_search_insights import (
    SearchInsight, PromotionInsight, RegulatoryInsight, MarketSentimentInsight,
    FraudTrendInsight, ServiceStatusInsight, SocialSentimentInsight,
    CompetitiveAnalysisInsight, NewsImpactInsight, MerchantFeedbackInsight,
    PerformanceBenchmarkInsight, InsightType
)


class BusinessType(Enum):
    STARTUP = "startup"
    SMALL_BUSINESS = "small_business"
    ENTERPRISE = "enterprise"
    ECOMMERCE = "ecommerce"
    SAAS = "saas"
    MARKETPLACE = "marketplace"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SyntheticProcessorProfile:
    """Complete processor profile with realistic characteristics"""
    id: str
    name: str
    base_fee_percentage: float
    success_rate: float
    avg_response_time: int
    supported_regions: List[str]
    supported_currencies: List[str]
    features: List[str]
    reputation_score: float
    market_share: float
    founded_year: int
    current_status: str = "operational"


@dataclass
class SyntheticTransaction:
    """Realistic transaction with all necessary fields"""
    request_id: str
    amount: float
    currency: str
    merchant_id: str
    customer_id: str
    timestamp: datetime
    payment_method: str
    risk_score: float
    fraud_indicators: List[str]
    geographic_region: str
    business_type: str
    metadata: Dict[str, Any]


@dataclass
class SyntheticRiskProfile:
    """Comprehensive risk assessment profile"""
    overall_risk: RiskLevel
    fraud_probability: float
    chargeback_risk: float
    regulatory_risk: float
    merchant_reputation: float
    transaction_pattern_risk: float
    geographic_risk: float
    risk_factors: List[str]


class SyntheticDataGenerator:
    """
    Generates realistic synthetic data for payment orchestration testing
    """
    
    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)
            np.random.seed(seed)
        
        self.processors = self._generate_processor_profiles()
        self.merchant_profiles = self._generate_merchant_profiles()
        
    def _generate_processor_profiles(self) -> List[SyntheticProcessorProfile]:
        """Generate realistic processor profiles"""
        return [
            SyntheticProcessorProfile(
                id="stripe",
                name="Stripe",
                base_fee_percentage=2.9,
                success_rate=0.959,
                avg_response_time=180,
                supported_regions=["US", "EU", "APAC", "LATAM"],
                supported_currencies=["USD", "EUR", "GBP", "JPY", "CAD"],
                features=["recurring_payments", "marketplace", "connect", "radar"],
                reputation_score=9.2,
                market_share=0.28,
                founded_year=2010
            ),
            SyntheticProcessorProfile(
                id="paypal",
                name="PayPal",
                base_fee_percentage=3.49,
                success_rate=0.934,
                avg_response_time=220,
                supported_regions=["US", "EU", "APAC", "LATAM", "MEA"],
                supported_currencies=["USD", "EUR", "GBP", "JPY", "CAD", "AUD"],
                features=["express_checkout", "recurring", "invoicing", "dispute_resolution"],
                reputation_score=8.7,
                market_share=0.21,
                founded_year=1998
            ),
            SyntheticProcessorProfile(
                id="visa",
                name="Visa Direct",
                base_fee_percentage=2.5,
                success_rate=0.972,
                avg_response_time=150,
                supported_regions=["US", "EU", "APAC"],
                supported_currencies=["USD", "EUR", "GBP"],
                features=["push_payments", "real_time", "bank_transfer", "fraud_protection"],
                reputation_score=9.5,
                market_share=0.31,
                founded_year=1958
            ),
            SyntheticProcessorProfile(
                id="adyen",
                name="Adyen",
                base_fee_percentage=2.95,
                success_rate=0.945,
                avg_response_time=190,
                supported_regions=["EU", "US", "APAC"],
                supported_currencies=["USD", "EUR", "GBP", "JPY"],
                features=["unified_commerce", "risk_management", "data_insights", "omnichannel"],
                reputation_score=8.9,
                market_share=0.12,
                founded_year=2006
            ),
            SyntheticProcessorProfile(
                id="square",
                name="Square",
                base_fee_percentage=2.75,
                success_rate=0.941,
                avg_response_time=200,
                supported_regions=["US", "CA", "AU", "JP"],
                supported_currencies=["USD", "CAD", "AUD", "JPY"],
                features=["pos_integration", "small_business", "invoicing", "analytics"],
                reputation_score=8.4,
                market_share=0.08,
                founded_year=2009
            )
        ]
    
    def _generate_merchant_profiles(self) -> Dict[str, Dict]:
        """Generate merchant profile templates"""
        return {
            "startup_tech": {
                "business_type": BusinessType.STARTUP.value,
                "avg_transaction": 150.0,
                "volume_per_month": 50000,
                "risk_tolerance": "medium",
                "preferred_processors": ["stripe", "square"],
                "geographic_focus": ["US"],
                "growth_rate": 0.25
            },
            "enterprise_retail": {
                "business_type": BusinessType.ENTERPRISE.value,
                "avg_transaction": 750.0,
                "volume_per_month": 2000000,
                "risk_tolerance": "low",
                "preferred_processors": ["visa", "adyen"],
                "geographic_focus": ["US", "EU", "APAC"],
                "growth_rate": 0.08
            },
            "ecommerce_medium": {
                "business_type": BusinessType.ECOMMERCE.value,
                "avg_transaction": 85.0,
                "volume_per_month": 500000,
                "risk_tolerance": "medium",
                "preferred_processors": ["paypal", "stripe"],
                "geographic_focus": ["US", "EU"],
                "growth_rate": 0.15
            },
            "saas_b2b": {
                "business_type": BusinessType.SAAS.value,
                "avg_transaction": 299.0,
                "volume_per_month": 300000,
                "risk_tolerance": "low",
                "preferred_processors": ["stripe", "adyen"],
                "geographic_focus": ["US", "EU"],
                "growth_rate": 0.20
            }
        }
    
    def generate_transactions(
        self,
        count: int = 100,
        business_type: Optional[str] = None,
        risk_distribution: Dict[str, float] = None,
        time_range_hours: int = 24
    ) -> List[SyntheticTransaction]:
        """Generate realistic transaction batches"""
        
        if risk_distribution is None:
            risk_distribution = {"low": 0.7, "medium": 0.25, "high": 0.04, "critical": 0.01}
        
        transactions = []
        base_time = datetime.utcnow() - timedelta(hours=time_range_hours)
        
        # Select merchant profile
        if business_type and business_type in self.merchant_profiles:
            merchant_profile = self.merchant_profiles[business_type]
        else:
            merchant_profile = random.choice(list(self.merchant_profiles.values()))
        
        for i in range(count):
            # Generate transaction timing (more during business hours)
            hour_offset = self._generate_realistic_timing(time_range_hours)
            timestamp = base_time + timedelta(hours=hour_offset)
            
            # Generate amount based on merchant profile with realistic distribution
            base_amount = merchant_profile["avg_transaction"]
            amount = max(1.0, np.random.lognormal(np.log(base_amount), 0.8))
            
            # Determine risk level based on distribution
            risk_level = np.random.choice(
                list(risk_distribution.keys()),
                p=list(risk_distribution.values())
            )
            
            # Generate risk score and indicators
            risk_score, fraud_indicators = self._generate_risk_profile(risk_level, amount)
            
            transaction = SyntheticTransaction(
                request_id=f"req_{uuid.uuid4().hex[:12]}",
                amount=round(amount, 2),
                currency=random.choice(["USD", "EUR", "GBP"]),
                merchant_id=f"merchant_{hash(business_type or 'default') % 10000}",
                customer_id=f"customer_{uuid.uuid4().hex[:8]}",
                timestamp=timestamp,
                payment_method=random.choice(["card", "bank_transfer", "digital_wallet", "ach"]),
                risk_score=risk_score,
                fraud_indicators=fraud_indicators,
                geographic_region=random.choice(merchant_profile["geographic_focus"]),
                business_type=merchant_profile["business_type"],
                metadata={
                    "customer_age_days": random.randint(1, 2000),
                    "repeat_customer": random.random() < 0.4,
                    "device_fingerprint": f"device_{uuid.uuid4().hex[:8]}",
                    "ip_reputation": random.uniform(0.1, 1.0),
                    "checkout_time_seconds": random.randint(10, 300)
                }
            )
            transactions.append(transaction)
        
        return transactions
    
    def _generate_realistic_timing(self, time_range_hours: int) -> float:
        """Generate realistic transaction timing (more during business hours)"""
        # Weight towards business hours (9 AM - 6 PM)
        weights = []
        for hour in range(24):
            if 9 <= hour <= 18:
                weights.append(3.0)  # 3x more likely during business hours
            elif 6 <= hour <= 22:
                weights.append(1.5)  # Moderate activity
            else:
                weights.append(0.5)  # Low activity at night
        
        # Normalize weights
        weights = np.array(weights) / sum(weights)
        
        # Sample hour and add minutes
        hour = np.random.choice(24, p=weights)
        minutes = random.uniform(0, 60)
        
        return (hour * time_range_hours / 24) + (minutes / 60)
    
    def _generate_risk_profile(self, risk_level: str, amount: float) -> Tuple[float, List[str]]:
        """Generate risk score and fraud indicators"""
        
        fraud_indicators = []
        
        if risk_level == "low":
            risk_score = random.uniform(0.05, 0.25)
            if random.random() < 0.1:
                fraud_indicators.append("repeat_customer")
        
        elif risk_level == "medium":
            risk_score = random.uniform(0.25, 0.65)
            if random.random() < 0.3:
                fraud_indicators.extend(["new_customer", "high_amount"])
        
        elif risk_level == "high":
            risk_score = random.uniform(0.65, 0.85)
            fraud_indicators.extend(["velocity_check", "geographic_mismatch"])
            if amount > 1000:
                fraud_indicators.append("large_transaction")
        
        else:  # critical
            risk_score = random.uniform(0.85, 0.98)
            fraud_indicators.extend([
                "multiple_failed_attempts",
                "suspicious_device",
                "blacklist_match"
            ])
            if amount > 5000:
                fraud_indicators.append("unusually_large")
        
        return risk_score, fraud_indicators
    
    def generate_synthetic_insights(
        self,
        processors: List[str],
        insight_count_per_type: int = 3
    ) -> Dict[str, Dict[str, List[SearchInsight]]]:
        """Generate realistic synthetic insights for testing"""
        
        synthetic_insights = {}
        
        for processor_id in processors:
            processor_insights = {
                "promotions": self._generate_promotion_insights(processor_id, insight_count_per_type),
                "regulations": self._generate_regulatory_insights(processor_id, insight_count_per_type),
                "market_sentiment": self._generate_market_sentiment_insights(processor_id, insight_count_per_type),
                "fraud_trends": self._generate_fraud_trend_insights(processor_id, insight_count_per_type),
                "service_status": self._generate_service_status_insights(processor_id, insight_count_per_type),
                "social_sentiment": self._generate_social_sentiment_insights(processor_id, insight_count_per_type),
                "competitive_analysis": self._generate_competitive_insights(processor_id, insight_count_per_type),
                "news_impact": self._generate_news_impact_insights(processor_id, insight_count_per_type),
                "merchant_feedback": self._generate_merchant_feedback_insights(processor_id, insight_count_per_type),
                "performance_benchmarking": self._generate_performance_benchmark_insights(processor_id, insight_count_per_type)
            }
            synthetic_insights[processor_id] = processor_insights
        
        return synthetic_insights
    
    def _generate_promotion_insights(self, processor_id: str, count: int) -> List[PromotionInsight]:
        """Generate synthetic promotion insights"""
        insights = []
        
        promotion_templates = [
            ("Q4 Business Promotion", "Special rates for business accounts", 0.5, 90),
            ("New Merchant Discount", "First 6 months reduced fees", 0.8, 180),
            ("Volume Discount", "Reduced rates for high-volume merchants", 0.3, 365),
            ("Startup Special", "Special pricing for startups", 1.0, 60),
            ("Holiday Processing Rates", "Reduced fees during peak season", 0.4, 30)
        ]
        
        for i in range(min(count, len(promotion_templates))):
            template = promotion_templates[i]
            
            insight = PromotionInsight(
                insight_type=InsightType.PROMOTIONS,
                processor_id=processor_id,
                title=f"{processor_id.title()} {template[0]}",
                content=template[1],
                source_url=f"https://{processor_id}.com/promotions/{i}",
                confidence_score=random.uniform(0.7, 0.95),
                timestamp=datetime.utcnow(),
                discount_percentage=template[2],
                valid_until=datetime.utcnow() + timedelta(days=template[3]),
                minimum_transaction=random.choice([None, 100.0, 500.0, 1000.0]),
                impact_score=template[2] / 100 * 2
            )
            insights.append(insight)
        
        return insights
    
    def _generate_fraud_trend_insights(self, processor_id: str, count: int) -> List[FraudTrendInsight]:
        """Generate synthetic fraud trend insights"""
        insights = []
        
        fraud_scenarios = [
            ("account_takeover", "high", "increasing", ["US", "EU"], ["2fa_required"]),
            ("synthetic_identity", "medium", "stable", ["US"], ["enhanced_verification"]),
            ("card_testing", "low", "decreasing", ["global"], ["velocity_limits"]),
            ("social_engineering", "high", "increasing", ["US", "APAC"], ["user_education"])
        ]
        
        for i, scenario in enumerate(fraud_scenarios[:count]):
            insight = FraudTrendInsight(
                insight_type=InsightType.FRAUD_TRENDS,
                processor_id=processor_id,
                title=f"{processor_id.title()} {scenario[0].replace('_', ' ').title()} Alert",
                content=f"Recent trends in {scenario[0]} affecting {processor_id} merchants",
                source_url=f"https://security.{processor_id}.com/alerts/{i}",
                confidence_score=random.uniform(0.8, 0.95),
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 7)),
                fraud_type=scenario[0],
                risk_level=scenario[1],
                trend_direction=scenario[2],
                affected_regions=scenario[3],
                mitigation_measures=scenario[4],
                impact_score={"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 0.95}[scenario[1]]
            )
            insights.append(insight)
        
        return insights
    
    def _generate_service_status_insights(self, processor_id: str, count: int) -> List[ServiceStatusInsight]:
        """Generate synthetic service status insights"""
        insights = []
        
        status_scenarios = [
            ("operational", 99.9, 0, ["api", "dashboard"]),
            ("degraded", 95.2, 45, ["payment_processing"]),
            ("maintenance", 100.0, 120, ["reporting"]),
        ]
        
        for i, scenario in enumerate(status_scenarios[:count]):
            insight = ServiceStatusInsight(
                insight_type=InsightType.SERVICE_STATUS,
                processor_id=processor_id,
                title=f"{processor_id.title()} Service Status: {scenario[0].title()}",
                content=f"Current service status for {processor_id} showing {scenario[0]} conditions",
                source_url=f"https://status.{processor_id}.com",
                confidence_score=0.95,
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(5, 180)),
                service_status=scenario[0],
                uptime_percentage=scenario[1],
                incident_duration_minutes=scenario[2],
                affected_services=scenario[3],
                impact_score={"operational": 1.0, "degraded": 0.6, "maintenance": 0.8, "outage": 0.0}[scenario[0]]
            )
            insights.append(insight)
        
        return insights
    
    def _generate_social_sentiment_insights(self, processor_id: str, count: int) -> List[SocialSentimentInsight]:
        """Generate synthetic social sentiment insights"""
        insights = []
        platforms = ["Twitter", "Reddit", "LinkedIn", "Facebook"]
        
        for i, platform in enumerate(platforms[:count]):
            sentiment_score = random.uniform(-0.3, 0.8) if processor_id != "stripe" else random.uniform(0.4, 0.9)
            
            insight = SocialSentimentInsight(
                insight_type=InsightType.SOCIAL_SENTIMENT,
                processor_id=processor_id,
                title=f"{processor_id.title()} {platform} Sentiment Analysis",
                content=f"Community sentiment analysis from {platform} discussions",
                source_url=f"https://sentiment-analysis.com/{processor_id}/{platform.lower()}",
                confidence_score=random.uniform(0.6, 0.85),
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
                platform=platform,
                sentiment_score=sentiment_score,
                mention_count=random.randint(50, 500),
                positive_mentions=int(random.randint(50, 500) * max(0, sentiment_score + 1) / 2),
                negative_mentions=int(random.randint(50, 500) * max(0, 1 - sentiment_score) / 2),
                trending_topics=random.sample(["pricing", "reliability", "support", "features", "outages"], 2)
            )
            insights.append(insight)
        
        return insights
    
    def _generate_competitive_insights(self, processor_id: str, count: int) -> List[CompetitiveAnalysisInsight]:
        """Generate synthetic competitive analysis insights with numerical rankings"""
        insights = []
        all_processors = [p.id for p in self.processors]
        competitors = [p for p in all_processors if p != processor_id]
        
        # Define ranking system based on realistic market data
        market_rankings = {
            "visa": 1,      # Market leader
            "stripe": 2,    # Strong challenger  
            "paypal": 3,    # Established player
            "adyen": 4,     # Growing competitor
            "square": 5     # Niche player
        }
        
        for i in range(count):
            compared_processors = random.sample(competitors, min(2, len(competitors)))
            
            # Generate competitive advantage based on actual market knowledge
            advantages = {
                "visa": "Global acceptance and established trust network",
                "stripe": "Developer-friendly API and innovative features", 
                "paypal": "Consumer trust and ease of use",
                "adyen": "Unified payment solutions and global reach",
                "square": "Integrated POS and small business focus"
            }
            
            ranking = market_rankings.get(processor_id, random.randint(3, 5))
            
            insight = CompetitiveAnalysisInsight(
                insight_type=InsightType.COMPETITIVE_ANALYSIS,
                processor_id=processor_id,
                title=f"{processor_id.title()} Market Position - Rank #{ranking}",
                content=f"Market ranking analysis: #{ranking} position with key competitive advantages",
                source_url=f"https://market-research.com/payment-processors/{processor_id}",
                confidence_score=random.uniform(0.7, 0.9),
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                compared_processors=compared_processors,
                competitive_advantage=advantages.get(processor_id, "Specialized market positioning"),
                market_position=str(ranking),  # Now uses numerical ranking
                pricing_comparison={comp: random.uniform(2.0, 4.0) for comp in compared_processors},
                feature_comparison={
                    "international": processor_id in ["visa", "stripe", "adyen"],
                    "subscriptions": processor_id in ["stripe", "adyen"],
                    "marketplace": processor_id in ["stripe", "paypal", "adyen"]
                }
            )
            insights.append(insight)
        
        return insights
    
    def _generate_news_impact_insights(self, processor_id: str, count: int) -> List[NewsImpactInsight]:
        """Generate synthetic news impact insights"""
        insights = []
        news_types = [
            ("financial", "medium", 0.1, ["fintech", "payments"]),
            ("regulatory", "high", -0.2, ["compliance", "banking"]),
            ("security", "high", -0.4, ["cybersecurity", "fraud"]),
            ("business", "low", 0.3, ["growth", "partnerships"])
        ]
        
        for i, news_type in enumerate(news_types[:count]):
            insight = NewsImpactInsight(
                insight_type=InsightType.NEWS_IMPACT,
                processor_id=processor_id,
                title=f"{processor_id.title()} {news_type[0].title()} News Impact",
                content=f"Recent {news_type[0]} news affecting {processor_id} market position",
                source_url=f"https://finance-news.com/{processor_id}/{i}",
                confidence_score=random.uniform(0.6, 0.85),
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 7)),
                news_category=news_type[0],
                impact_level=news_type[1],
                market_impact=news_type[2],
                affected_sectors=news_type[3],
                publication_source=random.choice(["TechCrunch", "Reuters", "WSJ", "Bloomberg"])
            )
            insights.append(insight)
        
        return insights
    
    def _generate_merchant_feedback_insights(self, processor_id: str, count: int) -> List[MerchantFeedbackInsight]:
        """Generate synthetic merchant feedback insights"""
        insights = []
        feedback_sources = ["reddit", "merchant_forum", "trustpilot", "g2_reviews"]
        
        for i, source in enumerate(feedback_sources[:count]):
            satisfaction_score = random.uniform(3.2, 4.8) if processor_id in ["stripe", "visa"] else random.uniform(2.8, 4.2)
            
            insight = MerchantFeedbackInsight(
                insight_type=InsightType.MERCHANT_FEEDBACK,
                processor_id=processor_id,
                title=f"{processor_id.title()} Merchant Reviews - {source.title()}",
                content=f"Merchant feedback analysis from {source}",
                source_url=f"https://{source}.com/{processor_id}/reviews",
                confidence_score=random.uniform(0.7, 0.9),
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 14)),
                feedback_source=source,
                satisfaction_score=satisfaction_score,
                common_issues=random.sample(["fees", "support", "documentation", "integration"], 2),
                recommended_alternatives=random.sample([p for p in ["stripe", "paypal", "visa"] if p != processor_id], 1),
                merchant_segment=random.choice(["small_business", "enterprise", "startup"])
            )
            insights.append(insight)
        
        return insights
    
    def _generate_performance_benchmark_insights(self, processor_id: str, count: int) -> List[PerformanceBenchmarkInsight]:
        """Generate synthetic performance benchmark insights"""
        insights = []
        benchmark_types = ["speed", "reliability", "cost", "features"]
        
        for i, bench_type in enumerate(benchmark_types[:count]):
            # Generate realistic scores based on processor
            if processor_id == "visa":
                benchmark_score = random.uniform(8.5, 9.5)
                percentile_rank = random.uniform(85, 95)
            elif processor_id == "stripe":
                benchmark_score = random.uniform(8.0, 9.2)
                percentile_rank = random.uniform(80, 92)
            else:
                benchmark_score = random.uniform(7.0, 8.5)
                percentile_rank = random.uniform(65, 85)
            
            insight = PerformanceBenchmarkInsight(
                insight_type=InsightType.PERFORMANCE_BENCHMARKING,
                processor_id=processor_id,
                title=f"{processor_id.title()} {bench_type.title()} Benchmark Report",
                content=f"Performance benchmark analysis for {bench_type} metrics",
                source_url=f"https://payment-benchmarks.com/{processor_id}/{bench_type}",
                confidence_score=random.uniform(0.8, 0.95),
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                benchmark_type=bench_type,
                benchmark_score=benchmark_score,
                industry_average=7.5,
                percentile_rank=percentile_rank,
                comparison_processors=random.sample([p.id for p in self.processors if p.id != processor_id], 2),
                data_source="Industry Benchmark Report 2024"
            )
            insights.append(insight)
        
        return insights
    
    def _generate_regulatory_insights(self, processor_id: str, count: int) -> List[RegulatoryInsight]:
        """Generate synthetic regulatory insights"""
        insights = []
        
        reg_types = ["PCI DSS", "GDPR", "AML", "KYC"]
        for i, reg_type in enumerate(reg_types[:count]):
            insight = RegulatoryInsight(
                insight_type=InsightType.REGULATIONS,
                processor_id="all",
                title=f"New {reg_type} Requirements 2024",
                content=f"Updated {reg_type} compliance requirements affecting payment processors",
                source_url=f"https://compliance.gov/{reg_type.lower()}/updates",
                confidence_score=random.uniform(0.85, 0.95),
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                regulation_type=reg_type,
                region="US",
                compliance_requirement=f"Enhanced {reg_type} compliance measures",
                effective_date=datetime.utcnow() + timedelta(days=random.randint(30, 180)),
                impact_score=0.7 if reg_type != "general" else 0.4
            )
            insights.append(insight)
        
        return insights
    
    def _generate_market_sentiment_insights(self, processor_id: str, count: int) -> List[MarketSentimentInsight]:
        """Generate synthetic market sentiment insights"""
        insights = []
        
        for i in range(count):
            sentiment_score = random.uniform(-0.2, 0.8)
            reliability_rating = random.uniform(3.5, 4.8)
            
            insight = MarketSentimentInsight(
                insight_type=InsightType.MARKET_SENTIMENT,
                processor_id=processor_id,
                title=f"{processor_id.title()} Market Sentiment Analysis",
                content=f"Overall market sentiment analysis for {processor_id}",
                source_url=f"https://market-sentiment.com/{processor_id}",
                confidence_score=random.uniform(0.7, 0.9),
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
                sentiment_score=sentiment_score,
                review_count=random.randint(100, 1000),
                reliability_rating=reliability_rating,
                impact_score=abs(sentiment_score) * 0.6
            )
            insights.append(insight)
        
        return insights
    
    def generate_processor_scenarios(
        self,
        scenario_type: str = "normal"
    ) -> List[Dict[str, Any]]:
        """Generate processor configurations for different scenarios"""
        
        base_processors = [
            {
                "id": "stripe",
                "name": "Stripe",
                "fee_percentage": 2.9,
                "metrics": {"success_rate": 0.95, "avg_response_time": 180},
                "supported_regions": ["US", "EU", "APAC"],
                "priority_score": 0.8
            },
            {
                "id": "paypal",
                "name": "PayPal", 
                "fee_percentage": 3.49,
                "metrics": {"success_rate": 0.93, "avg_response_time": 220},
                "supported_regions": ["US", "EU", "APAC", "LATAM"],
                "priority_score": 0.6
            },
            {
                "id": "visa",
                "name": "Visa Direct",
                "fee_percentage": 2.5,
                "metrics": {"success_rate": 0.97, "avg_response_time": 150},
                "supported_regions": ["US", "EU"],
                "priority_score": 0.7
            }
        ]
        
        if scenario_type == "stripe_outage":
            base_processors[0]["metrics"]["success_rate"] = 0.0  # Stripe down
            base_processors[0]["priority_score"] = 0.0
        
        elif scenario_type == "high_fraud_alert":
            for processor in base_processors:
                processor["fraud_alert"] = random.choice([True, False])
                if processor["fraud_alert"]:
                    processor["priority_score"] *= 0.7
        
        elif scenario_type == "promotional_period":
            base_processors[0]["fee_percentage"] = 2.4  # Stripe promotion
            base_processors[0]["priority_score"] = 0.9
        
        return base_processors
    
    def export_test_data(self, filename: str, data_type: str = "transactions", **kwargs):
        """Export generated data to file for testing"""
        
        if data_type == "transactions":
            data = self.generate_transactions(**kwargs)
            data_dict = [asdict(t) for t in data]
        elif data_type == "insights":
            data = self.generate_synthetic_insights(**kwargs)
            # Convert insights to dict format
            data_dict = {}
            for processor, insights_by_type in data.items():
                data_dict[processor] = {}
                for insight_type, insights in insights_by_type.items():
                    data_dict[processor][insight_type] = [asdict(insight) for insight in insights]
        else:
            raise ValueError(f"Unknown data_type: {data_type}")
        
        with open(filename, 'w') as f:
            json.dump(data_dict, f, indent=2, default=str)
        
        print(f"Exported {data_type} data to {filename}")


# Example usage and testing
async def demo_synthetic_data():
    """Demo the synthetic data generation capabilities"""
    
    print("🎯 Synthetic Data Generation Demo")
    print("=" * 50)
    
    generator = SyntheticDataGenerator(seed=42)
    
    # Generate transactions
    print("\n1. Generating Transaction Data...")
    transactions = generator.generate_transactions(
        count=50,
        business_type="startup_tech",
        risk_distribution={"low": 0.6, "medium": 0.3, "high": 0.08, "critical": 0.02}
    )
    
    print(f"Generated {len(transactions)} transactions")
    print(f"Sample transaction: {transactions[0].request_id}, ${transactions[0].amount}, Risk: {transactions[0].risk_score:.2f}")
    
    # Generate insights
    print("\n2. Generating Synthetic Insights...")
    insights = generator.generate_synthetic_insights(
        processors=["stripe", "paypal", "visa"],
        insight_count_per_type=2
    )
    
    for processor, processor_insights in insights.items():
        total_insights = sum(len(insights_list) for insights_list in processor_insights.values())
        print(f"{processor}: {total_insights} total insights across {len(processor_insights)} types")
    
    # Generate scenarios
    print("\n3. Generating Processor Scenarios...")
    scenarios = {
        "normal": generator.generate_processor_scenarios("normal"),
        "stripe_outage": generator.generate_processor_scenarios("stripe_outage"),
        "promotional": generator.generate_processor_scenarios("promotional_period")
    }
    
    for scenario_name, processors in scenarios.items():
        print(f"{scenario_name}: {len(processors)} processors configured")
    
    # Export data
    print("\n4. Exporting Test Data...")
    generator.export_test_data("sample_transactions.json", "transactions", count=100)
    generator.export_test_data("sample_insights.json", "insights", 
                              processors=["stripe", "paypal"], insight_count_per_type=3)
    
    print("\n✅ Synthetic data generation complete!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_synthetic_data())