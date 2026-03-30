from contextlib import asynccontextmanager, contextmanager
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from time import time
import json
import logging
import os
import random
import re
import sqlite3
import string

import tldextract
from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from openai import OpenAI

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DB_PATH     = os.getenv("DB_PATH", "urls.db")
RATE_LIMIT  = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
CODE_LENGTH = 6

_rate_store: dict[str, list[float]] = defaultdict(list)

def is_rate_limited(ip: str) -> bool:
    now = time()
    _rate_store[ip] = [t for t in _rate_store[ip] if now - t < 60.0]
    if len(_rate_store[ip]) >= RATE_LIMIT:
        return True
    _rate_store[ip].append(now)
    return False

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db() -> None:
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS urls (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                original       TEXT    NOT NULL,
                short          TEXT    UNIQUE NOT NULL,
                alias          TEXT,
                created_at     TEXT    NOT NULL,
                expires_at     TEXT    NOT NULL,
                click_count    INTEGER NOT NULL DEFAULT 0,
                threat_score   INTEGER NOT NULL DEFAULT 0,
                threat_reasons TEXT    NOT NULL DEFAULT '[]',
                is_suspected   INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS global_stats (
                key   TEXT PRIMARY KEY,
                value INTEGER NOT NULL DEFAULT 0
            );

            INSERT OR IGNORE INTO global_stats (key, value) VALUES
                ('phishing_blocked', 0),
                ('suspected_count',  0);
        """)
        for col, typ, default in [
            ("threat_score",   "INTEGER", "0"),
            ("threat_reasons", "TEXT",    "'[]'"),
            ("is_suspected",   "INTEGER", "0"),
        ]:
            try:
                conn.execute(f"ALTER TABLE urls ADD COLUMN {col} {typ} NOT NULL DEFAULT {default}")
            except Exception:
                pass
    logger.info("DB ready at '%s'", DB_PATH)

def bump_stat(conn, key: str, amount: int = 1):
    conn.execute(
        "INSERT INTO global_stats (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = value + ?",
        (key, amount, amount),
    )

def get_global_stats() -> dict:
    with get_db() as conn:
        rows         = conn.execute("SELECT key, value FROM global_stats").fetchall()
        stats        = {r["key"]: r["value"] for r in rows}
        total_urls   = conn.execute("SELECT COUNT(*) as c FROM urls").fetchone()["c"]
        total_clicks = conn.execute("SELECT COALESCE(SUM(click_count),0) as c FROM urls").fetchone()["c"]
    return {
        "total_urls":       total_urls,
        "total_clicks":     total_clicks,
        "phishing_blocked": stats.get("phishing_blocked", 0),
        "suspected_count":  stats.get("suspected_count",  0),
    }

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield

app = FastAPI(title="LinkCut", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

# ── Trusted Domain Whitelist ───────────────────────────────────────────────────
# Root domains only (no subdomains). tldextract will match any subdomain of these.
TRUSTED_DOMAINS: frozenset[str] = frozenset([
    # Search & Productivity
    "google.com", "google.co.in", "google.co.uk", "google.com.au",
    "googleapis.com", "googleusercontent.com", "gstatic.com",
    "bing.com", "yahoo.com", "duckduckgo.com", "baidu.com", "yandex.com",

    # Microsoft
    "microsoft.com", "microsoftonline.com", "live.com", "outlook.com",
    "office.com", "office365.com", "sharepoint.com", "azure.com",
    "onedrive.com", "xbox.com", "skype.com", "teams.microsoft.com",

    # Apple
    "apple.com", "icloud.com", "me.com",

    # Social Media
    "facebook.com", "fb.com", "instagram.com", "threads.net",
    "twitter.com", "x.com", "t.co",
    "linkedin.com", "lnkd.in",
    "tiktok.com", "snapchat.com", "pinterest.com",
    "reddit.com", "redd.it", "tumblr.com",
    "whatsapp.com", "telegram.org", "signal.org",
    "discord.com", "discordapp.com",
    "mastodon.social", "bsky.app",

    # Video & Media
    "youtube.com", "youtu.be", "vimeo.com", "twitch.tv",
    "netflix.com", "hulu.com", "disneyplus.com", "primevideo.com",
    "spotify.com", "soundcloud.com", "pandora.com",
    "dailymotion.com", "rumble.com",

    # E-Commerce & Finance
    "amazon.com", "amazon.in", "amazon.co.uk", "amazon.de",
    "ebay.com", "etsy.com", "shopify.com",
    "paypal.com", "stripe.com", "square.com",
    "razorpay.com", "paytm.com", "phonepe.com",
    "visa.com", "mastercard.com", "americanexpress.com",
    "flipkart.com", "myntra.com", "meesho.com", "nykaa.com",
    "walmart.com", "target.com", "bestbuy.com",

    # Banking & Finance (India + Global)
    "sbi.co.in", "hdfcbank.com", "icicibank.com", "axisbank.com",
    "kotakbank.com", "yesbank.in", "pnbindia.in", "bankofbaroda.in",
    "chase.com", "bankofamerica.com", "wellsfargo.com", "citibank.com",
    "hsbc.com", "barclays.com",

    # Cloud & Dev
    "github.com", "gitlab.com", "bitbucket.org",
    "stackoverflow.com", "stackexchange.com",
    "aws.amazon.com", "cloudflare.com", "digitalocean.com",
    "heroku.com", "render.com", "vercel.com", "netlify.com",
    "firebase.google.com", "supabase.com", "railway.app",
    "npmjs.com", "pypi.org", "packagist.org", "rubygems.org",
    "docker.com", "kubernetes.io", "terraform.io",
    "replit.com", "codepen.io", "jsfiddle.net",

    # News & Information
    "wikipedia.org", "wikimedia.org", "wikidata.org",
    "bbc.com", "bbc.co.uk", "cnn.com", "nytimes.com",
    "theguardian.com", "reuters.com", "apnews.com",
    "ndtv.com", "thehindu.com", "hindustantimes.com", "timesofindia.com",
    "forbes.com", "bloomberg.com", "wsj.com", "techcrunch.com",
    "theverge.com", "wired.com", "arstechnica.com", "engadget.com",

    # Education
    "coursera.org", "udemy.com", "edx.org", "khanacademy.org",
    "duolingo.com", "skillshare.com", "pluralsight.com",
    "mit.edu", "stanford.edu", "harvard.edu",

    # AI & Tech
    "openai.com", "anthropic.com", "claude.ai",
    "gemini.google.com", "copilot.microsoft.com",
    "huggingface.co", "kaggle.com",

    # Government (India + US)
    "gov.in", "nic.in", "india.gov.in", "irctc.co.in",
    "gov", "usa.gov", "irs.gov", "ssa.gov",

    # Utilities & Tools
    "bit.ly", "tinyurl.com", "ow.ly",
    "dropbox.com", "box.com", "wetransfer.com",
    "notion.so", "airtable.com", "trello.com", "asana.com",
    "slack.com", "zoom.us", "meet.google.com", "webex.com",
    "canva.com", "figma.com", "adobe.com",
    "medium.com", "substack.com", "ghost.org",
    "wordpress.com", "wix.com", "squarespace.com",
])

SUSPICIOUS_WORDS: frozenset[str] = frozenset([
    "login", "verify", "bank", "free", "bonus",
    "crypto", "password", "signin", "update", "secure",
])

# ── URL Analysis ───────────────────────────────────────────────────────────────

def get_root_domain(url: str) -> str:
    """Extract just the registered domain, e.g. 'mail.google.com' → 'google.com'."""
    ext = tldextract.extract(url)
    if ext.domain and ext.suffix:
        return f"{ext.domain}.{ext.suffix}".lower()
    return ""

def is_trusted(url: str) -> bool:
    """Return True if the URL belongs to a known trusted domain."""
    root = get_root_domain(url)
    return root in TRUSTED_DOMAINS

def analyze_url(url: str) -> tuple[int, list[str]]:
    """
    Score a URL for phishing signals.
    Trusted domains always return (0, []) — fully bypassing keyword checks.
    """
    # ── Whitelist check first ──────────────────────────────────────
    if is_trusted(url):
        logger.debug("Trusted domain, skipping checks: %s", url)
        return 0, []

    # ── Rule-based scoring for untrusted domains ───────────────────
    score, reasons = 0, []

    if len(url) > 120:
        score += 1
        reasons.append("URL is unusually long")

    special_count = len(re.findall(r"[?=&%$@]", url))
    if special_count > 5:
        score += 1
        reasons.append(f"Too many special characters ({special_count})")

    for word in SUSPICIOUS_WORDS:
        if word in url.lower():
            score += 1
            reasons.append(f"Suspicious keyword: '{word}'")

    ext = tldextract.extract(url)
    if ext.subdomain.count(".") >= 2:
        score += 1
        reasons.append("Excessive subdomains (potential spoofing)")

    if re.match(r"https?://\d+\.\d+\.\d+\.\d+", url):
        score += 2
        reasons.append("Raw IP address used instead of a domain name")

    return score, reasons

# ── LLM Explanation ───────────────────────────────────────────────────────────

def explain_with_llm(url: str, reasons: list[str]) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        return "This URL was flagged for multiple suspicious patterns commonly seen in phishing attacks."
    try:
        client = OpenAI(timeout=5.0)
        prompt = (
            f"URL: {url}\nFlags raised: {', '.join(reasons)}\n\n"
            "In 2-3 short sentences, explain clearly why this URL may be unsafe "
            "for someone who is not technical."
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.error("LLM call failed: %s", exc)
        return "This URL was blocked due to suspicious patterns commonly used in phishing or scam links."

# ── Code Generation ────────────────────────────────────────────────────────────

def _generate_code(length: int = CODE_LENGTH) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def get_unique_code() -> str:
    with get_db() as conn:
        for _ in range(10):
            code = _generate_code()
            if not conn.execute("SELECT 1 FROM urls WHERE short = ?", (code,)).fetchone():
                return code
    raise RuntimeError("Could not generate unique code.")

def expiry_from_option(option: str) -> datetime:
    now = datetime.now(timezone.utc)
    return {"1h": now + timedelta(hours=1), "1d": now + timedelta(days=1)}.get(
        option, now + timedelta(days=7)
    )

def safe_dt(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

def time_remaining(expires_at: datetime) -> str:
    delta = expires_at - datetime.now(timezone.utc)
    if delta.total_seconds() <= 0:
        return "Expired"
    s = int(delta.total_seconds())
    if s >= 86400:  return f"{s//86400}d {(s%86400)//3600}h remaining"
    if s >= 3600:   return f"{s//3600}h {(s%3600)//60}m remaining"
    return f"{s//60}m remaining"

def threat_label(score: int) -> str:
    if score == 0:  return "clean"
    if score <= 2:  return "suspected"
    return "dangerous"

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, **get_global_stats()})

@app.get("/api/stats", response_class=JSONResponse)
async def api_global_stats():
    return get_global_stats()

@app.post("/shorten", response_class=HTMLResponse)
async def shorten(
    request: Request,
    url: str = Form(...),
    expiry: str = Form(...),
    alias: str = Form(""),
):
    client_ip = request.client.host
    gstats = get_global_stats()

    if is_rate_limited(client_ip):
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "⚠️ Too many requests. Please wait a minute.", **gstats},
        )

    score, reasons = analyze_url(url)
    is_suspected = 1 if 1 <= score <= 2 else 0

    if score >= 3:
        explanation = explain_with_llm(url, reasons)
        logger.warning("Blocked URL [score=%d] from %s: %.80s", score, client_ip, url)
        with get_db() as conn:
            bump_stat(conn, "phishing_blocked")
        return templates.TemplateResponse(
            "index.html",
            {
                "request":        request,
                "error":          "⚠️ This URL looks unsafe",
                "llm_explanation": explanation,
                "threat_reasons": reasons,
                **get_global_stats(),
            },
        )

    alias = alias.strip()
    if alias:
        if not re.match(r"^[a-zA-Z0-9_-]{3,20}$", alias):
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": "❌ Alias: 3–20 chars, letters/digits/- only.", **gstats},
            )
        with get_db() as conn:
            if conn.execute("SELECT 1 FROM urls WHERE short = ?", (alias,)).fetchone():
                return templates.TemplateResponse(
                    "index.html",
                    {"request": request, "error": "❌ That alias is already taken.", **gstats},
                )
        code = alias
    else:
        code = get_unique_code()

    expires_at = expiry_from_option(expiry)
    created_at = datetime.now(timezone.utc)

    with get_db() as conn:
        conn.execute(
            """INSERT INTO urls
               (original, short, alias, created_at, expires_at, threat_score, threat_reasons, is_suspected)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (url, code, alias or None, created_at.isoformat(),
             expires_at.isoformat(), score, json.dumps(reasons), is_suspected),
        )
        if is_suspected:
            bump_stat(conn, "suspected_count")

    logger.info("Created /%s → %.80s (expires %s, score=%d)", code, url, expires_at.date(), score)
    base = str(request.base_url).rstrip("/")

    return templates.TemplateResponse(
        "index.html",
        {
            "request":        request,
            "short_url":      f"{base}/{code}",
            "stats_url":      f"{base}/stats/{code}",
            "expiry_info":    expires_at.strftime("%d %b %Y · %H:%M UTC"),
            "is_suspected":   is_suspected,
            "threat_score":   score,
            "threat_reasons": reasons,
            **get_global_stats(),
        },
    )

@app.get("/stats/{code}", response_class=HTMLResponse)
async def stats_page(request: Request, code: str):
    with get_db() as conn:
        row = conn.execute(
            """SELECT original, short, created_at, expires_at, click_count,
                      threat_score, threat_reasons, is_suspected
               FROM urls WHERE short = ?""",
            (code,),
        ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Short URL not found.")

    expires_at = safe_dt(datetime.fromisoformat(row["expires_at"]))
    created_at = safe_dt(datetime.fromisoformat(row["created_at"]))

    try:
        reasons = json.loads(row["threat_reasons"])
    except Exception:
        reasons = []

    base = str(request.base_url).rstrip("/")
    return templates.TemplateResponse(
        "stats.html",
        {
            "request":        request,
            "original":       row["original"],
            "short":          row["short"],
            "created_at":     created_at.strftime("%d %b %Y · %H:%M UTC"),
            "expires_at":     expires_at.strftime("%d %b %Y · %H:%M UTC"),
            "click_count":    row["click_count"],
            "is_expired":     datetime.now(timezone.utc) > expires_at,
            "time_remaining": time_remaining(expires_at),
            "base_url":       base,
            "threat_score":   row["threat_score"],
            "threat_label":   threat_label(row["threat_score"]),
            "threat_reasons": reasons,
            "is_suspected":   row["is_suspected"],
            **get_global_stats(),
        },
    )

@app.get("/{code}")
async def redirect_to_url(request: Request, code: str, proceed: str = ""):
    with get_db() as conn:
        row = conn.execute(
            """SELECT original, expires_at, threat_score, threat_reasons, is_suspected
               FROM urls WHERE short = ?""",
            (code,),
        ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Short URL not found.")

        expires_at = safe_dt(datetime.fromisoformat(row["expires_at"]))
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=410, detail="This link has expired.")

        score = row["threat_score"]
        label = threat_label(score)

        try:
            reasons = json.loads(row["threat_reasons"])
        except Exception:
            reasons = []

        # DANGEROUS → always block, no way through
        if label == "dangerous":
            return templates.TemplateResponse(
                "warning.html",
                {
                    "request":        request,
                    "original":       row["original"],
                    "code":           code,
                    "threat_label":   label,
                    "threat_score":   score,
                    "threat_reasons": reasons,
                    "proceed":        False,
                },
                status_code=403,
            )

        # SUSPECTED → show warning, let user decide
        if label == "suspected" and proceed != "yes":
            return templates.TemplateResponse(
                "warning.html",
                {
                    "request":        request,
                    "original":       row["original"],
                    "code":           code,
                    "threat_label":   label,
                    "threat_score":   score,
                    "threat_reasons": reasons,
                    "proceed":        True,
                },
                status_code=200,
            )

        # SAFE or user proceeded → count click and redirect
        conn.execute("UPDATE urls SET click_count = click_count + 1 WHERE short = ?", (code,))

    logger.info("Redirect /%s → %.80s", code, row["original"])
    return RedirectResponse(row["original"], status_code=302)