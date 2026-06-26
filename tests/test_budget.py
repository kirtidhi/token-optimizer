import pytest
from token_optimizer.budget import TokenBudget, BudgetTracker

def test_budget_within_limit():
    budget = TokenBudget(total=1000)
    tracker = BudgetTracker(budget)
    assert tracker.check_budget(500) == True

def test_budget_exceeds_limit():
    budget = TokenBudget(total=1000)
    tracker = BudgetTracker(budget)
    tracker.add_usage(800)
    assert tracker.check_budget(300) == False

def test_prompt_budget():
    budget = TokenBudget(total=1000, prompt_limit=500)
    tracker = BudgetTracker(budget)
    assert tracker.check_budget(600, is_prompt=True) == False
    assert tracker.check_budget(400, is_prompt=True) == True
