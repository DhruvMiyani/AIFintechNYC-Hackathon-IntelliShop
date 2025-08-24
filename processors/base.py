from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import uuid


class ProcessorStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    FAILED = "failed"


class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ProcessorMetrics:
    uptime_percentage: float
    average_latency_ms: float
    success_rate: float
    last_failure: Optional[datetime] = None
    total_processed: int = 0
    total_volume: float = 0.0
    fraud_flags: int = 0
    

@dataclass
class PaymentRequest:
    request_id: str
    amount: float
    currency: str
    merchant_id: str
    customer_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    routing_hints: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.routing_hints is None:
            self.routing_hints = {}
        if not self.request_id:
            self.request_id = str(uuid.uuid4())


@dataclass
class PaymentResponse:
    request_id: str
    processor_id: str
    status: PaymentStatus
    transaction_id: Optional[str] = None
    processor_response: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    processing_time_ms: float = 0.0
    fees: Optional[float] = None
    

class PaymentProcessor(ABC):
    def __init__(self, processor_id: str, config: Dict[str, Any]):
        self.processor_id = processor_id
        self.config = config
        self.status = ProcessorStatus.ACTIVE
        self.metrics = ProcessorMetrics(
            uptime_percentage=99.0,
            average_latency_ms=100.0,
            success_rate=95.0
        )
        
    @abstractmethod
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        pass
    
    @abstractmethod
    async def check_status(self, transaction_id: str) -> PaymentStatus:
        pass
    
    @abstractmethod
    async def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> bool:
        pass
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "processor_id": self.processor_id,
            "status": self.status.value,
            "supported_currencies": self.config.get("supported_currencies", ["USD"]),
            "min_amount": self.config.get("min_amount", 0.01),
            "max_amount": self.config.get("max_amount", 1000000),
            "features": self.config.get("features", []),
            "regions": self.config.get("regions", []),
            "fee_percentage": self.config.get("fee_percentage", 2.0)
        }
    
    def get_metrics(self) -> ProcessorMetrics:
        return self.metrics
    
    def update_metrics(self, success: bool, latency_ms: float):
        self.metrics.total_processed += 1
        if not success:
            self.metrics.last_failure = datetime.utcnow()
        
        alpha = 0.1
        self.metrics.average_latency_ms = (1 - alpha) * self.metrics.average_latency_ms + alpha * latency_ms
        
        success_count = int(self.metrics.success_rate * max(1, self.metrics.total_processed - 1))
        if success:
            success_count += 1
        self.metrics.success_rate = success_count / self.metrics.total_processed