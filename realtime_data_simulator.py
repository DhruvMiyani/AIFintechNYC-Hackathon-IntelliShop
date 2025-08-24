"""
Real-time Data Streaming Simulator for GPT-5 Payment Orchestration
Generates continuous Stripe transaction streams for live data pipeline
"""

import asyncio
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from claude_client import ClaudeClient
from stripe_synthetic_data_generator import GPT5StripeDataGenerator, StripeTransaction


class StreamingMode(Enum):
    NORMAL = "normal"
    HIGH_VOLUME = "high_volume"
    RISK_PATTERN = "risk_pattern"
    MIXED = "mixed"


@dataclass
class StreamData:
    transaction: StripeTransaction
    metadata: Dict[str, Any]
    stream_timestamp: datetime


class RealtimeStreamSimulator:
    """
    Simulates continuous Stripe transaction streams for data pipeline testing
    """
    
    def __init__(self):
        self.claude_client = ClaudeClient()
        self.data_generator = GPT5StripeDataGenerator()
        self.is_active = False
        self.stream_buffer = []
        self.transaction_counter = 0
        
        # Stream configuration
        self.base_rate = 2.0  # transactions per second
        self.burst_probability = 0.1
        self.risk_injection_rate = 0.05  # 5% of transactions are risky
        
    async def start_continuous_stream(
        self,
        mode: StreamingMode = StreamingMode.NORMAL,
        target_rate: float = 2.0
    ) -> AsyncGenerator[StreamData, None]:
        """
        Generate continuous transaction stream
        """
        
        self.is_active = True
        self.base_rate = target_rate
        
        print(f"Starting continuous stream in {mode.value} mode at {target_rate} TPS")
        
        while self.is_active:
            # Generate transaction
            transaction = await self._generate_stream_transaction(mode)
            
            # Create stream data
            stream_data = StreamData(
                transaction=transaction,
                metadata={
                    "stream_mode": mode.value,
                    "transaction_id": self.transaction_counter,
                    "stream_rate": self.base_rate
                },
                stream_timestamp=datetime.utcnow()
            )
            
            # Add to buffer
            self.stream_buffer.append(stream_data)
            if len(self.stream_buffer) > 1000:  # Keep buffer manageable
                self.stream_buffer = self.stream_buffer[-500:]
            
            self.transaction_counter += 1
            
            yield stream_data
            
            # Calculate next transaction delay
            delay = 1.0 / self.base_rate
            
            # Add burst patterns
            if random.random() < self.burst_probability:
                delay *= random.uniform(0.1, 0.5)  # Faster for bursts
            
            await asyncio.sleep(delay)
    
    async def _generate_stream_transaction(self, mode: StreamingMode) -> StripeTransaction:
        """
        Generate single transaction based on streaming mode
        """
        
        current_time = datetime.utcnow()
        
        # Base transaction parameters
        if mode == StreamingMode.HIGH_VOLUME:
            amount = random.uniform(20, 200)  # Smaller amounts for high volume
        elif mode == StreamingMode.RISK_PATTERN:
            amount = random.uniform(500, 2000)  # Higher amounts for risk
        else:
            amount = random.uniform(50, 500)  # Normal range
        
        # Calculate fees
        fee = amount * 0.029 + 0.30
        net = amount - fee
        
        # Determine if this should be a risky transaction
        is_risky = random.random() < self.risk_injection_rate
        risk_score = random.uniform(70, 95) if is_risky else random.uniform(5, 30)
        
        transaction = StripeTransaction(
            id=f"txn_{uuid.uuid4().hex[:24]}",
            amount=int(amount * 100),
            created=int(current_time.timestamp()),
            available_on=int((current_time + timedelta(days=2)).timestamp()),
            currency="usd",
            description=self._get_stream_description(mode, is_risky),
            fee=int(fee * 100),
            fee_details=[{
                "amount": int(fee * 100),
                "currency": "usd",
                "description": "Stripe processing fee",
                "type": "stripe_fee"
            }],
            net=int(net * 100),
            source=f"ch_{uuid.uuid4().hex[:24]}",
            type="charge",
            metadata={
                "stream_mode": mode.value,
                "risk_score": risk_score,
                "is_risky": is_risky,
                "stream_id": self.transaction_counter
            }
        )
        
        return transaction
    
    def _get_stream_description(self, mode: StreamingMode, is_risky: bool) -> str:
        """Generate realistic descriptions for stream transactions"""
        
        if is_risky:
            return random.choice([
                "Large enterprise purchase",
                "Bulk license acquisition", 
                "Premium service upgrade",
                "High-value transaction"
            ])
        
        if mode == StreamingMode.HIGH_VOLUME:
            return random.choice([
                "API usage charge",
                "Micro-transaction fee",
                "Small purchase",
                "Quick payment"
            ])
        else:
            return random.choice([
                "Monthly subscription",
                "Software license",
                "Service payment",
                "Platform fee"
            ])
    
    async def generate_batch_data(self, count: int, mode: StreamingMode) -> List[StripeTransaction]:
        """
        Generate batch of transactions for testing
        """
        
        transactions = []
        
        for i in range(count):
            transaction = await self._generate_stream_transaction(mode)
            transactions.append(transaction)
            
            # Small delay to simulate realistic timing
            await asyncio.sleep(0.01)
        
        return transactions
    
    def export_stream_buffer(self, filename: str):
        """
        Export current stream buffer to file
        """
        
        data = {
            "stream_metadata": {
                "export_timestamp": datetime.utcnow().isoformat(),
                "total_transactions": len(self.stream_buffer),
                "stream_mode": "mixed",
                "transaction_counter": self.transaction_counter
            },
            "transactions": [
                {
                    "transaction": asdict(stream_data.transaction),
                    "metadata": stream_data.metadata,
                    "stream_timestamp": stream_data.stream_timestamp.isoformat()
                }
                for stream_data in self.stream_buffer
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Exported {len(self.stream_buffer)} transactions to {filename}")
    
    def get_stream_stats(self) -> Dict[str, Any]:
        """
        Get current streaming statistics
        """
        
        if not self.stream_buffer:
            return {}
        
        transactions = [s.transaction for s in self.stream_buffer]
        amounts = [t.amount / 100 for t in transactions]
        risk_scores = [t.metadata.get("risk_score", 0) for t in transactions]
        
        return {
            "total_transactions": len(self.stream_buffer),
            "transaction_counter": self.transaction_counter,
            "avg_amount": sum(amounts) / len(amounts) if amounts else 0,
            "total_volume": sum(amounts),
            "avg_risk_score": sum(risk_scores) / len(risk_scores) if risk_scores else 0,
            "high_risk_count": sum(1 for score in risk_scores if score > 50),
            "stream_rate": self.base_rate,
            "is_active": self.is_active
        }
    
    def stop_stream(self):
        """Stop the continuous stream"""
        self.is_active = False


class StreamDataStore:
    """
    In-memory data store for streaming transactions
    """
    
    def __init__(self, max_size: int = 10000):
        self.transactions = []
        self.max_size = max_size
        self.total_processed = 0
    
    def add_transaction(self, stream_data: StreamData):
        """Add transaction to store"""
        
        self.transactions.append(stream_data)
        self.total_processed += 1
        
        # Keep store size manageable
        if len(self.transactions) > self.max_size:
            self.transactions = self.transactions[-self.max_size//2:]
    
    def get_recent_transactions(self, count: int = 100) -> List[StreamData]:
        """Get most recent transactions"""
        return self.transactions[-count:]
    
    def get_transactions_by_timerange(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[StreamData]:
        """Get transactions within time range"""
        
        return [
            data for data in self.transactions
            if start_time <= data.stream_timestamp <= end_time
        ]
    
    def get_high_risk_transactions(self, threshold: float = 50.0) -> List[StreamData]:
        """Get high risk transactions"""
        
        return [
            data for data in self.transactions
            if data.transaction.metadata.get("risk_score", 0) > threshold
        ]
    
    def export_to_jsonl(self, filename: str):
        """Export all transactions to JSONL format"""
        
        with open(filename, 'w') as f:
            for stream_data in self.transactions:
                record = {
                    "transaction": asdict(stream_data.transaction),
                    "metadata": stream_data.metadata,
                    "stream_timestamp": stream_data.stream_timestamp.isoformat()
                }
                f.write(json.dumps(record) + '\n')
        
        print(f"Exported {len(self.transactions)} transactions to {filename}")


async def demo_streaming():
    """
    Demo the streaming simulator
    """
    
    simulator = RealtimeStreamSimulator()
    data_store = StreamDataStore()
    
    print("Starting real-time transaction stream demo...")
    
    # Generate some initial data
    batch_data = await simulator.generate_batch_data(50, StreamingMode.NORMAL)
    print(f"Generated {len(batch_data)} initial transactions")
    
    # Start continuous stream for 30 seconds
    stream_duration = 30
    start_time = time.time()
    
    async for stream_data in simulator.start_continuous_stream(
        mode=StreamingMode.MIXED,
        target_rate=3.0
    ):
        data_store.add_transaction(stream_data)
        
        # Print every 10th transaction
        if stream_data.metadata["transaction_id"] % 10 == 0:
            txn = stream_data.transaction
            print(f"Transaction {stream_data.metadata['transaction_id']}: "
                  f"${txn.amount/100:.2f} (risk: {txn.metadata.get('risk_score', 0):.1f})")
        
        # Stop after duration
        if time.time() - start_time > stream_duration:
            simulator.stop_stream()
            break
    
    # Export results
    stats = simulator.get_stream_stats()
    print(f"\nStream Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Export data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    simulator.export_stream_buffer(f"stream_data_{timestamp}.json")
    data_store.export_to_jsonl(f"stream_transactions_{timestamp}.jsonl")


if __name__ == "__main__":
    asyncio.run(demo_streaming())