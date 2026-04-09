from hashlib import sha256
from urllib.parse import urlsplit, urlunsplit


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def build_job_fingerprint(company: str, title: str, url: str) -> str:
    raw = f"{company.strip().lower()}|{title.strip().lower()}|{canonicalize_url(url)}"
    return sha256(raw.encode("utf-8")).hexdigest()
