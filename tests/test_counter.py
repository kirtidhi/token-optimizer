import pytest
from token_optimizer.counter import TokenCounter

def test_count_tokens():
    counter = TokenCounter(default_model="gpt-4o")
    text = "Hello world, this is a test prompt."
    # Depending on cl100k_base, this should be a specific small number (e.g. 8-10)
    count = counter.count_tokens(text)
    assert count > 0
    assert count < 20

def test_estimate_cost_gpt4o():
    counter = TokenCounter()
    cost = counter.estimate_cost(prompt_tokens=1000, completion_tokens=1000, model="gpt-4o")
    # 0.005 + 0.015 = 0.02
    assert abs(cost - 0.02) < 0.0001

def test_estimate_cost_gemini():
    counter = TokenCounter()
    cost = counter.estimate_cost(prompt_tokens=1000, completion_tokens=1000, model="gemini-3.1-pro-preview")
    # 0.00125 + 0.005 = 0.00625
    assert abs(cost - 0.00625) < 0.0001
