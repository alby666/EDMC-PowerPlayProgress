# Copilot / AI Agent Instructions — EDMC-PowerPlayProgress

Goal: Get an AI agent productive quickly in this repository by explaining the big picture, common flows, and project-specific conventions.

## Big picture (one-paragraph)
- This repository is an EDMC plugin (EDMarketConnector) that tracks and displays PowerPlay merits/activities. The runtime is inside EDMC; `src/load.py` exposes the plugin hooks (plugin_start3, plugin_stop, journal_entry, plugin_prefs, plugin_app). The main implementation is `src/powerplayprogress.py` (UI + state) and `src/recentjournal.py` / `src/sessionprogress.py` / `src/systemprogress.py` (core parsing and state).

## Key files & responsibilities
- `src/load.py` — EDMC entry points and the main `journal_entry` dispatcher (pattern-match by event name).
- `src/powerplayprogress.py` — Main plugin class, UI setup, config keys, and wiring to `RecentJournal` and session state.
- `src/recentjournal.py` — Journal event sequencing and classification helpers (e.g., isBounty, isScan, MultiSellExplorationData handling).
- `src/sessionprogress.py`, `src/systemprogress.py` — Data models & aggregation logic.
- `src/canvasprogressbar.py`, `src/multiHyperlinkLabel.py` — UI widgets.
- `tests/` & `tests/inprog/` — Unit tests (use `unittest` + `unittest.mock`/MagicMock frequently).
- `.vscode/RestartEDMarketConnector.ps1` and VS Code tasks in workspace — local deploy and restart utilities.

## Runtime / integration notes (critical)
- EDMC provides objects and modules at runtime (examples: `myNotebook`, `EDMCLogging`, `config`, `theme`, `plug`). These are NOT installed via pip and are mocked in tests.
- Plugin lifecycle is controlled by the exported functions in `src/load.py`. Keep their signatures intact when changing behavior.
- UI uses `tkinter` with EDMC's notebook wrapper (`myNotebook`), and preferences are stored via `config` keys (prefixes like `options_view_*`). When adding a preference, add a corresponding config key and load/save in `PowerPlayProgress`.

## How to run tests locally
- From repository root: ensure the workspace root is on `PYTHONPATH` so `import src.*` works.
- Run: `python -m unittest discover -v` or a specific file: `python -m unittest tests.test_recentjournal`.
- Tests assume EDMC-provided modules are patched/mocked (see `tests/inprog/test_load.py`). When adding tests that import `src/load.py`, follow the existing mocking pattern.

## Deploy / debug workflow (Windows, documented tasks)
- Build / copy plugin files to EDMC plugin folder: use the VS Code task `Copy files to target folder` or run the `xcopy` command from `.vscode/tasks.json` (it copies `src/` into `%APPDATA%\EDMarketConnector\plugins\EDMC-PowerPlayProgress`).
- Restart EDMC: use the `Restart EDMarketConnector` task (calls `.vscode/RestartEDMarketConnector.ps1` and updates the local `launch.json`).
- Combined task: `Deploy Files and Restart EDMC` runs copy + restart + opens log.
- Debugging: `Start Debug Session` runs `python -m debugpy --listen 5678 --wait-for-client <EDMC plugin load.py>` in the plugin folder—attach VS Code to that session or use `Attach to EDMarketConnector` after restart (the script updates `launch.json` with PID).

## Conventions & patterns to follow
- Tests: prefer `unittest` + `MagicMock`/`patch` to isolate EDMC runtime dependencies.
- Config keys: use the `options_view_*` prefix and store UI state using `tk.Variable` instances like existing code (see `PowerPlayProgress.__init__`).
- Journal processing: `load.py::journal_entry` is the single entry point that matches on lowercase event names. Add event handling here and keep parsing logic in `RecentJournal` (so logic is easy to test).
- Logging: use `EDMCLogging.get_plugin_logger` with `f"{appname}.{PLUGIN_NAME}"` for consistent logs.
- Keep side-effects predictable: when changing merit accounting, ensure you update `SessionProgress` and write unit tests that assert aggregated numbers and classification of activities.

## Adding features (concrete example)
Example: Add support for a new journal event `PowerplayX` that contributes merits by activity:
1. Add detection logic in `src/recentjournal.py` (e.g., add a new `isPowerPlayX` helper and unit tests in `tests/`).
2. Add event handling in `src/load.py::journal_entry` under `case 'powerplayx':` and call `ppp.current_session.activities.add_powerplayx_merits(...)` or equivalent.
3. Update `src/sessionprogress.py` / `activities` with a new method to accumulate merits and corresponding unit tests.
4. Add a UI display if needed in `src/powerplayprogress.py` and a new preference option if it is user-visible.
5. Add unit tests covering recognition (RecentJournal), aggregation (SessionProgress), and the `journal_entry` path (use `tests/inprog/test_load.py` style mocks).

## Helpful search keywords for a code agent
- `journal_entry`, `PowerplayMerits`, `MultiSellExplorationData`, `RecentJournal`, `SessionProgress`, `canvasprogressbar`, `options_view_*`, `EDMCLogging`.

## Quick gotchas
- Many external EDMC modules are only available at runtime — tests and CI must mock them.
- Tests import as `from src import ...` so ensure project root is on `PYTHONPATH` when running tests or in CI.
- UI code uses `tk.Variable` objects (e.g., `tk.BooleanVar`) to store options — changing variable types requires updating UI and config logic.

---
If anything here is unclear or you'd like a different focus (more CI steps, examples of typical bug fixes, or explicit test templates), tell me what to expand and I will iterate.