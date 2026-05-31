import os
import time
import json
import requests
from pathlib import Path
from groq import Groq

DATASET_PATH = Path("datasets/training_data.jsonl")
TRAINING_THRESHOLD = 50

client = Groq(api_key=os.environ["GROQ_API_KEY"])

TOPICS = [
    "Build a complete REST API with FastAPI including JWT authentication, database models with SQLAlchemy, input validation with Pydantic, error handling middleware, and unit tests with pytest",
    "Build a Python web scraper that handles pagination, rate limiting, retry logic, proxy rotation, data cleaning, and saves results to both CSV and SQLite database",
    "Build a Python CLI tool with argparse that manages a local task database with CRUD operations, priority levels, due dates, filtering, and colorized terminal output",
    "Build a Python data pipeline that reads from multiple CSV files, cleans and validates data, performs aggregations, detects anomalies, and generates a summary report",
    "Build a Python class hierarchy for a banking system with accounts, transactions, interest calculation, overdraft protection, and full test coverage",
    "Build a Python async web crawler using aiohttp that crawls multiple URLs concurrently, extracts structured data, handles errors gracefully, and respects robots.txt",
    "Build a Python caching system with TTL expiry, LRU eviction, thread safety, statistics tracking, and both in-memory and file-based backends",
    "Build a Python event system with publishers, subscribers, async event handling, error isolation, event filtering, and a complete working example",
    "Build a complete Python package with proper structure, setup.py, documentation, logging, configuration management, and example usage",
    "Build a Python monitoring system that tracks CPU, memory, disk usage, sends alerts when thresholds exceeded, logs to file, and generates daily reports",
]

def post_activity(message):
    try:
        requests.post("http://localhost:8080/activity", json={"message": message}, timeout=2)
    except:
        pass

def get_student_response(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] Student failed: {e}")
        return None

def research_topic(topic):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert Python teacher. Research the given topic and generate one specific coding task for a student."},
            {"role": "user", "content": f"Research this topic and give me ONE specific Python coding task: {topic}"}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content

def evaluate(prompt, output):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert Python teacher. Evaluate the student code and provide detailed corrections."},
            {"role": "user", "content": f"Task: {prompt}\n\nStudent output:\n{output}\n\nEvaluate and correct."}
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

def run_loop():
    print("[AAES] Autonomous loop started!")
    topic_index = 0
    last_trained_at = count_records()

    while True:
        try:
            topic = TOPICS[topic_index % len(TOPICS)]
            topic_index += 1

            print(f"[Teacher] Researching: {topic}")
            post_activity(f"Researching: {topic}")

            prompt = research_topic(topic)
            print(f"[Teacher] Task generated.")
            post_activity(f"Task: {prompt[:80]}...")

            output = get_student_response(prompt)
            if not output:
                time.sleep(10)
                continue

            print(f"[Student] Response received.")
            post_activity(f"Student responded. Evaluating...")

            correction, score = evaluate(prompt, output)
            store(prompt, output, correction, score)

            total = count_records()
            print(f"[Dataset] Total records: {total} | Score: {score}")
            post_activity(f"Stored record #{total}. Score: {score}")

            if total - last_trained_at >= TRAINING_THRESHOLD:
                print(f"[Training] {TRAINING_THRESHOLD} new examples — time to fine-tune!")
                post_activity(f"Training triggered! {total} total records.")
                last_trained_at = total

            time.sleep(15)

        except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                print(f"[Rate Limit] Waiting 60 seconds...")
                post_activity("Rate limit hit. Waiting 60s...")
                time.sleep(60)
            else:
                print(f"[ERROR] {e}")
                time.sleep(10)

if __name__ == "__main__":
    run_loop()
