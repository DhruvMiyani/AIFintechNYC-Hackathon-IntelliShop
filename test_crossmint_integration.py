#!/usr/bin/env python3
"""
Test script for Crossmint integration
Verifies that the CrossmintProcessor is properly integrated with the payment orchestration system
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from processors import CrossmintProcessor, PaymentRequest, PaymentStatus
from processor_registry import ProcessorRegistry


async def test_crossmint_processor():
    """Test the CrossmintProcessor directly"""
    print("🧪 Testing Crossmint Processor Integration")
    print("=" * 60)
    
    # Initialize the processor
    processor = CrossmintProcessor()
    print(f"✅ CrossmintProcessor initialized")
    print(f"   API Endpoint: {processor.config['api_endpoint']}")
    print(f"   Default Chain: {processor.config['default_chain']}")
    print(f"   Supported Currencies: {processor.config['supported_currencies']}")
    print()
    
    # Test 1: Valid USDC payment
    print("🔬 Test 1: Valid USDC Payment")
    test_request = PaymentRequest(
        request_id="test_usdc_001",
        amount=100.50,
        currency="USDC",
        merchant_id="test_merchant",
        metadata={"test": True}
    )
    
    try:
        result = await processor.process_payment(test_request)
        print(f"   Status: {result.status.value}")
        print(f"   Transaction ID: {result.transaction_id}")
        if result.error_message:
            print(f"   Error: {result.error_message}")
        else:
            print(f"   Processing Time: {result.processing_time_ms:.2f}ms")
            print(f"   Processor Response: {result.processor_response}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    print()
    
    # Test 2: Invalid currency
    print("🔬 Test 2: Invalid Currency (should fail)")
    invalid_request = PaymentRequest(
        request_id="test_invalid_001",
        amount=50.00,
        currency="USD",  # Not supported by Crossmint
        merchant_id="test_merchant"
    )
    
    try:
        result = await processor.process_payment(invalid_request)
        print(f"   Status: {result.status.value}")
        print(f"   Error: {result.error_message}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
    print()
    
    # Test 3: Amount too small
    print("🔬 Test 3: Amount Too Small (should fail)")
    small_request = PaymentRequest(
        request_id="test_small_001",
        amount=0.005,  # Below minimum
        currency="USDC",
        merchant_id="test_merchant"
    )
    
    try:
        result = await processor.process_payment(small_request)
        print(f"   Status: {result.status.value}")
        print(f"   Error: {result.error_message}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
    print()


async def test_processor_registry():
    """Test that Crossmint is properly registered"""
    print("🧪 Testing Processor Registry Integration")
    print("=" * 60)
    
    registry = ProcessorRegistry()
    
    # Check if Crossmint is in the registry
    if "crossmint" in registry.processors:
        print("✅ Crossmint found in processor registry")
        crossmint_proc = registry.processors["crossmint"]
        print(f"   Name: {crossmint_proc.name}")
        print(f"   Type: {crossmint_proc.type}")
        print(f"   Status: {crossmint_proc.status.value}")
        print(f"   Capabilities: {crossmint_proc.capabilities}")
        print(f"   Fee Structure: {crossmint_proc.fee_structure}")
        print(f"   Fallback Priority: {crossmint_proc.fallback_priority}")
    else:
        print("❌ Crossmint not found in processor registry")
    print()
    
    # Test GPT analysis data
    context = {
        "amount": 500.0,
        "currency": "USDC",
        "merchant_id": "test_merchant",
        "urgency": "normal"
    }
    
    analysis_data = await registry.get_processor_for_gpt5_analysis(context)
    
    if "crossmint" in analysis_data["available_processors"]:
        print("✅ Crossmint available in GPT-5 analysis")
        crossmint_data = analysis_data["available_processors"]["crossmint"]
        print(f"   Recommendation: {crossmint_data['recommendation']}")
        print(f"   Health Metrics: {crossmint_data['health_metrics']}")
        print(f"   Risk Assessment: {crossmint_data['risk_assessment']}")
    else:
        print("❌ Crossmint not found in GPT-5 analysis data")
    print()


async def test_status_checking():
    """Test the status checking functionality"""
    print("🧪 Testing Status Checking")
    print("=" * 60)
    
    processor = CrossmintProcessor()
    
    # Create a mock order for status testing
    processor.orders["test_order_123"] = {
        "client_secret": "cs_test_123",
        "request_id": "req_123",
        "amount": 100.0,
        "currency": "USDC",
        "created_at": datetime.utcnow(),
        "status": "pending"
    }
    
    # Test status check
    try:
        status = await processor.check_status("test_order_123")
        print(f"   Order Status: {status.value}")
        print("   ✅ Status checking works (will fail with real API without valid credentials)")
    except Exception as e:
        print(f"   Expected error with mock data: {str(e)}")
    print()


async def test_refund_functionality():
    """Test the refund functionality"""
    print("🧪 Testing Refund Functionality")
    print("=" * 60)
    
    processor = CrossmintProcessor()
    
    # Test refund (should return False as per requirements)
    try:
        result = await processor.refund_payment("test_transaction_123", 50.0)
        print(f"   Refund Result: {result}")
        if result is False:
            print("   ✅ Refund correctly returns False (not supported in test environment)")
        else:
            print("   ⚠️  Unexpected refund result")
    except Exception as e:
        print(f"   ❌ Error during refund test: {str(e)}")
    print()


async def main():
    """Run all tests"""
    print("🚀 Crossmint Integration Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.utcnow().isoformat()}")
    print()
    
    try:
        await test_crossmint_processor()
        await test_processor_registry()
        await test_status_checking()
        await test_refund_functionality()
        
        print("🎉 All tests completed!")
        print("=" * 60)
        print("Note: Some tests may show expected errors when using placeholder API keys.")
        print("Replace CROSSMINT_API_KEY in .env with a real key for full functionality.")
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())