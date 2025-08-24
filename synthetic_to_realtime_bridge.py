#!/usr/bin/env python3
"""
Bridge between Claude Synthetic Data Generator and Real-time Routing
Sends synthetic transactions through the WebSocket for live routing visualization
"""

import asyncio
import json
import websockets
import random
from datetime import datetime
from typing import List, Dict, Any
from synthetic_data_generator import ClaudeSyntheticDataGenerator, SyntheticTransaction
from enhanced_routing_engine import EnhancedRoutingEngine, ProcessorType


class SyntheticToRealtimeBridge:
    """Connects synthetic data generation to real-time routing visualization"""
    
    def __init__(self, ws_url: str = "ws://localhost:8080"):
        self.ws_url = ws_url
        self.data_generator = ClaudeSyntheticDataGenerator()
        self.routing_engine = EnhancedRoutingEngine()
        self.websocket = None
        
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            print(f"✅ Connected to WebSocket at {self.ws_url}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to WebSocket: {e}")
            return False
    
    async def send_synthetic_transaction(self, transaction: SyntheticTransaction):
        """Send a synthetic transaction through the WebSocket for real-time routing"""
        if not self.websocket:
            print("❌ WebSocket not connected")
            return
            
        # Convert synthetic transaction to routing format
        routing_transaction = {
            "id": transaction.id,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "description": transaction.description or f"Synthetic transaction {transaction.type}",
            "customer_email": f"customer_{transaction.customer_id}@example.com" if transaction.customer_id else "synthetic@example.com",
            "metadata": {
                "type": transaction.type,
                "card_brand": transaction.card_brand,
                "status": transaction.status,
                "created": transaction.created.isoformat()
            }
        }
        
        # Send to WebSocket for routing
        message = {
            "command": "route_transaction",
            "transaction": routing_transaction
        }
        
        await self.websocket.send(json.dumps(message))
        print(f"📤 Sent synthetic transaction {transaction.id} for routing")
        
    async def generate_and_route_batch(
        self, 
        count: int = 10,
        pattern: str = "normal",
        delay_ms: int = 500
    ):
        """Generate synthetic transactions and send them for real-time routing"""
        
        print(f"🔄 Generating {count} synthetic transactions with pattern: {pattern}")
        
        transactions = []
        
        if pattern == "normal":
            # Generate normal baseline transactions
            transactions = await self.data_generator.generate_normal_baseline(
                days=1,
                daily_volume=count,
                avg_amount=random.uniform(50, 200)
            )
        elif pattern == "high_risk":
            # Generate high-risk pattern
            transactions = await self.data_generator.generate_freeze_trigger_pattern(
                pattern_type="sudden_spike",
                duration_hours=1,
                intensity=10.0
            )
        elif pattern == "refunds":
            # Generate high refund rate pattern
            transactions = await self.data_generator.generate_freeze_trigger_pattern(
                pattern_type="high_refund_rate",
                duration_hours=1,
                intensity=5.0
            )
        else:
            # Mixed patterns
            normal = await self.data_generator.generate_normal_baseline(days=1, daily_volume=count//2)
            risky = await self.data_generator.generate_freeze_trigger_pattern(
                pattern_type="pattern_deviation",
                duration_hours=1,
                intensity=3.0
            )
            transactions = normal + risky
            random.shuffle(transactions)
        
        # Send transactions through WebSocket with delay
        for transaction in transactions[:count]:
            await self.send_synthetic_transaction(transaction)
            await asyncio.sleep(delay_ms / 1000.0)
            
        print(f"✅ Sent {len(transactions[:count])} synthetic transactions for routing")
        
    async def start_continuous_generation(
        self,
        transactions_per_minute: int = 12,
        pattern_mix: Dict[str, float] = None
    ):
        """Continuously generate and route synthetic transactions"""
        
        if pattern_mix is None:
            pattern_mix = {
                "normal": 0.7,
                "high_risk": 0.15,
                "refunds": 0.1,
                "mixed": 0.05
            }
        
        delay_ms = 60000 // transactions_per_minute  # Calculate delay between transactions
        
        print(f"🚀 Starting continuous generation: {transactions_per_minute} transactions/minute")
        print(f"📊 Pattern mix: {pattern_mix}")
        
        while True:
            # Choose pattern based on mix probabilities
            rand = random.random()
            cumulative = 0
            pattern = "normal"
            
            for p, prob in pattern_mix.items():
                cumulative += prob
                if rand < cumulative:
                    pattern = p
                    break
            
            # Generate and send single transaction
            await self.generate_and_route_batch(
                count=1,
                pattern=pattern,
                delay_ms=0
            )
            
            await asyncio.sleep(delay_ms / 1000.0)


async def main():
    """Main function for testing the bridge"""
    bridge = SyntheticToRealtimeBridge()
    
    # Connect to WebSocket
    if not await bridge.connect():
        print("Failed to connect to WebSocket server")
        return
    
    print("\n" + "="*60)
    print("🌉 Synthetic Data to Real-time Routing Bridge")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1. Generate 10 normal transactions")
        print("2. Generate 10 high-risk transactions")
        print("3. Generate 10 refund-heavy transactions")
        print("4. Generate 20 mixed transactions")
        print("5. Start continuous generation")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            await bridge.generate_and_route_batch(10, "normal", 500)
        elif choice == "2":
            await bridge.generate_and_route_batch(10, "high_risk", 500)
        elif choice == "3":
            await bridge.generate_and_route_batch(10, "refunds", 500)
        elif choice == "4":
            await bridge.generate_and_route_batch(20, "mixed", 300)
        elif choice == "5":
            try:
                await bridge.start_continuous_generation()
            except KeyboardInterrupt:
                print("\n⏹️ Stopping continuous generation")
        elif choice == "6":
            break
        else:
            print("Invalid option")
    
    await bridge.websocket.close()
    print("👋 Bridge closed")


if __name__ == "__main__":
    asyncio.run(main())