# Token Optimizer

Provider-agnostic token budget management, caching, and compression for LLM pipelines. 

**Proven Results (MA(h)GIC A/B Test on 100 Equities):**
- **Before TokenOptimizer**: 2,773,001 tokens 
- **After TokenOptimizer**: 2,273,490 tokens
- **Savings**: ~500k tokens (18%) with zero degradation in reasoning quality.

## Features
- **Budget Tracking**: Stops runs before they exceed token limits.
- **Caching**: Disk-based persistent cache to avoid re-evaluating unchanged prompts.
- **Compression**: Smart truncation (cutting off redundant SEC tails) and regex pruning to shrink context size safely.
- **Seamless Wrapper**: Drops into any codebase with zero refactoring.

## Installation
```bash
pip install token-optimizer
```
