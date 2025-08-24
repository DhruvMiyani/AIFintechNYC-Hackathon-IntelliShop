import asyncio
import random
from typing import Dict, Any, Optional
from datetime import datetime
from .base import PaymentProcessor, PaymentRequest, PaymentResponse, PaymentStatus
import uuid


class VisaProcessor(PaymentProcessor):
    def __init__(self, processor_id: str = "visa", config: Dict[str, Any] = None):
        default_config = {
            "api_endpoint": config.get("api_endpoint", "https://sandbox.api.visa.com") if config else "https://sandbox.api.visa.com",
            "api_key": config.get("api_key", "mock_visa_api_key") if config else "mock_visa_api_key",
            "shared_secret": config.get("shared_secret", "mock_shared_secret") if config else "mock_shared_secret",
            "supported_currencies": ["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "SGD", "HKD", "INR", "CNY"],
            "min_amount": 0.01,
            "max_amount": 50000000,
            "fee_percentage": 2.4,
            "fixed_fee": 0.10,
            "features": ["tokenization", "3ds", "recurring", "international", "fraud_protection", "chargeback_protection"],
            "regions": ["US", "EU", "APAC", "LATAM", "MEA"],
            "timeout_seconds": 45,
            "requires_3ds": True,
            "interchange_plus": True
        }
        super().__init__(processor_id, default_config if not config else {**default_config, **config})
        self.authorization_cache = {}
        
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        start_time = datetime.utcnow()
        
        if request.currency not in self.config["supported_currencies"]:
            return PaymentResponse(
                request_id=request.request_id,
                processor_id=self.processor_id,
                status=PaymentStatus.FAILED,
                error_message=f"Currency {request.currency} not supported by Visa",
                error_code="INVALID_CURRENCY",
                processing_time_ms=0
            )
        
        if request.amount < self.config["min_amount"] or request.amount > self.config["max_amount"]:
            return PaymentResponse(
                request_id=request.request_id,
                processor_id=self.processor_id,
                status=PaymentStatus.FAILED,
                error_message=f"Amount {request.amount} outside Visa processing limits",
                error_code="AMOUNT_LIMIT_EXCEEDED",
                processing_time_ms=0
            )
        
        transaction_id = f"VIS{datetime.utcnow().strftime('%Y%m%d')}{uuid.uuid4().hex[:12].upper()}"
        auth_code = f"{random.randint(100000, 999999)}"
        
        await asyncio.sleep(random.uniform(0.3, 1.5))
        
        fraud_score = random.random()
        is_high_risk = request.routing_hints.get("high_risk", False)
        requires_3ds = self.config["requires_3ds"] or request.amount > 1000 or is_high_risk
        
        if requires_3ds:
            await asyncio.sleep(random.uniform(0.5, 1.0))
            three_ds_success = random.random() < 0.95
            if not three_ds_success:
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                self.update_metrics(False, processing_time)
                
                return PaymentResponse(
                    request_id=request.request_id,
                    processor_id=self.processor_id,
                    status=PaymentStatus.FAILED,
                    transaction_id=transaction_id,
                    error_message="3D Secure authentication failed",
                    error_code="3DS_AUTHENTICATION_FAILED",
                    processor_response={
                        "3ds_version": "2.2.0",
                        "eci": "07",
                        "authentication_value": None,
                        "directory_response": "N"
                    },
                    processing_time_ms=processing_time
                )
        
        success_rate = 0.94
        if is_high_risk or fraud_score > 0.8:
            success_rate = 0.70
        
        success = random.random() < success_rate
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        self.update_metrics(success, processing_time)
        
        if success:
            interchange_fee = request.amount * 0.0185
            assessment_fee = request.amount * 0.0014
            total_fee = (request.amount * (self.config["fee_percentage"] / 100)) + self.config["fixed_fee"] + interchange_fee + assessment_fee
            
            return PaymentResponse(
                request_id=request.request_id,
                processor_id=self.processor_id,
                status=PaymentStatus.SUCCESS,
                transaction_id=transaction_id,
                processor_response={
                    "transaction_id": transaction_id,
                    "authorization_code": auth_code,
                    "approval_code": f"APP{random.randint(1000, 9999)}",
                    "network_transaction_id": f"NTI{uuid.uuid4().hex[:16].upper()}",
                    "card_details": {
                        "last_four": f"{random.randint(1000, 9999)}",
                        "brand": "VISA",
                        "type": random.choice(["CREDIT", "DEBIT", "PREPAID"]),
                        "issuer_country": "US",
                        "issuing_bank": "CHASE"
                    },
                    "risk_assessment": {
                        "score": round(fraud_score * 100, 2),
                        "decision": "APPROVE",
                        "factors": ["velocity_check", "address_verification", "cvv_match"]
                    },
                    "3ds": {
                        "version": "2.2.0",
                        "eci": "05" if requires_3ds else None,
                        "cavv": uuid.uuid4().hex[:20].upper() if requires_3ds else None,
                        "authentication_value": uuid.uuid4().hex if requires_3ds else None
                    },
                    "settlement": {
                        "expected_date": datetime.utcnow().isoformat(),
                        "interchange_fee": interchange_fee,
                        "assessment_fee": assessment_fee
                    },
                    "stan": f"{random.randint(100000, 999999)}",
                    "rrn": f"{random.randint(100000000000, 999999999999)}",
                    "response_code": "00",
                    "response_message": "Approved"
                },
                processing_time_ms=processing_time,
                fees=total_fee
            )
        else:
            decline_reasons = [
                ("05", "Do not honor", "GENERIC_DECLINE"),
                ("51", "Insufficient funds", "INSUFFICIENT_FUNDS"),
                ("54", "Expired card", "EXPIRED_CARD"),
                ("61", "Exceeds withdrawal limit", "LIMIT_EXCEEDED"),
                ("65", "Exceeds withdrawal frequency", "VELOCITY_EXCEEDED"),
                ("82", "Negative CAM, dCVV, iCVV, or CVV results", "CVV_FAILURE"),
                ("14", "Invalid card number", "INVALID_CARD"),
                ("43", "Stolen card", "STOLEN_CARD"),
                ("59", "Suspected fraud", "FRAUD_SUSPECTED"),
                ("63", "Security violation", "SECURITY_VIOLATION")
            ]
            
            response_code, response_msg, error_code = random.choice(decline_reasons)
            
            return PaymentResponse(
                request_id=request.request_id,
                processor_id=self.processor_id,
                status=PaymentStatus.FAILED,
                transaction_id=transaction_id,
                error_message=response_msg,
                error_code=error_code,
                processor_response={
                    "transaction_id": transaction_id,
                    "response_code": response_code,
                    "response_message": response_msg,
                    "decline_code": error_code,
                    "risk_assessment": {
                        "score": round(fraud_score * 100, 2),
                        "decision": "DECLINE",
                        "factors": ["high_risk_merchant", "unusual_activity"] if fraud_score > 0.8 else ["standard_decline"]
                    },
                    "network_advice_code": "01",
                    "retrieval_reference_number": f"{random.randint(100000000000, 999999999999)}"
                },
                processing_time_ms=processing_time
            )
    
    async def check_status(self, transaction_id: str) -> PaymentStatus:
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        if transaction_id in self.authorization_cache:
            return self.authorization_cache[transaction_id]
        
        status_options = [
            (PaymentStatus.SUCCESS, 0.85),
            (PaymentStatus.PENDING, 0.05),
            (PaymentStatus.FAILED, 0.08),
            (PaymentStatus.CANCELLED, 0.02)
        ]
        
        rand = random.random()
        cumulative = 0
        for status, probability in status_options:
            cumulative += probability
            if rand < cumulative:
                return status
        
        return PaymentStatus.SUCCESS
    
    async def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> bool:
        await asyncio.sleep(random.uniform(0.5, 1.5))
        return random.random() < 0.97