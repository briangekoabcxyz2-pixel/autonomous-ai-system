from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATASET_PATH = Path("datasets/training_data.jsonl")
activity_log = []
teacher_instructions = []

@app.get("/status")
def get_status():
    return {"status": "online", "version": "2.0"}

@app.get("/logs")
def get_logs():
    logs = []
    if DATASET_PATH.exists():
        with open(DATASET_PATH) as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except:
                    pass
    return {"logs": logs}

@app.get("/benchmarks")
def get_benchmarks():
    logs = []
    if DATASET_PATH.exists():
        with open(DATASET_PATH) as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except:
                    pass
    total = len(logs)
    passed = sum(1 for l in logs if l.get("evaluation_score", 0) >= 1)
    accuracy = round((passed / total * 100), 1) if total > 0 else 0
    return {"total_tasks": total, "passed": passed, "accuracy": accuracy}

@app.get("/training")
def get_training():
    return {"status": "idle", "loss": None, "epoch": None, "examples": None, "checkpoint": None}

@app.get("/activity")
def get_activity():
    return {"activity": activity_log[-20:]}

@app.post("/activity")
def post_activity(data: dict):
    activity_log.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "message": data.get("message", "")
    })
    return {"ok": True}

@app.get("/instructions")
def get_instructions():
    return {"instructions": teacher_instructions}

@app.post("/instructions")
def post_instruction(data: dict):
    teacher_instructions.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "instruction": data.get("instruction", "")
    })
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
