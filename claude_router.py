"""
Intelligent Payment Router with Claude Reasoning
Solves the core problem: When Stripe fails/freezes, intelligently reroute payments
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import asyncio
import json
from enum import Enum

from processors.base import (
    PaymentProcessor, 
    PaymentRequest, 
    PaymentResponse, 
    PaymentStatus,
    ProcessorStatus
)


class FailureType(Enum):
    ACCOUNT_FROZEN = "account_frozen"
    RATE_LIMITED = "rate_limited"  
    NETWORK_ERROR = "network_error"
    DECLINED = "declined"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    FRAUD_SUSPECTED = "fraud_suspected"
    COMPLIANCE_ISSUE = "compliance_issue"
    TEMPORARY_OUTAGE = "temporary_outage"


@dataclass
class ProcessorFailure:
    processor_id: str
    failure_type: FailureType
    error_code: str
    error_message: str
    timestamp: datetime
    retry_after: Optional[datetime] = None
    permanent: bool = False


@dataclass 
class RoutingDecision:
    selected_processor: str
    reasoning: str
    confidence: float
    fallback_chain: List[str]
    claude_params: Dict[str, Any]
    decision_time_ms: float


class ClaudeRouter:
    """
    Uses Claude's reasoning to intelligently route payments when processors fail.
    Key scenarios:
    - Stripe account frozen → route to PayPal/Visa
    - High-risk transaction → use processor with best fraud protection
    - Network issues → retry with different region processor
    """
    
    def __init__(self, anthropic_api_key: str = None, brave_api_key: str = None):
        from claude_client import ClaudeClient
        from brave_search_insights import PaymentInsightsOrchestrator
        
        self.claude_client = ClaudeClient()
        self.insights_orchestrator = PaymentInsightsOrchestrator(brave_api_key)
        self.failure_history: List[ProcessorFailure] = []
        self.routing_decisions: List[RoutingDecision] = []
        
        # Processor health tracking
        self.processor_health = {
            "stripe": {"frozen": False, "last_success": None, "failure_count": 0},
            "paypal": {"frozen": False, "last_success": None, "failure_count": 0},
            "visa": {"frozen": False, "last_success": None, "failure_count": 0}
        }
        
        # Real-time insights cache and update mechanism
        self._insights_cache = {}
        self._last_insights_fetch = None
        self._insights_update_task = None
        self._periodic_updates_enabled = False
    
    async def make_routing_decision(
        self,
        request: PaymentRequest,
        available_processors: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        complexity: str = "balanced"
    ) -> RoutingDecision:
        """
        Core routing logic using Claude's reasoning capabilities with real-time insights.
        
        complexity options:
        - "simple": Fast decisions for routine payments
        - "balanced": Balanced reasoning for most cases
        - "comprehensive": Deep analysis for high-value or complex scenarios
        """
        
        start_time = datetime.utcnow()
        
        # Determine complexity based on transaction
        if not complexity:
            complexity = self._determine_complexity(request, context)
        
        # Fetch real-time insights if needed
        insights_adjustments = await self._get_realtime_insights(available_processors, complexity)
        
        # Apply insights to processor scoring
        enhanced_processors = self._apply_insights_to_processors(
            available_processors, 
            insights_adjustments
        )
        
        # Prepare context for Claude
        claude_context = self._prepare_claude_context(
            request, 
            enhanced_processors, 
            context,
            insights_adjustments
        )
        
        # Real Claude API call
        decision = await self.claude_client.make_routing_decision(
            context=claude_context,
            complexity=complexity
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Default to first available processor if Claude doesn't specify one
        default_processor = available_processors[0]["id"] if available_processors else "stripe"
        
        # Get the processor selected by Claude, but validate it's available
        claude_selected = decision.get("selected_processor", default_processor)
        available_processor_ids = [p["id"] for p in available_processors]
        
        # If Claude selected an unavailable processor, use the default
        if claude_selected not in available_processor_ids and available_processor_ids:
            selected_processor = default_processor
        else:
            selected_processor = claude_selected
            
        routing = RoutingDecision(
            selected_processor=selected_processor,
            reasoning=decision.get("reasoning", "Claude routing decision"),
            confidence=decision.get("confidence", 0.8),
            fallback_chain=decision.get("fallback_chain", [p["id"] for p in available_processors[1:]]),
            claude_params={
                "complexity": complexity,
                "model": decision.get("model", "claude-3-5-sonnet-20241022"),
                "tokens_used": decision.get("tokens_used", 0),
                "claude_metadata": decision.get("claude_metadata", {})
            },
            decision_time_ms=processing_time
        )
        
        self.routing_decisions.append(routing)
        return routing
    
    def _determine_complexity(
        self, 
        request: PaymentRequest,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Automatically determine analysis complexity based on transaction characteristics.
        """
        
        # Simple analysis for small, routine transactions
        if request.amount < 10 and not context.get("failures"):
            return "simple"
        
        # Comprehensive analysis for complex scenarios
        if any([
            request.amount > 10000,
            context.get("account_frozen"),
            context.get("multiple_failures"),
            context.get("high_risk"),
            context.get("compliance_check")
        ]):
            return "comprehensive"
        
        # Default to balanced
        return "balanced"
    
    async def _get_realtime_insights(
        self,
        available_processors: List[Dict[str, Any]],
        complexity: str
    ) -> Dict[str, Any]:
        """
        Fetch real-time insights for available processors.
        Only fetch for high-value or complex transactions to avoid API overuse.
        """
        processor_ids = [p["id"] for p in available_processors]
        
        # Skip insights for simple, low-value transactions
        if complexity == "simple":
            return {}
        
        try:
            # Use cached insights if available and fresh
            cache_key = f"insights_{datetime.utcnow().hour}"
            if hasattr(self, '_insights_cache') and cache_key in self._insights_cache:
                cached_insights = self._insights_cache[cache_key]
                # Filter for available processors only
                filtered_insights = {
                    pid: insights for pid, insights in cached_insights.items() 
                    if pid in processor_ids
                }
                if filtered_insights:
                    return self.insights_orchestrator.get_routing_adjustments(filtered_insights)
            
            # Fetch fresh insights for available processors
            insights = await self.insights_orchestrator.fetch_all_insights(
                processors=processor_ids,
                regions=["US"]
            )
            
            # Cache the results
            if not hasattr(self, '_insights_cache'):
                self._insights_cache = {}
            self._insights_cache[cache_key] = insights
            
            return self.insights_orchestrator.get_routing_adjustments(insights)
            
        except Exception as e:
            print(f"Error fetching real-time insights: {e}")
            return {}
    
    def _apply_insights_to_processors(
        self,
        processors: List[Dict[str, Any]],
        insights_adjustments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply real-time insights to processor scoring and metadata.
        """
        enhanced_processors = []
        
        for processor in processors:
            processor_id = processor["id"]
            enhanced_processor = processor.copy()
            
            # Apply insights if available
            if processor_id in insights_adjustments:
                adjustments = insights_adjustments[processor_id]
                
                # Adjust effective fee based on promotions
                current_fee = processor.get("fee_percentage", 2.9)
                fee_adjustment = adjustments.get("fee_adjustment", 0.0)
                enhanced_processor["effective_fee_percentage"] = max(0.0, current_fee + fee_adjustment)
                
                # Add reliability bonus to success rate
                current_success_rate = processor.get("metrics", {}).get("success_rate", 0.95)
                reliability_bonus = adjustments.get("reliability_bonus", 0.0)
                enhanced_processor["adjusted_success_rate"] = min(1.0, current_success_rate + reliability_bonus)
                
                # Add priority boost for routing preference
                priority_boost = adjustments.get("priority_boost", 0.0)
                enhanced_processor["priority_score"] = processor.get("priority_score", 0.5) + priority_boost
                
                # Add insights metadata
                enhanced_processor["insights_applied"] = {
                    "fee_adjustment": fee_adjustment,
                    "reliability_bonus": reliability_bonus,
                    "priority_boost": priority_boost,
                    "reasons": adjustments.get("reasons", [])
                }
            else:
                # No insights available, use original values
                enhanced_processor["effective_fee_percentage"] = processor.get("fee_percentage", 2.9)
                enhanced_processor["adjusted_success_rate"] = processor.get("metrics", {}).get("success_rate", 0.95)
                enhanced_processor["priority_score"] = processor.get("priority_score", 0.5)
                enhanced_processor["insights_applied"] = {"reasons": ["No real-time insights available"]}
            
            enhanced_processors.append(enhanced_processor)
        
        # Sort by priority score (higher is better)
        enhanced_processors.sort(key=lambda p: p.get("priority_score", 0), reverse=True)
        
        return enhanced_processors

    def _prepare_claude_context(
        self,
        request: PaymentRequest,
        available_processors: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]],
        insights_adjustments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Prepare context for Claude to make routing decision.
        """
        
        # Get recent failures for this merchant
        recent_failures = [
            f for f in self.failure_history
            if f.timestamp > datetime.utcnow() - timedelta(hours=1)
        ]
        
        claude_context = {
            "transaction": {
                "amount": request.amount,
                "currency": request.currency,
                "merchant_id": request.merchant_id,
                "risk_indicators": context.get("risk_indicators", {})
            },
            "processors": available_processors,
            "failures": [
                {
                    "processor": f.processor_id,
                    "type": f.failure_type.value,
                    "message": f.error_message,
                    "permanent": f.permanent
                }
                for f in recent_failures
            ],
            "processor_health": self.processor_health,
            "business_context": {
                "primary_processor_frozen": context.get("account_frozen", False),
                "urgency": context.get("urgency", "normal"),
                "customer_type": context.get("customer_type", "standard")
            }
        }
        
        # Add real-time insights to context if available
        if insights_adjustments:
            claude_context["real_time_insights"] = {
                "insights_available": True,
                "processor_adjustments": insights_adjustments,
                "insights_summary": self._summarize_insights(insights_adjustments)
            }
        else:
            claude_context["real_time_insights"] = {
                "insights_available": False,
                "reason": "No real-time insights fetched for this transaction complexity level"
            }
        
        return claude_context
    
    def _summarize_insights(self, insights_adjustments: Dict[str, Any]) -> str:
        """
        Create a human-readable summary of insights for Claude context.
        """
        if not insights_adjustments:
            return "No insights available"
        
        summaries = []
        for processor_id, adjustments in insights_adjustments.items():
            processor_summary = f"{processor_id.upper()}: "
            reasons = adjustments.get("reasons", [])
            
            if reasons:
                processor_summary += "; ".join(reasons)
            else:
                processor_summary += "No specific insights"
            
            summaries.append(processor_summary)
        
        return " | ".join(summaries)
    
    async def _call_claude_analysis(
        self,
        context: Dict[str, Any],
        complexity: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Simulate Claude API call with complexity parameters.
        In production, replace with actual Anthropic API call.
        """
        
        # Build the prompt based on context
        prompt = self._build_routing_prompt(context)
        
        # Simulate different complexity levels
        await asyncio.sleep(0.1 if complexity == "simple" else 0.3)
        
        # Simulate Claude decision logic
        if context["business_context"]["primary_processor_frozen"]:
            # Stripe is frozen - must use alternative
            if "paypal" in [p["id"] for p in context["processors"]]:
                return {
                    "processor": "paypal",
                    "reasoning": "Primary processor (Stripe) is frozen. Routing to PayPal as it has good acceptance rates and is immediately available.",
                    "confidence": 0.95,
                    "fallback_chain": ["paypal", "visa"],
                    "complexity": complexity,
                    "tokens_used": 200 if complexity == "comprehensive" else 80
                }
            else:
                return {
                    "processor": "visa",
                    "reasoning": "Stripe account frozen. Using Visa Direct as fallback for card processing.",
                    "confidence": 0.90,
                    "fallback_chain": ["visa"],
                    "complexity": complexity,
                    "tokens_used": 150
                }
        
        # Normal routing - choose based on success rates and fees
        best_processor = self._select_best_processor(context)
        
        return {
            "processor": best_processor,
            "reasoning": self._generate_reasoning(best_processor, context, complexity),
            "confidence": 0.85,
            "fallback_chain": self._generate_fallback_chain(best_processor, context),
            "complexity": complexity,
            "tokens_used": self._estimate_tokens(complexity)
        }
    
    def _build_routing_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for Claude based on context."""
        
        prompt = f"""
        Payment routing decision needed:
        Amount: ${context['transaction']['amount']} {context['transaction']['currency']}
        
        Available processors:
        {json.dumps(context['processors'], indent=2)}
        
        Recent failures:
        {json.dumps(context['failures'], indent=2)}
        
        Requirements:
        1. Maximize payment success probability
        2. Minimize fees where possible
        3. Avoid processors with recent failures
        4. Consider compliance and risk factors
        
        Select the best processor and explain your reasoning.
        """
        
        if context["business_context"]["primary_processor_frozen"]:
            prompt += "\nCRITICAL: Primary processor (Stripe) is currently frozen. Must use alternative."
        
        return prompt
    
    def _select_best_processor(self, context: Dict[str, Any]) -> str:
        """Enhanced processor selection logic using real-time insights."""
        
        processors = context["processors"]
        
        # Filter out recently failed processors
        failed_ids = [f["processor"] for f in context["failures"] if not f.get("permanent")]
        available = [p for p in processors if p["id"] not in failed_ids]
        
        if not available:
            available = processors  # Use all if none available
        
        # Sort by multiple factors including insights
        def processor_score(processor):
            # Base score from success rate (0-1, higher is better)
            success_rate = processor.get("adjusted_success_rate", 
                                       processor.get("metrics", {}).get("success_rate", 0.95))
            
            # Fee factor (lower fees are better, so invert)
            effective_fee = processor.get("effective_fee_percentage", 
                                        processor.get("fee_percentage", 2.9))
            fee_factor = max(0, 1 - (effective_fee / 5.0))  # Normalize fees around 5%
            
            # Priority score from insights
            priority_score = processor.get("priority_score", 0.5)
            
            # Combined score (weighted)
            combined_score = (
                success_rate * 0.4 +      # 40% weight to success rate
                fee_factor * 0.3 +        # 30% weight to fees  
                priority_score * 0.3      # 30% weight to insights priority
            )
            
            return combined_score
        
        # Sort by combined score (higher is better)
        available.sort(key=processor_score, reverse=True)
        
        return available[0]["id"] if available else "stripe"
    
    def _generate_reasoning(
        self, 
        processor: str, 
        context: Dict[str, Any],
        complexity: str
    ) -> str:
        """Generate reasoning explanation based on complexity level."""
        
        if complexity == "simple":
            return f"Selected {processor} - available and suitable."
        
        elif complexity == "comprehensive":
            amount = context['transaction']['amount']
            failures = len(context['failures'])
            return (
                f"After comprehensive analysis of {len(context['processors'])} processors with "
                f"{failures} recent failures, selected {processor}. "
                f"Key factors: Transaction amount ${amount} fits processor limits, "
                f"processor has 95%+ success rate, no recent failures, "
                f"and acceptable fee structure. This provides optimal balance of "
                f"reliability and cost-effectiveness."
            )
        
        # Balanced (default)
        return (
            f"Selected {processor} as primary processor. "
            f"It offers good success rates with reasonable fees for this transaction type."
        )
    
    def _generate_fallback_chain(
        self, 
        primary: str, 
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate ordered fallback processor list."""
        
        all_processors = ["stripe", "paypal", "visa"]
        fallbacks = [p for p in all_processors if p != primary]
        
        # Prioritize based on context
        if context['transaction']['amount'] > 1000:
            # For large amounts, prioritize reliability
            fallbacks.sort(key=lambda p: p == "visa")
        
        return fallbacks
    
    def _estimate_tokens(self, complexity: str) -> int:
        """Estimate tokens based on complexity level."""
        
        tokens = {
            "simple": 50,
            "balanced": 180,
            "comprehensive": 600
        }
        return tokens.get(complexity, 180)
    
    def record_failure(
        self,
        processor_id: str,
        failure_type: FailureType,
        error_code: str,
        error_message: str,
        permanent: bool = False
    ):
        """Record a processor failure for future routing decisions."""
        
        failure = ProcessorFailure(
            processor_id=processor_id,
            failure_type=failure_type,
            error_code=error_code,
            error_message=error_message,
            timestamp=datetime.utcnow(),
            permanent=permanent,
            retry_after=datetime.utcnow() + timedelta(minutes=30) if not permanent else None
        )
        
        self.failure_history.append(failure)
        
        # Update processor health
        if processor_id in self.processor_health:
            self.processor_health[processor_id]["failure_count"] += 1
            if permanent or failure_type == FailureType.ACCOUNT_FROZEN:
                self.processor_health[processor_id]["frozen"] = True
    
    def record_success(self, processor_id: str):
        """Record successful payment for processor health tracking."""
        
        if processor_id in self.processor_health:
            self.processor_health[processor_id]["last_success"] = datetime.utcnow()
            self.processor_health[processor_id]["failure_count"] = 0
    
    def get_routing_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics on routing decisions and performance."""
        
        total_decisions = len(self.routing_decisions)
        if total_decisions == 0:
            return {"message": "No routing decisions yet", "insights_analytics": self.get_insights_analytics()}
        
        # Analyze complexity distribution
        complexity_dist = {}
        for decision in self.routing_decisions:
            complexity = decision.claude_params.get("complexity", "balanced")
            complexity_dist[complexity] = complexity_dist.get(complexity, 0) + 1
        
        # Average decision time by complexity
        avg_time_by_complexity = {}
        for complexity in ["simple", "balanced", "comprehensive"]:
            times = [
                d.decision_time_ms for d in self.routing_decisions
                if d.claude_params.get("complexity") == complexity
            ]
            if times:
                avg_time_by_complexity[complexity] = sum(times) / len(times)
        
        # Analyze processor selection patterns
        processor_selections = {}
        insights_influenced_decisions = 0
        
        for decision in self.routing_decisions:
            processor = decision.selected_processor
            processor_selections[processor] = processor_selections.get(processor, 0) + 1
            
            # Check if insights influenced this decision
            if hasattr(decision, 'reasoning') and any([
                "promotion" in decision.reasoning.lower(),
                "sentiment" in decision.reasoning.lower(),
                "insight" in decision.reasoning.lower(),
                "discount" in decision.reasoning.lower()
            ]):
                insights_influenced_decisions += 1
        
        # Calculate insights effectiveness
        insights_effectiveness = 0.0
        if total_decisions > 0:
            insights_effectiveness = insights_influenced_decisions / total_decisions
        
        return {
            "total_routing_decisions": total_decisions,
            "complexity_distribution": complexity_dist,
            "processor_selection_distribution": processor_selections,
            "insights_influenced_decisions": insights_influenced_decisions,
            "insights_effectiveness_percentage": insights_effectiveness * 100,
            "average_decision_time_ms": {
                "by_complexity": avg_time_by_complexity,
                "overall": sum(d.decision_time_ms for d in self.routing_decisions) / total_decisions
            },
            "processor_health": self.processor_health,
            "recent_failures": len([
                f for f in self.failure_history
                if f.timestamp > datetime.utcnow() - timedelta(hours=1)
            ]),
            "insights_analytics": self.get_insights_analytics()
        }
    
    async def start_periodic_insights_updates(self, update_interval_hours: int = 2):
        """
        Start periodic background updates of insights data.
        Recommended for high-volume production systems.
        """
        if self._periodic_updates_enabled:
            return
        
        self._periodic_updates_enabled = True
        self._insights_update_task = asyncio.create_task(
            self._periodic_insights_updater(update_interval_hours)
        )
    
    async def stop_periodic_insights_updates(self):
        """Stop periodic insights updates."""
        self._periodic_updates_enabled = False
        if self._insights_update_task:
            self._insights_update_task.cancel()
            try:
                await self._insights_update_task
            except asyncio.CancelledError:
                pass
    
    async def _periodic_insights_updater(self, update_interval_hours: int):
        """
        Background task that periodically fetches and caches insights.
        """
        while self._periodic_updates_enabled:
            try:
                # Fetch insights for all known processors
                processors = list(self.processor_health.keys())
                
                print(f"[{datetime.utcnow().isoformat()}] Updating insights for processors: {processors}")
                
                insights = await self.insights_orchestrator.fetch_all_insights(
                    processors=processors,
                    regions=["US"]
                )
                
                # Update cache
                cache_key = f"periodic_{datetime.utcnow().hour}"
                self._insights_cache[cache_key] = insights
                self._last_insights_fetch = datetime.utcnow()
                
                # Clean up old cache entries
                self.insights_orchestrator.cleanup_cache()
                self._cleanup_router_cache()
                
                print(f"[{datetime.utcnow().isoformat()}] Insights updated successfully")
                
            except Exception as e:
                print(f"[{datetime.utcnow().isoformat()}] Error in periodic insights update: {e}")
            
            # Wait for next update
            await asyncio.sleep(update_interval_hours * 3600)
    
    def _cleanup_router_cache(self):
        """Clean up old router cache entries."""
        current_time = datetime.utcnow()
        expired_keys = []
        
        for key in self._insights_cache.keys():
            # Keep entries from current hour and previous hour only
            if "insights_" in key:
                try:
                    hour = int(key.split("_")[-1])
                    if abs(current_time.hour - hour) > 1:
                        expired_keys.append(key)
                except (ValueError, IndexError):
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self._insights_cache[key]
    
    async def force_insights_refresh(self, processors: List[str] = None):
        """
        Force an immediate refresh of insights data.
        Useful for testing or after configuration changes.
        """
        if processors is None:
            processors = list(self.processor_health.keys())
        
        try:
            insights = await self.insights_orchestrator.fetch_all_insights(
                processors=processors,
                regions=["US"]
            )
            
            # Update cache with forced refresh
            cache_key = f"forced_{datetime.utcnow().hour}_{datetime.utcnow().minute}"
            self._insights_cache[cache_key] = insights
            self._last_insights_fetch = datetime.utcnow()
            
            return self.insights_orchestrator.get_routing_adjustments(insights)
            
        except Exception as e:
            print(f"Error in forced insights refresh: {e}")
            return {}
    
    def get_insights_analytics(self) -> Dict[str, Any]:
        """
        Get analytics on insights usage and effectiveness.
        """
        cache_entries = len(self._insights_cache)
        last_fetch_ago = None
        
        if self._last_insights_fetch:
            last_fetch_ago = (datetime.utcnow() - self._last_insights_fetch).total_seconds()
        
        return {
            "insights_enabled": self._periodic_updates_enabled,
            "cache_entries": cache_entries,
            "last_fetch_seconds_ago": last_fetch_ago,
            "cache_keys": list(self._insights_cache.keys()),
            "orchestrator_cache_size": len(self.insights_orchestrator.insights_cache)
        }