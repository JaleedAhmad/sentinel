# Sentinel — Multi-Agent Red-Team

Sentinel is a 3-agent system that tests a target agent for prompt-injection and tool-misuse vulnerabilities.

## Quick Start

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies (including `google-adk` and `fastmcp`):
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the `.env.example` file to `.env` and configure your API key:
   ```bash
   cp .env.example .env
   # Edit .env and set GEMINI_API_KEY
   ```
4. Run the end-to-end execution:
   ```bash
   python main.py
   ```
