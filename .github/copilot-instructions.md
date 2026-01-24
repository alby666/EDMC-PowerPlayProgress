# Copilot / AI Agent Instructions — EDMC-PowerPlayProgress

Goal: Get an AI agent productive quickly in this repository by explaining the big picture, common flows, and project-specific conventions.

## Big picture (one-paragraph)
This repository is an EDMC plugin (EDMarketConnector) that tracks and displays PowerPlay merits and activities from Elite Dangerous game journal events. The plugin runs inside the EDMC application; [src/load.py](src/load.py) exposes the required plugin hooks (`plugin_start3`, `plugin_stop`, `journal_entry`, `plugin_prefs`). The main implementation splits responsibility: [src/powerplayprogress.py](src/powerplayprogress.py) handles UI/state management, while [src/recentjournal.py](src/recentjournal.py), [src/sessionprogress.py](src/sessionprogress.py), and [src/systemprogress.py](src/systemprogress.py) provide journal event parsing and merit aggregation logic. The plugin displays merit progress bars, activity breakdowns, system-by-system tracking, and commodity delivery counts.

## Key files & responsibilities
- [src/load.py](src/load.py) — EDMC entry points and the main `journal_entry` dispatcher (pattern-match by lowercase event name).
- [src/powerplayprogress.py](src/powerplayprogress.py) — Main plugin class, UI setup (tkinter + EDMC notebook), config keys, and wiring to `RecentJournal` and session state.
- [src/recentjournal.py](src/recentjournal.py) — Journal event sequencing and classification helpers (e.g., `isBounty()`, `isScan()`, rare goods detection, MultiSellExplorationData handling).
- [src/sessionprogress.py](src/sessionprogress.py) — Session data model with nested `Activities` class that aggregates merits by activity type (bounties, scans, donations, etc.).
- [src/systemprogress.py](src/systemprogress.py) — Per-system merit tracking and delivery counts.
- [src/canvasprogressbar.py](src/canvasprogressbar.py), [src/multiHyperlinkLabel.py](src/multiHyperlinkLabel.py) — Custom tkinter UI widgets.
- [src/socials.py](src/socials.py), [src/rares.py](src/rares.py) — Rare commodity detection and social media links for PowerPlay factions.
- [src/consts.py](src/consts.py) — Plugin metadata (name, version, headings).
- [tests/](tests/) — Unit tests using `unittest` + `unittest.mock`/MagicMock; [tests/inprog/](tests/inprog/) contains integration tests for `load.py` with full mocking patterns.
- [.vscode/tasks.json](.vscode/tasks.json), [.vscode/RestartEDMarketConnector.ps1](.vscode/RestartEDMarketConnector.ps1) — Local deploy and restart utilities (Windows PowerShell).

## Runtime / integration notes (critical)
- **EDMC-provided modules at runtime** (NOT installed via pip): `myNotebook`, `EDMCLogging`, `config`, `theme`, `plug`. All must be mocked in tests; see [tests/inprog/test_load.py](tests/inprog/test_load.py) for the mocking pattern.
- **Plugin lifecycle**: controlled by exported functions in [src/load.py](src/load.py). Keep their signatures intact (`plugin_start3`, `plugin_stop`, `journal_entry`, `plugin_prefs`, `prefs_changed`).
- **UI framework**: tkinter with EDMC's `myNotebook` wrapper. Preferences stored via `config` keys with `options_view_*` prefix. Always use `tk.Variable` instances (e.g., `tk.BooleanVar`) for UI state.
- **Journal entry processing**: `journal_entry()` in [src/load.py](src/load.py) is the single dispatcher. Always match event names in lowercase. Keep parsing logic in `RecentJournal` for testability.
- **Rare commodities**: loaded from [src/rare-commodities.json](src/rare-commodities.json) and detected via `RecentJournal.rare_goods` set and `Rares` class.
- **Known issue**: Donation missions have duplicate entries in Elite Dangerous journal; plugin filters this but merits may be miscounted. See README and journal processing logic.
## How to run tests locally
- **Setup**: Ensure workspace root is on `PYTHONPATH` so `import src.*` works: `$env:PYTHONPATH = "<workspace>"`.
- **Run all tests**: `python -m unittest discover -v` from repository root.
- **Run specific test file**: `python -m unittest tests.test_recentjournal -v`.
- **With coverage**: `python -m coverage run -m unittest discover && python -m coverage report` or `report --include=src/`.
- **Mocking pattern**: Tests assume EDMC-provided modules are patched/mocked. See [tests/inprog/test_load.py](tests/inprog/test_load.py) for integration test patterns using MagicMock on EDMC modules.
- **Common pitfall**: If you import `src/load.py`, follow the mocking pattern in `tests/inprog/` to avoid runtime errors from missing EDMC modules.

## Deploy / debug workflow (Windows, documented tasks)
- **Copy files to plugin folder**: Use VS Code task `Copy files to target folder` or run `xcopy` from [.vscode/tasks.json](.vscode/tasks.json). Copies `src/` to `%APPDATA%\EDMarketConnector\plugins\EDMC-PowerPlayProgress` (excludes files listed in [.vscode/exclude.txt](.vscode/exclude.txt)).
- **Restart EDMC**: Use VS Code task `Restart EDMarketConnector` (calls [.vscode/RestartEDMarketConnector.ps1](.vscode/RestartEDMarketConnector.ps1)).
- **Combined deployment**: Use task `Deploy Files and Restart EDMC` (copies + restarts + opens EDMC log).
- **Debug session**: Use task `Start Debug Session` which runs `python -m debugpy --listen 5678 --wait-for-client` on the plugin. Then use VS Code's debugger to attach (port 5678) or use task `Attach to EDMarketConnector` after restart.
- **View logs**: Task `Open EDMC Log` opens `%APPDATA%\EDMarketConnector\logs\EDMarketConnector.log` in Notepad for quick debugging.

## Conventions & patterns to follow
- **Tests**: Prefer `unittest` + `MagicMock`/`patch` to isolate EDMC runtime dependencies.
- **Config keys**: Use `options_view_*` prefix and store UI state using `tk.Variable` instances like existing code (see [src/powerplayprogress.py](src/powerplayprogress.py#L48)).
- **Journal processing**: [src/load.py](src/load.py#L73) `journal_entry()` is the single entry point matching on lowercase event names. Add event handling here and keep parsing logic in `RecentJournal` for testability.
- **Activity tracking**: Merit aggregation happens in `SessionProgress.Activities` class with separate methods for each activity type (e.g., `add_bounty_merits()`, `add_ship_scan_merits()`). This pattern ensures clear audit trails and unit testing.
- **Logging**: Use `EDMCLogging.get_plugin_logger(f"{appname}.{PLUGIN_NAME}")` for consistent plugin logs.
- **Keep side-effects predictable**: When changing merit accounting, update both `SessionProgress` (aggregation) and `SystemProgress` (per-system tracking), then add corresponding unit tests that assert aggregated numbers.

## Adding features (concrete example)
Example: Add support for a new journal event `PowerplayX` that contributes merits by activity:
1. Add detection logic in [src/recentjournal.py](src/recentjournal.py) (e.g., add a new `isPowerPlayX()` helper and unit tests in `tests/`).
2. Add event handling in [src/load.py](src/load.py#L73) under `case 'powerplayx':` and call `ppp.current_session.activities.add_powerplayx_merits(...)`.
3. Update [src/sessionprogress.py](src/sessionprogress.py) `Activities` class with a new method to accumulate merits and corresponding unit tests.
4. Add per-system tracking in [src/systemprogress.py](src/systemprogress.py) if needed.
5. Add UI display in [src/powerplayprogress.py](src/powerplayprogress.py) and a new preference option if user-visible.
6. Add unit tests covering: recognition (RecentJournal), aggregation (SessionProgress), and the full `journal_entry` path (use [tests/inprog/test_load.py](tests/inprog/test_load.py) mocking style).

## Helpful search keywords for a code agent
- `journal_entry`, `PowerplayMerits`, `MultiSellExplorationData`, `RecentJournal`, `SessionProgress`, `Activities`, `canvasprogressbar`, `options_view_*`, `EDMCLogging`, `case '` (for event dispatch).

## Quick gotchas
- Many external EDMC modules are only available at runtime — tests and CI must mock them.
- Tests import as `from src import ...` so ensure project root is on `PYTHONPATH` when running tests or in CI.
- UI code uses `tk.Variable` objects (e.g., `tk.BooleanVar`) to store options — changing variable types requires updating UI and config logic.
- **Journal event dispatch** uses lowercase event name matching in `journal_entry()`. Elite Dangerous sends uppercase in journal; always normalize to lowercase before pattern matching.
- **Duplicate donation mission entries** are a known Elite Dangerous journal bug (see README). The plugin handles this by filtering duplicates, but be aware when testing donation mission logic.

---
If anything here is unclear or you'd like a different focus (more CI steps, examples of typical bug fixes, or explicit test templates), tell me what to expand and I will iterate.