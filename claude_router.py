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
    
    def __init__(self, anthropic_api_key: str = None):
        from claude_client import ClaudeClient
        
        self.claude_client = ClaudeClient()
        self.failure_history: List[ProcessorFailure] = []
        self.routing_decisions: List[RoutingDecision] = []
        
        # Processor health tracking
        self.processor_health = {
            "stripe": {"frozen": False, "last_success": None, "failure_count": 0},
            "paypal": {"frozen": False, "last_success": None, "failure_count": 0},
            "visa": {"frozen": False, "last_success": None, "failure_count": 0}
        }
    
    async def make_routing_decision(
        self,
        request: PaymentRequest,
        available_processors: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        complexity: str = "balanced"
    ) -> RoutingDecision:
        """
        Core routing logic using Claude's reasoning capabilities.
        
        complexity options:
        - "simple": Fast decisions for routine payments
        - "balanced": Balanced reasoning for most cases
        - "comprehensive": Deep analysis for high-value or complex scenarios
        """
        
        start_time = datetime.utcnow()
        
        # Determine complexity based on transaction
        if not complexity:
            complexity = self._determine_complexity(request, context)
        
        # Prepare context for Claude
        claude_context = self._prepare_claude_context(
            request, 
            available_processors, 
            context
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
    
    def _prepare_claude_context(
        self,
        request: PaymentRequest,
        available_processors: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Prepare context for Claude to make routing decision.
        """
        
        # Get recent failures for this merchant
        recent_failures = [
            f for f in self.failure_history
            if f.timestamp > datetime.utcnow() - timedelta(hours=1)
        ]
        
        return {
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
        """Simple processor selection logic for demo."""
        
        processors = context["processors"]
        
        # Filter out recently failed processors
        failed_ids = [f["processor"] for f in context["failures"] if not f.get("permanent")]
        available = [p for p in processors if p["id"] not in failed_ids]
        
        if not available:
            available = processors  # Use all if none available
        
        # Sort by success rate and fees
        available.sort(
            key=lambda p: (-p.get("metrics", {}).get("success_rate", 0), 
                          p.get("fee_percentage", 99))
        )
        
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
        """Get analytics on routing decisions and performance."""
        
        total_decisions = len(self.routing_decisions)
        if total_decisions == 0:
            return {"message": "No routing decisions yet"}
        
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
        
        return {
            "total_routing_decisions": total_decisions,
            "complexity_distribution": complexity_dist,
            "average_decision_time_ms": {
                "by_complexity": avg_time_by_complexity,
                "overall": sum(d.decision_time_ms for d in self.routing_decisions) / total_decisions
            },
            "processor_health": self.processor_health,
            "recent_failures": len([
                f for f in self.failure_history
                if f.timestamp > datetime.utcnow() - timedelta(hours=1)
            ])
        }