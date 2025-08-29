import os
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv

import os, sys
os.environ.setdefault("PYTHONUTF8", "1")
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Load env vars from .env.test if present
load_dotenv(dotenv_path=os.getenv("DOTENV_PATH", ".env.test"))

def _resolve_base_url() -> str:
    """
    Determine the API base URL from env.
    Tries API_BASE_URL then LOCAL_HOST_URL for backward-compatibility.
    """
    base = os.getenv("API_BASE_URL") or os.getenv("LOCAL_HOST_URL")
    if not base:
        raise RuntimeError(
            "Set API_BASE_URL (preferred) or LOCAL_HOST_URL in your environment/.env.test"
        )
    return base.rstrip("/")

def _get_access_token(base_url: str) -> str:
    """
    Log in against the API and return a bearer token.
    Expects username/password in env: PORTAL_USERNAME / PORTAL_PASSWORD.
    Assumes login endpoint: /v1/authorization/login
    """
    username = os.getenv("PORTAL_USERNAME")
    password = os.getenv("PORTAL_PASSWORD")
    if not username or not password:
        raise RuntimeError("PORTAL_USERNAME and PORTAL_PASSWORD must be set in env/.env.test")

    login_url = f"{base_url}/v1/authorization/login"
    resp = requests.post(
        login_url,
        data={"username": username, "password": password},
        timeout=30,
        verify=False,  # set to True if your certs are valid
    )
    resp.raise_for_status()
    payload = resp.json()

    # Be flexible about token key
    if isinstance(payload, str):
        token = payload
    elif isinstance(payload, dict):
        token = (
            payload.get("access_token")
            or payload.get("token")
            or payload.get("id_token")
            or payload.get("jwt")
        )
    else:
        token = None

    if not token:
        raise ValueError(f"Could not find access token in login response: {payload!r}")
    return token

# -------------------- Pytest fixtures --------------------
@pytest.fixture(scope="session")
def base_url() -> str:
    return _resolve_base_url()

@pytest.fixture(scope="session")
def access_token(base_url: str) -> str:
    return _get_access_token(base_url)

@pytest.fixture(scope="session")
def api(base_url: str, access_token: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {access_token}"})
    # s.verify = True  # enable for trusted TLS
    return s

@pytest.fixture(scope="session")
def reports_dir() -> Path:
    d = Path(__file__).resolve().parent / "reports"
    d.mkdir(parents=True, exist_ok=True)
    return d
