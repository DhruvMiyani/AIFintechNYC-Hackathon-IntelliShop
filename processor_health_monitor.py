"""
Payment Processor Health Monitoring System
Real-time monitoring for GPT-5 decision making in payment orchestration
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid
import random
import time


class ProcessorStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    DOWN = "down"
    MAINTENANCE = "maintenance"


class HealthCheckType(Enum):
    PING = "ping"
    TRANSACTION_TEST = "transaction_test"
    API_HEALTH = "api_health"
    LOAD_TEST = "load_test"


@dataclass
class ProcessorMetrics:
    """Real-time processor performance metrics"""
    processor_name: str
    success_rate: float
    avg_response_time_ms: int
    current_load: float
    freeze_risk_score: float
    uptime_percentage: float
    last_failure_time: Optional[datetime] = None
    failure_count_24h: int = 0
    total_volume_24h: int = 0
    
    # Performance thresholds
    min_success_rate: float = 0.95
    max_response_time: int = 3000
    max_freeze_risk: float = 5.0


@dataclass
class HealthCheckResult:
    """Individual health check result"""
    check_id: str
    processor: str
    check_type: HealthCheckType
    timestamp: datetime
    status: ProcessorStatus
    response_time_ms: int
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PaymentProcessorMonitor:
    """
    Real-time payment processor health monitoring system
    Provides data for GPT-5 routing decisions
    """
    
    def __init__(self):
        self.processors: Dict[str, ProcessorMetrics] = {}
        self.health_history: List[HealthCheckResult] = []
        self.monitoring_active = False
        self.check_interval = 30  # seconds
        
        # Initialize known processors
        self._initialize_processors()
    
    def _initialize_processors(self):
        """Initialize processor configurations"""
        
        processor_configs = {
            "stripe": {
                "base_success_rate": 0.989,
                "base_response_time": 245,
                "freeze_risk": 2.1,
                "api_endpoint": "https://api.stripe.com/v1/charges",
                "test_mode": True
            },
            "paypal": {
                "base_success_rate": 0.983,
                "base_response_time": 312,
                "freeze_risk": 1.8,
                "api_endpoint": "https://api.paypal.com/v1/payments",
                "test_mode": True
            },
            "visa": {
                "base_success_rate": 0.995,
                "base_response_time": 189,
                "freeze_risk": 0.9,
                "api_endpoint": "https://api.visa.com/cybersource",
                "test_mode": True
            },
            "square": {
                "base_success_rate": 0.976,
                "base_response_time": 334,
                "freeze_risk": 2.8,
                "api_endpoint": "https://connect.squareup.com/v2/payments",
                "test_mode": True
            }
        }
        
        for name, config in processor_configs.items():
            self.processors[name] = ProcessorMetrics(
                processor_name=name,
                success_rate=config["base_success_rate"],
                avg_response_time_ms=config["base_response_time"],
                current_load=random.uniform(0.1, 0.4),  # Initial load
                freeze_risk_score=config["freeze_risk"],
                uptime_percentage=99.9,
                failure_count_24h=random.randint(0, 3),
                total_volume_24h=random.randint(1000, 10000)
            )
    
    async def start_monitoring(self):
        """Start continuous processor monitoring"""
        
        print("🔍 Starting payment processor health monitoring...")
        self.monitoring_active = True
        
        # Start monitoring tasks
        monitoring_tasks = [
            asyncio.create_task(self._continuous_health_checks()),
            asyncio.create_task(self._simulate_realistic_changes()),
            asyncio.create_task(self._cleanup_old_data())
        ]
        
        try:
            await asyncio.gather(*monitoring_tasks)
        except asyncio.CancelledError:
            print("🛑 Monitoring stopped")
        finally:
            self.monitoring_active = False
    
    def stop_monitoring(self):
        """Stop processor monitoring"""
        self.monitoring_active = False
    
    async def _continuous_health_checks(self):
        """Perform continuous health checks on all processors"""
        
        while self.monitoring_active:
            try:
                # Check all processors
                check_tasks = []
                for processor_name in self.processors.keys():
                    check_tasks.append(
                        self._perform_health_check(processor_name, HealthCheckType.API_HEALTH)
                    )
                
                # Execute all checks in parallel
                results = await asyncio.gather(*check_tasks, return_exceptions=True)
                
                # Process results
                for result in results:
                    if isinstance(result, HealthCheckResult):
                        self._update_processor_metrics(result)
                        self.health_history.append(result)
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                print(f"⚠️  Health check error: {e}")
                await asyncio.sleep(5)
    
    async def _perform_health_check(
        self, 
        processor_name: str, 
        check_type: HealthCheckType
    ) -> HealthCheckResult:
        """Perform individual processor health check"""
        
        check_id = f"hc_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        try:
            if check_type == HealthCheckType.API_HEALTH:
                # Simulate API health check (mock for demo)
                await asyncio.sleep(random.uniform(0.1, 0.5))  # Simulate network call
                
                processor = self.processors[processor_name]
                
                # Determine success based on current processor state
                success = random.random() < processor.success_rate
                response_time = int(processor.avg_response_time_ms + random.uniform(-50, 100))
                
                status = ProcessorStatus.HEALTHY
                if not success:
                    status = ProcessorStatus.DEGRADED if random.random() > 0.3 else ProcessorStatus.DOWN
                elif response_time > processor.max_response_time:
                    status = ProcessorStatus.DEGRADED
                
                return HealthCheckResult(
                    check_id=check_id,
                    processor=processor_name,
                    check_type=check_type,
                    timestamp=datetime.utcnow(),
                    status=status,
                    response_time_ms=response_time,
                    success=success,
                    metadata={
                        "current_load": processor.current_load,
                        "freeze_risk": processor.freeze_risk_score
                    }
                )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return HealthCheckResult(
                check_id=check_id,
                processor=processor_name,
                check_type=check_type,
                timestamp=datetime.utcnow(),
                status=ProcessorStatus.DOWN,
                response_time_ms=processing_time,
                success=False,
                error_message=str(e)
            )
    
    def _update_processor_metrics(self, health_result: HealthCheckResult):
        """Update processor metrics based on health check results"""
        
        processor = self.processors.get(health_result.processor)
        if not processor:
            return
        
        # Update response time (moving average)
        processor.avg_response_time_ms = int(
            processor.avg_response_time_ms * 0.8 + health_result.response_time_ms * 0.2
        )
        
        # Update success rate (recent weighted average)
        if health_result.success:
            processor.success_rate = min(1.0, processor.success_rate * 0.95 + 0.05)
        else:
            processor.success_rate = max(0.0, processor.success_rate * 0.95)
            processor.failure_count_24h += 1
            processor.last_failure_time = health_result.timestamp
        
        # Update freeze risk based on recent performance
        if health_result.status == ProcessorStatus.DOWN:
            processor.freeze_risk_score = min(10.0, processor.freeze_risk_score + 0.5)
        elif health_result.status == ProcessorStatus.HEALTHY:
            processor.freeze_risk_score = max(0.0, processor.freeze_risk_score - 0.1)
        
        # Calculate uptime
        recent_checks = [
            h for h in self.health_history[-50:] 
            if h.processor == health_result.processor
        ]
        if recent_checks:
            successful_checks = sum(1 for h in recent_checks if h.success)
            processor.uptime_percentage = (successful_checks / len(recent_checks)) * 100
    
    async def _simulate_realistic_changes(self):
        """Simulate realistic processor performance changes"""
        
        while self.monitoring_active:
            try:
                # Randomly adjust processor metrics to simulate real-world changes
                for processor in self.processors.values():
                    
                    # Simulate load fluctuations
                    load_change = random.uniform(-0.1, 0.1)
                    processor.current_load = max(0.0, min(1.0, processor.current_load + load_change))
                    
                    # Simulate occasional performance degradation
                    if random.random() < 0.05:  # 5% chance per cycle
                        # Temporary degradation
                        processor.success_rate *= 0.95
                        processor.avg_response_time_ms = int(processor.avg_response_time_ms * 1.2)
                        processor.freeze_risk_score += 0.3
                    
                    # Recovery tendency
                    if processor.success_rate < 0.98:
                        processor.success_rate += 0.01
                    if processor.avg_response_time_ms > 300:
                        processor.avg_response_time_ms = int(processor.avg_response_time_ms * 0.99)
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                print(f"⚠️  Simulation error: {e}")
                await asyncio.sleep(10)
    
    async def _cleanup_old_data(self):
        """Clean up old health check data"""
        
        while self.monitoring_active:
            try:
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                
                # Remove old health history
                self.health_history = [
                    h for h in self.health_history 
                    if h.timestamp > cutoff_time
                ]
                
                # Reset 24h counters if needed
                for processor in self.processors.values():
                    if processor.last_failure_time and processor.last_failure_time < cutoff_time:
                        processor.failure_count_24h = max(0, processor.failure_count_24h - 1)
                
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                print(f"⚠️  Cleanup error: {e}")
                await asyncio.sleep(600)
    
    def get_processor_status(self, processor_name: str) -> Optional[ProcessorMetrics]:
        """Get current status of specific processor"""
        return self.processors.get(processor_name)
    
    def get_all_processor_status(self) -> Dict[str, ProcessorMetrics]:
        """Get status of all processors"""
        return self.processors.copy()
    
    def get_healthy_processors(self) -> List[str]:
        """Get list of currently healthy processors"""
        
        healthy = []
        for name, metrics in self.processors.items():
            if (metrics.success_rate >= metrics.min_success_rate and 
                metrics.avg_response_time_ms <= metrics.max_response_time and
                metrics.freeze_risk_score <= metrics.max_freeze_risk):
                healthy.append(name)
        
        return healthy
    
    def get_best_processor(self) -> Optional[str]:
        """Get the best performing processor for GPT-5 routing"""
        
        healthy_processors = self.get_healthy_processors()
        if not healthy_processors:
            # Return least bad option
            return min(
                self.processors.keys(),
                key=lambda p: self.processors[p].freeze_risk_score
            )
        
        # Score processors based on multiple factors
        def processor_score(processor_name: str) -> float:
            metrics = self.processors[processor_name]
            
            # Weighted score (higher is better)
            score = (
                metrics.success_rate * 40 +  # 40% weight on success rate
                (1 - metrics.current_load) * 20 +  # 20% weight on available capacity  
                (3000 - metrics.avg_response_time_ms) / 3000 * 20 +  # 20% weight on speed
                (10 - metrics.freeze_risk_score) / 10 * 20  # 20% weight on freeze risk
            )
            
            return score
        
        return max(healthy_processors, key=processor_score)
    
    def get_processor_ranking(self) -> List[Dict[str, Any]]:
        """Get processors ranked by performance for GPT-5 decision making"""
        
        rankings = []
        
        for name, metrics in self.processors.items():
            # Calculate composite score
            success_score = metrics.success_rate * 100
            speed_score = max(0, 100 - (metrics.avg_response_time_ms / 30))  
            load_score = (1 - metrics.current_load) * 100
            risk_score = max(0, 100 - (metrics.freeze_risk_score * 10))
            
            composite_score = (success_score + speed_score + load_score + risk_score) / 4
            
            rankings.append({
                "processor": name,
                "composite_score": composite_score,
                "success_rate": metrics.success_rate,
                "response_time_ms": metrics.avg_response_time_ms,
                "current_load": metrics.current_load,
                "freeze_risk": metrics.freeze_risk_score,
                "uptime": metrics.uptime_percentage,
                "failures_24h": metrics.failure_count_24h,
                "recommendation": self._get_recommendation(metrics)
            })
        
        # Sort by composite score (descending)
        rankings.sort(key=lambda x: x["composite_score"], reverse=True)
        
        return rankings
    
    def _get_recommendation(self, metrics: ProcessorMetrics) -> str:
        """Get recommendation for processor usage"""
        
        if metrics.success_rate < 0.90:
            return "AVOID - Poor success rate"
        elif metrics.freeze_risk_score > 7.0:
            return "CAUTION - High freeze risk"
        elif metrics.avg_response_time_ms > 2000:
            return "SLOW - High latency"
        elif metrics.current_load > 0.8:
            return "BUSY - High current load"
        elif metrics.success_rate > 0.98 and metrics.freeze_risk_score < 2.0:
            return "PREFERRED - Excellent performance"
        else:
            return "ACCEPTABLE - Standard performance"
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get summary of monitoring data for GPT-5 context"""
        
        return {
            "monitoring_active": self.monitoring_active,
            "total_processors": len(self.processors),
            "healthy_processors": len(self.get_healthy_processors()),
            "best_processor": self.get_best_processor(),
            "total_health_checks": len(self.health_history),
            "check_interval_seconds": self.check_interval,
            "last_check_time": max(h.timestamp for h in self.health_history) if self.health_history else None,
            "processor_rankings": self.get_processor_ranking(),
            "system_health_score": self._calculate_system_health_score()
        }
    
    def _calculate_system_health_score(self) -> float:
        """Calculate overall system health score"""
        
        if not self.processors:
            return 0.0
        
        total_score = 0.0
        for metrics in self.processors.values():
            processor_score = (
                metrics.success_rate * 0.4 +
                (1 - metrics.current_load) * 0.2 +
                (3000 - metrics.avg_response_time_ms) / 3000 * 0.2 +
                (10 - metrics.freeze_risk_score) / 10 * 0.2
            )
            total_score += max(0, processor_score)
        
        return (total_score / len(self.processors)) * 100


async def demo_processor_monitoring():
    """
    Demo the processor health monitoring system
    """
    
    print("🔍 PAYMENT PROCESSOR HEALTH MONITORING DEMO")
    print("=" * 60)
    print("Real-time processor monitoring for GPT-5 routing decisions")
    print("=" * 60)
    
    monitor = PaymentProcessorMonitor()
    
    print(f"\n📊 Initial processor status:")
    for name, metrics in monitor.get_all_processor_status().items():
        print(f"   {name}: {metrics.success_rate:.1%} success, {metrics.avg_response_time_ms}ms, risk={metrics.freeze_risk_score:.1f}")
    
    print(f"\n🚀 Starting monitoring for 60 seconds...")
    
    # Start monitoring task
    monitor_task = asyncio.create_task(monitor.start_monitoring())
    
    # Run demo for 60 seconds, showing updates
    start_time = datetime.utcnow()
    demo_duration = 60  # seconds
    
    try:
        while (datetime.utcnow() - start_time).seconds < demo_duration:
            await asyncio.sleep(10)  # Update every 10 seconds
            
            print(f"\n⏱️  {(datetime.utcnow() - start_time).seconds}s - Current Status:")
            
            rankings = monitor.get_processor_ranking()
            for i, ranking in enumerate(rankings[:3], 1):  # Top 3
                print(f"   {i}. {ranking['processor']}: Score={ranking['composite_score']:.1f}, {ranking['recommendation']}")
            
            best = monitor.get_best_processor()
            healthy = monitor.get_healthy_processors()
            print(f"   🏆 Best: {best} | 🟢 Healthy: {len(healthy)}/{len(monitor.processors)}")
    
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted")
    
    finally:
        print("\n🛑 Stopping monitoring...")
        monitor.stop_monitoring()
        monitor_task.cancel()
        
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
    
    # Final summary
    print(f"\n{'='*60}")
    print("📊 MONITORING SUMMARY")
    print("="*60)
    
    summary = monitor.get_monitoring_summary()
    
    print(f"🎯 RESULTS:")
    print(f"   Total Health Checks: {summary['total_health_checks']}")
    print(f"   System Health Score: {summary['system_health_score']:.1f}/100")
    print(f"   Healthy Processors: {summary['healthy_processors']}/{summary['total_processors']}")
    print(f"   Best Processor: {summary['best_processor']}")
    
    print(f"\n🏆 PROCESSOR RANKINGS:")
    for i, ranking in enumerate(summary['processor_rankings'], 1):
        print(f"   {i}. {ranking['processor']}: {ranking['composite_score']:.1f} - {ranking['recommendation']}")
    
    print(f"\n✅ Monitoring system ready for GPT-5 integration!")


if __name__ == "__main__":
    asyncio.run(demo_processor_monitoring())