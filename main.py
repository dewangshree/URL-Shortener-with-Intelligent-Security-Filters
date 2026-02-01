from dotenv import load_dotenv
load_dotenv()

import os
import sqlite3
import random
import string
import re
import tldextract
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from openai import OpenAI

# ---------------- APP ----------------
app = FastAPI()
templates = Jinja2Templates(directory="templates")

DB = "urls.db"

# ---------------- DB INIT ----------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original TEXT,
            short TEXT UNIQUE,
            expires_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- UTILS ----------------
def generate_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


def analyze_url(url: str):
    score = 0
    reasons = []

    if len(url) > 120:
        score += 1
        reasons.append("The URL is unusually long")

    if len(re.findall(r"[?=&%$@]", url)) > 5:
        score += 1
        reasons.append("Too many special characters")

    suspicious_words = ["login", "verify", "bank", "free", "bonus", "crypto", "password"]
    for word in suspicious_words:
        if word in url.lower():
            score += 1
            reasons.append(f"Contains suspicious word: {word}")

    ext = tldextract.extract(url)
    if ext.subdomain.count('.') >= 2:
        score += 1
        reasons.append("Too many subdomains")

    if re.match(r"https?://\d+\.\d+\.\d+\.\d+", url):
        score += 2
        reasons.append("Uses IP address instead of domain")

    return score, reasons


def explain_with_llm(url: str, reasons: list[str]) -> str:
    """
    ⚡ FAST, SAFE, NON-BLOCKING AI
    - Hard timeout
    - Graceful fallback
    - Never crashes server
    """
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("AI key not configured")

        client = OpenAI(timeout=1.0)  # ⏱ hard timeout

        prompt = f"""
URL: {url}
Reasons: {', '.join(reasons)}
Explain briefly why this URL may be unsafe.
"""

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        return response.output_text.strip()

    except Exception:
        return (
            "This link was blocked due to multiple suspicious patterns "
            "commonly used in phishing or scam URLs."
        )

# ---------------- ROUTES ----------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html"
    )


@app.post("/shorten", response_class=HTMLResponse)
def shorten(
    request: Request,
    url: str = Form(...),
    expiry: str = Form(...)
):
    score, reasons = analyze_url(url)

    # 🚨 BLOCK UNSAFE URLS INSTANTLY
    if score >= 3:
        explanation = explain_with_llm(url, reasons)
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "error": "⚠️ This URL looks unsafe",
                "llm_explanation": explanation
            }
        )

    # -------- EXPIRY (timezone-aware) --------
    now = datetime.now(timezone.utc)

    if expiry == "1h":
        expires_at = now + timedelta(hours=1)
    elif expiry == "1d":
        expires_at = now + timedelta(days=1)
    else:
        expires_at = now + timedelta(days=7)

    code = generate_code()

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO urls (original, short, expires_at) VALUES (?, ?, ?)",
        (url, code, expires_at.isoformat())
    )
    conn.commit()
    conn.close()

    short_url = f"http://127.0.0.1:8000/{code}"

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "short_url": short_url,
            "expiry_info": expires_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    )


@app.get("/{code}")
def redirect(code: str):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT original, expires_at FROM urls WHERE short = ?", (code,))
    row = c.fetchone()
    conn.close()

    if not row:
        return {"error": "Not found"}

    original, expires_at = row
    expires_at = datetime.fromisoformat(expires_at)

    if datetime.now(timezone.utc) > expires_at:
        return {"error": "This link has expired"}

    return RedirectResponse(original)
