"""
cache.py - Token Optimization Engine

Caching module to prevent re-calling the LLM for identical prompts.
Provides massive ROI during iterative development by using `diskcache` 
for persistent state across runs, while gracefully falling back to an in-memory dict.
"""
import hashlib
import json
import logging
from typing import Optional, Tuple, Dict

try:
    import diskcache
    HAS_DISKCACHE = True
except ImportError:
    HAS_DISKCACHE = False

logger = logging.getLogger(__name__)

class TokenCache:
    def __init__(self, use_disk: bool = True, cache_dir: str = ".token_cache", ttl_seconds: Optional[int] = None):
        self.use_disk = use_disk and HAS_DISKCACHE
        self.ttl_seconds = ttl_seconds
        if self.use_disk:
            self._cache = diskcache.Cache(cache_dir)
            logger.info(f"Initialized DiskCache at {cache_dir} (TTL: {ttl_seconds}s)")
        else:
            self._cache = {}
            logger.info("Initialized In-Memory Cache (install diskcache for persistence)")

    def _generate_key(self, prompt: str, system_instruction: str) -> str:
        """Create a deterministic hash for the cache key."""
        # We hash the combination of prompt and system instruction
        combined = f"sys:{system_instruction}|prompt:{prompt}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    def get(self, prompt: str, system_instruction: str) -> Optional[Tuple[str, Dict]]:
        """Retrieve a cached response if it exists."""
        key = self._generate_key(prompt, system_instruction)
        result = self._cache.get(key)
        if result:
            logger.info("Cache HIT!")
            # Convert back from stored format
            if isinstance(result, str):
                try:
                    data = json.loads(result)
                    return data["text"], data["usage"]
                except Exception:
                    pass
            elif isinstance(result, tuple):
                return result
        return None

    def set(self, prompt: str, system_instruction: str, response_text: str, token_usage: Dict):
        """Save a response to the cache."""
        key = self._generate_key(prompt, system_instruction)
        # We store as JSON string or tuple depending on backend
        if self.use_disk:
            data = json.dumps({"text": response_text, "usage": token_usage})
            self._cache.set(key, data, expire=self.ttl_seconds)
        else:
            self._cache[key] = (response_text, token_usage)
