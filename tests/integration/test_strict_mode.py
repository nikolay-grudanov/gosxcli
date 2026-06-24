"""Integration tests for strict mode validation.

These tests use ``typer.testing.CliRunner`` to invoke the ``typst-gost-docx``
command in-process — no subprocess, no ``cwd`` plumbing, no venv
activation. The runner calls the same ``app`` object that the installed
console-script entry point wraps, so this is the closest possible test
to the real CLI without spawning a process.
"""

from typer.testing import CliRunner

from typst_gost_docx.cli import app


runner = CliRunner()


_TYPST_WITH_UNDEFINED = """
#figure(
  image("plot.png"),
  caption: [Results],
) <fig:results>

See @missing for details.
"""


_TYPST_CLEAN = """
#figure(
  image("plot.png"),
  caption: [Results],
) <fig>

See @fig for details.
"""


def test_strict_mode_with_undefined_reference(tmp_path):
    """Strict mode must exit with code 1 when a reference is undefined."""
    typst_file = tmp_path / "test.typ"
    output_file = tmp_path / "test.docx"
    typst_file.write_text(_TYPST_WITH_UNDEFINED, encoding="utf-8")

    result = runner.invoke(
        app,
        [str(typst_file), "-o", str(output_file), "--strict"],
    )

    assert result.exit_code == 1, (
        f"Expected exit code 1, got {result.exit_code}. "
        f"stdout: {result.stdout!r}, stderr: {result.stderr!r}"
    )
    combined = (result.stdout or "") + (result.stderr or "")
    assert "WARNING" in combined or "undefined" in combined.lower(), (
        f"Expected WARNING/undefined in output, got: {combined!r}"
    )


def test_strict_mode_without_undefined_reference(tmp_path):
    """Strict mode must pass when every reference is defined."""
    typst_file = tmp_path / "test.typ"
    output_file = tmp_path / "test.docx"
    typst_file.write_text(_TYPST_CLEAN, encoding="utf-8")

    result = runner.invoke(
        app,
        [str(typst_file), "-o", str(output_file), "--strict"],
    )

    assert result.exit_code == 0, (
        f"Expected exit code 0, got {result.exit_code}. "
        f"stdout: {result.stdout!r}, stderr: {result.stderr!r}"
    )
    assert output_file.exists(), "Output DOCX file should be created"


def test_normal_mode_with_undefined_reference(tmp_path):
    """Without --strict, undefined references must be reported but exit 0."""
    typst_file = tmp_path / "test.typ"
    output_file = tmp_path / "test.docx"
    typst_file.write_text(_TYPST_WITH_UNDEFINED, encoding="utf-8")

    result = runner.invoke(app, [str(typst_file), "-o", str(output_file)])

    assert result.exit_code == 0, (
        f"Expected exit code 0, got {result.exit_code}. "
        f"stdout: {result.stdout!r}, stderr: {result.stderr!r}"
    )
    combined = (result.stdout or "") + (result.stderr or "")
    assert "WARNING" in combined or "undefined" in combined.lower(), (
        f"Expected WARNING/undefined in output, got: {combined!r}"
    )
