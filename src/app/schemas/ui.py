from pydantic import BaseModel


class SettingsResponse(BaseModel):
    search_interval_minutes: int
    immediate_alert_min_score: float
    target_locations: list[str]
    company_page_source_enabled: bool = False
    company_page_source_url: str = ""
