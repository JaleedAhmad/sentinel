import os
import json
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional

from orchestrator import run_attack_pipeline

app = FastAPI(title="Sentinel Framework API")

class RunRequest(BaseModel):
    mode: str = "dev"
    config: str = "naive"

@app.get("/health")
def health():
    return {
        "status": "ok",
        "mode": os.environ.get("SENTINEL_MODE", "dev")
    }

@app.post("/run")
def run_pipeline_endpoint(req: RunRequest):
    os.environ["SENTINEL_MODE"] = req.mode
    os.environ["SENTINEL_TARGET_CONFIG"] = req.config
    
    # Remove existing summary.json to ensure we read the new one
    if os.path.exists("summary.json"):
        os.remove("summary.json")
    
    # Execute the attack pipeline synchronously using asyncio.run()
    asyncio.run(run_attack_pipeline())
    
    if os.path.exists("summary.json"):
        with open("summary.json", "r") as f:
            summary = json.load(f)
    else:
        summary = {}
        
    summary_resp = {
        "total_attempts": summary.get("total_attempts", 0),
        "successful_exploits": summary.get("successful_exploits", 0),
        "max_severity": summary.get("max_severity", 0),
        "skills_triggered": list(summary.get("success_rate_by_skill", {}).keys())
    }
    
    return summary_resp

@app.get("/report", response_class=HTMLResponse)
def get_report():
    try:
        with open("sentinel_report.html", "r") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return HTMLResponse("<h1>Report not generated yet. Run the pipeline first.</h1>", status_code=404)

@app.get("/results")
def get_results():
    try:
        with open("comparison_results.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "comparison_results.json not found. Run Phase B first."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
