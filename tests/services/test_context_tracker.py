from pathlib import Path

import pytest

from app.services.context_tracker import ensure_project_context, record_progress


def test_ensure_project_context_seeds_markdown_sections(tmp_path):
    context_path = tmp_path / "project-context.md"

    ensure_project_context(context_path)

    assert context_path.exists()
    content = context_path.read_text(encoding="utf-8")
    assert "## Current Status\n" in content
    assert "## Completed Milestones\n" in content
    assert "## Next Steps\n" in content


def test_record_progress_updates_sections_and_appends_progress_entry(tmp_path):
    context_path = tmp_path / "project-context.md"
    ensure_project_context(context_path)

    record_progress(
        context_path,
        status="Task 2 in progress",
        completed_items=("Added durable context tracking", "Added file-backed settings store"),
        next_steps=("Wire startup bootstrap",),
        progress_entry="Persisted settings and refreshed project context.",
    )

    content = context_path.read_text(encoding="utf-8")

    assert "## Current Status\nTask 2 in progress\n" in content
    assert "## Completed Milestones\n- Added durable context tracking\n- Added file-backed settings store\n" in content
    assert "## Next Steps\n- Wire startup bootstrap\n" in content
    assert "## Progress Log\n- Persisted settings and refreshed project context.\n" in content


def test_record_progress_preserves_unknown_content_in_existing_context_file(tmp_path):
    context_path = tmp_path / "project-context.md"
    context_path.write_text(
        "# Project Context\n\n"
        "Intro text that should stay.\n\n"
        "## Current Status\n"
        "Paused\n\n"
        "## Completed Milestones\n"
        "- Task 1 complete\n\n"
        "## Custom Notes\n"
        "- Keep this section\n\n"
        "## Next Steps\n"
        "- Finish Task 2\n\n"
        "## Progress Log\n"
        "- Previous entry\n",
        encoding="utf-8",
    )

    record_progress(
        context_path,
        status="Task 2 complete",
        completed_items=("Task 2 hardened",),
        next_steps=("Start Task 3",),
        progress_entry="Task 2 review fixes applied.",
    )

    content = context_path.read_text(encoding="utf-8")

    assert "Intro text that should stay." in content
    assert "## Custom Notes\n- Keep this section\n" in content
    assert "## Current Status\nTask 2 complete\n" in content
    assert "## Progress Log\n- Previous entry\n- Task 2 review fixes applied.\n" in content


def test_record_progress_keeps_existing_context_when_write_fails(tmp_path, monkeypatch):
    context_path = tmp_path / "project-context.md"
    original_content = "# Project Context\n\n## Current Status\nPaused\n\n## Progress Log\n- Previous entry\n"
    context_path.write_text(original_content, encoding="utf-8")

    original_write_text = Path.write_text

    def failing_write_text(self, data, *args, **kwargs):
        original_write_text(self, "corrupted", *args, **kwargs)
        raise OSError("disk full")

    monkeypatch.setattr(Path, "write_text", failing_write_text)

    with pytest.raises(OSError):
        record_progress(
            context_path,
            status="Task 2 complete",
            completed_items=("Task 2 hardened",),
            next_steps=("Start Task 3",),
            progress_entry="Task 2 review fixes applied.",
        )

    assert context_path.read_text(encoding="utf-8") == original_content
