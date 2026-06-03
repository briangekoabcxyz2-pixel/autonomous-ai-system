import os
import json
import time
from pathlib import Path
from groq import Groq

try:
    from memory_store import get_memory_summary, add_topic
    MEMORY_ENABLED = True
except Exception as e:
    print(f"[Memory] Unavailable: {e}")
    MEMORY_ENABLED = False
    def get_memory_summary(): return ""
    def add_topic(t, s): pass

DATASET_PATH = Path("datasets/training_data.jsonl")
DAILY_TARGET = 100

groq_keys = []
for key_name in ["GROQ_API_KEY", "GROQ_API_KEY_2", "GROQ_API_KEY_3"]:
    key = os.environ.get(key_name)
    if key:
        groq_keys.append(key)

print(f"[AAES] Loaded {len(groq_keys)} Groq keys (rotating)")

LEVELS = {
    1: "basic Python functions, variables, loops, and conditionals",
    2: "Python classes, objects, inheritance, and encapsulation",
    3: "error handling, file operations, and input validation",
    4: "REST APIs with FastAPI, routing, and request handling",
    5: "database operations with SQLAlchemy and data modeling",
    6: "async programming, concurrency, and background tasks",
    7: "testing with pytest, mocking, and test coverage",
    8: "complete backend systems with authentication and authorization",
    9: "frontend integration, HTML, CSS, JavaScript, and React components",
    10: "full stack web applications with deployment and production config",
}

def get_client(key_index):
    return Groq(api_key=groq_keys[key_index % len(groq_keys)])

def ask_ai(prompt, key_index, max_tokens=1024):
    for attempt in range(3):
        try:
            client = get_client(key_index)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            time.sleep(3)
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                print(f"[Key {key_index+1}] Rate limited, waiting 30s...")
                time.sleep(30)
            else:
                print(f"[Key {key_index+1}] Error: {e}")
                time.sleep(5)
    return None

def ask_student(prompt, key_index):
    for attempt in range(3):
        try:
            client = get_client(key_index)
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024
            )
            time.sleep(3)
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                print(f"[Student Key {key_index+1}] Rate limited, waiting 30s...")
                time.sleep(30)
            else:
                time.sleep(5)
    return None

def get_total():
    if not DATASET_PATH.exists():
        return 0
    with open(DATASET_PATH) as f:
        return sum(1 for line in f if line.strip())

def get_stats():
    if not DATASET_PATH.exists():
        DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
        return 0, 0, 1
    records = []
    with open(DATASET_PATH) as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except:
                pass
    if not records:
        return 0, 0, 1
    total = len(records)
    recent = records[-20:]
    avg_score = sum(r.get("evaluation_score", 0) for r in recent) / len(recent)
    current_level = min(10, max(1, (total // 50) + 1))
    return total, avg_score, current_level

def store_record(prompt, output, correction, score, level, topic):
    record = {
        "prompt": prompt,
        "student_output": output,
        "teacher_correction": correction,
        "evaluation_score": score,
        "level": level,
        "topic": topic
    }
    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATASET_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")

def run_one(run_id, key_index):
    total, avg_score, level = get_stats()
    level_desc = LEVELS[level]
    memory_summary = get_memory_summary() if MEMORY_ENABLED else ""
    difficulty = "straightforward" if avg_score < 0.5 else "moderately challenging" if avg_score < 0.8 else "advanced"

    topic_prompt = f"""You are an expert Python teacher designing a curriculum.
Student level: {level}/10. Average score: {round(avg_score*100)}%. Tasks completed: {total}.
Level focus: {level_desc}. Memory of past lessons: {memory_summary}
Generate ONE specific coding topic. Avoid repeating covered topics. Return ONLY the topic name."""

    topic = ask_ai(topic_prompt, key_index, max_tokens=100)
    if not topic:
        print(f"[Run {run_id}] Topic generation failed, skipping")
        return False

    task_prompt = f"""You are an expert Python teacher.
Create ONE specific {difficulty} coding task for a student at level {level}/10.
Topic: {topic}. Level focus: {level_desc}
Return ONLY the task description."""

    task = ask_ai(task_prompt, key_index, max_tokens=400)
    if not task:
        print(f"[Run {run_id}] Task generation failed, skipping")
        return False

    output = ask_student(task, key_index)
    if not output:
        print(f"[Run {run_id}] Student response failed, skipping")
        return False

    eval_prompt = f"""You are an expert Python teacher evaluating a level {level}/10 student.
Task: {task}
Student output: {output}
Evaluate correctness, code quality, best practices, completeness.
End with exactly: SCORE: X (where X is 0-10)"""

    correction = ask_ai(eval_prompt, key_index, max_tokens=1024)
    if not correction:
        correction = "Evaluation unavailable."
        score = 0.5
    else:
        try:
            score_line = [l for l in correction.split("\n") if "SCORE:" in l][-1]
            score = int(score_line.split("SCORE:")[-1].strip().split()[0]) / 10
        except:
            score = 0.5

    store_record(task, output, correction, score, level, topic)
    add_topic(topic, score)

    current_total = get_total()
    print(f"[Run {run_id}] Complete | Score: {round(score*10)}/10 | Level: {level} | Total: {current_total} | Key: {key_index+1}")
    return True

if __name__ == "__main__":
    start_time = time.time()
    initial_total = get_total()
    target = initial_total + DAILY_TARGET
    print(f"[AAES] Starting | Current: {initial_total} | Target: {target} | Keys: {len(groq_keys)}")

    run_id = 0
    key_index = 0
    succeeded = 0
    failed = 0

    while get_total() < target:
        elapsed = time.time() - start_time
        if elapsed > 20000:
            print("[AAES] Max runtime reached, stopping.")
            break
        run_id += 1
        result = run_one(run_id, key_index)
        if result:
            succeeded += 1
        else:
            failed += 1
        key_index = (key_index + 1) % len(groq_keys)

    final_total = get_total()
    print(f"[AAES] Complete | Final: {final_total} | Added: {final_total - initial_total} | Success: {succeeded} | Failed: {failed}")
