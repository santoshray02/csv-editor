# Sub-project 1: FastMCP 3 Migration + Dependency Bumps + Python Floor (v2.0.0)

**Status:** Draft
**Date:** 2026-04-19
**Author:** santoshray02
**Target release:** csv-editor v2.0.0

## Context

`csv-editor` is an MCP server (pandas-based, FastMCP 2.x, ~40 tools, 22 GitHub stars as of April 2026) published to PyPI and Smithery. The last substantive work on the stack landed in August 2025. Since then:

- The MCP spec has shipped revision [2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) (async Tasks, OAuth overhaul, elicitation).
- [FastMCP 3.x](https://gofastmcp.com/getting-started/upgrading/from-fastmcp-2) is the current major line (3.2.4 as of April 14, 2026) with breaking changes vs. 2.x.
- DuckDB and Polars have matured into production-ready engines and a MotherDuck-published MCP server is now a direct competitor for large-file analytics.
- Many Python libraries have dropped 3.8/3.9 support; pandas 3.0 requires 3.11+.

The full modernization roadmap breaks into six sub-projects:
0. **Docs migration: Docusaurus → MkDocs-Material** (parallel track, independent of 1–5)
1. **FastMCP 3 + dep bumps + Python floor cleanup** (this spec — prerequisite for 2–5)
2. DuckDB / Polars engine layer
3. Async Tasks + Resource Links
4. Remote HTTP + OAuth deployment mode
5. Elicitation for ambiguous CSV dialects

This spec covers **only Sub-project 1**. Sub-project 0 runs in parallel and does not block it.

## Goals

1. Restore the project to a current, maintainable baseline so Sub-projects 2–5 can be built on top.
2. Ship a clean **v2.0.0** with honest breaking-change signaling.
3. Establish automated test coverage so future changes don't regress silently.

## Non-goals

- Upgrading to pandas 3.0 (Copy-on-Write migration) — deferred to a later sub-project because the default-dtype and CoW changes will touch many of the 40 existing tools and deserve focused testing.
- Adding new tools, engines, or MCP protocol features.
- Re-platforming the Docusaurus docs site.
- Fixing the `.venv` drift on the maintainer's machine via a PR (documentation fix only).

## Decisions (locked)

| Decision | Choice | Rationale |
|---|---|---|
| Python floor | **3.11** (tested/recommended 3.14) | Enables later pandas 3.0; still covers mainstream user base. 3.14 as hard floor would exclude too many users. |
| Dependency scope | Medium: FastMCP 3 + non-breaking deps only | Defer pandas 3.0 / numpy 2.4 to focused sub-project. |
| Release version | **2.0.0** (direct, no pre-release) | Breaking changes (Python floor, FastMCP major, SSE removal) justify a major. User explicitly opted out of pre-release. |
| Remote transport | Drop `sse`; keep `stdio` + `http` (Streamable HTTP) | Per [FastMCP 3 docs](https://gofastmcp.com/clients/transports): SSE is "backward compatibility only, shouldn't be used in new projects." Major version is the right time to drop it. |
| CI | Add pytest matrix workflow (Python 3.11/3.12/3.13/3.14, Ubuntu) | No test CI exists today. Migration PRs would be blind without it. |
| Rollout | Phased PRs to `main`, each green in CI | Isolates risk; each PR is a revertable checkpoint. |

## Architecture / scope

### In-scope changes

- `pyproject.toml`:
  - `requires-python = ">=3.11"`
  - Classifiers: drop 3.8/3.9/3.10; keep 3.11–3.13; add 3.14.
  - `dependencies`:
    - `fastmcp>=3.2,<4` (from `>=2.11.3`)
    - `pyarrow>=23` (from `>=17.0.0`)
    - `pydantic>=2.13` (from `>=2.10.4`)
    - `pydantic-settings>=2.13` (from `>=2.10.1`)
    - `httpx>=0.28` (from `>=0.27.0`)
    - `aiofiles>=25` (from `>=24.1.0`)
    - `tabulate>=0.10` (from `>=0.9.0`)
    - pandas, numpy, openpyxl, python-dateutil, pytz: **unchanged**
  - `[tool.black] target-version`, `[tool.ruff] target-version`, `[tool.mypy] python_version`: bump to `py311` / `3.11`.
  - `version = "2.0.0"` (in the final release PR).
- `src/csv_editor/server.py`:
  - `argparse --transport` choices: `["stdio", "http"]` (drop `"sse"`).
  - `health_check` `version` field: `"2.0.0"`.
  - No other code changes — the `FastMCP("CSV Editor")` constructor and `mcp.run(transport=..., host=..., port=...)` calls are already compatible with FastMCP 3.
- `README.md`: update Python badge, remove 3.8/3.9 claims, scrub SSE references in config examples.
- `Dockerfile`: already `python:3.11-slim`; bump to a pinned bookworm tag for reproducibility.
- `smithery.yaml`: verify Python version if specified; update.
- `MCP_CONFIG.md`: scrub SSE references.
- `CHANGELOG.md`: add a `[2.0.0]` section with `### BREAKING CHANGES`, `### Added`, `### Changed`, `### Removed`.
- `.github/workflows/test.yml`: **new file** (see PR 1).

### Out-of-scope

- `pandas>=3.0` and `numpy>=2.4` (separate sub-project).
- Any of the five sub-projects 2–5.
- Docusaurus content changes beyond badge/README updates.
- Raising or lowering the `fail_under = 80` coverage gate.

### Breaking-change surface for users

1. Python < 3.11 no longer supported.
2. `--transport sse` is no longer a valid CLI argument.
3. `csv-editor` depends on `fastmcp>=3.2,<4`, which is a breaking change for any consumer importing FastMCP APIs transitively.

Users who pinned `csv-editor>=1,<2` are unaffected; 1.x remains on PyPI.

## PR sequence

Four PRs to `main`, each green in CI before the next.

### PR 1 — CI workflow baseline

**Single file:** `.github/workflows/test.yml`

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
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      - name: Sync deps
        run: uv sync --all-extras
      - name: Run tests
        run: uv run pytest tests/ -v
```

**Notes:**
- Matrix includes 3.10 so PR 1 can pass against current main (which declares `>=3.10`). PR 2 removes 3.10 from the matrix.
- No coverage gate on the initial workflow — the `pyproject.toml` `fail_under = 80` is advisory until we know the actual pass rate.
- Windows and macOS matrix axes are deferred to a follow-up issue; Ubuntu is sufficient for release gating.

**Acceptance:** runner exists, matrix runs, green or red is documented. If baseline is red, PR 1 still merges (the runner is the deliverable); a follow-up issue tracks the failures.

### PR 2 — Python floor + non-breaking dep bumps

**Changes** (per "In-scope changes" above, excluding the FastMCP and version bumps):

- `pyproject.toml`: `requires-python`, classifiers, non-breaking dep bumps, tool target-versions.
- `.github/workflows/test.yml`: drop `"3.10"` from matrix.
- `README.md`: Python badge, remove 3.8/3.9 claims.
- `Dockerfile`: change `FROM python:3.11-slim` to `FROM python:3.11-slim-bookworm` for a pinned base image.
- `smithery.yaml`: verify any Python version or runtime declarations; update to 3.11 if present.
- `[tool.black]`, `[tool.ruff]`, `[tool.mypy]` `target-version`/`python_version`: bump to `py311`/`3.11`.

**Acceptance:** all four CI matrix rows (3.11/3.12/3.13/3.14) green; no test behavior changes.

**Risk mitigations:**
- If pydantic 2.13 union-serialization change breaks a tool return type, pin `pydantic<2.13` as a hotfix and open a follow-up issue. This is not a release blocker for v2.0.0.
- If pyarrow 23 wheels are missing for 3.14 on any platform, document in CHANGELOG.

### PR 3 — FastMCP 3 migration + SSE removal

**Changes:**
- `pyproject.toml`: `fastmcp>=3.2,<4`.
- `src/csv_editor/server.py`:
  - `--transport` argparse: `choices=["stdio", "http"]`, help text updated.
  - No other code changes (verified against [FastMCP 3 upgrade guide](https://gofastmcp.com/getting-started/upgrading/from-fastmcp-2)).
- `README.md`, `MCP_CONFIG.md`: remove SSE mentions.
- `Dockerfile`: verify `CMD`/`ENTRYPOINT` doesn't reference SSE.
- **New file:** `tests/test_server_boot.py`:
  - `test_server_imports_clean` — `import csv_editor.server` without errors.
  - `test_tool_registry_populated` — after import, the `mcp` instance has ≥40 registered tools.
  - `test_cli_rejects_sse_transport` — invoking `main` with `--transport sse` raises `SystemExit` from argparse.

**Acceptance:**
- CI matrix green on 3.11/3.12/3.13/3.14.
- Manual smoke test: `uv run csv-editor --transport stdio` responds to an MCP `tools/list` request; `--transport http --port 8765` boots and serves at `/mcp`.
- Claude Desktop smoke test (manual): the server loads end-to-end; `health_check` returns `status: "healthy"` and `load_csv` successfully loads a small fixture file.

### PR 4 — v2.0.0 release cut

**Changes:**
- `pyproject.toml`: `version = "2.0.0"`.
- `CHANGELOG.md`: add `[2.0.0] - YYYY-MM-DD` section:
  - `### BREAKING CHANGES`: Python floor 3.11; SSE transport removed; FastMCP 3 required.
  - `### Added`: CI test workflow; `tests/test_server_boot.py`.
  - `### Changed`: dependency bumps (list each with from → to).
  - `### Removed`: `--transport sse` CLI option.
- `src/csv_editor/server.py` `health_check`: `"version": "2.0.0"`.
- Git tag `v2.0.0` pushed after merge; existing `publish.yml` handles PyPI publish.

**Acceptance:**
- Tag pushed; PyPI publish workflow green.
- `pip install csv-editor==2.0.0` on a fresh Python 3.11 venv succeeds.
- Smithery listing reflects 2.0.0 (manual refresh if needed).

## Testing strategy

| PR | Tests |
|---|---|
| PR 1 | No new tests. Runner ships; baseline pass rate documented. |
| PR 2 | Existing tests must pass on all four Python versions. |
| PR 3 | Add `tests/test_server_boot.py` (three tests listed above). Manual smoke tests against stdio, http, and Claude Desktop. |
| PR 4 | No new tests. Full suite green on the release commit. |

**Coverage:** the `pyproject.toml` `fail_under = 80` gate is not enforced by PR 1's workflow (no `--cov` flag). Raising or lowering it is a follow-up issue.

**Local dev:** maintainer's `.venv` currently points at a removed conda interpreter. Fix instructions are added to `CONTRIBUTING.md` in PR 2:

```bash
rm -rf .venv
uv sync --all-extras
```

## Risks & rollback

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| pydantic 2.13 union-serialization regression | Low | Medium | CI catches in PR 2. Hotfix: pin `pydantic<2.13`. Not a v2.0.0 blocker. |
| pyarrow 23 wheel missing on 3.14 for some platform | Low | Low | Document in CHANGELOG; user can fall back to 3.13. |
| FastMCP 3 `run()` signature drift from our call site | Very Low | Medium | Verified against official docs; smoke tests catch any runtime break. |
| User on `--transport sse` hits v2.0.0 and breaks | Medium | Low | Major version signals it; CHANGELOG documents it. `csv-editor>=1,<2` users are unaffected. |
| Existing tests are red on current main | Unknown | Blocks PR 1 acceptance criteria only if treated as a block | PR 1 ships the runner regardless; broken tests get a follow-up issue. |
| Smithery/Glama listings out of sync post-release | Low | Cosmetic | Manually refresh after 2.0.0 publish. |

**Rollback per PR:**
- **PR 1:** revert the workflow file. Zero blast radius.
- **PR 2:** revert the pyproject commit. Users on current main are unaffected (no tag cut yet).
- **PR 3:** revert; independent of PR 2 because the FastMCP pin doesn't require newer pyarrow/pydantic.
- **PR 4:** PyPI is append-only. Critical bug → publish 2.0.1. Security-critical only → yank 2.0.0. `csv-editor>=1,<2` users unaffected either way.

## Decision gates

- **After PR 1:** baseline test pass count is known and documented in an issue.
- **After PR 2:** CI matrix confirms new dep set works on 3.11/3.12/3.13/3.14.
- **After PR 3:** manual Claude Desktop smoke test confirms end-to-end functionality (highest-value manual check).
- **After PR 4:** `pip install csv-editor==2.0.0` on a clean 3.11 venv succeeds; Smithery listing refreshed.

## Open questions

None at spec sign-off — all structural decisions locked via clarifying questions on 2026-04-19.

## References

- [MCP Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25)
- [FastMCP Upgrade Guide (2 → 3)](https://gofastmcp.com/getting-started/upgrading/from-fastmcp-2)
- [FastMCP Running Your Server](https://gofastmcp.com/deployment/running-server)
- [FastMCP Client Transports (SSE status)](https://gofastmcp.com/clients/transports)
- [FastMCP v3.2.4 release notes](https://github.com/PrefectHQ/fastmcp/releases/tag/v3.2.4)
- [pandas 3.0 What's New](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html) (for Sub-project 1b)
- [PyArrow 23.0 release](https://arrow.apache.org/blog/2026/01/18/23.0.0-release/)
