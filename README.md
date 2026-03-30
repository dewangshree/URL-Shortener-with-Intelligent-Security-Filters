<div align="center">

# 🔗 LinkCut
### URL Shortener with Intelligent Security Filters

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Deployed on Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

> **Shorten smarter. Share safer.**  
> LinkCut shortens URLs while running every link through an AI-powered security pipeline — blocking phishing, malware, and malicious redirects before they reach anyone.

[🌐 Live Demo](https://ai-url-shortner-ly68.onrender.com) · [📄 API Docs](https://ai-url-shortner-ly68.onrender.com/docs) · [🐛 Report a Bug](https://github.com/dewangshree/URL-Shortener-with-Intelligent-Security-Filters/issues)

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [Security Pipeline](#-security-pipeline)
- [Project Structure](#-project-structure)
- [Environment Variables](#-environment-variables)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

---

## 🧠 Overview

**LinkCut** is a production-grade URL shortener that goes beyond simple redirection. Every URL submitted is passed through an **intelligent, LLM-backed security layer** that detects malicious intent — including phishing attempts, suspicious redirects, and known malware patterns — before a short link is ever generated.

This project was built to demonstrate how AI can be integrated into utility-grade APIs to add real-world safety value, not just convenience.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔗 **URL Shortening** | Generates clean, collision-free short codes for any valid URL |
| 🤖 **AI Security Analysis** | Uses OpenAI to classify URLs as safe, suspicious, or malicious before shortening |
| 🛡️ **Phishing Detection** | Identifies deceptive domains mimicking trusted services |
| 📊 **Click Tracking** | Logs every redirect with timestamp metadata |
| 🗃️ **Persistent Storage** | SQLite-backed with proper schema for URLs and request logs |
| 📄 **Auto-generated API Docs** | Full Swagger UI at `/docs` and ReDoc at `/redoc` |
| 🚀 **Production Deployment** | Hosted on Render with zero-config continuous deployment |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                        CLIENT                            │
│              (Browser / API Consumer)                    │
└─────────────────────────┬────────────────────────────────┘
                          │  HTTP Request
                          ▼
┌──────────────────────────────────────────────────────────┐
│                    FastAPI Backend                        │
│                                                          │
│   POST /shorten                GET /{short_code}         │
│        │                              │                  │
│        ▼                              ▼                  │
│  ┌─────────────────┐      ┌──────────────────────┐       │
│  │ Security Filter │      │   Redirect Handler   │       │
│  │  (AI Pipeline)  │      │  (Click Log + 302)   │       │
│  └────────┬────────┘      └──────────────────────┘       │
│           │                                              │
│           ▼                                              │
│  ┌─────────────────┐                                     │
│  │   OpenAI API    │  ← URL Classification Prompt        │
│  │  (GPT-4o-mini)  │                                     │
│  └────────┬────────┘                                     │
│           │ SAFE / SUSPICIOUS / MALICIOUS                │
│           ▼                                              │
│  ┌─────────────────┐                                     │
│  │  SQLite Database│                                     │
│  │  urls | logs    │                                     │
│  └─────────────────┘                                     │
└──────────────────────────────────────────────────────────┘
```

**Request flow for `POST /shorten`:**
1. Validate URL format
2. Send URL to OpenAI for security classification
3. If classified **SAFE** → generate short code → store in DB → return short URL
4. If **SUSPICIOUS** or **MALICIOUS** → reject with a descriptive error

**Request flow for `GET /{short_code}`:**
1. Look up short code in DB
2. Log the redirect event (timestamp, IP if available)
3. Return `302 Redirect` to the original URL

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **API Framework** | FastAPI | High-performance async REST API |
| **AI Layer** | OpenAI GPT-4o-mini | Intelligent URL security classification |
| **Database** | SQLite + SQLAlchemy | Lightweight persistent storage |
| **Validation** | Pydantic v2 | Request/response schema enforcement |
| **Hosting** | Render | Cloud deployment with auto-deploy from GitHub |
| **Docs** | Swagger UI (built-in) | Interactive API exploration at `/docs` |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### 1. Clone the repository

```bash
git clone https://github.com/dewangshree/URL-Shortener-with-Intelligent-Security-Filters.git
cd URL-Shortener-with-Intelligent-Security-Filters
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

```bash
cp .env.example .env
# Then edit .env and add your OPENAI_API_KEY
```

### 5. Run the server

```bash
uvicorn main:app --reload
```

The API will be live at `http://localhost:8000`  
Swagger docs at `http://localhost:8000/docs`

> 🌐 **Live deployment:** [https://ai-url-shortner-ly68.onrender.com](https://ai-url-shortner-ly68.onrender.com)  
> 📄 **Live API docs:** [https://ai-url-shortner-ly68.onrender.com/docs](https://ai-url-shortner-ly68.onrender.com/docs)

---

## 📡 API Reference

### `POST /shorten`

Shorten a URL after running it through the AI security filter.

**Request Body:**
```json
{
  "url": "https://example.com/some/long/path"
}
```

**Response (200 — Safe URL):**
```json
{
  "short_url": "http://localhost:8000/aB3kQz",
  "original_url": "https://example.com/some/long/path",
  "security_status": "safe"
}
```

**Response (400 — Malicious URL):**
```json
{
  "detail": "URL flagged as malicious by security filter. Short link not created."
}
```

---

### `GET /{short_code}`

Redirect to the original URL.

| Status | Meaning |
|---|---|
| `302` | Successful redirect |
| `404` | Short code not found |

---

### `GET /docs`

Auto-generated interactive Swagger UI for all endpoints.

---

## 🛡️ Security Pipeline

LinkCut's AI security layer uses a structured prompt sent to **GPT-4o-mini** that instructs the model to evaluate URLs across several threat dimensions:

- **Domain spoofing** — lookalike domains mimicking trusted brands (e.g., `paypa1.com`)
- **Suspicious TLDs** — common in phishing campaigns (`.xyz`, `.tk`, `.ml`, etc.)
- **Redirector abuse** — URL shorteners used to mask final destinations
- **Known malware patterns** — paths and query strings matching known attack vectors
- **Structural anomalies** — excessive subdomains, unusually long paths, encoded payloads

The model returns one of three verdicts:

```
SAFE         → Short link is created and returned
SUSPICIOUS   → Request is rejected with a warning
MALICIOUS    → Request is rejected with a clear error
```

This keeps the pipeline honest: the AI does not guess, it classifies with structured output enforced by the system prompt.

---

## 📁 Project Structure

```
URL-Shortener-with-Intelligent-Security-Filters/
├── main.py               # FastAPI app, route definitions
├── database.py           # SQLAlchemy setup, models, session
├── security.py           # OpenAI security classification logic
├── models.py             # Pydantic request/response schemas
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
└── README.md
```

---

## 🔐 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | ✅ | Your OpenAI API key |
| `BASE_URL` | Optional | Base URL for generated short links (defaults to `localhost:8000`) |
| `DATABASE_URL` | Optional | SQLite DB path (defaults to `./linkcut.db`) |

---

## ☁️ Deployment

This project is deployed on **Render** with the following configuration:

- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment:** Python 3.11
- **Build:** `pip install -r requirements.txt`

To deploy your own instance:

1. Fork this repository
2. Connect it to [Render](https://render.com)
3. Add `OPENAI_API_KEY` as an environment variable in the Render dashboard
4. Deploy — Render will auto-build and serve the app

---

## 🤝 Contributing

Contributions are welcome. To get started:

```bash
# Fork the repo, then:
git checkout -b feature/your-feature-name
git commit -m "feat: add your feature"
git push origin feature/your-feature-name
# Open a Pull Request
```

Please keep PRs focused and include a brief description of what changed and why.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

Built by [Shreyas Dewangswami](https://github.com/dewangshree)

</div>
