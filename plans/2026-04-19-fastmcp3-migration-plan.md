# FastMCP 3 Migration + v2.0.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `csv-editor` v2.0.0 with Python 3.11 floor, FastMCP 3.2, non-breaking dep bumps, SSE transport removed, and automated test CI — as four sequential PRs against `main`.

**Architecture:** Phased rollout — each PR is independently reviewable, lands on `main`, and is green in CI before the next begins. No long-lived release branch. Four PRs total:
1. Add CI test workflow
2. Python floor 3.11 + non-breaking dep bumps
3. FastMCP 2 → 3 migration + SSE removal
4. CHANGELOG + version bump + v2.0.0 tag

**Tech Stack:** Python 3.11+, FastMCP 3.2, pydantic 2.13, pyarrow 23, pytest 8, uv, GitHub Actions.

**Spec:** [`specs/2026-04-19-fastmcp3-migration-design.md`](../specs/2026-04-19-fastmcp3-migration-design.md)

---

## File Structure

**New files:**
- `.github/workflows/test.yml` — pytest matrix workflow
- `tests/test_server_boot.py` — regression tests for server boot, tool registry, SSE rejection

**Modified files:**
- `pyproject.toml` — Python floor, classifiers, deps, tool target-versions, version bump
- `src/csv_editor/server.py` — argparse `--transport` choices, `health_check` version
- `README.md` — Python badge, remove 3.8/3.9 claims, remove SSE references
- `Dockerfile` — pin base image to `python:3.11-slim-bookworm`
- `MCP_CONFIG.md` — remove SSE references
- `CONTRIBUTING.md` — add `.venv` rebuild note
- `CHANGELOG.md` — new `[2.0.0]` section

**Unchanged (verify only):**
- `smithery.yaml` — uses stdio transport only; no SSE reference
- `.github/workflows/publish.yml`, `publish-github.yml`, `deploy-docs.yml` — unrelated
- `src/csv_editor/tools/*.py` — no code changes needed
- `src/csv_editor/models/*.py` — no code changes needed

---

## Pre-flight: Fix local dev environment

The maintainer's `.venv` points at a removed conda interpreter. This blocks local test runs. Fix once before starting.

### Task 0: Rebuild local venv

**Files:** none (local only)

- [ ] **Step 1: Remove broken venv**

```bash
rm -rf .venv
```

- [ ] **Step 2: Verify uv is installed**

Run: `uv --version`
Expected: prints a version (e.g., `uv 0.5.x`). If not: `curl -LsSf https://astral.sh/uv/install.sh | sh`

- [ ] **Step 3: Sync dependencies**

Run: `uv sync --all-extras`
Expected: creates fresh `.venv/`, installs deps, exits 0.

- [ ] **Step 4: Verify tests can run**

Run: `uv run pytest tests/ --collect-only -q`
Expected: pytest collects test files without import errors. Record the total count in a scratch note (needed for PR 1 baseline).

- [ ] **Step 5: Run full suite to establish baseline**

Run: `uv run pytest tests/ -v`
Expected: tests execute; record PASS/FAIL counts. Any failures are pre-existing and not this plan's concern — they'll be tracked as a follow-up issue in Task 5.

No commit for Task 0 (local-only, `.venv` is gitignored).

---

## PR 1: CI Workflow Baseline

**Branch name:** `ci/add-test-workflow`
**Goal:** add pytest matrix GitHub Actions workflow that runs on every PR and push to main.

### Task 1: Add test workflow file

**Files:**
- Create: `.github/workflows/test.yml`

- [ ] **Step 1: Create branch**

```bash
git checkout main
git pull --ff-only origin main
git checkout -b ci/add-test-workflow
```

- [ ] **Step 2: Write the workflow file**

Create `.github/workflows/test.yml` with:

```yaml
name: test

on:
  pull_request:
  push:
    branches: [main]

jobs:
  pytest:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13", "3.14"]
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Sync dependencies
        run: uv sync --all-extras

      - name: Run pytest
        run: uv run pytest tests/ -v --tb=short
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/test.yml
git commit -m "ci: add pytest matrix workflow (3.10-3.14 on ubuntu)"
```

- [ ] **Step 4: Push and open PR**

```bash
git push -u origin ci/add-test-workflow
```

Then open a PR on GitHub with title `ci: add pytest matrix workflow` and body describing: "Adds a GitHub Actions workflow that runs pytest on Python 3.10–3.14 for every PR and push to main. Prerequisite for PR 2 (dep bumps) and PR 3 (FastMCP 3 migration)."

- [ ] **Step 5: Verify workflow triggers**

On the PR page, confirm a `test` check appears. Wait for matrix to complete.

Expected: All 5 matrix rows complete (green or red is both OK — the runner existing is the deliverable).

- [ ] **Step 6: Document baseline result**

If any rows are red, open a new GitHub issue titled "Pre-existing test failures on main" listing the failing tests per Python version. Link the issue in the PR description.

If all green: note that in the PR description ("baseline clean").

- [ ] **Step 7: Merge PR 1**

Merge via GitHub UI (squash merge). Confirm `main` now runs the workflow on subsequent pushes.

---

## PR 2: Python 3.11 Floor + Non-Breaking Dep Bumps

**Branch name:** `deps/python-311-and-bumps`
**Goal:** bump Python floor and non-breaking dependencies; update tooling target-versions; CI matrix drops 3.10.

### Task 2: Create branch and bump Python floor in pyproject.toml

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Create branch**

```bash
git checkout main
git pull --ff-only origin main
git checkout -b deps/python-311-and-bumps
```

- [ ] **Step 2: Bump `requires-python` and classifiers**

In `pyproject.toml`:

Change:
```toml
requires-python = ">=3.10"
```
to:
```toml
requires-python = ">=3.11"
```

Change classifiers from:
```toml
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
```
to:
```toml
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
```

(Delete the 3.8, 3.9, 3.10 lines; add the 3.14 line.)

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: bump Python floor to 3.11, add 3.14 classifier"
```

### Task 3: Bump non-breaking dependencies

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Update dependency pins**

In `pyproject.toml`, change the `dependencies` block from:

```toml
dependencies = [
    "fastmcp>=2.11.3",
    "pandas>=2.2.3",
    "numpy>=2.1.3",
    "pydantic>=2.10.4",
    "aiofiles>=24.1.0",
    "python-dateutil>=2.9.0",
    "httpx>=0.27.0",
    "openpyxl>=3.1.5",
    "pyarrow>=17.0.0",
    "tabulate>=0.9.0",
    "pytz>=2024.2",
    "pydantic-settings>=2.10.1",
]
```

to (note: `fastmcp` pin is **unchanged** in this PR; PR 3 handles it):

```toml
dependencies = [
    "fastmcp>=2.11.3",
    "pandas>=2.2.3",
    "numpy>=2.1.3",
    "pydantic>=2.13",
    "aiofiles>=25",
    "python-dateutil>=2.9.0",
    "httpx>=0.28",
    "openpyxl>=3.1.5",
    "pyarrow>=23",
    "tabulate>=0.10",
    "pytz>=2024.2",
    "pydantic-settings>=2.13",
]
```

- [ ] **Step 2: Sync and run tests locally**

```bash
uv sync --all-extras
uv run pytest tests/ -v --tb=short
```

Expected: tests execute; pass rate matches PR 1 baseline (from Task 0 Step 5 / Task 1 Step 6).

If any test that was green on baseline now fails, **stop**: the bump introduced a regression. Bisect by reverting dep pins one at a time to identify which dep caused it. Most likely suspect: pydantic 2.13 union serialization. Hotfix by pinning `pydantic<2.13` and opening a follow-up issue.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: bump non-breaking deps (pydantic 2.13, pyarrow 23, httpx 0.28, aiofiles 25, tabulate 0.10)"
```

### Task 4: Bump tool target-versions

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Update black target-version**

In `pyproject.toml`:

Change:
```toml
[tool.black]
line-length = 100
target-version = ["py38", "py39", "py310", "py311", "py312", "py313"]
```
to:
```toml
[tool.black]
line-length = 100
target-version = ["py311", "py312", "py313", "py314"]
```

- [ ] **Step 2: Update ruff target-version**

Change:
```toml
[tool.ruff]
line-length = 100
target-version = "py38"
```
to:
```toml
[tool.ruff]
line-length = 100
target-version = "py311"
```

- [ ] **Step 3: Update mypy python_version**

Change:
```toml
[tool.mypy]
python_version = "3.8"
```
to:
```toml
[tool.mypy]
python_version = "3.11"
```

- [ ] **Step 4: Run linters to confirm no regressions**

```bash
uv run ruff check src/ tests/
uv run black --check src/ tests/
```

Expected: both exit 0 (no formatting/lint changes needed from the target-version bump alone).

If ruff suggests any `UP` (pyupgrade) rule changes because 3.11+ is now the floor, accept them as a separate step below.

- [ ] **Step 5: If ruff proposed UP fixes, apply them**

```bash
uv run ruff check src/ tests/ --fix
```

- [ ] **Step 6: Re-run tests**

```bash
uv run pytest tests/ -v --tb=short
```

Expected: pass rate matches baseline.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml src/ tests/
git commit -m "chore: bump black/ruff/mypy target-version to Python 3.11"
```

### Task 5: Update Dockerfile, README, CONTRIBUTING

**Files:**
- Modify: `Dockerfile`
- Modify: `README.md`
- Modify: `CONTRIBUTING.md`

- [ ] **Step 1: Pin Dockerfile base image**

In `Dockerfile`, change line 2 from:
```dockerfile
FROM python:3.11-slim
```
to:
```dockerfile
FROM python:3.11-slim-bookworm
```

- [ ] **Step 2: Update README Python badge**

In `README.md`, find the Python badge near the top:
```markdown
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
```
Change to:
```markdown
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
```

- [ ] **Step 3: Scrub 3.8/3.9/3.10 claims from README**

Grep: `grep -n "3\.8\|3\.9\|3\.10" README.md`

For each match, update the sentence to reflect the 3.11 floor (or delete if the line is an obsolete compatibility note). Do **not** touch version numbers of libraries that happen to contain these digits.

- [ ] **Step 4: Add .venv rebuild note to CONTRIBUTING.md**

In `CONTRIBUTING.md`, find the "Development Setup" or equivalent section. Add (or update if one exists) a subsection:

```markdown
### Rebuilding the local virtualenv

If your `.venv/` points at a missing Python interpreter (common after upgrading Python or removing a conda env), rebuild it:

```bash
rm -rf .venv
uv sync --all-extras
```

This requires Python 3.11+ available on your PATH (3.14 recommended).
```

If `CONTRIBUTING.md` has no "Development Setup" section, append the subsection at the end of the file with a `## Development` heading.

- [ ] **Step 5: Commit**

```bash
git add Dockerfile README.md CONTRIBUTING.md
git commit -m "docs: pin Dockerfile base, update README badge, add venv rebuild guide"
```

### Task 6: Drop Python 3.10 from CI matrix

**Files:**
- Modify: `.github/workflows/test.yml`

- [ ] **Step 1: Remove 3.10 from matrix**

In `.github/workflows/test.yml`, change:
```yaml
        python-version: ["3.10", "3.11", "3.12", "3.13", "3.14"]
```
to:
```yaml
        python-version: ["3.11", "3.12", "3.13", "3.14"]
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/test.yml
git commit -m "ci: drop Python 3.10 from matrix (floor bumped to 3.11)"
```

### Task 7: Push and merge PR 2

- [ ] **Step 1: Push branch**

```bash
git push -u origin deps/python-311-and-bumps
```

- [ ] **Step 2: Open PR**

Title: `deps: bump Python floor to 3.11 and non-breaking dependencies`
Body: "Bumps Python floor from 3.10 to 3.11. Bumps pydantic, pydantic-settings, pyarrow, httpx, aiofiles, tabulate to current major versions. FastMCP and pandas are **not** bumped in this PR. Drops 3.10 from CI matrix. Part of v2.0.0 preparation (spec: `specs/2026-04-19-fastmcp3-migration-design.md`)."

- [ ] **Step 3: Wait for CI green**

All four matrix rows (3.11, 3.12, 3.13, 3.14) must be green.

If red on pydantic 2.13: follow the risk mitigation in the spec (pin `pydantic<2.13`, open issue).

- [ ] **Step 4: Merge**

Squash merge via GitHub UI. Delete the branch.

---

## PR 3: FastMCP 3 Migration + SSE Removal

**Branch name:** `feat/fastmcp-3-migration`
**Goal:** bump FastMCP to 3.2; remove `sse` from CLI `--transport` choices; add boot regression tests.

### Task 8: Create branch and add failing boot tests

**Files:**
- Create: `tests/test_server_boot.py`

- [ ] **Step 1: Create branch**

```bash
git checkout main
git pull --ff-only origin main
git checkout -b feat/fastmcp-3-migration
```

- [ ] **Step 2: Write test file**

Create `tests/test_server_boot.py`:

```python
"""Smoke tests for server boot, tool registry, and CLI argument handling."""

import pytest


def test_server_imports_clean():
    """Importing the server module must not raise."""
    import csv_editor.server  # noqa: F401


def test_tool_registry_populated():
    """After import, the FastMCP instance must have at least 40 registered tools."""
    from csv_editor.server import mcp

    # FastMCP exposes registered tools via _tool_manager in 3.x; fall back to list_tools-style APIs
    # if the attribute name differs. We probe several plausible locations to stay robust.
    tool_count = _count_registered_tools(mcp)

    assert tool_count >= 40, f"Expected at least 40 tools registered, got {tool_count}"


def test_cli_rejects_sse_transport():
    """The CLI must reject --transport sse with a non-zero exit."""
    from csv_editor.server import main

    with pytest.raises(SystemExit) as exc_info:
        main(["--transport", "sse"])  # argparse exits on invalid choice

    # argparse uses exit code 2 for argument errors
    assert exc_info.value.code == 2


def _count_registered_tools(mcp) -> int:
    """Robustly count registered tools across FastMCP 2.x/3.x attribute naming."""
    for attr in ("_tool_manager", "tool_manager", "_tools", "tools"):
        obj = getattr(mcp, attr, None)
        if obj is None:
            continue
        tools = getattr(obj, "_tools", None) or getattr(obj, "tools", None) or obj
        try:
            return len(tools)
        except TypeError:
            continue
    # Fall back to calling a list-tools coroutine if present (FastMCP 3)
    list_tools = getattr(mcp, "list_tools", None)
    if callable(list_tools):
        import asyncio
        result = asyncio.run(list_tools())
        return len(result)
    raise RuntimeError("Could not locate FastMCP tool registry")
```

- [ ] **Step 3: Run the tests — two must fail**

```bash
uv run pytest tests/test_server_boot.py -v
```

Expected:
- `test_server_imports_clean` — **PASS** (server already imports cleanly)
- `test_tool_registry_populated` — **PASS or FAIL** depending on how FastMCP 2.11 exposes the registry; if FAIL, the `_count_registered_tools` helper needs adjustment. If you cannot locate the registry in 2.x, mark the test `@pytest.mark.skip(reason="registry location verified after FastMCP 3 migration")` and remove the skip in Task 10.
- `test_cli_rejects_sse_transport` — **FAIL**: `sse` is currently a valid choice, so `main` will proceed rather than SystemExit. This is the red we want — PR 3 will turn it green.

Note: `main` is defined but does not currently accept `argv` as a parameter. You will need to refactor `main` in Task 9 to accept `argv: list[str] | None = None` so tests can invoke it. Record this as a prerequisite for Task 9.

- [ ] **Step 4: Commit the failing tests**

```bash
git add tests/test_server_boot.py
git commit -m "test: add server boot + CLI regression tests (one intentionally failing)"
```

### Task 9: Refactor `main` to accept argv and drop `sse` choice

**Files:**
- Modify: `src/csv_editor/server.py` (lines around 635–679)

- [ ] **Step 1: Refactor `main` signature**

In `src/csv_editor/server.py`, change the `def main():` line to accept an optional argv parameter. Change the `parser.parse_args()` call to pass `argv` through.

Find:
```python
def main():
    """Main entry point for the server."""
    import argparse

    parser = argparse.ArgumentParser(description="CSV Editor")
```

Change to:
```python
def main(argv: list[str] | None = None):
    """Main entry point for the server."""
    import argparse

    parser = argparse.ArgumentParser(description="CSV Editor")
```

Find:
```python
    args = parser.parse_args()
```

Change to:
```python
    args = parser.parse_args(argv)
```

- [ ] **Step 2: Drop `sse` from `--transport` choices**

Find:
```python
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="Transport method"
    )
```

Change to:
```python
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport method (stdio for local clients, http for Streamable HTTP remote)"
    )
```

- [ ] **Step 3: Run tests — expect test_cli_rejects_sse_transport to pass now**

```bash
uv run pytest tests/test_server_boot.py -v
```

Expected: `test_cli_rejects_sse_transport` now **PASS**.

- [ ] **Step 4: Commit**

```bash
git add src/csv_editor/server.py
git commit -m "feat: drop sse from --transport CLI choices, refactor main to accept argv"
```

### Task 10: Bump FastMCP pin to 3.2

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Update FastMCP pin**

In `pyproject.toml`, change:
```toml
    "fastmcp>=2.11.3",
```
to:
```toml
    "fastmcp>=3.2,<4",
```

- [ ] **Step 2: Sync**

```bash
uv sync --all-extras
```

Expected: resolves to FastMCP 3.2.x, no conflicts.

- [ ] **Step 3: Run full test suite**

```bash
uv run pytest tests/ -v --tb=short
```

Expected:
- All three tests in `test_server_boot.py` pass (including `test_tool_registry_populated` — if it was skipped in Task 8 Step 3, remove the skip marker now and confirm pass).
- Other tests pass at the rate matching baseline.

If any tool-decorator test fails due to FastMCP API drift (e.g., `Context` API changed), consult the [FastMCP 3 upgrade guide](https://gofastmcp.com/getting-started/upgrading/from-fastmcp-2) and patch `src/csv_editor/server.py` or the affected tool module. Common fixes:
- `Context` import path unchanged.
- Tool decorator (`@mcp.tool`) unchanged.
- Constructor already minimal (`FastMCP("CSV Editor")`), no kwargs to strip.

- [ ] **Step 4: Manually smoke-test stdio transport**

Start the server in one terminal:
```bash
uv run csv-editor --transport stdio
```

In a second terminal, send a `tools/list` JSON-RPC request via stdin (or use an MCP client like Claude Desktop configured against the local build).

Expected: server responds with a list of ≥40 tools.

Kill the server with Ctrl-C.

- [ ] **Step 5: Manually smoke-test http transport**

```bash
uv run csv-editor --transport http --port 8765
```

In a second terminal:
```bash
curl -sv http://127.0.0.1:8765/mcp
```

Expected: HTTP response (likely 400 or 405 for a bare GET, since Streamable HTTP expects JSON-RPC POST — the point is the server bound and is listening, not that curl completes a handshake).

Kill the server.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml tests/test_server_boot.py
git commit -m "feat: migrate to FastMCP 3.2"
```

(`tests/test_server_boot.py` is included in case the skip marker was removed in Step 3.)

### Task 11: Scrub SSE references from docs

**Files:**
- Modify: `README.md`
- Modify: `MCP_CONFIG.md`

- [ ] **Step 1: Find SSE references**

```bash
grep -n -i "sse\|server-sent" README.md MCP_CONFIG.md
```

Record each match.

- [ ] **Step 2: Update each reference**

For each match:
- If the line documents `--transport sse` as a valid option: **delete** the line or replace with `--transport http`.
- If the line explains SSE as a transport alternative: **delete** the paragraph.
- If the line is in a table of transports: **remove the SSE row**.

Do not touch any line that happens to contain "SSE" as part of an unrelated word (search is case-insensitive to catch `sse` fragments; verify context before editing).

- [ ] **Step 3: Verify no remaining SSE references**

```bash
grep -n -i "sse\|server-sent" README.md MCP_CONFIG.md
```

Expected: no matches (or only matches in unrelated words you've already verified).

- [ ] **Step 4: Commit**

```bash
git add README.md MCP_CONFIG.md
git commit -m "docs: remove SSE transport references"
```

### Task 12: Verify Dockerfile and Smithery config

**Files:** none changed (verification only)

- [ ] **Step 1: Confirm Dockerfile CMD uses stdio**

```bash
grep "CMD\|ENTRYPOINT" Dockerfile
```

Expected: `CMD ["csv-editor", "--transport", "stdio"]` — no SSE reference.

- [ ] **Step 2: Confirm smithery.yaml uses stdio**

```bash
grep -i "transport\|sse\|http" smithery.yaml
```

Expected: references to `stdio` only; no `sse`. If any `sse` appears, fix by replacing with `stdio` (or `http` if the intent was remote) and commit separately with message `fix: update smithery config to stdio-only transport`.

### Task 13: Push and merge PR 3

- [ ] **Step 1: Push branch**

```bash
git push -u origin feat/fastmcp-3-migration
```

- [ ] **Step 2: Open PR**

Title: `feat: FastMCP 3 migration + SSE transport removal`
Body:

```markdown
## Summary
- Bumps FastMCP to `>=3.2,<4`
- Removes `sse` from `--transport` CLI choices (breaking — users should migrate to `--transport http` for remote)
- Refactors `main()` to accept `argv` for testability
- Adds `tests/test_server_boot.py` with three regression tests
- Scrubs SSE references from README and MCP_CONFIG docs

## Breaking changes
- `--transport sse` is no longer accepted. Use `--transport http` (Streamable HTTP) instead.
- Consumers importing FastMCP APIs transitively may need updates per the [FastMCP 3 upgrade guide](https://gofastmcp.com/getting-started/upgrading/from-fastmcp-2).

## Test plan
- [x] `uv run pytest tests/` green on all four Python matrix rows
- [x] Manual stdio smoke test via `uv run csv-editor --transport stdio`
- [x] Manual http smoke test via `uv run csv-editor --transport http --port 8765`
- [ ] Claude Desktop smoke test — will verify post-merge on a release candidate build

Part of v2.0.0 preparation (spec: `specs/2026-04-19-fastmcp3-migration-design.md`).
```

- [ ] **Step 3: Wait for CI green**

All four matrix rows must be green.

- [ ] **Step 4: Manual Claude Desktop smoke test**

Before merging, install the PR branch locally into Claude Desktop:

1. Build: `uv build`
2. Point Claude Desktop's `claude_desktop_config.json` at the built wheel or a local `uv tool install` of the branch.
3. Restart Claude Desktop.
4. Invoke `health_check` — expect `status: "healthy"`.
5. Invoke `load_csv` on a small fixture file — expect success with shape/columns returned.

If either invocation fails, **do not merge**. Diagnose the FastMCP 3 API call, patch, push.

- [ ] **Step 5: Merge**

Squash merge via GitHub UI. Delete the branch.

---

## PR 4: v2.0.0 Release Cut

**Branch name:** `release/v2.0.0`
**Goal:** finalize CHANGELOG, bump version string in two places, merge, tag, push.

### Task 14: Create branch and bump version

**Files:**
- Modify: `pyproject.toml`
- Modify: `src/csv_editor/server.py` (`health_check` response)

- [ ] **Step 1: Create branch**

```bash
git checkout main
git pull --ff-only origin main
git checkout -b release/v2.0.0
```

- [ ] **Step 2: Bump version in pyproject.toml**

In `pyproject.toml`, find:
```toml
version = "1.0.1"
```
Change to:
```toml
version = "2.0.0"
```

- [ ] **Step 3: Bump version in health_check**

In `src/csv_editor/server.py`, find the `health_check` function (around line 28–54) and locate the `"version": "1.0.0"` line. Change to:
```python
            "version": "2.0.0",
```

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/ -v
```

Expected: all green (if any tests assert against the version string, they should already be using `csv_editor.__version__` or similar — if they assert the literal `"1.0.0"`, update them in this task).

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/csv_editor/server.py
git commit -m "chore: bump version to 2.0.0"
```

### Task 15: Write CHANGELOG entry

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add [2.0.0] section**

In `CHANGELOG.md`, insert after the header comment and before `## [1.0.1]`:

```markdown
## [2.0.0] - 2026-04-DD

### BREAKING CHANGES
- **Python floor raised to 3.11.** Users on 3.8, 3.9, or 3.10 must upgrade. Users who pinned `csv-editor>=1,<2` are unaffected.
- **`--transport sse` CLI option removed.** Use `--transport http` (Streamable HTTP) for remote deployments. This aligns with the MCP 2025-11-25 spec and FastMCP 3 guidance.
- **FastMCP dependency bumped to `>=3.2,<4`.** Any code importing FastMCP APIs transitively may require updates per the [FastMCP 3 upgrade guide](https://gofastmcp.com/getting-started/upgrading/from-fastmcp-2).

### Added
- GitHub Actions `test.yml` workflow: pytest matrix on Python 3.11–3.14.
- `tests/test_server_boot.py` regression tests for server import, tool registry, and CLI argument handling.
- Python 3.14 classifier and test coverage.
- Contributing guide: local virtualenv rebuild instructions.

### Changed
- Python floor: `>=3.10` → `>=3.11`.
- `fastmcp`: `>=2.11.3` → `>=3.2,<4`.
- `pydantic`: `>=2.10.4` → `>=2.13`.
- `pydantic-settings`: `>=2.10.1` → `>=2.13`.
- `pyarrow`: `>=17.0.0` → `>=23`.
- `httpx`: `>=0.27.0` → `>=0.28`.
- `aiofiles`: `>=24.1.0` → `>=25`.
- `tabulate`: `>=0.9.0` → `>=0.10`.
- `black`/`ruff`/`mypy` target-version: Python 3.8 → 3.11.
- Dockerfile base image pinned to `python:3.11-slim-bookworm`.
- `main()` signature: now accepts optional `argv` for testability.

### Removed
- `--transport sse` CLI option.
- Python 3.8, 3.9, 3.10 classifier entries.

### Unchanged
- `pandas>=2.2.3` and `numpy>=2.1.3` — upgrading to 3.0/2.4 is deferred to a follow-up release (Sub-project 1b) due to pandas' Copy-on-Write behavioral change requiring focused testing.
```

Replace `2026-04-DD` with the actual release date when you push the tag.

- [ ] **Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: add v2.0.0 CHANGELOG entry"
```

### Task 16: Push, open PR, and merge

- [ ] **Step 1: Push**

```bash
git push -u origin release/v2.0.0
```

- [ ] **Step 2: Open PR**

Title: `release: v2.0.0`
Body: paste the CHANGELOG `[2.0.0]` section.

- [ ] **Step 3: Wait for CI green**

All four matrix rows must be green.

- [ ] **Step 4: Merge**

Squash merge via GitHub UI.

### Task 17: Tag and verify release

**Files:** none (tagging and publishing)

- [ ] **Step 1: Update CHANGELOG date**

Checkout main, pull, and if the `2026-04-DD` placeholder is still in CHANGELOG.md, make a quick follow-up commit with the real date (e.g., `2026-04-22`):

```bash
git checkout main
git pull --ff-only origin main
# If CHANGELOG still has 2026-04-DD:
sed -i.bak 's/2026-04-DD/2026-04-22/' CHANGELOG.md && rm CHANGELOG.md.bak
git add CHANGELOG.md
git commit -m "docs: set v2.0.0 release date"
git push origin main
```

Skip this step if the date was already correct in PR 4.

- [ ] **Step 2: Create and push tag**

```bash
git tag -a v2.0.0 -m "Release v2.0.0: FastMCP 3 + Python 3.11 floor"
git push origin v2.0.0
```

- [ ] **Step 3: Wait for publish workflow**

`publish.yml` (existing) should trigger on the tag and publish to PyPI. Watch the Actions tab.

Expected: green publish run; `csv-editor 2.0.0` visible on PyPI.

- [ ] **Step 4: Verify pip install in a clean venv**

```bash
cd /tmp
python3.11 -m venv verify-venv
./verify-venv/bin/pip install csv-editor==2.0.0
./verify-venv/bin/csv-editor --help
```

Expected: `--help` output lists `--transport {stdio,http}` (no `sse`).

- [ ] **Step 5: Verify Smithery listing**

Open https://smithery.ai/server/@santoshray02/csv-editor in a browser. Confirm the version badge shows `2.0.0` (may take minutes to refresh; manually redeploy via Smithery dashboard if stale).

- [ ] **Step 6: Announce**

Optional but recommended: post a GitHub Release note (copy the CHANGELOG `[2.0.0]` section) at https://github.com/santoshray02/csv-editor/releases/new with tag `v2.0.0`.

---

## Post-release: Follow-up Issues to Open

After v2.0.0 ships, open these GitHub issues to track the rest of the roadmap:

- [ ] **Issue: Sub-project 0 — Migrate docs from Docusaurus to MkDocs-Material**
- [ ] **Issue: Sub-project 1b — pandas 3.0 + numpy 2.4 migration**
- [ ] **Issue: Sub-project 2 — Add DuckDB engine (default for files >100 MB) + Polars engine**
- [ ] **Issue: Sub-project 3 — Adopt MCP async Tasks for `load_csv`, `export_csv`, `profile_data`; Resource Links for large outputs**
- [ ] **Issue: Sub-project 4 — Remote HTTP + OAuth (CIMD) deployment mode for ChatGPT Connectors reach**
- [ ] **Issue: Sub-project 5 — Elicitation for ambiguous CSV dialect/encoding detection**

For each, paste the relevant sections from the April 2026 relevance audit as the issue body, link the design spec once written.

---

## Self-Review Checklist (meta)

Before starting implementation:

- [ ] Spec and plan locations match user preference (specs/, plans/ — not docs/ which is Docusaurus).
- [ ] Every task has exact file paths and complete code in every code step.
- [ ] No "TBD", "similar to Task N", or "implement appropriate error handling" placeholders.
- [ ] Types and function signatures referenced late in the plan (e.g., `main(argv)`) are defined in an earlier task.
- [ ] PR 1 → PR 2 → PR 3 → PR 4 ordering is enforced (each PR 2+ task assumes the previous PR merged).
- [ ] CI matrix in `test.yml` matches the Python floor at each point (3.10–3.14 in PR 1, 3.11–3.14 after PR 2).
- [ ] Manual Claude Desktop smoke test is called out explicitly as a gate before merging PR 3.
