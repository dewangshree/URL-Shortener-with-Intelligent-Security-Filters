URL Shortener API with Intelligent Security Filters

This project is a backend URL shortening service built using Python and FastAPI.
It allows users to generate short URLs, automatically redirect to original URLs, and block unsafe or suspicious links using intelligent security checks.
The system is designed with reliability, low latency, and testability in mind.

Features

Shorten long URLs into compact codes
Redirect short URLs to original destinations
Automatic URL expiration handling
Heuristic-based malicious URL detection
AI-powered explanation for blocked URLs with safe fallback
SQLite-based persistent storage
RESTful API design
Automated testing with pytest
CI pipeline integration using Azure DevOps

Tech Stack

Backend Framework: FastAPI
Language: Python
Database: SQLite
Security Logic: Rule-based URL analysis
LLM Integration: OpenAI GPT-4.1-mini (optional, non-blocking)
Testing: pytest
CI/CD: Azure DevOps Pipelines

Project Structure

main.py
templates/
tests/
urls.db (created at runtime)

Installation and Setup

Clone the repository

git clone https://github.com/dewangshree/AI-URL-Shortener.git

cd AI-URL-Shortener

Create and activate virtual environment

python -m venv venv
source venv/bin/activate

Install dependencies

pip install -r requirements.txt

(Optional) Set OpenAI API key for AI explanations

export OPENAI_API_KEY=your_api_key_here

Running the Application

Start the FastAPI server

uvicorn main:app --reload

Open browser and visit

http://127.0.0.1:8000

API Endpoints

POST /shorten

Purpose
Create a short URL

Request Body (form data)

url = https://example.com

expiry = 1h | 1d | 7d

Response (success)

short_url
expiry_info

Response (blocked)

error
llm_explanation

GET /{short_code}

Purpose
Redirect to original URL

Response
Redirects to original URL if valid and not expired

GET /{short_code}/info

Purpose
Fetch metadata about a short URL

Response

original_url
short_code
expiry_time

Security Logic

URLs are analyzed using multiple heuristic checks such as:

URL length
Suspicious keywords
Special characters count
Subdomain depth
IP-based URLs

If a URL crosses the risk threshold, it is blocked immediately.
AI explanations are generated only when available and never block request processing.

Testing

Run all tests using pytest

python -m pytest

All critical flows are covered including:

Safe URL shortening
Malicious URL blocking
Invalid short code handling

CI Pipeline

This project includes a CI pipeline configured using Azure DevOps.
The pipeline automatically installs dependencies and runs pytest on every commit.
