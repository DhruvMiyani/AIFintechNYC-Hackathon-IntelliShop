import asyncio
import random
from typing import Dict, Any, Optional
from datetime import datetime
from .base import PaymentProcessor, PaymentRequest, PaymentResponse, PaymentStatus
import uuid


class StripeProcessor(PaymentProcessor):
    def __init__(self, processor_id: str = "stripe", config: Dict[str, Any] = None):
        default_config = {
            "api_endpoint": config.get("api_endpoint", "https://api.stripe.com") if config else "https://api.stripe.com",
            "api_key": config.get("api_key", "sk_test_mock") if config else "sk_test_mock",
            "webhook_secret": config.get("webhook_secret", "whsec_mock") if config else "whsec_mock",
            "supported_currencies": ["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "SGD", "HKD", "CNY", "INR", "MXN", "BRL"],
            "min_amount": 0.50,
            "max_amount": 999999.99,
            "fee_percentage": 2.9,
            "fixed_fee": 0.30,
            "features": ["subscriptions", "invoicing", "connect", "radar", "3ds", "wallets", "ach", "sepa"],
            "regions": ["US", "EU", "APAC", "LATAM"],
            "timeout_seconds": 30
        }
        super().__init__(processor_id, default_config if not config else {**default_config, **config})
        self.payment_intents = {}
        
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        start_time = datetime.utcnow()
        
        if request.currency not in self.config["supported_currencies"]:
            return PaymentResponse(
                request_id=request.request_id,
                processor_id=self.processor_id,
                status=PaymentStatus.FAILED,
                error_message=f"Currency {request.currency} not supported",
                error_code="invalid_currency",
                processing_time_ms=0
            )
        
        if request.amount < self.config["min_amount"]:
            return PaymentResponse(
                request_id=request.request_id,
                processor_id=self.processor_id,
                status=PaymentStatus.FAILED,
                error_message=f"Amount must be at least {self.config['min_amount']} {request.currency}",
                error_code="amount_too_small",
                processing_time_ms=0
            )
        
        payment_intent_id = f"pi_{uuid.uuid4().hex[:24]}"
        charge_id = f"ch_{uuid.uuid4().hex[:24]}"
        
        await asyncio.sleep(random.uniform(0.3, 1.2))
        
        radar_score = random.randint(1, 99)
        is_high_risk = request.routing_hints.get("high_risk", False) or radar_score > 85
        
        success_rate = 0.93
        if is_high_risk:
            success_rate = 0.65
        
        success = random.random() < success_rate
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        self.update_metrics(success, processing_time)
        
        if success:
            fee = (request.amount * (self.config["fee_percentage"] / 100)) + self.config["fixed_fee"]
            
            return PaymentResponse(
                request_id=request.request_id,
                processor_id=self.processor_id,
                status=PaymentStatus.SUCCESS,
                transaction_id=payment_intent_id,
                processor_response={
                    "id": payment_intent_id,
                    "object": "payment_intent",
                    "amount": int(request.amount * 100),
                    "currency": request.currency.lower(),
                    "status": "succeeded",
                    "client_secret": f"{payment_intent_id}_secret_{uuid.uuid4().hex[:16]}",
                    "charges": {
                        "object": "list",
                        "data": [{
                            "id": charge_id,
                            "object": "charge",
                            "amount": int(request.amount * 100),
                            "currency": request.currency.lower(),
                            "paid": True,
                            "refunded": False,
                            "outcome": {
                                "network_status": "approved_by_network",
                                "reason": None,
                                "risk_level": "normal" if radar_score < 65 else "elevated",
                                "risk_score": radar_score,
                                "type": "authorized"
                            },
                            "payment_method_details": {
                                "card": {
                                    "brand": random.choice(["visa", "mastercard", "amex"]),
                                    "last4": f"{random.randint(1000, 9999)}",
                                    "funding": random.choice(["credit", "debit"]),
                                    "country": "US",
                                    "three_d_secure": {
                                        "succeeded": True,
                                        "authenticated": True
                                    } if request.amount > 1000 else None
                                }
                            },
                            "balance_transaction": f"txn_{uuid.uuid4().hex[:24]}"
                        }]
                    },
                    "created": int(datetime.utcnow().timestamp()),
                    "livemode": False,
                    "metadata": request.metadata or {},
                    "application_fee_amount": int(fee * 100) if request.routing_hints.get("platform_fee") else None
                },
                processing_time_ms=processing_time,
                fees=fee
            )
        else:
            decline_codes = [
                ("card_declined", "Your card was declined"),
                ("insufficient_funds", "Your card has insufficient funds"),
                ("lost_card", "Your card is reported lost"),
                ("stolen_card", "Your card is reported stolen"),
                ("generic_decline", "Your card was declined"),
                ("fraudulent", "This transaction may be fraudulent"),
                ("invalid_amount", "The payment amount is invalid"),
                ("processing_error", "An error occurred while processing your card"),
                ("expired_card", "Your card has expired"),
                ("incorrect_cvc", "Your card's security code is incorrect")
            ]
            
            decline_code, message = random.choice(decline_codes)
            
            return PaymentResponse(
                request_id=request.request_id,
                processor_id=self.processor_id,
                status=PaymentStatus.FAILED,
                transaction_id=payment_intent_id,
                error_message=message,
                error_code=decline_code,
                processor_response={
                    "error": {
                        "code": decline_code,
                        "doc_url": f"https://stripe.com/docs/error-codes/{decline_code}",
                        "message": message,
                        "payment_intent": {
                            "id": payment_intent_id,
                            "object": "payment_intent",
                            "amount": int(request.amount * 100),
                            "currency": request.currency.lower(),
                            "status": "requires_payment_method",
                            "last_payment_error": {
                                "code": decline_code,
                                "message": message,
                                "type": "card_error"
                            }
                        },
                        "type": "card_error"
                    }
                },
                processing_time_ms=processing_time
            )
    
    async def check_status(self, transaction_id: str) -> PaymentStatus:
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        if transaction_id in self.payment_intents:
            return self.payment_intents[transaction_id]
        
        status_map = {
            "succeeded": PaymentStatus.SUCCESS,
            "processing": PaymentStatus.PROCESSING,
            "requires_payment_method": PaymentStatus.PENDING,
            "canceled": PaymentStatus.CANCELLED
        }
        
        stripe_status = random.choice(list(status_map.keys()))
        return status_map[stripe_status]
    
    async def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> bool:
        await asyncio.sleep(random.uniform(0.3, 0.8))
        return random.random() < 0.98