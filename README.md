<div align="center">

# 🔗 URL Shortener API

### Intelligent Security Filters · FastAPI · Azure DevOps CI

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4.1-412991?style=for-the-badge&logo=openai)
![Azure DevOps](https://img.shields.io/badge/Azure%20DevOps-CI%20Pipeline-0078D7?style=for-the-badge&logo=azuredevops)
![pytest](https://img.shields.io/badge/pytest-Tested-0A9EDC?style=for-the-badge&logo=pytest)
![Render](https://img.shields.io/badge/Deployed-Render-46E3B7?style=for-the-badge&logo=render)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

A backend URL shortening service built with **Python** and **FastAPI** that generates short URLs, handles redirects, enforces expiry, and blocks malicious links using intelligent rule-based security scoring — with optional AI-powered explanations via GPT-4.1-mini.

🚀 **[Live Demo →](https://ai-url-shortner-ly68.onrender.com)**

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Security Logic](#-security-logic)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Running the Application](#-running-the-application)
- [API Endpoints](#-api-endpoints)
- [Running Tests](#-running-tests)
- [CI Pipeline](#-ci-pipeline)
- [Screenshots](#-screenshots)
- [Future Improvements](#-future-improvements)

---

## 🔷 Overview

> A production-ready URL shortening API designed for **fast response time**, **reliability**, and **clean backend architecture**. The system scores every URL against a rule-based security engine before shortening — and optionally generates an AI explanation when a URL is blocked.

| Capability | Implementation |
|---|---|
| URL Shortening | FastAPI + SQLite persistence |
| Malicious URL Detection | Rule-based risk scoring engine |
| AI Explanations | OpenAI GPT-4.1-mini (optional, safe fallback) |
| URL Expiry | Configurable 1h / 1d / 7d expiry |
| Testing | pytest automated test suite |
| CI/CD | Azure DevOps Pipelines (multi-Python) |

---

## ✨ Features

```
✅ Shorten long URLs to compact short codes
✅ Redirect short URLs to original destinations
✅ URL expiration handling (1h / 1d / 7d)
✅ Malicious URL detection via rule-based scoring
✅ Optional AI explanation for blocked URLs
✅ Safe fallback — AI errors never crash the app
✅ SQLite database for persistent storage
✅ Clean REST API design
✅ Automated test suite with pytest
✅ CI pipeline via Azure DevOps (multi-Python)
```

---

## 🏗 System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        USER / CLIENT                         │
│             Web Browser / API Client / curl                  │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           │  HTTP Request
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                          │
│  • POST /shorten   →  Create short URL                       │
│  • GET /{code}     →  Redirect to original                   │
│  • GET /{code}/info →  Fetch URL metadata                    │
└──────────────────────────┬───────────────────────────────────┘
                           │
               ┌───────────┴────────────┐
               ▼                        ▼
┌──────────────────────┐   ┌────────────────────────────────────┐
│  SECURITY SCORING    │   │         SQLITE DATABASE            │
│  ENGINE              │   │                                    │
│                      │   │  • short_code                      │
│  • URL length check  │   │  • original_url                    │
│  • Keyword scanning  │   │  • created_at                      │
│  • Special chars     │   │  • expires_at                      │
│  • Subdomain depth   │   │  • click_count                     │
│  • IP-based URLs     │   └────────────────────────────────────┘
└──────────┬───────────┘
           │
           │ If URL blocked
           ▼
┌──────────────────────────────────────────────────────────────┐
│              OPENAI GPT-4.1-mini (Optional)                  │
│  • Generates human-readable explanation for blocked URL      │
│  • Falls back gracefully if API key not set                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Logic

Every submitted URL is scored across **5 risk signals** before being shortened:

```
Signal 1 → URL length              (unusually long URLs score higher risk)
Signal 2 → Suspicious keywords     (known malware/phishing terms)
Signal 3 → Special character freq  (excessive symbols suggest obfuscation)
Signal 4 → Multiple subdomains     (deep subdomain chains are a red flag)
Signal 5 → IP-based URLs           (raw IP addresses instead of domains)
```

**Decision logic:**

```
Total Risk Score < Threshold  →  URL is shortened and stored
Total Risk Score ≥ Threshold  →  URL is blocked instantly
                                 AI explanation generated (if key set)
                                 Safe fallback message if AI unavailable
```

> AI explanations are **optional** and **never crash the application** — the system works fully without an OpenAI key.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **Backend Framework** | FastAPI |
| **Database** | SQLite (auto-created at runtime) |
| **AI Layer** | OpenAI GPT-4.1-mini (optional) |
| **Testing** | pytest |
| **CI/CD** | Azure DevOps Pipelines |
| **Server** | Uvicorn |
| **Deployment** | Render |

---

## 📂 Project Structure

```
AI-URL-Shortener/
│
├── main.py                 # FastAPI app, routes, core logic
├── templates/              # HTML templates (frontend UI)
│
├── tests/                  # pytest test suite
│   └── test_main.py
│
├── urls.db                 # SQLite database (auto-generated)
├── requirements.txt        # Python dependencies
├── azure-pipelines.yml     # Azure DevOps CI config
├── .env                    # Environment variables (not committed)
├── .gitignore
└── README.md
```

---

## ⚙ Installation

**1. Clone the repository**

```bash
git clone https://github.com/dewangshree/AI-URL-Shortener.git
cd AI-URL-Shortener
```

**2. Create a virtual environment**

```bash
python -m venv venv
```

**3. Activate the virtual environment**

macOS / Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

**5. (Optional) Set OpenAI API key for AI explanations**

```bash
export OPENAI_API_KEY=your_openai_key_here
```

Verify the key is set:

```bash
echo $OPENAI_API_KEY
```

> If not set, the app runs fully — AI explanations are simply skipped with a safe fallback message.

---

## ▶ Running the Application

```bash
uvicorn main:app --reload
```

Application available at:

```
http://127.0.0.1:8000
```

Interactive API docs at:

```
http://127.0.0.1:8000/docs
```

---

## 🔌 API Endpoints

### `POST /shorten` — Create a short URL

**Request (form data):**

```
url    = https://example.com
expiry = 1h | 1d | 7d
```

**Success response:**

```json
{
  "short_url": "http://127.0.0.1:8000/abc123",
  "expires_at": "2024-11-16T20:00:00Z"
}
```

**Blocked URL response:**

```json
{
  "error": "URL blocked",
  "explanation": "This URL contains suspicious patterns associated with phishing."
}
```

---

### `GET /{short_code}` — Redirect to original URL

```
http://127.0.0.1:8000/abc123
```

Redirects the user to the original long URL. Returns `404` if expired or not found.

---

### `GET /{short_code}/info` — Fetch URL metadata

```json
{
  "short_code": "abc123",
  "original_url": "https://example.com",
  "created_at": "2024-11-15T19:00:00Z",
  "expires_at": "2024-11-16T19:00:00Z",
  "click_count": 14
}
```

---

## 🧪 Running Tests

```bash
python -m pytest
```

**Test coverage includes:**

```
✔  Home page loading
✔  Safe URL shortening flow
✔  Malicious URL blocking
✔  Invalid short code handling
✔  Expiry validation
```

---

## 🔄 CI Pipeline

Azure DevOps pipeline automatically runs the full test suite on every push across multiple Python versions.

```yaml
# Triggers on every push
trigger:
  - main

# Runs pytest across Python 3.10, 3.11, 3.12
strategy:
  matrix:
    Python310:
      pythonVersion: "3.10"
    Python311:
      pythonVersion: "3.11"
    Python312:
      pythonVersion: "3.12"
```

---

## 📸 Screenshots

### URL Shortener Interface

<img width="670" alt="URL Shortener - Home" src="https://github.com/user-attachments/assets/4d55cab0-d123-4d22-b68c-259f2703b7e8" />

### Malicious URL Blocked

<img width="670" alt="URL Shortener - Blocked URL" src="https://github.com/user-attachments/assets/c9893530-416c-4047-8071-440e81371178" />

---

## 🚀 Future Improvements

```
[ ] User authentication and personal URL dashboards
[ ] Click analytics with geographic breakdown
[ ] QR code generation for short URLs
[ ] Custom short code aliases
[ ] Rate limiting per IP address
[ ] Upgrade to PostgreSQL for production scale
[ ] Webhook support on redirect events
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with FastAPI · SQLite · OpenAI · Azure DevOps · Render**

⭐ Star this repo if you found it helpful!

</div>
