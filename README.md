# repo-audit

`repo-audit` is a lightweight CLI that scores a source repository against the baseline signals people expect on GitHub: README quality, license, tests, CI, ignore rules, community docs, and dependency metadata.

It is intentionally dependency-free so it can run in local repos, CI jobs, or pre-release checks without extra setup.

## Why this project

If you want a stronger GitHub profile, shipping a tool that other developers can actually use is better than another generic CRUD app. `repo-audit` is small enough to finish cleanly, but useful enough to demonstrate product thinking, code quality, documentation, testing, and CI.

## Five portfolio ideas

These were the five project directions considered for a GitHub-strengthening project:

1. `repo-audit`: a CLI that audits repository quality signals and outputs a score plus actionable recommendations.
2. `release-digest`: a tool that generates release notes from commits, PR titles, and labels.
3. `issue-to-spec`: an assistant that turns GitHub issues into implementation-ready technical specs.
4. `dep-watch`: a dependency risk monitor that flags stale, vulnerable, or abandoned packages.
5. `readme-lab`: a generator that creates polished project README files from repository structure and metadata.

## Features

- Scores repositories out of 100.
- Produces `text`, `json`, or `markdown` reports.
- Highlights exactly which checks are missing or partial.
- Supports CI gating with `--fail-under`.
- Uses only the Python standard library.

## Installation

```bash
python -m pip install .
```

## Usage

Audit the current repository:

```bash
repo-audit .
```

Export a machine-readable report:

```bash
repo-audit . --format json --output audit-report.json
```

Use it as a CI quality gate:

```bash
repo-audit . --fail-under 80
```

## Sample output

```text
Repository: repo-audit
Score: 100/100 (A)

[PASS] Git metadata          10/10  Repository contains a .git directory.
[PASS] README quality        20/20  README includes installation and usage guidance.
[PASS] License               10/10  Found LICENSE.
[PASS] Ignore rules          10/10  Found .gitignore.
[PASS] Dependency manifest   10/10  Found pyproject.toml.
[PASS] Tests                 15/15  Found tests in tests.
[PASS] CI workflows          15/15  Found GitHub Actions workflow files.
[PASS] Community docs        10/10  Found CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md.
```

## What gets checked

- Git metadata
- README presence and basic usability sections
- License file
- Ignore rules
- Dependency/package manifest
- Tests
- GitHub Actions workflow files
- Community-facing docs

## Development

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

Run the CLI against this project:

```bash
python -m repo_audit .
```

## Roadmap

- Add framework-specific checks for Python, Node.js, Rust, and Go.
- Add badge generation for README integration.
- Add optional SARIF export for code scanning workflows.

## License

MIT
