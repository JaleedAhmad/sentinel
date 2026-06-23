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

---

## 🚧 Current Status & Blockers

**Status**: 🟢 **Completed & Synced** 
Sentinel is now feature-complete. The pipeline runs cleanly, aggregates statistical benchmarks without crashing, automatically generates polished security reports, and is fully documented on GitHub. 

**Blockers**: None. Previous API token limits have been successfully circumvented via pacing and subprocess isolation.

---

## 📝 Next Steps

1. **Update Notebook Link**: Once the Kaggle notebook is published, update the placeholder Kaggle badge URL in `README.md` to point to the live notebook.
2. **Review Output**: Share `sentinel_report.html` or the GitHub repo as part of the final course submission/presentation.
