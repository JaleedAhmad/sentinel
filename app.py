import os
import json
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import Optional

from orchestrator import run_attack_pipeline
from compare_targets import run_phase_b
from generate_report import generate_report

app = FastAPI(title="Sentinel Framework API")

class RunRequest(BaseModel):
    mode: str = "dev"
    config: str = "naive"

class CompareRequest(BaseModel):
    mode: str = "dev"

@app.get("/")
def root():
    return RedirectResponse(url="/report")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "mode": os.environ.get("SENTINEL_MODE", "dev")
    }

@app.post("/run")
async def run_pipeline_endpoint(req: RunRequest):
    os.environ["SENTINEL_MODE"] = req.mode
    os.environ["SENTINEL_TARGET_CONFIG"] = req.config
    
    # Remove existing summary.json to ensure we read the new one
    if os.path.exists("summary.json"):
        os.remove("summary.json")
    
    # Execute the attack pipeline natively using await
    await run_attack_pipeline()
    
    # Regenerate report synchronously
    generate_report("attack_log.json", "comparison_results.json", "sentinel_report.html")
    
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

@app.post("/compare")
async def compare_endpoint(req: CompareRequest):
    os.environ["SENTINEL_MODE"] = req.mode
    
    # run_phase_b is synchronous, so run it in a threadpool to avoid blocking
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_phase_b)
    
    try:
        with open("comparison_results.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "comparison_results.json not found. Run Phase B first."}

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

@app.get("/stream")
async def stream_pipeline():
    queue = asyncio.Queue()

    async def run():
        await run_attack_pipeline(event_queue=queue)
        generate_report("attack_log.json", "comparison_results.json", "sentinel_report.html")

    asyncio.create_task(run())

    async def event_generator():
        while True:
            event = await queue.get()
            yield f"data: {json.dumps(event)}\n\n"
            if event.get("type") == "pipeline_complete":
                break

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/dashboard")
async def dashboard():
    return FileResponse("dashboard.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
