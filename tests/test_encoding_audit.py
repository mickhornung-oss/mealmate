from tools.diagnostics.encoding_audit import run_audit


def test_encoding_audit_is_clean() -> None:
    report = run_audit()
    assert not report.has_errors, (
        f"decode={len(report.decode_issues)} "
        f"replacement={len(report.replacement_issues)} "
        f"suspicious={len(report.suspicious_issues)}"
    )
