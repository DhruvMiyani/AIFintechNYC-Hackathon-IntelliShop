"""
Crossmint Processor - USDC Payment Integration
Implements Crossmint's Headless Checkout API for stablecoin payments
"""

import os
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import httpx

from .base import PaymentProcessor, PaymentRequest, PaymentResponse, PaymentStatus


class CrossmintProcessor(PaymentProcessor):
    """Crossmint payment processor for USDC transactions using Headless Checkout API"""
    
    def __init__(self, processor_id: str = "crossmint", config: Dict[str, Any] = None):
        # Get configuration from environment variables
        api_key = os.getenv("CROSSMINT_API_KEY", "test_api_key")
        api_endpoint = os.getenv("CROSSMINT_API_ENDPOINT", "https://staging.crossmint.com/api/2025-06-09")
        default_chain = os.getenv("CROSSMINT_DEFAULT_CHAIN", "arbitrum-sepolia")
        default_currency = os.getenv("CROSSMINT_DEFAULT_CURRENCY", "usdc")
        settlement_email = os.getenv("CROSSMINT_SETTLEMENT_EMAIL", "merchant@example.com")
        
        default_config = {
            "api_key": api_key,
            "api_endpoint": api_endpoint,
            "default_chain": default_chain,
            "default_currency": default_currency,
            "settlement_email": settlement_email,
            "supported_currencies": ["USDC"],
            "min_amount": 0.01,
            "max_amount": 1000000.0,
            "fee_percentage": 1.5,
            "fixed_fee": 0.0,
            "features": ["stablecoin_payments", "crypto", "instant_settlement"],
            "regions": ["US", "EU", "GLOBAL"],
            "timeout_seconds": 30
        }
        
        super().__init__(processor_id, default_config if not config else {**default_config, **config})
        
        # Storage for order tracking
        self.orders = {}
        
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Process payment using Crossmint's Headless Checkout API"""
        start_time = datetime.utcnow()
        
        try:
            # Validate currency support
            if request.currency not in self.config["supported_currencies"]:
                return PaymentResponse(
                    request_id=request.request_id,
                    processor_id=self.processor_id,
                    status=PaymentStatus.FAILED,
                    error_message=f"Currency {request.currency} not supported. Supported currencies: {self.config['supported_currencies']}",
                    error_code="invalid_currency",
                    processing_time_ms=0
                )
            
            # Validate amount limits
            if request.amount < self.config["min_amount"]:
                return PaymentResponse(
                    request_id=request.request_id,
                    processor_id=self.processor_id,
                    status=PaymentStatus.FAILED,
                    error_message=f"Amount must be at least {self.config['min_amount']} {request.currency}",
                    error_code="amount_too_small",
                    processing_time_ms=0
                )
            
            if request.amount > self.config["max_amount"]:
                return PaymentResponse(
                    request_id=request.request_id,
                    processor_id=self.processor_id,
                    status=PaymentStatus.FAILED,
                    error_message=f"Amount must not exceed {self.config['max_amount']} {request.currency}",
                    error_code="amount_too_large",
                    processing_time_ms=0
                )
            
            # Create order payload
            order_payload = {
                "recipient": {
                    "email": self.config["settlement_email"]
                },
                "payment": {
                    "method": self.config["default_chain"],
                    "currency": self.config["default_currency"]
                },
                "lineItems": {
                    "callData": {
                        "totalPrice": str(request.amount)
                    }
                }
            }
            
            # Include payer address if provided
            if request.metadata and request.metadata.get("payer_address"):
                order_payload["payment"]["payerAddress"] = request.metadata["payer_address"]
            
            # Make API call to create order
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.config['api_endpoint']}/orders",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-KEY": self.config["api_key"]
                    },
                    json=order_payload
                )
                
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                if response.status_code == 201:
                    # Success - parse response
                    order_data = response.json()
                    order_id = order_data.get("orderId")
                    client_secret = order_data.get("clientSecret")
                    
                    # Store order details for status checking
                    self.orders[order_id] = {
                        "client_secret": client_secret,
                        "request_id": request.request_id,
                        "amount": request.amount,
                        "currency": request.currency,
                        "created_at": datetime.utcnow(),
                        "status": "pending"
                    }
                    
                    # Update metrics
                    self.update_metrics(True, processing_time)
                    
                    return PaymentResponse(
                        request_id=request.request_id,
                        processor_id=self.processor_id,
                        status=PaymentStatus.PENDING,
                        transaction_id=order_id,
                        processor_response={
                            "order_id": order_id,
                            "client_secret": client_secret,
                            "payment_method": self.config["default_chain"],
                            "currency": self.config["default_currency"]
                        },
                        processing_time_ms=processing_time
                    )
                
                else:
                    # API error
                    error_data = {}
                    try:
                        error_data = response.json()
                    except:
                        pass
                    
                    error_message = error_data.get("message", f"HTTP {response.status_code}")
                    error_code = error_data.get("code", str(response.status_code))
                    
                    # Update metrics
                    self.update_metrics(False, processing_time)
                    
                    return PaymentResponse(
                        request_id=request.request_id,
                        processor_id=self.processor_id,
                        status=PaymentStatus.FAILED,
                        error_message=f"Crossmint API error: {error_message}",
                        error_code=error_code,
                        processor_response=error_data,
                        processing_time_ms=processing_time
                    )
        
        except httpx.TimeoutException:
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.update_metrics(False, processing_time)
            
            return PaymentResponse(
                request_id=request.request_id,
                processor_id=self.processor_id,
                status=PaymentStatus.TIMEOUT,
                error_message="Request timed out",
                error_code="timeout",
                processing_time_ms=processing_time
            )
        
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.update_metrics(False, processing_time)
            
            return PaymentResponse(
                request_id=request.request_id,
                processor_id=self.processor_id,
                status=PaymentStatus.FAILED,
                error_message=f"Unexpected error: {str(e)}",
                error_code="internal_error",
                processing_time_ms=processing_time
            )
    
    async def check_status(self, transaction_id: str) -> PaymentStatus:
        """Check payment status by polling Crossmint orders endpoint"""
        
        try:
            # Get stored order details
            order_details = self.orders.get(transaction_id)
            if not order_details:
                return PaymentStatus.FAILED
            
            client_secret = order_details["client_secret"]
            
            # Poll order status
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.config['api_endpoint']}/orders/{transaction_id}",
                    headers={
                        "X-API-KEY": self.config["api_key"],
                        "Authorization": client_secret
                    }
                )
                
                if response.status_code == 200:
                    order_data = response.json()
                    phase = order_data.get("phase", "unknown")
                    
                    # Update stored order status
                    order_details["last_checked"] = datetime.utcnow()
                    order_details["phase"] = phase
                    
                    # Map Crossmint phases to PaymentStatus
                    if phase == "completed":
                        order_details["status"] = "completed"
                        return PaymentStatus.SUCCESS
                    elif phase in ["payment", "delivery"]:
                        order_details["status"] = "processing"
                        return PaymentStatus.PROCESSING
                    else:
                        # Assume failed for unknown phases or error states
                        order_details["status"] = "failed"
                        return PaymentStatus.FAILED
                
                else:
                    # API error during status check
                    return PaymentStatus.FAILED
        
        except Exception as e:
            # Error during status check
            return PaymentStatus.FAILED
    
    async def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> bool:
        """
        Refund payment - stub implementation
        
        Crossmint's headless checkout does not directly support refunds in test environment.
        In production, this would implement wallet transfer reversal.
        """
        # For now, return False as refunds are not supported
        # In production, you could implement wallet-to-wallet transfer for refunds
        return False