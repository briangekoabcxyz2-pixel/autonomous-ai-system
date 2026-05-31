import os
import time
import json
import random
from pathlib import Path
from groq import Groq

DATASET_PATH = Path("datasets/training_data.jsonl")

client = Groq(api_key=os.environ["GROQ_API_KEY"])

TOPICS = [
    "Build a complete REST API with FastAPI including JWT authentication, database models with SQLAlchemy, input validation with Pydantic, error handling middleware, and unit tests with pytest",
    "Build a Python web scraper that handles pagination, rate limiting, retry logic, data cleaning, and saves results to both CSV and SQLite database",
    "Build a Python CLI tool with argparse that manages a local task database with CRUD operations, priority levels, due dates, and filtering",
    "Build a Python data pipeline that reads from multiple CSV files, cleans and validates data, performs aggregations, detects anomalies, and generates a summary report",
    "Build a Python class hierarchy for a banking system with accounts, transactions, interest calculation, overdraft protection, and full test coverage",
    "Build a Python async web crawler using aiohttp that crawls multiple URLs concurrently, extracts structured data, and handles errors gracefully",
    "Build a Python caching system with TTL expiry, LRU eviction, thread safety, and both in-memory and file-based backends",
    "Build a Python event system with publishers, subscribers, async event handling, error isolation, and event filtering",
    "Build a complete Python package with proper structure, setup.py, documentation, logging, and configuration management",
    "Build a Python monitoring system that tracks CPU, memory, disk usage, sends alerts when thresholds exceeded, and generates daily reports",
]

def research_topic(topic):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert Python teacher. Generate one specific, detailed coding task based on the topic."},
            {"role": "user", "content": f"Generate ONE specific Python coding task for a student based on: {topic}"}
        ],
        max_tokens=400
    )
    return response.choices[0].message.content

def get_student_response(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1024
    )
    return response.choices[0].message.content

def evaluate(prompt, output):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert Python teacher. Evaluate the student code and provide detailed corrections and improvements."},
            {"role": "user", "content": f"Task: {prompt}\n\nStudent output:\n{output}\n\nEvaluate thoroughly and provide corrections."}
        ],
        max_tokens=1024
    )
    correction = response.choices[0].message.content
    score = 1 if "error" not in output.lower() else 0
    return correction, score

def store(prompt, output, correction, score):
    record = {
        "prompt": prompt,
        "student_output": output,
        "teacher_correction": correction,
        "evaluation_score": score
    }
    with open(DATASET_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")

def count_records():
    if not DATASET_PATH.exists():
        return 0
    with open(DATASET_PATH) as f:
        return sum(1 for _ in f)

def run():
    print("[AAES] GitHub Actions run started!")
    topic = random.choice(TOPICS)
    
    try:
        print(f"[Teacher] Researching: {topic[:60]}...")
        prompt = research_topic(topic)
        print(f"[Teacher] Task generated.")

        output = get_student_response(prompt)
        print(f"[Student] Response received.")

        correction, score = evaluate(prompt, output)
        store(prompt, output, correction, score)

        total = count_records()
        print(f"[Dataset] Total records: {total} | Score: {score}")
        print("[AAES] Run complete!")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    run()
