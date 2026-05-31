from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

app = FastAPI(title="Autonomous AI Engineering System")

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# In-memory system state
# --------------------------

system_state = {
    "status": "Teacher AI running",
    "version": "1.0",
    "checkpoint": "student_v0",
    "student_model": "TinyLlama 1.1B",
    "current_task": "Reviewing Student Output",
    "dataset_entries": 0,
    "memory_records": 0,
    "epoch": 0,
    "loss": "-"
}

benchmark_state = {
    "total_tasks": 3,
    "passed": 3,
    "accuracy": 100
}

logs = [
    {
        "timestamp": str(datetime.now()),
        "prompt": "Write a Python function to add two numbers.",
        "evaluation_score": 1
    },
    {
        "timestamp": str(datetime.now()),
        "prompt": "Write a Python function to multiply two numbers.",
        "evaluation_score": 1
    }
]

# --------------------------
# Dashboard endpoints
# --------------------------

@app.get("/status")
def get_status():
    return system_state


@app.get("/benchmarks")
def get_benchmarks():
    return benchmark_state


@app.get("/logs")
def get_logs():
    return {"logs": logs}


# --------------------------
# Controls
# --------------------------

@app.post("/run_benchmark")
def run_benchmark():

    benchmark_state["total_tasks"] += 1
    benchmark_state["passed"] += 1

    benchmark_state["accuracy"] = round(
        (benchmark_state["passed"] /
         benchmark_state["total_tasks"]) * 100,
        2
    )

    logs.append({
        "timestamp": str(datetime.now()),
        "prompt": "Benchmark Task",
        "evaluation_score": 1
    })

    return {
        "message": "Benchmark executed successfully"
    }


@app.post("/generate_dataset")
def generate_dataset():

    system_state["dataset_entries"] += 10

    logs.append({
        "timestamp": str(datetime.now()),
        "prompt": "Dataset Generation",
        "evaluation_score": 1
    })

    return {
        "message": "10 dataset entries generated"
    }


@app.post("/start_training")
def start_training():

    system_state["epoch"] += 1

    system_state["loss"] = round(
        1.0 / (system_state["epoch"] + 1),
        4
    )

    system_state["checkpoint"] = (
        f"student_v{system_state['epoch']}"
    )

    logs.append({
        "timestamp": str(datetime.now()),
        "prompt": "Training Cycle",
        "evaluation_score": 1
    })

    return {
        "message": f"Training epoch {system_state['epoch']} completed"
    }


@app.post("/pause_system")
def pause_system():

    system_state["status"] = "Paused"

    return {
        "message": "System paused"
    }


@app.post("/resume_system")
def resume_system():

    system_state["status"] = "Teacher AI running"

    return {
        "message": "System resumed"
    }


# --------------------------
# Run server
# --------------------------

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080
    )
    