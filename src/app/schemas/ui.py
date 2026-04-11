from pydantic import BaseModel


class ProfileSettings(BaseModel):
    id: str
    name: str
    active: bool
    required_keywords: list[str]
    preferred_keywords: list[str]
    blocked_keywords: list[str]
    allowed_contract_terms: list[str]
    target_locations: list[str]


class SettingsResponse(BaseModel):
    search_interval_minutes: int
    immediate_alert_min_score: float
    profiles: list[ProfileSettings] = []
    company_page_source_enabled: bool = False
    company_page_source_url: str = ""
    browser_page_source_enabled: bool = False
    browser_page_source_url: str = ""
