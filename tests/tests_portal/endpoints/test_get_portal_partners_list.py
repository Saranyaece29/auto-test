# endpoints/test_get_portal_partners_list.py
"""
Smoke test for GET /v1/portal_partners/list
- Asserts HTTP 200
- Saves the JSON response for inspection
"""

import json
from pathlib import Path
from typing import Dict, Any

import pytest
import requests

@pytest.mark.parametrize(
    "query",
    [
        {},  # bare call
        {"page": 1, "per_page": 25},
        {"page": 1, "per_page": 50, "sorted_order": "asc"},
        {"page": 1, "per_page": 50, "sorted_order": "desc"},
    ],
)
def test_get_portal_partners_list(
    api: requests.Session,
    base_url: str,
    reports_dir: Path,
    query: Dict[str, Any],
):
    url = f"{base_url}/v1/portal_partners/list"

    # strip None values
    params = {k: v for k, v in (query or {}).items() if v is not None}

    resp = api.get(url, params=params, timeout=60)
    assert resp.status_code == 200, f"Unexpected status {resp.status_code}: {resp.text[:500]}"

    payload = resp.json()

    # Save response to a file for later use
    label = "_".join(f"{k}-{v}" for k, v in params.items()) if params else "default"
    out_file = reports_dir / f"portal_partners_list_{label}.json"
    out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    # Light sanity checks (won't be brittle)
    assert isinstance(payload, (list, dict)), f"Unexpected payload type: {type(payload)}"
    if isinstance(payload, list) and payload:
        assert isinstance(payload[0], dict)
        assert any(k in payload[0] for k in ("id", "partner_name", "name"))
