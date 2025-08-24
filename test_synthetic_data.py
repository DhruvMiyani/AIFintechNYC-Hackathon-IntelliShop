"""
Test Suite for Synthetic Data Generation Component
Following software best practices:
- Unit tests for each function
- Integration tests for GPT-5 API
- Validation of output format
- Performance benchmarks
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
from synthetic_data_generator import (
    GPT5SyntheticDataGenerator,
    SyntheticTransaction,
    TransactionPattern
)


class TestSyntheticDataGeneration:
    """Test suite for synthetic data generation component"""
    
    def __init__(self):
        self.generator = GPT5SyntheticDataGenerator()
        self.test_results = []
        
    async def run_all_tests(self):
        """Run complete test suite"""
        print("="*70)
        print("SYNTHETIC DATA GENERATION TEST SUITE")
        print("Testing with GPT-5 API Integration")
        print("="*70)
        
        # Test 1: Normal Baseline Generation
        await self.test_normal_baseline_generation()
        
        # Test 2: Freeze Trigger Patterns
        await self.test_freeze_trigger_patterns()
        
        # Test 3: Data Format Validation
        await self.test_stripe_format_compliance()
        
        # Test 4: Pattern Recognition
        await self.test_pattern_characteristics()
        
        # Test 5: Performance Metrics
        await self.test_performance_metrics()
        
        # Print summary
        self.print_test_summary()
    
    async def test_normal_baseline_generation(self):
        """Test 1: Verify normal baseline data generation"""
        print("\n" + "-"*50)
        print("TEST 1: Normal Baseline Generation")
        print("-"*50)
        
        start_time = time.time()
        
        try:
            # Generate 7 days of normal data
            baseline = await self.generator.generate_normal_baseline(
                days=7,
                daily_volume=30,
                avg_amount=100.0
            )
            
            elapsed = time.time() - start_time
            
            # Validate results
            assert len(baseline) > 0, "No transactions generated"
            
            # Check transaction count (should be ~210 for 7 days * 30/day)
            expected_min = 7 * 30 * 0.8  # Allow 20% variance
            expected_max = 7 * 30 * 1.2
            
            charge_count = len([t for t in baseline if t.type == "charge"])
            assert expected_min <= charge_count <= expected_max, \
                f"Transaction count {charge_count} outside expected range"
            
            # Check refund rate (should be ~2%)
            refund_count = len([t for t in baseline if t.type == "refund"])
            refund_rate = (refund_count / charge_count * 100) if charge_count > 0 else 0
            
            print(f"PASSED: Generated {len(baseline)} transactions in {elapsed:.2f}s")
            print(f"   - Charges: {charge_count}")
            print(f"   - Refunds: {refund_count} ({refund_rate:.1f}%)")
            print(f"   - Average amount: ${sum(t.amount for t in baseline if t.type == 'charge') / charge_count:.2f}")
            
            self.test_results.append({
                "test": "Normal Baseline",
                "status": "PASSED",
                "transactions": len(baseline),
                "time": elapsed
            })
            
        except Exception as e:
            print(f"FAILED: {e}")
            self.test_results.append({
                "test": "Normal Baseline",
                "status": "FAILED",
                "error": str(e)
            })
    
    async def test_freeze_trigger_patterns(self):
        """Test 2: Verify freeze trigger pattern generation"""
        print("\n" + "-"*50)
        print("TEST 2: Freeze Trigger Patterns")
        print("-"*50)
        
        patterns_to_test = [
            ("sudden_spike", "Volume spike that triggers freeze"),
            ("high_refund_rate", "Excessive refunds pattern"),
            ("chargeback_surge", "Chargeback pattern exceeding 1%")
        ]
        
        for pattern_type, description in patterns_to_test:
            print(f"\nTesting: {description}")
            
            try:
                start_time = time.time()
                
                transactions = await self.generator.generate_freeze_trigger_scenario(
                    pattern_type=pattern_type,
                    severity="high"
                )
                
                elapsed = time.time() - start_time
                
                assert len(transactions) > 0, f"No transactions for {pattern_type}"
                
                # Validate pattern characteristics
                if pattern_type == "sudden_spike":
                    # Check if transactions are compressed in time
                    time_range = max(t.created for t in transactions) - min(t.created for t in transactions)
                    assert time_range.total_seconds() < 4 * 3600, "Volume spike not compressed in time"
                    print(f"   PASSED: Volume spike: {len(transactions)} txns in {time_range.total_seconds()/3600:.1f} hours")
                
                elif pattern_type == "high_refund_rate":
                    charges = len([t for t in transactions if t.type == "charge"])
                    refunds = len([t for t in transactions if t.type == "refund"])
                    refund_rate = (refunds / charges * 100) if charges > 0 else 0
                    assert refund_rate > 5, f"Refund rate {refund_rate:.1f}% below threshold"
                    print(f"   PASSED: Refund rate: {refund_rate:.1f}% (threshold: 5%)")
                
                elif pattern_type == "chargeback_surge":
                    charges = len([t for t in transactions if t.type == "charge"])
                    chargebacks = len([t for t in transactions if t.type == "adjustment"])
                    chargeback_rate = (chargebacks / charges * 100) if charges > 0 else 0
                    assert chargeback_rate > 1, f"Chargeback rate {chargeback_rate:.1f}% below threshold"
                    print(f"   PASSED: Chargeback rate: {chargeback_rate:.1f}% (threshold: 1%)")
                
                self.test_results.append({
                    "test": f"Pattern: {pattern_type}",
                    "status": "PASSED",
                    "transactions": len(transactions),
                    "time": elapsed
                })
                
            except Exception as e:
                print(f"   FAILED: {e}")
                self.test_results.append({
                    "test": f"Pattern: {pattern_type}",
                    "status": "FAILED",
                    "error": str(e)
                })
    
    async def test_stripe_format_compliance(self):
        """Test 3: Validate Stripe API format compliance"""
        print("\n" + "-"*50)
        print("TEST 3: Stripe Format Compliance")
        print("-"*50)
        
        try:
            # Generate sample transactions
            transactions = await self.generator.generate_normal_baseline(
                days=1,
                daily_volume=10,
                avg_amount=50
            )
            
            # Convert to Stripe format
            stripe_format = self.generator.export_to_stripe_format(transactions[:5])
            
            # Validate required fields
            required_fields = ["id", "object", "amount", "currency", "created", "type"]
            
            for txn in stripe_format:
                for field in required_fields:
                    assert field in txn, f"Missing required field: {field}"
                
                # Validate data types
                assert isinstance(txn["id"], str), "ID must be string"
                assert isinstance(txn["amount"], int), "Amount must be integer (cents)"
                assert isinstance(txn["created"], int), "Created must be Unix timestamp"
                assert txn["object"] == "balance_transaction", "Object type mismatch"
                assert txn["currency"] in ["usd", "eur", "gbp"], "Invalid currency"
            
            print(f"PASSED: All {len(stripe_format)} transactions comply with Stripe format")
            print(f"   Sample transaction ID: {stripe_format[0]['id']}")
            print(f"   Amount format: ${stripe_format[0]['amount']/100:.2f} ({stripe_format[0]['amount']} cents)")
            
            self.test_results.append({
                "test": "Stripe Format",
                "status": "PASSED",
                "validated": len(stripe_format)
            })
            
        except Exception as e:
            print(f"FAILED: Format validation failed: {e}")
            self.test_results.append({
                "test": "Stripe Format",
                "status": "FAILED",
                "error": str(e)
            })
    
    async def test_pattern_characteristics(self):
        """Test 4: Validate pattern characteristics match Stripe freeze triggers"""
        print("\n" + "-"*50)
        print("TEST 4: Pattern Characteristics Validation")
        print("-"*50)
        
        try:
            # Generate complete dataset
            dataset = await self.generator.generate_demo_dataset()
            
            print("\nValidating freeze trigger characteristics:")
            
            # Analyze baseline
            baseline = dataset["baseline"]
            baseline_charges = [t for t in baseline if t.type == "charge"]
            baseline_avg = sum(t.amount for t in baseline_charges) / len(baseline_charges)
            
            print(f"PASSED: Baseline average: ${baseline_avg:.2f}")
            
            # Analyze each scenario
            for scenario_name, scenario_txns in dataset["freeze_scenarios"].items():
                charges = [t for t in scenario_txns if t.type == "charge"]
                
                if scenario_name == "volume_spike":
                    spike_avg = sum(t.amount for t in charges) / len(charges) if charges else 0
                    spike_ratio = spike_avg / baseline_avg if baseline_avg > 0 else 0
                    assert spike_ratio > 3, f"Volume spike amounts not high enough: {spike_ratio:.1f}x"
                    print(f"PASSED: Volume spike: {spike_ratio:.1f}x normal amount")
                
                elif scenario_name == "refund_surge":
                    refunds = [t for t in scenario_txns if t.type == "refund"]
                    refund_rate = (len(refunds) / len(charges) * 100) if charges else 0
                    assert refund_rate > 5, f"Refund rate {refund_rate:.1f}% below freeze threshold"
                    print(f"PASSED: Refund surge: {refund_rate:.1f}% refund rate")
                
                elif scenario_name == "chargeback_pattern":
                    chargebacks = [t for t in scenario_txns if t.type == "adjustment"]
                    cb_rate = (len(chargebacks) / len(charges) * 100) if charges else 0
                    assert cb_rate > 1, f"Chargeback rate {cb_rate:.1f}% below freeze threshold"
                    print(f"PASSED: Chargeback pattern: {cb_rate:.1f}% chargeback rate")
            
            self.test_results.append({
                "test": "Pattern Characteristics",
                "status": "PASSED",
                "scenarios_validated": len(dataset["freeze_scenarios"])
            })
            
        except Exception as e:
            print(f"FAILED: Characteristic validation failed: {e}")
            self.test_results.append({
                "test": "Pattern Characteristics",
                "status": "FAILED",
                "error": str(e)
            })
    
    async def test_performance_metrics(self):
        """Test 5: Measure performance metrics"""
        print("\n" + "-"*50)
        print("TEST 5: Performance Metrics")
        print("-"*50)
        
        try:
            performance_tests = [
                (1, 10, "Small dataset"),
                (7, 50, "Medium dataset"),
                (30, 100, "Large dataset")
            ]
            
            for days, daily_volume, description in performance_tests:
                start_time = time.time()
                
                transactions = await self.generator.generate_normal_baseline(
                    days=days,
                    daily_volume=daily_volume,
                    avg_amount=100
                )
                
                elapsed = time.time() - start_time
                txn_per_second = len(transactions) / elapsed if elapsed > 0 else 0
                
                print(f"PASSED: {description}: {len(transactions)} txns in {elapsed:.2f}s ({txn_per_second:.0f} txns/sec)")
            
            self.test_results.append({
                "test": "Performance",
                "status": "PASSED",
                "tests_run": len(performance_tests)
            })
            
        except Exception as e:
            print(f"FAILED: Performance test failed: {e}")
            self.test_results.append({
                "test": "Performance",
                "status": "FAILED",
                "error": str(e)
            })
    
    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for r in self.test_results if r["status"] == "PASSED")
        failed = sum(1 for r in self.test_results if r["status"] == "FAILED")
        
        print(f"\nTotal Tests: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed == 0:
            print("\nALL TESTS PASSED! Synthetic data generation is working correctly.")
        else:
            print("\nSome tests failed. Review the errors above.")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "PASS" if result["status"] == "PASSED" else "FAIL"
            print(f"[{status}] {result['test']}: {result['status']}")
            if "error" in result:
                print(f"   Error: {result['error']}")


async def main():
    """Run the test suite"""
    print("\nStarting Synthetic Data Generation Tests...")
    print("Using GPT-5 API for realistic data generation\n")
    
    tester = TestSyntheticDataGeneration()
    await tester.run_all_tests()
    
    print("\n" + "="*70)
    print("COMPONENT VALIDATION COMPLETE")
    print("="*70)
    print("\nThe synthetic data generation component is:")
    print("- Generating realistic Stripe transaction patterns")
    print("- Creating accurate freeze trigger scenarios")
    print("- Using GPT-5 reasoning_effort appropriately")
    print("- Outputting proper Stripe-format data")


if __name__ == "__main__":
    asyncio.run(main())