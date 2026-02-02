AI URL Shortener with Intelligent Security Filters

Description
This project is a backend-focused URL shortening service built using FastAPI.
It provides short URLs with expiry support and protects users by detecting malicious URLs using rule-based heuristics.
For unsafe links, an optional LLM (OpenAI GPT-4.1-mini) generates a simple human-readable explanation with safe fallbacks to ensure reliability.

The system is designed for high performance, fault tolerance, and interview-ready backend architecture.

Key Features

FastAPI-based REST backend

URL shortening with automatic expiry handling

SQLite database for lightweight persistence

Heuristic-based malicious URL detection

Optional LLM-powered safety explanation (non-blocking, timeout-protected)

Deterministic fallback when AI is unavailable or quota is exceeded

Sub-second response time for safe URLs

Automated testing using pytest

CI pipeline implemented using Azure DevOps

Tech Stack

Backend Framework: FastAPI
Database: SQLite
AI / LLM: OpenAI GPT-4.1-mini (optional, fallback enabled)
Testing: Pytest
CI/CD: Azure DevOps Pipelines
Language: Python
API Style: REST APIs

Project Structure

main.py
Contains all FastAPI routes, URL analysis logic, database handling, and AI integration.

templates/index.html
Minimal frontend to interact with backend APIs.

tests/
Contains automated test cases for core routes.

urls.db
SQLite database created automatically at runtime (not committed to repository).

Setup Instructions

Clone the repository
git clone https://github.com/dewangshree/AI-URL-Shortener.git

cd AI-URL-Shortener

Create and activate virtual environment
python -m venv venv
source venv/bin/activate

Install dependencies
pip install -r requirements.txt

If requirements.txt is not present, install manually:
pip install fastapi uvicorn python-multipart sqlite3 tldextract python-dotenv pytest openai

Environment Variable Setup

This project uses an OpenAI API key optionally.

Create a .env file in the project root and add:
OPENAI_API_KEY=your_secret_key_here

Alternatively, export the key in terminal:
export OPENAI_API_KEY=your_secret_key_here

If the key is missing or expired, the application will still work using safe fallback explanations.

Run the Application

Start the FastAPI server using:
uvicorn main:app --reload

Open browser and visit:
http://127.0.0.1:8000

API Endpoints

POST /shorten
Shortens a URL and applies safety checks.

Request form fields:
url
expiry (1h, 1d, 7d)

GET /{short_code}
Redirects to the original URL if not expired.

Running Tests

Run all automated tests using:
python -m pytest

All core routes are covered and validated through CI.

CI Pipeline

This project includes an Azure DevOps pipeline that:

Installs dependencies

Runs pytest on multiple Python versions

Blocks merge if tests fail

Design Decisions

Heuristic checks are always applied first for speed

LLM explanation is optional and non-blocking

Timeouts prevent AI calls from slowing down requests

Deterministic fallback ensures zero downtime

SQLite chosen for simplicity and portability

Use Case

This project demonstrates backend engineering skills including REST API design, security-focused logic, fault tolerance, testing, and CI/CD integration.

Future Enhancements (Optional)

Rate limiting

Analytics dashboard

Production database (PostgreSQL)

Containerization
