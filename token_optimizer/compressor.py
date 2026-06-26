"""
Compressors and Truncators to reduce prompt sizes before hitting the LLM.
"""
import logging
from typing import Optional
from .counter import counter

logger = logging.getLogger(__name__)

class Compressor:
    def __init__(self, target_tokens: int = 3000):
        self.target_tokens = target_tokens

    def compress(self, text: str) -> str:
        """
        Base compress method. Should be overridden by subclasses.
        """
        return text

class SmartTruncator(Compressor):
    """
    Truncates a document from the tail, preserving the beginning,
    which often contains the most important context for LLMs.
    """
    def __init__(self, target_tokens: int = 3000, keep_ratio: float = 1.0):
        """
        keep_ratio: 1.0 means keep 100% from the start and 0% from the end.
        """
        super().__init__(target_tokens)
        self.keep_ratio = keep_ratio

    def compress(self, text: str) -> str:
        current_tokens = counter.count_tokens(text)
        if current_tokens <= self.target_tokens:
            return text
            
        logger.info(f"SmartTruncator: Compressing from {current_tokens} down to ~{self.target_tokens}")
        
        # We'll do an approximate character-level truncation based on token ratio
        # Assuming ~4 chars per token on average
        char_limit = self.target_tokens * 4
        
        if len(text) <= char_limit:
            return text
            
        keep_start_chars = int(char_limit * self.keep_ratio)
        keep_end_chars = int(char_limit * (1 - self.keep_ratio))
        
        start_text = text[:keep_start_chars]
        end_text = text[-keep_end_chars:] if keep_end_chars > 0 else ""
        
        truncation_message = "\n\n...[CONTENT TRUNCATED BY TOKEN OPTIMIZER]...\n\n"
        
        return start_text + truncation_message + end_text

class RegexPruner(Compressor):
    """
    Removes patterns that are known to be safe to delete (e.g., standard disclaimers).
    """
    def __init__(self, patterns: list[str]):
        import re
        super().__init__()
        self.patterns = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in patterns]

    def compress(self, text: str) -> str:
        original_length = len(text)
        for pattern in self.patterns:
            text = pattern.sub("", text)
        
        if len(text) < original_length:
            logger.info(f"RegexPruner removed {original_length - len(text)} characters.")
        return text
