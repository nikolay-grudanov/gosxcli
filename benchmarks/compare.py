"""Compare benchmark results across runs and emit a trend report.

Spec 001 US4 T103: read every JSON file under ``benchmarks/results/``,
group by fixture name, and emit a Markdown/console summary of the most
recent run per fixture along with min/mean/max across all runs.

Usage:
    python benchmarks/compare.py            # human-readable console output
    python benchmarks/compare.py --markdown # Markdown table only
    python benchmarks/compare.py --limit 5   # only last 5 runs per fixture

Exit status: always 0 (informational only).
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


RESULTS_DIR = Path(__file__).parent / "results"


def load_results(results_dir: Path) -> list[dict[str, Any]]:
    """Read every JSON file in ``results_dir`` and return the parsed dicts.

    Files that don't look like the current schema (no ``fixture`` or
    ``duration_seconds`` fields) are skipped with a warning so the
    report stays consistent across schema versions.
    """
    if not results_dir.exists():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(results_dir.glob("*.json")):
        try:
            with path.open(encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[warn] skipping {path.name}: {exc}", file=sys.stderr)
            continue
        if "fixture" not in data or "duration_seconds" not in data:
            print(
                f"[warn] skipping {path.name}: missing fixture/duration fields "
                f"(older schema?)",
                file=sys.stderr,
            )
            continue
        data["_file"] = path.name
        out.append(data)
    return out


def group_by_fixture(
    results: list[dict[str, Any]],
    limit: int | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Group results by ``fixture`` field, newest first, truncated to ``limit``."""
    by_fixture: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in results:
        by_fixture[r.get("fixture", "<unknown>")].append(r)
    out: dict[str, list[dict[str, Any]]] = {}
    for name, runs in by_fixture.items():
        runs.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
        if limit is not None:
            runs = runs[:limit]
        out[name] = runs
    return out


def format_console(by_fixture: dict[str, list[dict[str, Any]]]) -> str:
    lines: list[str] = []
    lines.append("=" * 72)
    lines.append("Benchmark history report")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("=" * 72)
    if not by_fixture:
        lines.append("No benchmark results found.")
        return "\n".join(lines)
    for fixture, runs in by_fixture.items():
        latest = runs[0]
        durations = [r["duration_seconds"] for r in runs if "duration_seconds" in r]
        passed = sum(1 for r in runs if r.get("passed"))
        threshold = latest.get("threshold_seconds")
        lines.append("")
        lines.append(f"Fixture: {fixture}")
        lines.append(f"  runs:           {len(runs)}")
        lines.append(f"  passed:         {passed}/{len(runs)}")
        if threshold is not None:
            lines.append(f"  threshold:      {threshold * 1000:.1f} ms")
        if durations:
            lines.append(
                f"  duration:       "
                f"min={min(durations) * 1000:.1f} ms, "
                f"mean={statistics.mean(durations) * 1000:.1f} ms, "
                f"max={max(durations) * 1000:.1f} ms"
            )
            if len(durations) > 1:
                lines.append(f"  stddev:         {statistics.stdev(durations) * 1000:.2f} ms")
        latest_ts = latest.get("timestamp", "?")
        latest_dur = latest.get("duration_seconds")
        latest_pass = "✅" if latest.get("passed") else "❌"
        if latest_dur is not None:
            lines.append(f"  latest:         {latest_ts} → {latest_dur * 1000:.1f} ms {latest_pass}")
        else:
            lines.append(f"  latest:         {latest_ts} {latest_pass}")
    return "\n".join(lines)


def format_markdown(by_fixture: dict[str, list[dict[str, Any]]]) -> str:
    lines: list[str] = []
    lines.append("# Benchmark history")
    lines.append("")
    if not by_fixture:
        lines.append("_No benchmark results found._")
        return "\n".join(lines)
    lines.append("| Fixture | Runs | Pass | Threshold (ms) | Mean (ms) | Latest (ms) | Status |")
    lines.append("|---|---:|---:|---:|---:|---:|---|")
    for fixture, runs in by_fixture.items():
        durations = [r["duration_seconds"] for r in runs if "duration_seconds" in r]
        passed = sum(1 for r in runs if r.get("passed"))
        threshold = runs[0].get("threshold_seconds")
        threshold_ms = f"{threshold * 1000:.1f}" if threshold is not None else "—"
        mean_ms = f"{statistics.mean(durations) * 1000:.1f}" if durations else "—"
        latest = runs[0]
        latest_ms = (
            f"{latest['duration_seconds'] * 1000:.1f}"
            if "duration_seconds" in latest
            else "—"
        )
        status = "✅" if latest.get("passed") else "❌"
        lines.append(
            f"| {fixture} | {len(runs)} | {passed} | {threshold_ms} | {mean_ms} | {latest_ms} | {status} |"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=RESULTS_DIR,
        help="Directory containing benchmark JSON results",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Emit a Markdown table instead of console text",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit how many runs per fixture are considered (newest first)",
    )
    args = parser.parse_args(argv)

    results = load_results(args.results_dir)
    grouped = group_by_fixture(results, limit=args.limit)
    print(format_markdown(grouped) if args.markdown else format_console(grouped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
