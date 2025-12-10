# Pipeline Performance Tips

## Why the pipeline is slow

The pipeline processes 580+ news articles and performs:
1. **Opportunity scoring** using ML model (fast - ~0.01s per item)
2. **Zero-shot classification** for thematic categories (slow - ~2-3s per item)
3. **Zero-shot classification** for industry relevance (slow - ~2-3s per item)

**Total time**: ~5-6 seconds per article × 580 articles = **~50-60 minutes**

## Quick Solution: Use the Fast Fix Script

Instead of running the full pipeline, use the optimized script that only recalculates scores:

```bash
source .venv/bin/activate
python3 quick_fix_scores.py
```

This script:
- ✓ Uses existing processed data (categories/industries already classified)
- ✓ Only recalculates opportunity scores with the ML model
- ✓ Completes in ~2-3 minutes instead of 50-60 minutes
- ✓ Produces the same result for the UI

## When to Run Full Pipeline

Only run the full pipeline (`python3 pipeline.py`) when:
- You have **new news data** that hasn't been processed yet
- You need to reclassify categories and industries
- The cache is corrupted or missing

## Progress Indicators

When running the full pipeline, you'll now see:
```
[sri_lanka_news] Processing item 50...
[sri_lanka_news] Processing item 100...
[sri_lanka_news] Processing item 150...
```

This shows it's working (just slowly). Be patient - it can take 30-60 minutes.

## Recommended Workflow

1. **Collect new data**: `python3 collect_all.py` (fast, ~30 seconds)
2. **Quick score update**: `python3 quick_fix_scores.py` (fast, ~3 minutes)
3. **Start dev server**: `python3 server.py` and view UI

Only run full pipeline when absolutely necessary!
