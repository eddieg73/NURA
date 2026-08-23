import asyncio
import logging
from typing import Any, Dict, Optional, List
from enum import Enum

class ModelTier(Enum):
    GEMINI_FLASH = "gemini-1.5-flash"
    GEMINI_PRO = "gemini-1.5-pro"
    NVIDIA_MOE = "nvidia-deepseek-v3"
    CLAUDE_SONNET = "claude-3-5-sonnet"

class ReasoningPath(Enum):
    DIRECT = "direct"           # Fast, no overhead
    SOVEREIGN = "sovereign"    # Full decomposition, scoring, reflection

class OrionModelRouter:
    """The Sovereign Model Router for Project ORION.
    Now featuring Complexity-Aware Dispatching to prevent wasted cycles.
    """
    def __init__(self):
        self.priority_stack = [
            ModelTier.GEMINI_FLASH, 
            ModelTier.GEMINI_PRO, 
            ModelTier.NVIDIA_MOE, 
            ModelTier.CLAUDE_SONNET
        ]
        self.logger = logging.getLogger("OrionRouter")

    def triage_complexity(self, prompt: str) -> ReasoningPath:
        """Determines the required reasoning depth based on the prompt."""
        strategic_markers = ["pivot", "strategy", "business model", "differential", "architecture", "should i", "best move", "optimize"]
        
        # Trivial check: short, fact-based, or arithmetic
        if len(prompt.split()) < 10 and any(op in prompt for op in ["+", "-", "*", "/", "equals", "is the"]):
            return ReasoningPath.DIRECT
            
        # Strategic check: look for complexity markers
        if any(marker in prompt.lower() for marker in strategic_markers):
            return ReasoningPath.SOVEREIGN
            
        # Default to Direct for simple queries, Sovereign for ambiguous ones
        return ReasoningPath.DIRECT if len(prompt.split()) < 20 else ReasoningPath.SOVEREIGN

    async def route(self, prompt: str, context: Dict = None, task_type: str = "general", image_url: str = None) -> Dict:
        """Routes the prompt through the MoE hierarchy with complexity awareness."""
        
        # 1. DISPATCH: Match complexity to the problem
        path = self.triage_complexity(prompt)
        self.logger.info(f"Complexity Triage: {path.value}")

        if path == ReasoningPath.DIRECT:
            # Direct Path: Lowest latency, first available model (usually Gemini Flash)
            return await self._call_model(ModelTier.GEMINI_FLASH, prompt, context, image_url)

        # 2. SOVEREIGN PATH: Tiered MoE Escalation
        for tier in self.priority_stack:
            try:
                result = await self._call_model(tier, prompt, context, image_url)
                if self._should_escalate(result):
                    continue
                return result
            except Exception:
                continue
        
        return {"status": "error", "message": "Sovereign path failed."}

    async def _call_model(self, tier: ModelTier, prompt: str, context: Dict, image_url: str = None) -> Dict:
        # Mock Implementation
        return {"model": tier.value, "content": f"Result from {tier.value}", "confidence": 0.9}

    def _should_escalate(self, result: Dict) -> bool:
        if result.get("confidence", 0) < 0.8: return True
        return False
