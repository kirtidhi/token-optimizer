import pytest
from token_optimizer.compressor import SmartTruncator

def test_smart_truncator_passthrough():
    truncator = SmartTruncator(target_tokens=1000, keep_ratio=1.0)
    text = "Hello world " * 10
    compressed = truncator.compress(text)
    # Should be unmodified because it fits in budget
    assert compressed == text

def test_smart_truncator_compress():
    truncator = SmartTruncator(target_tokens=50, keep_ratio=1.0)
    # 1 word ~ 1 token, generate 200 words
    text = " ".join(["word"] * 200)
    compressed = truncator.compress(text)
    
    # Should be truncated
    assert len(compressed) < len(text)
    assert compressed.endswith("...") or compressed.startswith("...") or "..." in compressed
