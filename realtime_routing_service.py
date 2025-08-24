#!/usr/bin/env python3
"""
Real-time Payment Routing Service
WebSocket-based live routing demonstration with processor health monitoring
"""

import asyncio
import json
import random
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcessorStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"  
    FROZEN = "frozen"
    UNAVAILABLE = "unavailable"

class RoutingAction(Enum):
    EVALUATING = "evaluating"
    SELECTED = "selected"
    REJECTED = "rejected"
    FALLBACK = "fallback"

@dataclass
class ProcessorHealth:
    name: str
    status: ProcessorStatus
    risk: float
    freeze_resistance: float
    last_update: float
    issues: List[str]
    color: str
    
    def to_dict(self):
        return {
            'name': self.name,
            'status': self.status.value,
            'risk': self.risk,
            'freezeResistance': self.freeze_resistance,
            'lastUpdate': self.last_update,
            'issues': self.issues,
            'color': self.color
        }

@dataclass
class RoutingStep:
    step: int
    timestamp: float
    processor: str
    action: RoutingAction
    reason: str
    confidence: float
    processing_time: int
    
    def to_dict(self):
        return {
            'step': self.step,
            'timestamp': self.timestamp,
            'processor': self.processor,
            'action': self.action.value,
            'reason': self.reason,
            'confidence': self.confidence,
            'processingTime': self.processing_time
        }

@dataclass
class Transaction:
    id: str
    amount: float
    description: str
    currency: str
    status: str
    selected_processor: str = None
    routing_steps: List[RoutingStep] = None
    start_time: float = None
    
    def __post_init__(self):
        if self.routing_steps is None:
            self.routing_steps = []
        if self.start_time is None:
            self.start_time = time.time()
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'description': self.description,
            'currency': self.currency,
            'status': self.status,
            'selectedProcessor': self.selected_processor,
            'routingSteps': [step.to_dict() for step in self.routing_steps],
            'startTime': self.start_time
        }

class RealtimeRoutingEngine:
    """
    Real-time payment routing engine with WebSocket broadcasting
    """
    
    def __init__(self):
        self.processors = self._initialize_processors()
        self.connected_clients = set()
        self.active_transactions = []
        self.simulation_running = False
        
        # Transaction templates for simulation
        self.transaction_templates = [
            {"amount": 500, "description": "B2B software subscription", "currency": "USD"},
            {"amount": 200, "description": "NFT marketplace purchase", "currency": "USD"},
            {"amount": 1500, "description": "Enterprise software license", "currency": "USD"},
            {"amount": 300, "description": "DeFi protocol payment", "currency": "USDC"},
            {"amount": 75, "description": "Consumer purchase", "currency": "USD"},
            {"amount": 800, "description": "Web3 gaming token purchase", "currency": "USD"},
            {"amount": 2500, "description": "Cross-border remittance", "currency": "USD"},
            {"amount": 150, "description": "Retail POS payment", "currency": "USD"},
        ]
    
    def _initialize_processors(self) -> Dict[str, ProcessorHealth]:
        """Initialize processor health states"""
        return {
            'stripe': ProcessorHealth(
                name='Stripe',
                status=ProcessorStatus.FROZEN,
                risk=95.0,
                freeze_resistance=30.0,
                last_update=time.time(),
                issues=['Chargeback rate: 100%', 'Refund rate: 123%'],
                color='#E11D48'
            ),
            'paypal': ProcessorHealth(
                name='PayPal',
                status=ProcessorStatus.HEALTHY,
                risk=15.0,
                freeze_resistance=60.0,
                last_update=time.time(),
                issues=[],
                color='#10B981'
            ),
            'square': ProcessorHealth(
                name='Square',
                status=ProcessorStatus.HEALTHY,
                risk=20.0,
                freeze_resistance=70.0,
                last_update=time.time(),
                issues=[],
                color='#10B981'
            ),
            'visa': ProcessorHealth(
                name='Visa',
                status=ProcessorStatus.HEALTHY,
                risk=8.0,
                freeze_resistance=90.0,
                last_update=time.time(),
                issues=[],
                color='#10B981'
            ),
            'crossmint': ProcessorHealth(
                name='Crossmint',
                status=ProcessorStatus.HEALTHY,
                risk=5.0,
                freeze_resistance=95.0,
                last_update=time.time(),
                issues=[],
                color='#8B5CF6'
            )
        }
    
    async def register_client(self, websocket):
        """Register a new WebSocket client"""
        self.connected_clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.connected_clients)}")
        
        # Send initial state
        await self.send_processor_health_update()
        
    async def unregister_client(self, websocket):
        """Unregister a WebSocket client"""
        self.connected_clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.connected_clients)}")
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.connected_clients:
            return
        
        message_str = json.dumps(message)
        
        # Send to all clients
        disconnected = []
        for client in self.connected_clients:
            try:
                await client.send(message_str)
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(client)
        
        # Remove disconnected clients
        for client in disconnected:
            self.connected_clients.discard(client)
    
    async def send_processor_health_update(self):
        """Send processor health update to all clients"""
        message = {
            'type': 'processor_health',
            'data': [processor.to_dict() for processor in self.processors.values()],
            'timestamp': time.time()
        }
        await self.broadcast_message(message)
    
    async def simulate_processor_health_changes(self):
        """Simulate dynamic processor health changes"""
        while self.simulation_running:
            # Random processor health changes
            for processor_key, processor in self.processors.items():
                rand = random.random()
                
                if processor_key == 'stripe':
                    # Stripe occasionally recovers from freeze
                    if rand < 0.05:  # 5% chance
                        if processor.status == ProcessorStatus.FROZEN:
                            processor.status = ProcessorStatus.WARNING
                            processor.risk = 60.0
                            processor.issues = ['Elevated refund rate: 8%']
                        else:
                            processor.status = ProcessorStatus.FROZEN
                            processor.risk = 95.0
                            processor.issues = ['Chargeback rate: 100%', 'Refund rate: 123%']
                        
                        processor.last_update = time.time()
                
                elif rand < 0.02:  # 2% chance for other processors
                    if processor.status == ProcessorStatus.HEALTHY:
                        processor.status = ProcessorStatus.WARNING
                        processor.risk = min(50, processor.risk + 20)
                        processor.issues = ['Temporary network issues']
                    else:
                        processor.status = ProcessorStatus.HEALTHY
                        processor.risk = max(5, processor.risk - 10)
                        processor.issues = []
                    
                    processor.last_update = time.time()
            
            await self.send_processor_health_update()
            await asyncio.sleep(3)  # Update every 3 seconds
    
    async def process_transaction(self, template: Dict[str, Any]):
        """Process a single transaction with real-time routing"""
        
        # Create transaction
        transaction = Transaction(
            id=f"txn_{uuid.uuid4().hex[:12]}",
            amount=template["amount"],
            description=template["description"],
            currency=template["currency"],
            status="routing"
        )
        
        self.active_transactions.insert(0, transaction)
        if len(self.active_transactions) > 10:
            self.active_transactions.pop()
        
        # Broadcast new transaction
        await self.broadcast_message({
            'type': 'new_transaction',
            'data': transaction.to_dict(),
            'timestamp': time.time()
        })
        
        # Simulate Claude routing process
        await self._simulate_claude_routing(transaction)
    
    async def _simulate_claude_routing(self, transaction: Transaction):
        """Simulate Claude's intelligent routing process"""
        
        steps = []
        step_num = 1
        
        # Step 1: Context Analysis
        await asyncio.sleep(0.5)
        step = RoutingStep(
            step=step_num,
            timestamp=time.time(),
            processor='Claude',
            action=RoutingAction.EVALUATING,
            reason=f'Analyzing: "{transaction.description}" - ${transaction.amount}',
            confidence=0,
            processing_time=500
        )
        steps.append(step)
        transaction.routing_steps = steps
        
        await self.broadcast_message({
            'type': 'routing_step',
            'transaction_id': transaction.id,
            'step': step.to_dict(),
            'timestamp': time.time()
        })
        step_num += 1
        
        # Step 2: Processor Health Check
        await asyncio.sleep(0.8)
        healthy_count = sum(1 for p in self.processors.values() if p.status == ProcessorStatus.HEALTHY)
        step = RoutingStep(
            step=step_num,
            timestamp=time.time(),
            processor='Claude',
            action=RoutingAction.EVALUATING,
            reason=f'Processor health check: {healthy_count}/5 processors healthy',
            confidence=0,
            processing_time=800
        )
        steps.append(step)
        
        await self.broadcast_message({
            'type': 'routing_step',
            'transaction_id': transaction.id,
            'step': step.to_dict(),
            'timestamp': time.time()
        })
        step_num += 1
        
        # Step 3: Initial Processor Selection
        await asyncio.sleep(0.6)
        initial_processor = self._get_optimal_processor(transaction)
        
        # Check if initial selection is available
        processor_health = self.processors.get(initial_processor.lower())
        if processor_health and processor_health.status == ProcessorStatus.FROZEN:
            # Demonstrate re-routing
            step = RoutingStep(
                step=step_num,
                timestamp=time.time(),
                processor=initial_processor,
                action=RoutingAction.REJECTED,
                reason=f'Primary processor frozen - account freeze risk: {processor_health.risk:.0f}%',
                confidence=0,
                processing_time=600
            )
            steps.append(step)
            
            await self.broadcast_message({
                'type': 'routing_step',
                'transaction_id': transaction.id,
                'step': step.to_dict(),
                'timestamp': time.time()
            })
            step_num += 1
            
            # Select fallback processor
            await asyncio.sleep(0.4)
            fallback_processor = self._get_fallback_processor(transaction)
            step = RoutingStep(
                step=step_num,
                timestamp=time.time(),
                processor=fallback_processor,
                action=RoutingAction.FALLBACK,
                reason=f'Auto-rerouting to {fallback_processor} (freeze avoidance active)',
                confidence=92,
                processing_time=400
            )
            steps.append(step)
            selected_processor = fallback_processor
            
        else:
            # Direct selection
            step = RoutingStep(
                step=step_num,
                timestamp=time.time(),
                processor=initial_processor,
                action=RoutingAction.SELECTED,
                reason=self._get_selection_reason(initial_processor, transaction),
                confidence=95,
                processing_time=600
            )
            steps.append(step)
            selected_processor = initial_processor
        
        await self.broadcast_message({
            'type': 'routing_step',
            'transaction_id': transaction.id,
            'step': step.to_dict(),
            'timestamp': time.time()
        })
        step_num += 1
        
        # Step 4: Finalize
        await asyncio.sleep(0.3)
        step = RoutingStep(
            step=step_num,
            timestamp=time.time(),
            processor=selected_processor,
            action=RoutingAction.SELECTED,
            reason=f'Payment routed to {selected_processor} - processing initiated',
            confidence=100,
            processing_time=300
        )
        steps.append(step)
        
        transaction.selected_processor = selected_processor
        transaction.status = 'completed'
        
        await self.broadcast_message({
            'type': 'routing_step',
            'transaction_id': transaction.id,
            'step': step.to_dict(),
            'timestamp': time.time()
        })
        
        # Final transaction update
        await self.broadcast_message({
            'type': 'transaction_complete',
            'data': transaction.to_dict(),
            'timestamp': time.time()
        })
    
    def _get_optimal_processor(self, transaction: Transaction) -> str:
        """Get optimal processor for transaction"""
        desc = transaction.description.lower()
        
        # Crypto/Web3 keywords -> Crossmint
        crypto_keywords = ['nft', 'defi', 'crypto', 'web3', 'token', 'blockchain']
        if any(keyword in desc for keyword in crypto_keywords):
            return 'Crossmint'
        
        # High value -> Visa
        if transaction.amount > 1000:
            return 'Visa'
        
        # B2B/Enterprise -> Stripe
        if any(keyword in desc for keyword in ['b2b', 'enterprise', 'software', 'subscription']):
            return 'Stripe'
        
        # Retail -> Square
        if 'retail' in desc or 'pos' in desc:
            return 'Square'
        
        # Default -> PayPal
        return 'PayPal'
    
    def _get_fallback_processor(self, transaction: Transaction) -> str:
        """Get fallback processor when primary is unavailable"""
        healthy_processors = [
            (name, processor) for name, processor in self.processors.items()
            if processor.status == ProcessorStatus.HEALTHY
        ]
        
        # Sort by freeze resistance
        healthy_processors.sort(key=lambda x: x[1].freeze_resistance, reverse=True)
        
        desc = transaction.description.lower()
        
        # For crypto, prefer Crossmint if healthy
        crypto_keywords = ['nft', 'defi', 'crypto', 'web3', 'token', 'blockchain']
        if any(keyword in desc for keyword in crypto_keywords):
            if any(name == 'crossmint' for name, _ in healthy_processors):
                return 'Crossmint'
        
        # For high amounts, prefer Visa
        if transaction.amount > 1000:
            if any(name == 'visa' for name, _ in healthy_processors):
                return 'Visa'
        
        # Otherwise, use the processor with highest freeze resistance
        return healthy_processors[0][0].title() if healthy_processors else 'PayPal'
    
    def _get_selection_reason(self, processor: str, transaction: Transaction) -> str:
        """Get reason for processor selection"""
        reasons = {
            'Crossmint': 'Web3/Crypto transaction detected',
            'Visa': 'High-value enterprise transaction', 
            'Stripe': 'B2B/SaaS transaction optimized',
            'PayPal': 'Consumer-friendly processor selected',
            'Square': 'Retail/POS transaction optimized'
        }
        return reasons.get(processor, 'Default routing logic applied')
    
    async def start_simulation(self):
        """Start the real-time simulation"""
        if self.simulation_running:
            return
            
        self.simulation_running = True
        logger.info("Starting real-time routing simulation")
        
        # Start processor health monitoring
        asyncio.create_task(self.simulate_processor_health_changes())
        
        # Start transaction processing
        asyncio.create_task(self._transaction_generator())
    
    async def stop_simulation(self):
        """Stop the real-time simulation"""
        self.simulation_running = False
        logger.info("Stopping real-time routing simulation")
    
    async def _transaction_generator(self):
        """Generate transactions at random intervals"""
        while self.simulation_running:
            # Random delay between transactions (5-13 seconds)
            await asyncio.sleep(random.uniform(5.0, 13.0))
            
            if self.simulation_running:
                template = random.choice(self.transaction_templates)
                await self.process_transaction(template)

# WebSocket handler
async def websocket_handler(websocket, path):
    """Handle WebSocket connections"""
    routing_engine = RealtimeRoutingEngine()
    
    try:
        await routing_engine.register_client(websocket)
        
        async for message in websocket:
            try:
                data = json.loads(message)
                command = data.get('command')
                
                if command == 'start_simulation':
                    await routing_engine.start_simulation()
                    await websocket.send(json.dumps({
                        'type': 'simulation_status',
                        'running': True,
                        'timestamp': time.time()
                    }))
                
                elif command == 'stop_simulation':
                    await routing_engine.stop_simulation()
                    await websocket.send(json.dumps({
                        'type': 'simulation_status',
                        'running': False,
                        'timestamp': time.time()
                    }))
                
            except json.JSONDecodeError:
                logger.warning("Received invalid JSON message")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await routing_engine.unregister_client(websocket)

# Main server
async def main():
    """Start the WebSocket server"""
    logger.info("Starting Real-time Routing WebSocket Server on ws://localhost:8080")
    
    async with websockets.serve(websocket_handler, "localhost", 8080):
        logger.info("Server started. Waiting for connections...")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())