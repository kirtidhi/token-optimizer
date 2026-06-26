import pytest
import time
import tempfile
from token_optimizer.cache import TokenCache

def test_cache_hit_and_miss():
    cache = TokenCache(use_disk=False)
    cache.set("prompt1", "sys1", "response1", {"prompt": 10})
    
    # Hit
    result = cache.get("prompt1", "sys1")
    assert result is not None
    assert result[0] == "response1"
    
    # Miss
    miss = cache.get("prompt2", "sys1")
    assert miss is None

def test_cache_ttl():
    # diskcache supports ttl. We'll use a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # TTL of 1 second
        cache = TokenCache(use_disk=True, cache_dir=tmpdir, ttl_seconds=1)
        cache.set("prompt_ttl", "sys_ttl", "response_ttl", {"prompt": 5})
        
        # Should hit immediately
        res1 = cache.get("prompt_ttl", "sys_ttl")
        assert res1 is not None
        
        # Wait for TTL to expire
        time.sleep(1.1)
        
        # Should miss
        res2 = cache.get("prompt_ttl", "sys_ttl")
        assert res2 is None
