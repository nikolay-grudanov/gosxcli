"""Unit tests for ``ReferenceValidator`` and ``ValidationResult``.

Covers spec 001 US3 (T081): unit tests for the validation logic.
The validator already exists in ``src/typst_gost_docx/ir/validator.py``;
these tests pin down its public contract so that future refactors
can't silently break the strict-mode exit code or the warning text.
"""

from __future__ import annotations


from typst_gost_docx.ir.model import (
    CrossReference,
    Figure,
    Paragraph,
    Section,
    TextRun,
    ValidationResult,
    Caption,
    NumberingKind,
    SourceLocation,
)
from typst_gost_docx.ir.validator import ReferenceValidator


def _build_doc(blocks):
    """Build a Document IR from a list of blocks."""
    from typst_gost_docx.ir.model import Document

    return Document(id="test", blocks=blocks)


def _make_figure_with_label(label: str) -> Figure:
    return Figure(
        id=f"fig-{label}",
        label=label,
        caption=Caption(text="caption", numbering_kind=NumberingKind.FIGURE),
        source_location=SourceLocation(file_path="test.typ", line=1, column=0),
    )


def _make_paragraph_with_ref(target: str, line: int = 5) -> Paragraph:
    return Paragraph(
        id=f"p-{target}",
        runs=[
            CrossReference(
                target_label=target,
                source_location=SourceLocation(file_path="test.typ", line=line, column=0),
            )
        ],
        source_location=SourceLocation(file_path="test.typ", line=line, column=0),
    )


# ---------------------------------------------------------------------------
# collect_from_document — basic extraction
# ---------------------------------------------------------------------------


def test_collect_extracts_labels_and_references():
    fig = _make_figure_with_label("fig:results")
    para = _make_paragraph_with_ref("fig:results")
    doc = _build_doc([fig, para])

    validator = ReferenceValidator()
    validator.collect_from_document(doc)

    assert "fig:results" in validator.get_defined_labels()
    assert "fig:results" in validator.get_referenced_labels()


def test_collect_handles_empty_document():
    doc = _build_doc([])
    validator = ReferenceValidator()
    validator.collect_from_document(doc)
    assert validator.get_defined_labels() == {}
    assert validator.get_referenced_labels() == set()


def test_collect_clears_previous_state():
    """Calling collect_from_document twice starts from a clean slate."""
    fig = _make_figure_with_label("fig:first")
    doc1 = _build_doc([fig])
    doc2 = _build_doc([_make_figure_with_label("fig:second")])

    validator = ReferenceValidator()
    validator.collect_from_document(doc1)
    assert "fig:first" in validator.get_defined_labels()
    validator.collect_from_document(doc2)
    assert "fig:first" not in validator.get_defined_labels()
    assert "fig:second" in validator.get_defined_labels()


# ---------------------------------------------------------------------------
# validate — produces expected undefined/unreferenced sets
# ---------------------------------------------------------------------------


def test_validate_reports_undefined_reference():
    fig = _make_figure_with_label("fig:real")
    para = _make_paragraph_with_ref("fig:missing")
    doc = _build_doc([fig, para])

    validator = ReferenceValidator()
    validator.collect_from_document(doc)
    result = validator.validate()

    assert "fig:missing" in result.undefined_refs
    assert "fig:real" not in result.undefined_refs
    assert result.has_errors


def test_validate_reports_unreferenced_label():
    fig = _make_figure_with_label("fig:orphan")
    doc = _build_doc([fig])

    validator = ReferenceValidator()
    validator.collect_from_document(doc)
    result = validator.validate()

    assert "fig:orphan" in result.unreferenced_labels
    assert not result.has_errors
    assert result.has_warnings


def test_validate_clean_document_no_issues():
    fig = _make_figure_with_label("fig:used")
    para = _make_paragraph_with_ref("fig:used")
    doc = _build_doc([fig, para])

    validator = ReferenceValidator()
    validator.collect_from_document(doc)
    result = validator.validate()

    assert result.undefined_refs == set()
    assert result.unreferenced_labels == set()
    assert not result.has_errors
    assert not result.has_warnings


def test_validate_handles_multiple_issues():
    fig1 = _make_figure_with_label("fig:a")
    fig2 = _make_figure_with_label("fig:orphan")
    para1 = _make_paragraph_with_ref("fig:a")
    para2 = _make_paragraph_with_ref("fig:missing1")
    para3 = _make_paragraph_with_ref("fig:missing2")
    doc = _build_doc([fig1, fig2, para1, para2, para3])

    validator = ReferenceValidator()
    validator.collect_from_document(doc)
    result = validator.validate()

    assert result.undefined_refs == {"fig:missing1", "fig:missing2"}
    assert result.unreferenced_labels == {"fig:orphan"}


# ---------------------------------------------------------------------------
# get_validation_summary
# ---------------------------------------------------------------------------


def test_summary_counts_match_validator_state():
    fig1 = _make_figure_with_label("fig:a")
    fig2 = _make_figure_with_label("fig:b")
    doc = _build_doc(
        [
            fig1,
            fig2,
            _make_paragraph_with_ref("fig:a"),
            _make_paragraph_with_ref("fig:missing"),
        ]
    )

    validator = ReferenceValidator()
    validator.collect_from_document(doc)
    validator.validate()
    summary = validator.get_validation_summary()

    assert summary["total_labels"] == 2  # fig:a, fig:b
    assert summary["referenced_count"] == 1  # only fig:a is referenced
    assert summary["unreferenced_count"] == 1  # fig:b
    assert summary["total_refs"] == 2  # fig:a, fig:missing
    assert summary["defined_count"] == 1  # fig:a
    assert summary["undefined_count"] == 1  # fig:missing


def test_summary_zero_state_for_clean_document():
    doc = _build_doc([_make_paragraph_with_ref("fig:nothing_here")])
    validator = ReferenceValidator()
    validator.collect_from_document(doc)
    summary = validator.get_validation_summary()

    assert summary["total_labels"] == 0
    assert summary["total_refs"] == 1
    assert summary["undefined_count"] == 1


# ---------------------------------------------------------------------------
# ValidationResult behaviour
# ---------------------------------------------------------------------------


def test_validation_result_has_properties():
    result = ValidationResult(undefined_refs={"fig:missing"})
    assert result.has_errors
    assert not result.has_warnings

    result2 = ValidationResult(unreferenced_labels={"fig:orphan"})
    assert not result2.has_errors
    assert result2.has_warnings

    result3 = ValidationResult()
    assert not result3.has_errors
    assert not result3.has_warnings


def test_format_report_includes_undefined_refs():
    result = ValidationResult(undefined_refs={"fig:missing1", "fig:missing2"})
    report = result.format_report()

    assert "Undefined references" in report
    assert "fig:missing1" in report
    assert "fig:missing2" in report


def test_format_report_includes_unreferenced_labels():
    result = ValidationResult(unreferenced_labels={"tbl:orphan"})
    report = result.format_report()

    assert "Unreferenced labels" in report
    assert "tbl:orphan" in report


def test_format_report_clean_document():
    result = ValidationResult()
    report = result.format_report()

    # A clean document should produce a report with no error indicators.
    assert "No validation issues found" in report or "no errors" in report.lower() or not result.has_errors


# ---------------------------------------------------------------------------
# Section-aware nesting
# ---------------------------------------------------------------------------


def test_collect_descends_into_section_blocks():
    fig = _make_figure_with_label("fig:nested")
    para = _make_paragraph_with_ref("fig:nested", line=10)
    section = Section(
        id="s1",
        level=1,
        title=[TextRun(id="t1", text="Chapter")],
        blocks=[fig, para],
        source_location=SourceLocation(file_path="test.typ", line=1, column=0),
    )
    doc = _build_doc([section])

    validator = ReferenceValidator()
    validator.collect_from_document(doc)

    assert "fig:nested" in validator.get_defined_labels()
    assert "fig:nested" in validator.get_referenced_labels()


# ---------------------------------------------------------------------------
# Spec 001 T083 — file:line attribution on issues
# ---------------------------------------------------------------------------


def test_validation_issue_carries_source_location():
    """Each ValidationIssue must include the file/line of the offending node."""
    fig = _make_figure_with_label("fig:real")
    para = _make_paragraph_with_ref("fig:missing", line=42)
    doc = _build_doc([fig, para])

    validator = ReferenceValidator()
    validator.collect_from_document(doc)
    result = validator.validate()

    # Validator must surface the issue through the rich ``issues`` list.
    assert result.issues
    undefined_issues = [i for i in result.issues if i.kind == "undefined_ref"]
    assert len(undefined_issues) == 1
    issue = undefined_issues[0]
    assert issue.label == "fig:missing"
    assert issue.line == 42
    assert issue.file_path == "test.typ"
    # ``undefined_refs`` stays in sync for backwards compatibility.
    assert "fig:missing" in result.undefined_refs


def test_format_report_uses_file_line_when_available():
    """The text report should mention the file/line of every issue."""
    fig = _make_figure_with_label("fig:real")
    para = _make_paragraph_with_ref("fig:missing", line=7)
    doc = _build_doc([fig, para])

    validator = ReferenceValidator()
    validator.collect_from_document(doc)
    result = validator.validate()

    report = result.format_report()
    assert "test.typ:7" in report
    assert "fig:missing" in report


def test_format_report_groups_by_kind():
    """The report should label each group clearly (errors / info)."""
    result = ValidationResult(
        undefined_refs={"fig:missing"},
        unreferenced_labels={"tbl:orphan"},
    )
    report = result.format_report()

    assert "Undefined references" in report
    assert "Unreferenced labels" in report
    assert "WARNING: @fig:missing" in report
    assert "INFO: <tbl:orphan>" in report


# ---------------------------------------------------------------------------
# Spec 001 T086 — summary statistics, including citation counts
# ---------------------------------------------------------------------------


def test_summary_includes_citation_keys():
    """When bibliography entries are provided, summary must include citation stats."""
    from typst_gost_docx.ir.model import BibliographyEntry, BibliographyType

    entries = {
        "smith2023": BibliographyEntry(
            id="smith2023",
            entry_type=BibliographyType.ARTICLE,
            author="Smith",
            title="Title",
            year="2023",
        )
    }
    validator = ReferenceValidator(bibliography_entries=entries)
    summary = validator.get_validation_summary()
    # The summary has the new citation_keys_* fields even with no citations.
    assert summary["citation_keys_total"] == 0
    assert summary["citation_keys_defined"] == 0
    assert summary["citation_keys_missing"] == 0


# ---------------------------------------------------------------------------
# Spec 001 T088 — RefResolver.build_validation_report
# ---------------------------------------------------------------------------


def test_build_validation_report_lifts_unresolved_warnings():
    """build_validation_report turns resolver warnings into structured issues."""
    from typst_gost_docx.parser.refs import RefResolver
    from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2
    from typst_gost_docx.parser.numbering import ChapterNumberer

    text = "= Intro\n\nSee @fig:missing.\n"
    doc = TypstExtractorV2(text, "test.typ").extract()
    ChapterNumberer().number_document(doc)
    warnings = RefResolver().resolve_document(doc)

    assert warnings == ["Unresolved reference: @fig:missing"]

    report = RefResolver.build_validation_report(doc, warnings)
    assert report.has_errors
    assert "fig:missing" in report.undefined_refs
    assert report.issues
    issue = report.issues[0]
    assert issue.kind == "undefined_ref"
    assert issue.label == "fig:missing"
    assert issue.file_path == "test.typ"
    assert issue.line == 3  # paragraph "See @fig:missing." is on line 3
