# Performance Benchmark Results

This directory contains performance benchmarking results for the Typst GOST DOCX Converter.

## Structure

- `results/` — JSON files with benchmark results
- Each file should be named with timestamp or descriptive name: `YYYYMMDD_HHMMSS_<benchmark_name>.json`

## Running Benchmarks

```bash
# Run performance benchmarks
pytest benchmarks/ --benchmark-only

# Compare results
python -m benchmarks.compare results/*.json
```