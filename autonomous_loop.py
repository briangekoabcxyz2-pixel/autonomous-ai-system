import os
import time
import json
import requests
from pathlib import Path
from groq import Groq

STUDENT_API_URL = "https://brianageko1--aaes-student-generate.modal.run"
DATASET_PATH = Path("datasets/training_data.jsonl")
TRAINING_THRESHOLD = 10

SEARCH_TOPICS = [
    "python list comprehension examples",
    "python error handling best practices",
    "python file handling examples",
    "python class and objects tutorial",
    "python recursion examples",
    "python sorting algorithms",
    "python API requests tutorial",
    "python decorators explained",
    "python generators examples",
    "python unit testing pytest",
]

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def research_topic(topic):
    print(f"[Teacher] Researching: {topic}")
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a Python expert. Summarize key concepts and provide 2-3 code examples for the given topic. Be concise."},
                {"role": "user", "content": f"Explain and show examples for: {topic}"}
            ],
            max_tokens=500
        )
        print(f"[Teacher] Research complete.")
        return response.choices[0].message.content
    except Exception as e:
        if "429" in str(e) or "rate_limit" in str(e):
            print("[Rate Limit] Waiting 10 minutes...")
            time.sleep(600)
            return None
        print(f"[ERROR] Research failed: {e}")
        return None

def generate_task(topic, content):
    print("[Teacher] Generating task...")
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert Python teacher. Based on the content provided, create ONE specific Python coding task for a student. Return ONLY the task description, nothing else. Keep it under 2 sentences."},
                {"role": "user", "content": f"Topic: {topic}\n\nContent:\n{content}\n\nCreate one coding task:"}
            ],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        if "429" in str(e) or "rate_limit" in str(e):
            print("[Rate Limit] Waiting 10 minutes...")
            time.sleep(600)
            return None
        print(f"[ERROR] Task generation failed: {e}")
        return None


def post_activity(message):
    try:
        requests.post("http://localhost:8080/activity", json={"message": message}, timeout=2)
    except:
        pass

def get_student_response(prompt):
    try:
        response = requests.post(STUDENT_API_URL, json={"prompt": prompt}, timeout=120)
        return response.json()["response"]
    except Exception as e:
        print(f"[ERROR] Student failed: {e}")
        return None

def evaluate(prompt, output):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert Python teacher. Evaluate the student code and provide corrections."},
                {"role": "user", "content": f"Task: {prompt}\n\nStudent output:\n{output}\n\nEvaluate and correct."}
            ]
        )
        correction = response.choices[0].message.content
        score = 1 if "error" not in output.lower() else 0
        return correction, score
    except Exception as e:
        if "429" in str(e) or "rate_limit" in str(e):
            print("[Rate Limit] Waiting 10 minutes...")
            time.sleep(600)
            return "Rate limit - skipped", 0
        print(f"[ERROR] Evaluate failed: {e}")
        return "Error", 0

def store(prompt, output, correction, score):
    record = {"prompt": prompt, "student_output": output, "teacher_correction": correction, "evaluation_score": score}
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
        topic = SEARCH_TOPICS[topic_index % len(SEARCH_TOPICS)]
        topic_index += 1

        content = research_topic(topic)
        if not content:
            continue

        prompt = generate_task(topic, content)
        if not prompt:
            continue

        print(f"\n[Teacher] Task: {prompt}")
        output = get_student_response(prompt)
        if not output:
            time.sleep(5)
            continue

        print(f"[Student] Response received.")
        post_activity(f"Student responded. Evaluating...")
        correction, score = evaluate(prompt, output)
        store(prompt, output, correction, score)

        total = count_records()
        print(f"[Dataset] Total records: {total} | Score: {score}")
        post_activity(f"Stored record #{total}. Score: {score}")

        if total - last_trained_at >= TRAINING_THRESHOLD:
            print(f"[Training] Dataset grew by {TRAINING_THRESHOLD}. Time to fine-tune in Colab!")
            last_trained_at = total

        time.sleep(15)

if __name__ == "__main__":
    run_loop()