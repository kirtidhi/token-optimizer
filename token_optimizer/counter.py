"""
counter.py - Token Optimization Engine

Core token counting and cost estimation utilities for various LLM providers.
Everything in the token optimizer depends on accurate pre-flight counting to 
prevent context-window overflows and track budget consumption.
"""
import tiktoken
from typing import Optional

class TokenCounter:
    def __init__(self, default_model: str = "gpt-4o"):
        self.default_model = default_model
        # Cache encoding to avoid reloading
        self._encodings_cache = {}

    def get_encoding(self, model: str):
        if model not in self._encodings_cache:
            try:
                self._encodings_cache[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fallback to cl100k_base which is standard for newer OpenAI and generally 
                # a safe heuristic approximation for Anthropic/Gemini if specifics aren't needed
                self._encodings_cache[model] = tiktoken.get_encoding("cl100k_base")
        return self._encodings_cache[model]

    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Returns the number of tokens in a text string.
        """
        if not text:
            return 0
        model_to_use = model or self.default_model
        encoding = self.get_encoding(model_to_use)
        return len(encoding.encode(text))

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int = 0, model: Optional[str] = None) -> float:
        """
        Returns an estimated cost based on token counts.
        (Note: These rates should eventually be pulled from a config)
        """
        model_to_use = model or self.default_model
        
        # Very rough fallback estimates (per 1k tokens)
        rates = {
            "gpt-4o": {"prompt": 0.005, "completion": 0.015},
            "gemini-1.5-pro": {"prompt": 0.0035, "completion": 0.0105},
            "gemini-1.5-flash": {"prompt": 0.000075, "completion": 0.0003},
            "gemini-3.1-pro-preview": {"prompt": 0.00125, "completion": 0.005},
            "claude-sonnet-4-6": {"prompt": 0.003, "completion": 0.015},
        }
        
        rate = rates.get(model_to_use, rates["gpt-4o"]) # Fallback to 4o prices
        
        cost = (prompt_tokens / 1000.0) * rate["prompt"]
        cost += (completion_tokens / 1000.0) * rate["completion"]
        
        return cost

# Singleton instance for easy importing
counter = TokenCounter()
