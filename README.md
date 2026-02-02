URL Shortener API with Intelligent Security Filters

This project is a backend URL shortening service built using Python and FastAPI.
It generates short URLs, redirects users to original URLs, and blocks unsafe links using intelligent security checks.
The system is designed for fast response time, reliability, and clean backend architecture.

---

Features

• Shorten long URLs
• Redirect short URLs
• URL expiration handling
• Malicious URL detection using rule-based analysis
• Optional AI explanation for blocked URLs with safe fallback
• SQLite database for persistence
• REST API design
• Automated testing with pytest
• CI pipeline using Azure DevOps

---

Tech Stack

Backend: FastAPI
Language: Python
Database: SQLite
LLM: OpenAI GPT-4.1-mini (optional)
Testing: pytest
CI/CD: Azure DevOps Pipelines

---

Project Structure

main.py
templates/
tests/
urls.db (created automatically at runtime)

---

Setup Instructions

Clone the repository

```
git clone https://github.com/dewangshree/AI-URL-Shortener.git
cd AI-URL-Shortener
```

Create a virtual environment

```
python -m venv venv
```

Activate the virtual environment

macOS / Linux

```
source venv/bin/activate
```

Windows

```
venv\Scripts\activate
```

Install dependencies

```
pip install -r requirements.txt
```

(Optional) Set OpenAI API key for AI explanations

```
export OPENAI_API_KEY=your_openai_key_here
```

Verify the key

```
echo $OPENAI_API_KEY
```

---

Run the Application

Start the FastAPI server

```
uvicorn main:app --reload
```

Application will be available at

```
http://127.0.0.1:8000
```

---

API Endpoints

POST /shorten

Purpose
Create a short URL

Request (form data)

```
url = https://example.com
expiry = 1h | 1d | 7d
```

Success Response
Returns short URL and expiry time

Blocked URL Response
Returns error message and explanation

---

GET /{short_code}

Purpose
Redirect to the original URL

```
http://127.0.0.1:8000/abc123
```

---

GET /{short_code}/info

Purpose
Fetch metadata of a shortened URL

---

Security Logic

Each URL is scored using multiple checks:

• URL length
• Suspicious keywords
• Special character frequency
• Multiple subdomains
• IP-based URLs

URLs exceeding the risk threshold are blocked instantly.
AI explanations are optional and never crash the application.

---

Running Tests

Run all tests locally

```
python -m pytest
```

Test coverage includes:

• Home page loading
• Safe URL shortening
• Malicious URL blocking
• Invalid short code handling

---

CI Pipeline

Azure DevOps pipeline automatically runs tests on every push using multiple Python versions.

