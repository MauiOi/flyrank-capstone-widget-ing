import os
import httpx

GEO_PROVIDER_A_URL = os.getenv("GEO_PROVIDER_A_URL", "http://ip-api.com/json")
GEO_PROVIDER_B_URL = os.getenv("GEO_PROVIDER_B_URL", "https://ipapi.co")

# Toggle these to "true" in .env to simulate a provider being down,
# so the fallback proof is deterministic instead of depending on real uptime.
GEO_PROVIDER_A_DOWN = os.getenv("GEO_PROVIDER_A_DOWN", "false").lower() == "true"
GEO_PROVIDER_B_DOWN = os.getenv("GEO_PROVIDER_B_DOWN", "false").lower() == "true"


def _try_provider_a(ip: str):
    if GEO_PROVIDER_A_DOWN:
        raise RuntimeError("Provider A forced down (mock)")
    resp = httpx.get(f"{GEO_PROVIDER_A_URL}/{ip}", timeout=3)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "success":
        raise RuntimeError("Provider A returned failure status")
    return {"country": data.get("country"), "city": data.get("city")}


def _try_provider_b(ip: str):
    if GEO_PROVIDER_B_DOWN:
        raise RuntimeError("Provider B forced down (mock)")
    resp = httpx.get(f"{GEO_PROVIDER_B_URL}/{ip}/json/", timeout=3)
    resp.raise_for_status()
    data = resp.json()
    return {"country": data.get("country_name"), "city": data.get("city")}


def enrich_ip(ip: str):
    """Try provider A, then B, then give up gracefully. Never raises."""
    if not ip or ip in ("127.0.0.1", "localhost", "testclient"):
        return {"country": None, "city": None}

    for provider in (_try_provider_a, _try_provider_b):
        try:
            return provider(ip)
        except Exception:
            continue
    return {"country": None, "city": None}