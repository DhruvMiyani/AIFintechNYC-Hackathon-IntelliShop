"""
Database Models for Persistent Insights Storage
Production-ready SQLAlchemy models with proper indexing
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timedelta
import uuid

Base = declarative_base()

class ProcessorInsight(Base):
    """Main table for storing all processor insights"""
    __tablename__ = 'processor_insights'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    processor_id = Column(String(50), nullable=False, index=True)  # stripe, paypal, etc.
    insight_type = Column(String(50), nullable=False, index=True)  # promotions, fraud_trends, etc.
    
    # Core data
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source_url = Column(String(1000))
    confidence_score = Column(Float, default=0.0)
    impact_score = Column(Float, default=0.0)
    
    # Metadata
    is_synthetic = Column(Boolean, default=False, index=True)
    data_source = Column(String(50), default='brave_search')  # brave_search, synthetic, manual
    raw_data = Column(JSONB)  # Store original API response
    parsed_data = Column(JSONB)  # Store structured parsed data
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, index=True)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    
    # Quality metrics
    accuracy_score = Column(Float, default=0.0)  # ML-based accuracy prediction
    relevance_score = Column(Float, default=0.0)  # Business relevance
    freshness_score = Column(Float, default=1.0)  # How recent is the data
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_processor_type_created', 'processor_id', 'insight_type', 'created_at'),
        Index('idx_expires_synthetic', 'expires_at', 'is_synthetic'),
        Index('idx_confidence_impact', 'confidence_score', 'impact_score'),
    )

class MarketTrend(Base):
    """Time-series data for market trends and analytics"""
    __tablename__ = 'market_trends'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    processor_id = Column(String(50), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)  # fraud_rate, uptime, sentiment
    
    # Values
    numeric_value = Column(Float)
    string_value = Column(String(200))
    json_value = Column(JSONB)
    
    # Time-series
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    time_bucket = Column(String(20), index=True)  # hourly, daily, weekly
    
    # Source tracking
    source_insight_id = Column(UUID(as_uuid=True))
    confidence = Column(Float, default=0.0)

class RoutingDecision(Base):
    """Audit log of all routing decisions made"""
    __tablename__ = 'routing_decisions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(String(100), unique=True, index=True)
    
    # Request details
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    merchant_id = Column(String(100), index=True)
    
    # Decision
    selected_processor = Column(String(50), nullable=False, index=True)
    decision_reason = Column(Text)
    insights_used = Column(JSONB)  # List of insights that influenced decision
    
    # Performance metrics
    decision_time_ms = Column(Integer)
    success = Column(Boolean, index=True)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class DataQualityMetrics(Base):
    """Track data quality across different sources"""
    __tablename__ = 'data_quality_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type = Column(String(50), nullable=False, index=True)  # brave_search, synthetic
    processor_id = Column(String(50), index=True)
    
    # Quality scores
    accuracy_rate = Column(Float, default=0.0)
    completeness_rate = Column(Float, default=0.0)
    consistency_rate = Column(Float, default=0.0)
    timeliness_rate = Column(Float, default=0.0)
    
    # Sample sizes
    total_insights = Column(Integer, default=0)
    successful_insights = Column(Integer, default=0)
    failed_insights = Column(Integer, default=0)
    
    # Time period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemHealth(Base):
    """Overall system health and performance tracking"""
    __tablename__ = 'system_health'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # API Health
    brave_search_status = Column(String(20), default='unknown')  # healthy, degraded, down
    brave_search_rate_limit = Column(Integer, default=0)
    brave_search_quota_remaining = Column(Integer, default=0)
    
    # Cache Health
    redis_status = Column(String(20), default='unknown')
    cache_hit_rate = Column(Float, default=0.0)
    cache_size_mb = Column(Float, default=0.0)
    
    # Database Health  
    db_status = Column(String(20), default='unknown')
    db_query_avg_ms = Column(Float, default=0.0)
    db_connection_pool = Column(Integer, default=0)
    
    # Business Metrics
    insights_per_hour = Column(Float, default=0.0)
    routing_success_rate = Column(Float, default=0.0)
    avg_decision_time_ms = Column(Float, default=0.0)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

# Database Configuration
class DatabaseConfig:
    def __init__(self, db_url="postgresql://user:pass@localhost/payment_intel"):
        self.engine = create_engine(
            db_url,
            pool_size=20,
            max_overflow=0,
            pool_pre_ping=True,
            echo=False  # Set to True for SQL logging
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()

# Usage example
if __name__ == "__main__":
    # Initialize database
    db = DatabaseConfig()
    db.create_tables()
    
    # Example: Store an insight
    session = db.get_session()
    
    insight = ProcessorInsight(
        processor_id="stripe",
        insight_type="promotions",
        title="Stripe Q4 2024 Promotion",
        content="Lower transaction fees for new merchants",
        confidence_score=0.85,
        impact_score=0.7,
        is_synthetic=False,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    
    session.add(insight)
    session.commit()
    print("✅ Insight stored successfully!")
    session.close()