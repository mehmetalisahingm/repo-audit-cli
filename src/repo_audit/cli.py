from __future__ import annotations

import argparse
import sys
from pathlib import Path

from repo_audit import __version__
from repo_audit.analyzer import audit_repository
from repo_audit.reporting import render_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repo-audit",
        description="Score a repository for baseline engineering hygiene signals.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Repository path to audit.")
    parser.add_argument(
        "--format",
        choices=("text", "json", "markdown"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional file path to write the rendered report.",
    )
    parser.add_argument(
        "--fail-under",
        type=int,
        default=0,
        metavar="SCORE",
        help="Exit with status 1 if the score is below SCORE.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        report = audit_repository(args.path)
    except (FileNotFoundError, NotADirectoryError) as error:
        parser.error(str(error))

    rendered = render_report(report, args.format)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)

    if report.total_score < args.fail_under:
        print(
            f"Score {report.total_score} is below required threshold {args.fail_under}.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
