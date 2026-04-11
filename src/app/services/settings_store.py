import json
from pathlib import Path


DEFAULT_FILE_SETTINGS = {
    "search_interval_minutes": 180,
    "immediate_alert_min_score": 0.9,
    "target_locations": ["belo horizonte", "contagem", "betim", "nova lima"],
    "required_keywords": ["engenharia eletrica", "projetos eletricos", "automacao"],
    "preferred_keywords": ["clp", "ihm", "automacao industrial", "painel eletrico", "comandos eletricos"],
    "blocked_keywords": ["n8n", "marketing", "vendas", "telemarketing"],
    "allowed_contract_terms": ["estagio", "estagiario", "internship", "trainee"],
    "company_page_source_enabled": False,
    "company_page_source_url": "",
    "browser_page_source_enabled": False,
    "browser_page_source_url": "",
    "global_sources": [],
    "preferred_execution_window": "comercial",
}


class FileSettingsStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> dict:
        stored_settings = _normalize_payload(self._load_existing())
        merged_settings = dict(DEFAULT_FILE_SETTINGS)
        merged_settings.update(stored_settings)
        return merged_settings

    def save(self, settings: dict) -> Path:
        payload = dict(DEFAULT_FILE_SETTINGS)
        payload.update(_normalize_payload(self._load_existing()))
        payload.update(_normalize_payload(settings))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        _write_text_atomically(self.path, json.dumps(payload, indent=2) + "\n")
        return self.path

    def _load_existing(self) -> dict:
        if not self.path.exists():
            return {}

        try:
            stored_settings = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

        return stored_settings if isinstance(stored_settings, dict) else {}


def _write_text_atomically(path: Path, content: str) -> None:
    temp_path = path.with_name(f".{path.name}.tmp")
    try:
        temp_path.write_text(content, encoding="utf-8")
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _normalize_string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []

    items = []
    seen = set()
    for value in values:
        if not isinstance(value, str):
            continue
        item = value.strip()
        if not item:
            continue
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        items.append(item)
    return items


def _normalize_payload(payload: dict) -> dict:
    normalized = dict(payload)
    for key in (
        "global_sources",
        "target_locations",
        "required_keywords",
        "preferred_keywords",
        "blocked_keywords",
        "allowed_contract_terms",
    ):
        if key in normalized:
            normalized[key] = _normalize_string_list(normalized[key])
    return normalized
