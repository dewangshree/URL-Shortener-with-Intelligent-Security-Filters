import sys
import os
from fastapi.testclient import TestClient

# Allow importing main.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import app, analyze_url

client = TestClient(app)

# ------------------------
# BASIC PAGE TEST
# ------------------------

def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "URL Shortener" in response.text


# ------------------------
# SAFE URL TEST
# ------------------------

def test_shorten_safe_url():
    response = client.post(
        "/shorten",
        data={
            "url": "https://example.com",
            "expiry": "1h"
        }
    )
    assert response.status_code == 200
    assert "Short URL" in response.text


# ------------------------
# MALICIOUS URL TEST
# ------------------------

def test_block_malicious_url():
    response = client.post(
        "/shorten",
        data={
            "url": "http://192.168.1.1/login?verify=bank&password=123",
            "expiry": "1h"
        }
    )
    assert response.status_code == 200
    assert "unsafe" in response.text.lower()


# ------------------------
# INVALID SHORT CODE TEST
# ------------------------

def test_invalid_short_code():
    response = client.get("/thisdoesnotexist")
    assert response.status_code == 200
    assert "Not found" in response.text or response.json().get("error") == "Not found"


# ------------------------
# UNIT TEST (LOGIC ONLY)
# ------------------------

def test_analyze_url_logic():
    score, reasons = analyze_url("http://192.168.1.1/login")
    assert score >= 3
    assert len(reasons) > 0
