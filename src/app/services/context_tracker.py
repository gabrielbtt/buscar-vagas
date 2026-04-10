from pathlib import Path
import re


SECTION_ORDER = (
    "Current Status",
    "Completed Milestones",
    "Next Steps",
    "Progress Log",
)


def ensure_project_context(path: str | Path) -> Path:
    context_path = Path(path)
    context_path.parent.mkdir(parents=True, exist_ok=True)
    if not context_path.exists():
        context_path.write_text(_render_context(), encoding="utf-8")
    return context_path


def record_progress(
    path: str | Path,
    *,
    status: str,
    completed_items: tuple[str, ...],
    next_steps: tuple[str, ...],
    progress_entry: str,
) -> Path:
    context_path = ensure_project_context(path)
    content = context_path.read_text(encoding="utf-8")
    progress_items = _to_bullets(_read_section(content, "Progress Log"))
    progress_items.append(progress_entry)
    updated_content = content
    updated_content = _replace_section(updated_content, "Current Status", status)
    updated_content = _replace_section(updated_content, "Completed Milestones", _render_list(completed_items))
    updated_content = _replace_section(updated_content, "Next Steps", _render_list(next_steps))
    updated_content = _replace_section(updated_content, "Progress Log", _render_list(tuple(progress_items)))
    _write_text_atomically(context_path, updated_content)
    return context_path


def _read_section(content: str, title: str) -> str:
    match = _section_pattern(title).search(content)
    return match.group("body") if match else ""


def _render_context(
    *,
    status: str = "",
    completed_items: tuple[str, ...] = (),
    next_steps: tuple[str, ...] = (),
    progress_items: tuple[str, ...] = (),
) -> str:
    parts = [
        "# Project Context\n",
        _render_section("Current Status", status),
        _render_section("Completed Milestones", _render_list(completed_items)),
        _render_section("Next Steps", _render_list(next_steps)),
        _render_section("Progress Log", _render_list(progress_items)),
    ]
    return "\n".join(parts)


def _render_section(title: str, body: str) -> str:
    if body:
        return f"## {title}\n{body}\n"
    return f"## {title}\n"


def _render_list(items: tuple[str, ...]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _to_bullets(section_body: str) -> list[str]:
    items = []
    for line in section_body.splitlines():
        if line.startswith("- "):
            items.append(line[2:])
    return items


def _replace_section(content: str, title: str, body: str) -> str:
    pattern = _section_pattern(title)
    replacement = f"## {title}\n{body}\n\n"
    if pattern.search(content):
        return pattern.sub(replacement, content, count=1)
    return f"{content.rstrip()}\n\n{replacement}"


def _section_pattern(title: str) -> re.Pattern[str]:
    return re.compile(
        rf"^## {re.escape(title)}\n(?P<body>.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )


def _write_text_atomically(path: Path, content: str) -> None:
    temp_path = path.with_name(f".{path.name}.tmp")
    try:
        temp_path.write_text(content, encoding="utf-8")
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()
