"""
wrapper.py - Token Optimization Engine

The core integration point. Provides a drop-in `TokenOptimizer` decorator/wrapper
for any standard LLM provider's `generate()` call. Implements the orchestrator pattern
to silently apply budget checks, caching, and compression without altering upstream logic.
"""
import logging
from typing import Optional, Any
from .counter import counter
from .budget import TokenBudget, BudgetTracker
from .cache import TokenCache
from .compressor import SmartTruncator

logger = logging.getLogger(__name__)

class TokenOptimizer:
    """
    Wraps an existing LLM provider's generate() method to add
    budgeting, caching, compression, and metric tracking.
    """
    def __init__(
        self, 
        provider: Any, 
        budget: Optional[TokenBudget] = None,
        cache: bool = False,
        compress_above: Optional[int] = None
    ):
        self.provider = provider
        self.budget_tracker = BudgetTracker(budget) if budget else None
        self.use_cache = cache
        self.compress_above = compress_above
        
        self._cache = TokenCache(use_disk=True) if cache else None
        self._compressor = SmartTruncator(target_tokens=compress_above) if compress_above else None

    def generate(self, prompt: str, system_instruction: str, max_tokens: int = 8192, **kwargs) -> tuple[str, dict]:
        """
        Drop-in replacement for the provider's generate method.
        """
        estimated_prompt_tokens = counter.count_tokens(prompt) + counter.count_tokens(system_instruction)
        
        logger.info(f"Pre-flight token estimation: {estimated_prompt_tokens} tokens")
        
        # 1. Compression (if enabled and prompt is too large)
        if self.compress_above and estimated_prompt_tokens > self.compress_above:
            logger.info(f"Prompt > {self.compress_above} tokens. Triggering compression...")
            prompt = self._compressor.compress(prompt)
            estimated_prompt_tokens = counter.count_tokens(prompt) + counter.count_tokens(system_instruction)
            
        # 2. Cache Check (if enabled)
        if self.use_cache and self._cache:
            cached_result = self._cache.get(prompt, system_instruction)
            if cached_result:
                return cached_result[0], cached_result[1]
                
        # 3. Budget Check
        if self.budget_tracker:
            if not self.budget_tracker.check_budget(estimated_prompt_tokens, is_prompt=True):
                raise ValueError("Token budget exceeded before making the call.")

        # 4. Actual Provider Call
        try:
            # Assuming provider has a generate method with this signature (like MAhGIC)
            response_text, token_usage = self.provider.generate(
                prompt=prompt, 
                system_instruction=system_instruction, 
                max_tokens=max_tokens,
                **kwargs
            )
        except Exception as e:
            logger.error(f"Provider generate call failed: {e}")
            raise

        # 5. Post-call Accounting
        actual_prompt_tokens = token_usage.get("prompt", estimated_prompt_tokens)
        actual_completion_tokens = token_usage.get("response", 0)
        
        if self.budget_tracker:
            self.budget_tracker.add_usage(actual_prompt_tokens, actual_completion_tokens)
            
        # Optional: Print estimated cost
        model_name = kwargs.get("model") or getattr(self.provider, "model", None)
        cost = counter.estimate_cost(actual_prompt_tokens, actual_completion_tokens, model=model_name)
        logger.info(f"Run Cost Estimate: ${cost:.5f} | Total Tokens: {actual_prompt_tokens + actual_completion_tokens}")

        # 6. Cache Save (if enabled)
        if self.use_cache and self._cache:
            self._cache.set(prompt, system_instruction, response_text, token_usage)

        return response_text, token_usage
