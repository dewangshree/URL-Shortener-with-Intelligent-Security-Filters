URL Shortener API with Intelligent Security Filters

This project is a backend URL shortening service built using Python and FastAPI.
It allows users to generate short URLs, redirect to original URLs, and block unsafe links using intelligent security checks.
The system is optimized for low latency, reliability, and testability.

Features

Shorten long URLs
Redirect short URLs to original links
URL expiration support
Malicious URL detection using heuristic rules
AI-based explanation for blocked URLs with safe fallback
SQLite database for persistence
REST API implementation
Automated testing using pytest
CI pipeline using Azure DevOps

Tech Stack

Backend: FastAPI
Language: Python
Database: SQLite
Security Logic: Rule-based URL analysis
LLM: OpenAI GPT-4.1-mini (optional)
Testing: pytest
CI/CD: Azure DevOps Pipelines

Project Structure

main.py
templates/
tests/
urls.db (auto-created at runtime)


Setup Instructions
Clone the repository
git clone https://github.com/dewangshree/AI-URL-Shortener.git
cd AI-URL-Shortener
