import os
import json
import time
import threading
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
DAILY_TARGET = 500
MAX_RUNTIME_SECONDS = 20000  # ~5.5 hours, safe under GitHub 6hr limit
write_lock = threading.Lock()
stats_lock = threading.Lock()

groq_keys = []
for key_name in ["GROQ_API_KEY", "GROQ_API_KEY_2", "GROQ_API_KEY_3"]:
    key = os.environ.get(key_name)
    if key:
        groq_keys.append(key)

print(f"[AAES] Loaded {len(groq_keys)} Groq keys for parallel use")

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
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                print(f"[Key {key_index+1}] Rate limited, waiting 60s...")
                time.sleep(60)
            else:
                print(f"[Key {key_index+1}] Error: {e}")
                time.sleep(10)
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
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                print(f"[Student Key {key_index+1}] Rate limited, waiting 60s...")
                time.sleep(60)
            else:
                time.sleep(10)
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
    with write_lock:
        DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DATASET_PATH, "a") as f:
            f.write(json.dumps(record) + "\n")

def run_one(key_index, run_id):
    try:
        with stats_lock:
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
            print(f"[Worker {key_index+1}] Run {run_id}: topic generation failed, skipping")
            return

        task_prompt = f"""You are an expert Python teacher.
Create ONE specific {difficulty} coding task for a student at level {level}/10.
Topic: {topic}. Level focus: {level_desc}
The task should reflect actual production code patterns.
Return ONLY the task description."""

        task = ask_ai(task_prompt, key_index, max_tokens=400)
        if not task:
            print(f"[Worker {key_index+1}] Run {run_id}: task generation failed, skipping")
            return

        output = ask_student(task, key_index)
        if not output:
            print(f"[Worker {key_index+1}] Run {run_id}: student response failed, skipping")
            return

        eval_prompt = f"""You are an expert Python teacher evaluating a level {level}/10 student.
Task: {task}
Student output: {output}
Evaluate on correctness, code quality, best practices, completeness.
Provide detailed corrections.
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
        print(f"[Worker {key_index+1}] Run {run_id} complete | Score: {round(score*10)}/10 | Level: {level} | Total: {current_total}")

    except Exception as e:
        print(f"[Worker {key_index+1}] Run {run_id} error: {e}")

def worker_loop(key_index, target, start_time):
    run_id = 0
    while True:
        elapsed = time.time() - start_time
        if elapsed > MAX_RUNTIME_SECONDS:
            print(f"[Worker {key_index+1}] Max runtime reached, stopping.")
            break
        current = get_total()
        if current >= target:
            print(f"[Worker {key_index+1}] Target {target} reached ({current} records), stopping.")
            break
        run_id += 1
        run_one(key_index, run_id)
        time.sleep(2)  # small gap between calls per key

if __name__ == "__main__":
    start_time = time.time()
    initial_total = get_total()
    target = initial_total + DAILY_TARGET
    print(f"[AAES Batch] Starting | Current: {initial_total} | Target: {target} | Workers: {len(groq_keys)}")

    threads = []
    for i in range(len(groq_keys)):
        t = threading.Thread(target=worker_loop, args=(i, target, start_time))
        t.daemon = True
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    final_total = get_total()
    print(f"[AAES Batch] Complete | Final total: {final_total} | Added: {final_total - initial_total}")
