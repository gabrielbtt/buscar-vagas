import httpx


def build_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=30.0, follow_redirects=True)
