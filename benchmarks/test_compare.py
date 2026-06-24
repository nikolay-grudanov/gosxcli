"""Unit tests for ``benchmarks/compare.py``.

Covers spec 001 T103: the historical comparison script. Tests pin the
script's output format so future changes to ``benchmarks/results/*.json``
shape are caught early.
"""

from __future__ import annotations

import json
from pathlib import Path



# Import the compare script as a module without depending on a particular
# benchmark-results directory layout.
import importlib.util

_COMPARE_PATH = Path(__file__).parent / "compare.py"
_spec = importlib.util.spec_from_file_location("benchmarks_compare", _COMPARE_PATH)
_compare = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_compare)  # type: ignore[union-attr]


def _write_result(
    path: Path,
    fixture: str,
    duration: float,
    passed: bool = True,
    timestamp: str = "2026-06-24T15:00:00",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "timestamp": timestamp,
                "fixture": fixture,
                "duration_seconds": duration,
                "threshold_seconds": 1.0,
                "passed": passed,
            }
        ),
        encoding="utf-8",
    )


def test_load_results_groups_by_fixture(tmp_path: Path):
    _write_result(
        tmp_path / "minimal_old.json", "minimal", 0.020,
        timestamp="2026-01-01T12:00:00",
    )
    _write_result(
        tmp_path / "minimal_new.json", "minimal", 0.040,
        timestamp="2026-01-02T12:00:00",
    )
    _write_result(
        tmp_path / "math.json", "math_formulas", 0.030,
        timestamp="2026-01-03T12:00:00",
    )

    results = _compare.load_results(tmp_path)
    grouped = _compare.group_by_fixture(results)

    assert set(grouped) == {"minimal", "math_formulas"}
    assert len(grouped["minimal"]) == 2
    # Newest first — second timestamp wins.
    assert grouped["minimal"][0]["duration_seconds"] == 0.040


def test_load_results_skips_older_schema(tmp_path: Path, capsys):
    """Old files without ``fixture``/``duration_seconds`` must not appear in output."""
    # File with the current schema.
    _write_result(tmp_path / "20260101_a_minimal.json", "minimal", 0.020)
    # File with the old CLI-benchmark schema (no fixture field).
    (tmp_path / "20250101_legacy.json").write_text(
        json.dumps(
            {
                "timestamp": "2025-01-01T00:00:00",
                "total_time_seconds": 0.1,
            }
        ),
        encoding="utf-8",
    )

    results = _compare.load_results(tmp_path)
    assert len(results) == 1
    assert results[0]["fixture"] == "minimal"

    captured = capsys.readouterr()
    assert "skipping" in captured.err
    assert "older schema" in captured.err


def test_load_results_handles_missing_directory(tmp_path: Path):
    """If the results directory does not exist, load_results returns an empty list."""
    assert _compare.load_results(tmp_path / "nonexistent") == []


def test_format_console_includes_thresholds_and_status(tmp_path: Path):
    _write_result(tmp_path / "20260101_minimal.json", "minimal", 0.020, passed=True)
    _write_result(tmp_path / "20260102_minimal.json", "minimal", 0.030, passed=False)

    results = _compare.load_results(tmp_path)
    grouped = _compare.group_by_fixture(results)
    text = _compare.format_console(grouped)

    assert "Fixture: minimal" in text
    assert "threshold:" in text
    assert "✅" in text or "❌" in text
    # Two runs visible.
    assert "runs:           2" in text


def test_format_markdown_emits_table(tmp_path: Path):
    _write_result(tmp_path / "20260101_minimal.json", "minimal", 0.020)

    results = _compare.load_results(tmp_path)
    grouped = _compare.group_by_fixture(results)
    text = _compare.format_markdown(grouped)

    assert text.startswith("# Benchmark history")
    assert "| Fixture | Runs | Pass | Threshold (ms)" in text
    assert "| minimal | 1 | 1 |" in text


def test_format_console_empty_results():
    text = _compare.format_console({})
    assert "No benchmark results found." in text
    assert "Benchmark history report" in text


def test_main_returns_zero(tmp_path: Path):
    """The CLI must always exit 0 — it's informational, not a gate."""
    _write_result(tmp_path / "20260101_minimal.json", "minimal", 0.020)
    rc = _compare.main(["--results-dir", str(tmp_path)])
    assert rc == 0
