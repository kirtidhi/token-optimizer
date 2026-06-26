import pytest
from token_optimizer.counter import counter

def test_count_tokens():
    text = "Hello world, this is a test."
    count = counter.count_tokens(text)
    assert count > 0

def test_estimate_cost():
    cost = counter.estimate_cost(1000, 1000, "gpt-4o")
    # 0.005 + 0.015 = 0.02
    assert abs(cost - 0.02) < 0.0001
