import asyncio
import random
from typing import Dict, Any, Optional
from datetime import datetime
from .base import PaymentProcessor, PaymentRequest, PaymentResponse, PaymentStatus
import uuid


class PayPalProcessor(PaymentProcessor):
    def __init__(self, processor_id: str = "paypal", config: Dict[str, Any] = None):
        default_config = {
            "api_endpoint": config.get("api_endpoint", "https://api.sandbox.paypal.com") if config else "https://api.sandbox.paypal.com",
            "client_id": config.get("client_id", "mock_client_id") if config else "mock_client_id",
            "client_secret": config.get("client_secret", "mock_secret") if config else "mock_secret",
            "supported_currencies": ["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CNY"],
            "min_amount": 0.01,
            "max_amount": 10000000,
            "fee_percentage": 2.9,
            "fixed_fee": 0.30,
            "features": ["buyer_protection", "recurring", "international", "refunds", "disputes"],
            "regions": ["US", "EU", "APAC", "LATAM"],
            "timeout_seconds": 30
        }
        super().__init__(processor_id, default_config if not config else {**default_config, **config})
        self.active_sessions = {}
        
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        start_time = datetime.utcnow()
        
        if request.currency not in self.config["supported_currencies"]:
            return PaymentResponse(
                request_id=request.request_id,
                processor_id=self.processor_id,
                status=PaymentStatus.FAILED,
                error_message=f"Currency {request.currency} not supported",
                error_code="CURRENCY_NOT_SUPPORTED",
                processing_time_ms=0
            )
        
        if request.amount < self.config["min_amount"] or request.amount > self.config["max_amount"]:
            return PaymentResponse(
                request_id=request.request_id,
                processor_id=self.processor_id,
                status=PaymentStatus.FAILED,
                error_message=f"Amount {request.amount} outside allowed range",
                error_code="INVALID_AMOUNT",
                processing_time_ms=0
            )
        
        payment_id = f"PAYID-{uuid.uuid4().hex[:20].upper()}"
        order_id = f"{uuid.uuid4().hex[:12].upper()}"
        
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        success_rate = 0.92
        if request.routing_hints.get("high_risk"):
            success_rate = 0.75
        
        success = random.random() < success_rate
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        self.update_metrics(success, processing_time)
        
        if success:
            fee = (request.amount * (self.config["fee_percentage"] / 100)) + self.config["fixed_fee"]
            
            return PaymentResponse(
                request_id=request.request_id,
                processor_id=self.processor_id,
                status=PaymentStatus.SUCCESS,
                transaction_id=payment_id,
                processor_response={
                    "payment_id": payment_id,
                    "order_id": order_id,
                    "status": "COMPLETED",
                    "payer": {
                        "payer_id": f"PAYER{uuid.uuid4().hex[:8].upper()}",
                        "email": "customer@example.com",
                        "country_code": "US"
                    },
                    "purchase_units": [{
                        "reference_id": request.request_id,
                        "amount": {
                            "currency_code": request.currency,
                            "value": str(request.amount)
                        }
                    }],
                    "create_time": datetime.utcnow().isoformat(),
                    "update_time": datetime.utcnow().isoformat(),
                    "links": [
                        {"rel": "self", "href": f"{self.config['api_endpoint']}/v2/checkout/orders/{order_id}"}
                    ]
                },
                processing_time_ms=processing_time,
                fees=fee
            )
        else:
            failure_reasons = [
                ("INSTRUMENT_DECLINED", "The instrument presented was either declined by the processor or bank"),
                ("PAYER_CANNOT_PAY", "Payer cannot pay for this transaction"),
                ("PAYEE_ACCOUNT_RESTRICTED", "Payee account is restricted"),
                ("TRANSACTION_REFUSED", "Transaction was refused"),
                ("COMPLIANCE_VIOLATION", "Transaction violates compliance rules"),
                ("DUPLICATE_TRANSACTION", "Duplicate transaction detected")
            ]
            error_code, error_msg = random.choice(failure_reasons)
            
            return PaymentResponse(
                request_id=request.request_id,
                processor_id=self.processor_id,
                status=PaymentStatus.FAILED,
                transaction_id=payment_id,
                error_message=error_msg,
                error_code=error_code,
                processor_response={
                    "name": error_code,
                    "message": error_msg,
                    "debug_id": uuid.uuid4().hex,
                    "details": [{
                        "issue": error_code,
                        "description": error_msg
                    }]
                },
                processing_time_ms=processing_time
            )
    
    async def check_status(self, transaction_id: str) -> PaymentStatus:
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        status_options = [
            (PaymentStatus.SUCCESS, 0.7),
            (PaymentStatus.PENDING, 0.15),
            (PaymentStatus.FAILED, 0.1),
            (PaymentStatus.CANCELLED, 0.05)
        ]
        
        rand = random.random()
        cumulative = 0
        for status, probability in status_options:
            cumulative += probability
            if rand < cumulative:
                return status
        
        return PaymentStatus.SUCCESS
    
    async def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> bool:
        await asyncio.sleep(random.uniform(0.5, 1.0))
        return random.random() < 0.95