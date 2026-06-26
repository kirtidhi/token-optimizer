import pytest
from token_optimizer.cache import TokenCache
import tempfile
import os

def test_in_memory_cache():
    cache = TokenCache(use_disk=False)
    cache.set("prompt1", "sys1", "response1", {"prompt": 10})
    
    result = cache.get("prompt1", "sys1")
    assert result is not None
    assert result[0] == "response1"
    
    miss = cache.get("prompt2", "sys1")
    assert miss is None

def test_disk_cache():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = TokenCache(use_disk=True, cache_dir=tmpdir)
        cache.set("prompt1", "sys1", "response1", {"prompt": 10})
        
        result = cache.get("prompt1", "sys1")
        assert result is not None
        assert result[0] == "response1"
