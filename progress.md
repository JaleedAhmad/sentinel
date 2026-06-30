# Project Sentinel — Progress & Context Tracking

## 🎯 Project Overview
Sentinel is an automated, multi-agent adversarial testing framework designed to evaluate and harden target AI agents against prompt-injection and tool-misuse vulnerabilities.

The core architecture consists of:
1. **Target Agent**: A simulated customer support bot connected to a mock filesystem and external endpoints via the Model Context Protocol (MCP).
2. **Attacker Agent**: An adversarial LLM tasked with dynamically crafting malicious payloads to manipulate the Target into executing unauthorized actions.
3. **Judge Agent**: An impartial evaluator that analyzes the interactions, checks for successful exploits, and scores them on a Severity Scale (1-5).

---

## 🚀 What We Have Accomplished

### 1. Expanded Attack Surface & Tools
- Developed a local FastMCP server (`mcp_server.py`) exposing critical mock tools: `read_file`, `send_email`, `delete_file`, and `transfer_funds`.
- Expanded the Attacker's skill library (`attack_skills.py`) to include high-stakes injection types:
  - `destructive_action_injection` (tricking the target into deleting files).
  - `unauthorized_transaction_injection` (tricking the target into transferring funds).
- Updated the Judge's rubric to automatically assign a **Severity 5** rating if the Target incorrectly executes the `delete_file` or `transfer_funds` tools.

### 2. Defensive Calibration
- Implemented a configuration toggle (`SENTINEL_TARGET_CONFIG`) to test different system prompt postures.
- The `naive` configuration is a baseline support bot.
- The `nudged` configuration includes a lightweight system instruction asking the bot to be cautious of embedded commands. This successfully transformed the Attacker's exploit curve from a trivial Attempt-1 success to a realistic "fail-then-adapt" progression.

### 3. API & Infrastructure Management
- Re-routed the pipeline to execute entirely through Groq's API (`SENTINEL_MODE=dev`) via `litellm` using `llama-3.3-70b-versatile`.
- This decouples the extensive multi-attempt testing loops from the Gemini production quotas, saving costs and preventing hard rate limits on the primary model.

### 4. Comparative Evaluation Framework
- Built `compare_targets.py`, an automated benchmarking runner designed to systemically evaluate vulnerabilities.
- **Phase A**: Executes an exhaustive test without early-break logic to ensure all skills (especially the new high-severity ones) are tested sequentially.
- **Phase B**: Executes multiple, aggregated runs (currently configured for 2 runs) across both the `naive` and `nudged` configurations, calculating success rates and rendering a statistical `comparison_results.json` file.

---

### 5. Robust Benchmarking & Reporting
- Refactored `compare_targets.py` using `subprocess` to ensure complete crash resilience and isolate target state across multi-run benchmarks.
- Implemented robust pacing (30s sleep intervals) between API calls to successfully mitigate previous Groq rate-limit/TPM blockers.
- Built a zero-dependency Python script (`generate_report.py`) that consumes `attack_log.json` and `comparison_results.json` to output a fully self-contained HTML dashboard (`sentinel_report.html`).
- Enhanced the dashboard with an SVG severity timeline that visually color-codes exploits based on the specific `skill_used` (e.g., destructive actions in red, exfiltration in purple).
- Integrated the auto-generation of this report directly into the end of the `compare_targets.py` pipeline.

### 6. Finalized Documentation & Repository
- Completely updated `README.md` with Kaggle/course badges, a proof of concept disclaimer, key benchmark findings, and a feature summary of the new HTML report generator.
- Replaced the basic Mermaid diagram with a highly polished, custom `architecture.svg` vector graphic, correctly routing the Orchestrator/Attacker/Target/Judge workflow and verdict feedback loops.
- Fixed logging aggregation to correctly attribute and count all successful exploits per skill in multi-exploit runs.
- All code, reports, and graphics successfully committed and pushed to the remote GitHub repository.

### 7. API Wrapper & Containerization
- Built a minimal FastAPI application (`app.py`) to expose the benchmarking pipeline and reporting dashboard via HTTP endpoints (`/health`, `/run`, `/report`, `/results`).
- Containerized the entire framework using a `Dockerfile` based on `python:3.12-slim`, specifically tailored for zero-touch execution in Google Cloud Run.
- Hardened the environment configuration and fixed dependency management by enforcing `google-adk[extensions]` to ensure native `litellm` cross-provider support within the container.
- Verified local container execution with Uvicorn, confirming that all endpoints successfully interface with the Sentinel agentic workflow and mock filesystem.

### 8. Automated CI/CD & Deployment
- Set up a dedicated GCP IAM Service Account (`sentinel-deployer`) with granular permissions (`roles/run.admin`, `roles/storage.admin`, `roles/cloudbuild.builds.builder`, `roles/logging.viewer`).
- Created a GitHub Actions workflow (`deploy.yml`) to automatically build and deploy the container to Google Cloud Run on every push to the `master` branch.
- Resolved race conditions in the stateless Cloud Run environment by forcing the `POST /run` endpoint to generate the HTML report synchronously before returning, ensuring `GET /report` immediately serves the freshest data.

### 9. Real-Time UI Observability
- Refactored `orchestrator.py` and `app.py` to stream attack events asynchronously using Server-Sent Events (SSE) and an `asyncio.Queue`, enabling real-time visual tracking of the pipeline without blocking backend execution.
- Built a dynamic frontend (`dashboard.html`) featuring an animated 4-node SVG architecture map (Orchestrator -> Attacker -> Target -> Judge) that lights up step-by-step as payloads are executed and judged.
- Implemented a `/clear-log` endpoint and a minimal persistent navbar across the UI for seamless cross-navigation and rapid environment resetting between demo runs.
- Resolved key mismatches and edge cases (e.g., null Target responses escaping) in the `generate_report.py` logic, ensuring robust offline HTML generation even when the target strictly uses tool calls with no conversational output.
- Finalized Hybrid LLM routing (`dev` mode) where the heavy Attacker and Judge generation uses Groq while the Target stays native to Gemini (Google ADK) for authentic FastMCP tool binding, drastically reducing rate limits and 503 errors.

---

## 🚧 Current Status & Blockers

**Status**: 🟢 **Feature Complete & Demo Ready** 
Sentinel is now fully complete. The real-time SSE dashboard, hybrid LLM routing, and robust reporting mechanisms are all active and committed to the `dev` branch.

**Blockers**: 🔴 **GCP Billing Suspended**
The automated GitHub Actions CI/CD pipeline to Cloud Run is currently failing with a `403` error because the GCP project `sentinel-capstone-2026` has a disabled/closed billing account. The pipeline and code are correct; GCP billing must be reactivated manually in the console.

---

## 📝 Next Steps

1. **Reactivate GCP Billing**: Log into the Google Cloud Console, reactivate the billing account for `sentinel-capstone-2026`, and re-run the GitHub Action to push the latest dashboard features to Cloud Run.
2. **Record Demo**: Utilize the `/dashboard` UI and `/clear-log` endpoint to record a smooth, end-to-end 5-attempt attack visualization.
3. **Update Notebook Link**: Once the Kaggle notebook is published, update the placeholder Kaggle badge URL in `README.md` to point to the live notebook.
