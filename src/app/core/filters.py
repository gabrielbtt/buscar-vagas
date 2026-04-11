import unicodedata

from app.core.profile import JobProfile


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def matches_contract_type(title_or_type: str, profile: JobProfile) -> bool:
    if not profile.allowed_contract_terms:
        return True
    haystack = normalize_text(title_or_type)
    return any(term in haystack for term in profile.allowed_contract_terms)


def matches_location(location: str, work_model: str, profile: JobProfile) -> bool:
    if not profile.target_locations:
        return True
    normalized_location = normalize_text(location)
    normalized_work_model = normalize_text(work_model)
    if any(term in normalized_work_model for term in profile.allow_remote_terms):
        return True
    return any(city in normalized_location for city in profile.target_locations)
