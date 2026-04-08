from __future__ import annotations

import json

from repo_audit.analyzer import AuditReport


def render_report(report: AuditReport, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report.to_dict(), indent=2)
    if output_format == "markdown":
        return _render_markdown(report)
    return _render_text(report)


def _render_text(report: AuditReport) -> str:
    lines = [
        f"Repository: {report.repo_name}",
        f"Score: {report.total_score}/{report.max_score} ({report.grade})",
        "",
    ]

    for check in report.checks:
        lines.append(
            f"[{check.status}] {check.title:<18} {check.score:>2}/{check.max_score:<2}  {check.details}"
        )

    if report.recommendations:
        lines.extend(["", "Recommendations:"])
        for recommendation in report.recommendations:
            lines.append(f"- {recommendation}")

    return "\n".join(lines)


def _render_markdown(report: AuditReport) -> str:
    lines = [
        f"# Repository Audit: {report.repo_name}",
        "",
        f"**Score:** {report.total_score}/{report.max_score} ({report.grade})",
        "",
        "| Status | Check | Score | Details |",
        "| --- | --- | --- | --- |",
    ]

    for check in report.checks:
        lines.append(
            f"| {check.status} | {check.title} | {check.score}/{check.max_score} | {check.details} |"
        )

    if report.recommendations:
        lines.extend(["", "## Recommendations"])
        for recommendation in report.recommendations:
            lines.append(f"- {recommendation}")

    return "\n".join(lines)
