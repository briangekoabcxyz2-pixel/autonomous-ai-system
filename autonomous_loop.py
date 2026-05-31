import os
import time
import json
import requests
from pathlib import Path
from groq import Groq

STUDENT_API_URL = "https://brianageko1--aaes-student-generate.modal.run"
DATASET_PATH = Path("datasets/training_data.jsonl")
TRAINING_THRESHOLD = 10  # trigger training after every 10 new examples

client = Groq(api_key=os.environ["GROQ_API_KEY"])

TASKS = [
    "Write a Python function to reverse a string.",
    "Write a Python function to check if a number is prime.",
    "Write a Python function to find the factorial of a number.",
    "Write a Python function to flatten a nested list.",
    "Write a Python function to count word frequency in a string.",
    "Write a Python function to merge two sorted lists.",
    "Write a Python function to find duplicates in a list.",
    "Write a Python function to convert Celsius to Fahrenheit.",
    "Write a Python function to check if a string is a palindrome.",
    "Write a Python function to find the second largest number in a list.",
]

def get_student_response(prompt):
    try:
        response = requests.post(
            STUDENT_API_URL,
            json={"prompt": prompt},
            headers={"ngrok-skip-browser-warning": "true"},
            timeout=120
        )
        return response.json()["response"]
    except Exception as e:
        print(f"[ERROR] Student failed: {e}")
        return None

def evaluate(prompt, output):
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
    task_index = 0
    last_trained_at = count_records()

    while True:
        prompt = TASKS[task_index % len(TASKS)]
        task_index += 1

        print(f"\n[Teacher] Task: {prompt}")
        output = get_student_response(prompt)
        if not output:
            time.sleep(5)
            continue

        print(f"[Student] Response received.")
        correction, score = evaluate(prompt, output)
        store(prompt, output, correction, score)

        total = count_records()
        print(f"[Dataset] Total records: {total} | Score: {score}")

        if total - last_trained_at >= TRAINING_THRESHOLD:
            print(f"[Training] Dataset grew by {TRAINING_THRESHOLD}. Time to fine-tune!")
            print("[Training] Go to Colab and run the training cell.")
            last_trained_at = total

        time.sleep(10)

if __name__ == "__main__":
    run_loop()
