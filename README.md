# Sentinel — Agentic Red-Teaming Pipeline

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-Gemini%20|%20Groq%20|%20Llama3-orange)
![Security](https://img.shields.io/badge/Security-Red--Teaming-red)
![MCP](https://img.shields.io/badge/MCP-Supported-purple)
![Agents](https://img.shields.io/badge/Agents-Multi--Agent-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green.svg)
[![Kaggle](https://img.shields.io/badge/Kaggle-Notebook-blue?logo=kaggle)](#)

> **⚠️ Proof of Concept**: Sentinel is currently an experimental Proof of Concept (PoC) designed for research, benchmarking, and validation of AI Agent defensive configurations.

> Built as a capstone for the [Kaggle/Google 5-Day AI Agents Intensive](https://www.kaggle.com/learn-guide/5-day-genai) (June 2026). Demonstrates 7 course concepts: multi-agent orchestration, MCP servers, agent skills, agentic security, memory/context engineering, evaluation & observability, and production deployment.

Sentinel is an automated, multi-agent adversarial testing framework designed to evaluate and harden target AI agents against prompt-injection and tool-misuse vulnerabilities.

## 🏗️ Architecture

![Sentinel Architecture](architecture.svg)

The system operates via a continuous evaluation loop between three distinct AI agents:
- **Target Agent**: A simulated customer support bot for a financial services company with real access to tools (via the Model Context Protocol / MCP) including `read_file`, `send_email`, `delete_file`, and `transfer_funds`.
- **Attacker Agent**: An adversarial LLM tasked with dynamically crafting malicious payloads using a library of specific attack skills to trick the Target into unauthorized data exfiltration or destructive actions.
- **Judge Agent**: An impartial evaluator that analyzes the interaction, verifies whether the Target executed unauthorized tool calls, and scores the exploit on a Severity Scale (1-5).

## 📊 Key Findings
- Naive target exploited on **100% of evaluated runs**, typically on the first attempt
- Nudged target consistently resisted `roleplay_override` but fell to `tool_chain_exfiltration` by attempt 3 — demonstrating real adaptive escalation
- `destructive_action_injection` achieved Severity 5 on every Phase A attempt against the naive target
- `unauthorized_transaction_injection` achieved Severity 5 on 2/3 Phase A attempts — one failure correctly scored as Severity 1 (intent without tool call execution)
- Exploitability is model-dependent: identical tool surface and system prompt produced different resistance patterns across Gemini and Groq/Llama backends

## 🛠️ Attack Surface
The Attacker leverages the following injection strategies:
- `direct_injection`: Overt commands to misuse tools.
- `indirect_injection`: Malicious instructions embedded inside documents or data.
- `roleplay_override`: Social engineering to bypass systemic restrictions.
- `tool_chain_exfiltration`: Multi-step attacks combining read access with email capabilities.
- `destructive_action_injection`: Malicious requests prompting the agent to wipe critical system files.
- `unauthorized_transaction_injection`: Exploitation of the `transfer_funds` endpoint.

## 🚀 Key Features
- **Dynamic Adaptation**: The Attacker reads the history of failed attempts and actively changes its payload and skill choices based on what the Target successfully resisted.
- **HTML Security Report**: Auto-generates a self-contained `sentinel_report.html` after every benchmark run — includes a severity timeline, naive vs nudged comparison table, and a full attempt log with expandable target responses and Judge reasoning.
- **Pluggable LLM Backends**: Seamlessly toggle between Live execution (Gemini 2.5 Flash) and Dev modes (Groq / Llama 3.3 70B, NVIDIA NIM, X.AI Grok) to avoid production rate limits during testing.
- **Comparative Benchmarking**: Run isolated, exhaustive evaluations across different Target system prompts (e.g., `naive` vs `nudged` defensive configurations) using the `compare_targets.py` runner to generate statistical success metrics.

## ⚙️ Quick Start

### 1. Environment Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration
Copy the template and add your API keys:
```bash
cp .env.example .env
# Set GEMINI_API_KEY (for Live mode)
# Set GROQ_API_KEY (for Dev mode testing)
```

### 3. Execution Modes

**Live Interactive Attack Loop:**
Runs the standard single-session pipeline.
```bash
python main.py
```

**Dev Mode (No Gemini Quota):**
Overrides the backend with free-tier APIs (e.g. Groq) for high-volume testing without hitting Gemini rate limits.
```bash
SENTINEL_MODE=dev python main.py
```

**Aggregated Benchmarking:**
Executes an exhaustive, multi-run comparison against differing target configurations (Naive vs. Defensive Nudge) and exports results to `comparison_results.json`.
```bash
SENTINEL_MODE=dev python compare_targets.py
```

**HTML Report Generation:**
Creates a self-contained, offline-ready HTML dashboard summarizing the benchmark run, including timeline visualizations and comparison tables.
```bash
python generate_report.py --log attack_log.json --comparison comparison_results.json --output sentinel_report.html
```

### Environment Variables
- `SENTINEL_MODE`: Controls the backend API (`live`, `dev`, `mock`).
- `SENTINEL_TARGET_CONFIG`: Controls the defensive posture of the Target agent (`naive`, `nudged`).
- `SENTINEL_MAX_ATTEMPTS`: Limits the number of adversarial iterations per evaluation (default: `5`).
- `SENTINEL_EARLY_BREAK`: Set to `false` to force an exhaustive test of all skills even after a successful exploit.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
