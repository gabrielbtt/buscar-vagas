# Project Context

## Current Status
- MVP job finder is operational in worktree `C:\Users\gasb0\OneDrive\Documents\Codigos\Vibe Coding\busca_vagas\.worktrees\job-finder-ops-ui` on branch `feature/job-finder-ops-ui`.
- Scheduled searches, persisted operational settings, dashboard controls, email notification flow, source fallback, and admin visibility are implemented and revalidated.
- Full test suite passes and the branch is ready for the next integration step.
- Resume from this worktree: `C:\Users\gasb0\OneDrive\Documents\Codigos\Vibe Coding\busca_vagas\.worktrees\job-finder-ops-ui` on branch `feature/job-finder-ops-ui`.

## Completed Milestones
- Task 1 complete: profile defaults updated and verified.
- Task 2 complete: durable project context tracking and persisted UI settings storage hardened and revalidated.
- Task 3 complete: end-to-end collection, matching, persistence, and notification flow wired and covered by service tests.
- Task 4 complete: scheduled automatic execution is configurable from persisted settings and documented.
- Task 5 complete: initial dashboard UI with editable operational controls is available and covered by UI tests.
- Task 6 complete: HTTP connectors and browser fallback path are covered by source tests.
- Task 7 complete: admin endpoint now exposes notification state for recent jobs.
- Task 8 complete: full suite verification passed and final project context was reconciled.

## Next Steps
- Create a git commit when requested.
- Prepare merge/PR flow when requested.
- Tune runtime source settings and SMTP credentials for the target deployment environment.

## Progress Log
- 2026-04-09 23:58 - Baseline worktree verification passed with `pytest` (`14 passed`).
- 2026-04-09 23:58 - Task 1 verification passed with `pytest tests/core/test_profile.py tests/core/test_filters.py tests/core/test_scoring.py -v` (`8 passed`).
- 2026-04-09 23:58 - Task 2 service tests passed with `pytest tests/services/test_context_tracker.py tests/services/test_settings_store.py -v` (`4 passed`).
- 2026-04-09 23:58 - Task 2 code review flagged robustness gaps: unknown persisted keys can break `get_settings()`, and `record_progress()` rewrites the context file destructively.
- 2026-04-10 17:41 - Task 2 resumed from paused worktree state for robustness hardening before Task 3.
- 2026-04-10 17:41 - Added TDD coverage for unknown settings keys, malformed JSON, invalid persisted values, non-destructive context updates, and atomic write behavior.
- 2026-04-10 17:41 - Revalidated Task 2 with `pytest tests/services/test_context_tracker.py tests/services/test_settings_store.py tests/core/test_profile.py -v` (`17 passed`) and follow-up review; Task 3 is now unblocked.
- 2026-04-10 17:41 - Added Task 3 TDD coverage for orchestration results, immediate alerts, retry of persisted unnotified jobs, and collector pass-through behavior.
- 2026-04-10 17:41 - Revalidated Task 3 with `pytest tests/services/test_run_jobs.py tests/services/test_collector.py tests/services/test_notifier.py -v` (`6 passed`) and follow-up review; Task 4 is now unblocked.
- 2026-04-10 18:36 - Added Task 4 TDD coverage for scheduler interval registration, runtime collector construction from settings, startup scheduler wiring, persisted-settings precedence over `.env`, runtime refresh, and interval resync.
- 2026-04-10 18:36 - Revalidated Task 4 with `pytest tests/services/test_settings_store.py tests/services/test_collector.py tests/services/test_scheduler.py tests/test_health.py -v` (`21 passed`) and follow-up review; Task 5 is now unblocked.
- 2026-04-10 18:22 - Added Task 5 TDD coverage for dashboard HTML, manual run, editable settings persistence, visible source settings, and startup UI wiring.
- 2026-04-10 18:22 - Revalidated Task 5 with `pytest tests/test_ui.py tests/test_health.py -v` (`6 passed`) and follow-up review; Task 6 is now unblocked.
- 2026-04-10 18:37 - Added Task 6 TDD coverage for explicit browser fetch requests, browser page parsing, browser fallback on empty HTTP parses and HTTP failures, and collector wiring for mixed HTTP/browser-backed sources.
- 2026-04-10 18:37 - Revalidated Task 6 with `pytest tests/sources/test_connectors.py tests/sources/test_company_pages.py tests/sources/test_browser_pages.py -v` (`10 passed`) and follow-up review; Task 7 is now unblocked.
- 2026-04-10 18:44 - Added Task 7 TDD coverage for `/admin/jobs/recent` with persisted jobs exposing `notified` and `source_name`.
- 2026-04-10 18:44 - Revalidated Task 7 with `pytest tests/test_health.py -v` (`3 passed`) and follow-up review; Task 8 is now unblocked.
- 2026-04-10 18:46 - Revalidated the full project with `pytest -v` (`54 passed`) after reconciling matcher/settings expectations with the final MVP behavior.
