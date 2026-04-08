from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

README_CANDIDATES = ("README.md", "README.rst", "README.txt", "readme.md")
LICENSE_CANDIDATES = ("LICENSE", "LICENSE.md", "COPYING", "COPYING.md", "UNLICENSE")
MANIFEST_CANDIDATES = (
    "pyproject.toml",
    "package.json",
    "go.mod",
    "Cargo.toml",
    "pom.xml",
    "requirements.txt",
    "Pipfile",
    "composer.json",
)
EXCLUDED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
}


@dataclass(frozen=True)
class CheckResult:
    key: str
    title: str
    score: int
    max_score: int
    details: str
    recommendation: str

    @property
    def passed(self) -> bool:
        return self.score == self.max_score

    @property
    def status(self) -> str:
        if self.passed:
            return "PASS"
        if self.score == 0:
            return "FAIL"
        return "WARN"

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["passed"] = self.passed
        payload["status"] = self.status
        return payload


@dataclass(frozen=True)
class AuditReport:
    path: str
    repo_name: str
    total_score: int
    max_score: int
    checks: list[CheckResult]

    @property
    def percentage(self) -> int:
        return round((self.total_score / self.max_score) * 100) if self.max_score else 0

    @property
    def grade(self) -> str:
        if self.percentage >= 90:
            return "A"
        if self.percentage >= 80:
            return "B"
        if self.percentage >= 70:
            return "C"
        if self.percentage >= 60:
            return "D"
        return "E"

    @property
    def recommendations(self) -> list[str]:
        return [check.recommendation for check in self.checks if check.score < check.max_score]

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "repo_name": self.repo_name,
            "total_score": self.total_score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "grade": self.grade,
            "checks": [check.to_dict() for check in self.checks],
            "recommendations": self.recommendations,
        }


def audit_repository(target: str | Path) -> AuditReport:
    root = Path(target).resolve()
    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    checks = [
        _check_git_metadata(root),
        _check_readme(root),
        _check_license(root),
        _check_ignore_rules(root),
        _check_manifest(root),
        _check_tests(root),
        _check_ci(root),
        _check_community_docs(root),
    ]
    return AuditReport(
        path=str(root),
        repo_name=root.name,
        total_score=sum(check.score for check in checks),
        max_score=sum(check.max_score for check in checks),
        checks=checks,
    )


def _check_git_metadata(root: Path) -> CheckResult:
    has_git = (root / ".git").exists()
    return CheckResult(
        key="git_metadata",
        title="Git metadata",
        score=10 if has_git else 0,
        max_score=10,
        details="Repository contains a .git directory." if has_git else "No .git directory found.",
        recommendation="Initialize git before publishing the project." if not has_git else "",
    )


def _check_readme(root: Path) -> CheckResult:
    readme = _find_existing(root, README_CANDIDATES)
    if readme is None:
        return CheckResult(
            key="readme_quality",
            title="README quality",
            score=0,
            max_score=20,
            details="No README file found.",
            recommendation="Add a README with installation and usage sections.",
        )

    content = readme.read_text(encoding="utf-8", errors="ignore").lower()
    score = 8
    missing_sections: list[str] = []

    if _contains_any(content, ("installation", "getting started", "setup", "quickstart", "quick start")):
        score += 6
    else:
        missing_sections.append("installation")

    if _contains_any(content, ("usage", "example", "examples", "how to use")):
        score += 6
    else:
        missing_sections.append("usage")

    if not missing_sections:
        details = f"{readme.name} includes installation and usage guidance."
        recommendation = ""
    else:
        joined = " and ".join(missing_sections)
        details = f"{readme.name} exists but is missing {joined} guidance."
        recommendation = f"Expand {readme.name} with {joined} instructions."

    return CheckResult(
        key="readme_quality",
        title="README quality",
        score=score,
        max_score=20,
        details=details,
        recommendation=recommendation,
    )


def _check_license(root: Path) -> CheckResult:
    license_file = _find_existing(root, LICENSE_CANDIDATES)
    found = license_file is not None
    return CheckResult(
        key="license",
        title="License",
        score=10 if found else 0,
        max_score=10,
        details=f"Found {license_file.name}." if found else "No license file found.",
        recommendation="Add an open-source license file." if not found else "",
    )


def _check_ignore_rules(root: Path) -> CheckResult:
    ignore_file = root / ".gitignore"
    found = ignore_file.is_file()
    return CheckResult(
        key="ignore_rules",
        title="Ignore rules",
        score=10 if found else 0,
        max_score=10,
        details="Found .gitignore." if found else "No .gitignore file found.",
        recommendation="Add a .gitignore file that matches the project stack." if not found else "",
    )


def _check_manifest(root: Path) -> CheckResult:
    manifest = _find_existing(root, MANIFEST_CANDIDATES)
    found = manifest is not None
    return CheckResult(
        key="dependency_manifest",
        title="Dependency manifest",
        score=10 if found else 0,
        max_score=10,
        details=f"Found {manifest.name}." if found else "No recognized dependency or package manifest found.",
        recommendation="Add a package or dependency manifest such as pyproject.toml or package.json." if not found else "",
    )


def _check_tests(root: Path) -> CheckResult:
    test_locations = list(_find_test_locations(root))
    found = bool(test_locations)
    detail = f"Found tests in {', '.join(test_locations)}." if found else "No tests were detected."
    return CheckResult(
        key="tests",
        title="Tests",
        score=15 if found else 0,
        max_score=15,
        details=detail,
        recommendation="Add automated tests under a tests directory or test file naming convention." if not found else "",
    )


def _check_ci(root: Path) -> CheckResult:
    workflow_dir = root / ".github" / "workflows"
    workflows = sorted(path.name for path in workflow_dir.glob("*.y*ml")) if workflow_dir.is_dir() else []
    found = bool(workflows)
    detail = "Found GitHub Actions workflow files." if found else "No GitHub Actions workflows found."
    return CheckResult(
        key="ci",
        title="CI workflows",
        score=15 if found else 0,
        max_score=15,
        details=detail,
        recommendation="Add at least one CI workflow under .github/workflows." if not found else "",
    )


def _check_community_docs(root: Path) -> CheckResult:
    weights = {
        "CONTRIBUTING.md": 4,
        "CODE_OF_CONDUCT.md": 3,
        "SECURITY.md": 3,
    }
    present = [name for name in weights if (root / name).is_file()]
    score = sum(weights[name] for name in present)
    missing = [name for name in weights if name not in present]

    if not missing:
        details = "Found CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md."
        recommendation = ""
    elif present:
        details = f"Found {', '.join(present)} but missing {', '.join(missing)}."
        recommendation = f"Add the missing community docs: {', '.join(missing)}."
    else:
        details = "No community docs found."
        recommendation = "Add CONTRIBUTING.md, CODE_OF_CONDUCT.md, and SECURITY.md."

    return CheckResult(
        key="community_docs",
        title="Community docs",
        score=score,
        max_score=10,
        details=details,
        recommendation=recommendation,
    )


def _find_existing(root: Path, candidates: Iterable[str]) -> Path | None:
    for candidate in candidates:
        path = root / candidate
        if path.is_file():
            return path
    return None


def _contains_any(content: str, keywords: Iterable[str]) -> bool:
    return any(keyword in content for keyword in keywords)


def _find_test_locations(root: Path) -> Iterable[str]:
    seen: set[str] = set()
    test_markers = ("tests", "test", "spec")
    file_suffixes = (".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs")

    for path in root.rglob("*"):
        if any(part in EXCLUDED_DIRECTORIES for part in path.parts):
            continue
        relative = path.relative_to(root)
        if path.is_dir() and relative.name == "tests":
            seen.add(relative.as_posix())
            continue
        if not path.is_file() or path.suffix not in file_suffixes:
            continue
        name = path.name.lower()
        if any(marker in name for marker in test_markers):
            seen.add(relative.parent.as_posix() if relative.parent.as_posix() != "." else relative.as_posix())

    yield from sorted(seen)
