"""
Claude API Client Integration
Provides Claude's advanced reasoning capabilities for payment routing and data generation
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ClaudeClient:
    """
    Claude API client for payment routing and data generation.
    Uses Claude's advanced reasoning capabilities for payment routing and data generation.
    """
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = "claude-3-5-sonnet-20240620"
        self.client = AsyncAnthropic(api_key=self.api_key)
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    async def make_routing_decision(
        self,
        context: Dict[str, Any],
        complexity: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Use Claude to make intelligent payment routing decisions.
        
        Args:
            context: Payment context (processors, failures, transaction details)
            complexity: simple, balanced, comprehensive
        """
        
        prompt = self._build_routing_prompt(context, complexity)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse Claude response
            decision_text = response.content[0].text
            
            # Extract structured decision from Claude's response
            decision = self._parse_routing_decision(decision_text, context)
            
            # Add Claude metadata
            decision["claude_metadata"] = {
                "complexity": complexity,
                "model": self.model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
            
            return decision
            
        except Exception as e:
            # Fallback to simple logic if Claude fails
            return self._fallback_routing_decision(context, str(e))
    
    async def generate_synthetic_data(
        self,
        pattern_type: str,
        context: Dict[str, Any],
        complexity: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Use Claude to generate realistic synthetic transaction data.
        
        Args:
            pattern_type: normal, sudden_spike, high_refund_rate, etc.
            context: Business context and requirements
            complexity: simple, balanced, comprehensive
        """
        
        prompt = self._build_data_generation_prompt(pattern_type, context, complexity)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            generation_plan = response.content[0].text
            
            return {
                "pattern_type": pattern_type,
                "generation_plan": generation_plan,
                "claude_analysis": self._extract_analysis(generation_plan),
                "parameters_used": {
                    "complexity": complexity,
                    "model": self.model,
                    "tokens_used": response.usage.input_tokens + response.usage.output_tokens
                }
            }
            
        except Exception as e:
            return {
                "pattern_type": pattern_type,
                "error": str(e),
                "fallback": "Using deterministic generation"
            }
    
    async def analyze_transaction_risk(
        self,
        transactions: List[Dict[str, Any]],
        context: Dict[str, Any],
        complexity: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Use Claude to analyze transaction patterns for freeze risk.
        """
        
        prompt = self._build_risk_analysis_prompt(transactions, context, complexity)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            analysis = response.content[0].text
            
            return {
                "risk_analysis": analysis,
                "structured_assessment": self._parse_risk_analysis(analysis),
                "claude_reasoning": self._extract_analysis(analysis),
                "confidence": "high" if complexity == "comprehensive" else "medium"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "fallback_analysis": "Unable to perform Claude risk analysis"
            }
    
    def _build_routing_prompt(self, context: Dict[str, Any], complexity: str) -> str:
        """Build routing decision prompt for Claude."""
        
        base_prompt = f"""
        PAYMENT ROUTING DECISION REQUIRED

        Transaction Details:
        - Amount: ${context['transaction']['amount']} {context['transaction']['currency']}
        - Merchant: {context['transaction']['merchant_id']}
        - Risk Level: {context.get('business_context', {}).get('urgency', 'normal')}

        Available Processors:
        {self._serialize_context(context['processors'])}

        Recent Failures:
        {self._serialize_context(context.get('failures', []))}

        Processor Health Status:
        {self._serialize_context(context.get('processor_health', {}))}

        REQUIREMENTS:
        1. If primary processor is frozen, MUST use alternative
        2. Prioritize success rate over fees for high-value transactions
        3. Consider recent failure patterns
        4. Provide clear reasoning for your choice
        """
        
        if complexity == "comprehensive":
            base_prompt += """
            
        COMPREHENSIVE ANALYSIS REQUIRED:
        - Perform deep analysis of all risk factors
        - Consider historical patterns and trends
        - Evaluate processor reliability and cost optimization
        - Assess regulatory compliance implications
        - Provide detailed step-by-step reasoning
        """
        elif complexity == "balanced":
            base_prompt += """
            
        BALANCED ANALYSIS:
        - Consider key risk factors and processor health
        - Balance reliability with cost efficiency
        - Provide clear reasoning for decision
        """
        
        base_prompt += """

        Please respond with:
        1. Selected processor ID
        2. Reasoning for your choice
        3. Fallback chain (ordered list of alternatives)
        4. Risk assessment
        5. Confidence level (0-1)
        """
        
        return base_prompt
    
    def _build_data_generation_prompt(self, pattern_type: str, context: Dict[str, Any], complexity: str) -> str:
        """Build synthetic data generation prompt."""
        
        stripe_thresholds = {
            "refund_rate": 5.0,
            "chargeback_rate": 1.0,
            "volume_spike": 10.0
        }
        
        base_prompt = f"""
        GENERATE REALISTIC STRIPE TRANSACTION DATA

        Pattern Type: {pattern_type}
        Business Context: {context.get('business_type', 'B2B SaaS')}
        Historical Baseline: {context.get('historical_baseline', {})}

        Requirements for {pattern_type}:
        {self._get_pattern_requirements(pattern_type)}

        Stripe Freeze Thresholds:
        - Refund rate >5% = Investigation triggered
        - Chargeback rate >1% = Immediate freeze + 180-day hold
        - Volume spike >10x normal = Account review within 24 hours

        Generate a detailed plan for creating {context.get('transaction_count', 100)} transactions that:
        1. Follow authentic Stripe patterns (proper fees, timing, IDs)
        2. Create the specified risk scenario
        3. Include realistic failure reasons and customer behavior
        4. Use proper Stripe balance_transaction format
        """
        
        if complexity == "comprehensive":
            base_prompt += """
            
        COMPREHENSIVE GENERATION:
        - Include detailed behavioral patterns and timing analysis
        - Generate multiple risk scenarios with interconnected factors
        - Provide statistical analysis of generated patterns
        - Include fraud detection considerations
        - Generate compliance documentation
        """
        
        base_prompt += "\n\nFocus on realism - this data will be used to test payment systems."
        
        return base_prompt
    
    def _build_risk_analysis_prompt(self, transactions: List[Dict[str, Any]], context: Dict[str, Any], complexity: str) -> str:
        """Build risk analysis prompt."""
        
        base_prompt = f"""
        ANALYZE TRANSACTION PATTERNS FOR STRIPE FREEZE RISK

        Transaction Dataset:
        - Total transactions: {len(transactions)}
        - Sample data: {self._serialize_context(transactions[:5])}

        Analysis Context:
        - Business type: {context.get('business_type', 'B2B')}
        - Analysis window: {context.get('analysis_window', 'recent')}

        Stripe Risk Thresholds:
        - Refund rate >5% = Review triggered
        - Chargeback rate >1% = Immediate freeze
        - Volume spikes >10x = Account investigation
        - Pattern inconsistencies = Documentation required
        """
        
        if complexity == "comprehensive":
            base_prompt += """
            
        COMPREHENSIVE RISK ANALYSIS:
        - Perform deep statistical analysis of patterns
        - Identify subtle risk indicators and correlations
        - Provide timeline-based risk progression analysis
        - Include behavioral scoring and anomaly detection
        - Generate detailed mitigation strategies
        """
        
        base_prompt += """

        Please provide:
        1. Risk level assessment (low/medium/high/critical)
        2. Specific patterns detected
        3. Freeze probability (0-100%)
        4. Detailed reasoning for your assessment
        5. Actionable recommendations to reduce risk
        6. Timeline for potential freeze if patterns continue

        Be thorough in your analysis - account freezes can hold funds for 180 days.
        """
        
        return base_prompt
    
    def _get_pattern_requirements(self, pattern_type: str) -> str:
        """Get specific requirements for each pattern type."""
        
        requirements = {
            "sudden_spike": "Generate 10-15x normal daily volume compressed into 2-3 hours. Use larger transaction amounts ($200-2000). Include realistic promotional context.",
            "high_refund_rate": "Create 10-15% refund rate (vs normal 2%). Include varied refund reasons, proper timing delays, and customer service context.",
            "chargeback_surge": "Generate 2-3% chargeback rate. Include proper chargeback reasons, $15 fees, and 15-60 day delays from original transactions.",
            "pattern_deviation": "Create sudden changes in transaction size (5-10x), new geographic regions, or unusual timing patterns.",
            "normal": "Generate consistent daily patterns, 2% refund rate, standard transaction sizes, and predictable business rhythms."
        }
        
        return requirements.get(pattern_type, "Generate realistic transaction patterns")
    
    def _parse_routing_decision(self, decision_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Claude's routing decision into structured format."""
        
        # Extract key information from Claude's response
        lines = decision_text.split('\n')
        
        # Try to find processor selection
        selected_processor = "stripe"  # default
        confidence = 0.8
        
        for line in lines:
            if "select" in line.lower() or "choose" in line.lower() or "recommend" in line.lower():
                for processor_id in ["stripe", "paypal", "visa", "square", "adyen"]:
                    if processor_id in line.lower():
                        selected_processor = processor_id
                        break
            
            # Try to extract confidence
            if "confidence" in line.lower():
                import re
                conf_match = re.search(r'(\d+(?:\.\d+)?)', line)
                if conf_match:
                    conf_val = float(conf_match.group(1))
                    if conf_val <= 1:
                        confidence = conf_val
                    elif conf_val <= 100:
                        confidence = conf_val / 100
        
        return {
            "selected_processor": selected_processor,
            "reasoning": decision_text,
            "confidence": confidence,
            "fallback_chain": ["paypal", "visa"] if selected_processor == "stripe" else ["stripe", "visa"]
        }
    
    def _parse_risk_analysis(self, analysis: str) -> Dict[str, Any]:
        """Parse Claude's risk analysis into structured format."""
        
        # Extract risk level
        risk_level = "medium"
        analysis_lower = analysis.lower()
        
        if "critical" in analysis_lower:
            risk_level = "critical"
        elif "high" in analysis_lower and ("risk" in analysis_lower or "freeze" in analysis_lower):
            risk_level = "high"
        elif "low" in analysis_lower and ("risk" in analysis_lower or "freeze" in analysis_lower):
            risk_level = "low"
        
        # Extract freeze probability
        freeze_prob = 0.3
        try:
            import re
            prob_match = re.search(r'(\d+)%', analysis)
            if prob_match:
                freeze_prob = int(prob_match.group(1)) / 100
        except:
            pass
        
        return {
            "risk_level": risk_level,
            "freeze_probability": freeze_prob,
            "risk_score": freeze_prob * 100,
            "detected_patterns": [],
            "recommendations": ["Monitor transaction patterns", "Prepare documentation"]
        }
    
    def _extract_analysis(self, text: str) -> str:
        """Extract analysis chain from Claude response."""
        
        analysis_keywords = ["analysis:", "reasoning:", "because", "therefore", "given that", "considering"]
        
        for keyword in analysis_keywords:
            if keyword in text.lower():
                return text  # Return full text if analysis detected
        
        return text[:500] + "..." if len(text) > 500 else text
    
    def _serialize_context(self, obj: Any) -> str:
        """Serialize context objects with datetime handling."""
        def datetime_converter(o):
            if isinstance(o, datetime):
                return o.isoformat()
            return str(o)
        
        return json.dumps(obj, indent=2, default=datetime_converter)
    
    def _fallback_routing_decision(self, context: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Fallback decision if Claude API fails."""
        
        return {
            "selected_processor": "stripe",
            "reasoning": f"Claude API error: {error}. Using fallback logic.",
            "confidence": 0.5,
            "fallback_chain": ["paypal", "visa"],
            "error": error
        }