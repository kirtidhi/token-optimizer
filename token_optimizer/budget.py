"""
Per-phase budget tracking and alerts.
"""
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class TokenBudget(BaseModel):
    total: int
    prompt_limit: Optional[int] = None
    
class BudgetTracker:
    def __init__(self, budget: TokenBudget):
        self.budget = budget
        self.used_tokens = 0
        self.used_prompt_tokens = 0
        
    def check_budget(self, new_tokens: int, is_prompt: bool = True) -> bool:
        """
        Check if adding new_tokens will exceed the budget.
        Returns True if within budget, False if it exceeds.
        """
        projected_total = self.used_tokens + new_tokens
        if projected_total > self.budget.total:
            logger.warning(f"Budget exceeded! Projected: {projected_total}, Limit: {self.budget.total}")
            return False
            
        if is_prompt and self.budget.prompt_limit:
            projected_prompt = self.used_prompt_tokens + new_tokens
            if projected_prompt > self.budget.prompt_limit:
                logger.warning(f"Prompt budget exceeded! Projected: {projected_prompt}, Limit: {self.budget.prompt_limit}")
                return False
                
        return True
        
    def add_usage(self, prompt_tokens: int, completion_tokens: int = 0):
        """
        Record actual token usage after a successful call.
        """
        self.used_prompt_tokens += prompt_tokens
        self.used_tokens += (prompt_tokens + completion_tokens)
