import os
import httpx

GEO_PROVIDER_A_URL = os.getenv("GEO_PROVIDER_A_URL", "http://ip-api.com/json")

GEO_PROVIDER_A_DOWN = os.getenv("GEO_PROVIDER_A_DOWN", "false").lower() == "true"
GEO_PROVIDER_B_DOWN = os.getenv("GEO_PROVIDER_B_DOWN", "false").lower() == "true"

REQUEST_HEADERS = {"User-Agent": "flyrank-capstone-widget-platform/1.0 (student project)"}


def _try_provider_a(ip: str):
    """Live provider — ip-api.com."""
    if GEO_PROVIDER_A_DOWN:
        raise RuntimeError("Provider A forced down (mock)")
    resp = httpx.get(f"{GEO_PROVIDER_A_URL}/{ip}", headers=REQUEST_HEADERS, timeout=3)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "success":
        raise RuntimeError("Provider A returned failure status")
    return {"country": data.get("country"), "city": data.get("city")}


def _try_provider_b(ip: str):
    """
    Deterministic mock fallback provider. ipapi.co (the real second
    provider) sits behind a Cloudflare bot challenge that blocks
    automated requests entirely — confirmed during dev testing. Mocked
    per the capstone brief's guidance to keep the fallback proof
    deterministic rather than dependent on a live third-party's uptime.
    """
    if GEO_PROVIDER_B_DOWN:
        raise RuntimeError("Provider B forced down (mock)")
    return {"country": "Canada", "city": "Toronto"}


def enrich_ip(ip: str):
    if not ip or ip in ("127.0.0.1", "localhost", "testclient"):
        return {"country": None, "city": None}

    for provider in (_try_provider_a, _try_provider_b):
        try:
            return provider(ip)
        except Exception:
            continue
    return {"country": None, "city": None}