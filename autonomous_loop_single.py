import os
import json
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

# Load all available Groq keys for rotation
groq_keys = []
for key_name in ["GROQ_API_KEY", "GROQ_API_KEY_2", "GROQ_API_KEY_3"]:
    key = os.environ.get(key_name)
    if key:
        groq_keys.append(key)

groq_key_index = [0]
print(f"[AI] Groq loaded with {len(groq_keys)} API keys for rotation")

def get_groq_client():
    return Groq(api_key=groq_keys[groq_key_index[0] % len(groq_keys)])

def rotate_groq_key():
    groq_key_index[0] += 1
    if groq_key_index[0] >= len(groq_keys):
        print("[Rate Limit] All Groq keys exhausted. Exiting gracefully.")
        exit(0)
    print(f"[Rotation] Switching to Groq key {groq_key_index[0] + 1} of {len(groq_keys)}")

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

def ask_ai(prompt, max_tokens=1024):
    for attempt in range(len(groq_keys)):
        try:
            client = get_groq_client()
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                rotate_groq_key()
            else:
                raise
    print("[Rate Limit] All Groq keys exhausted. Exiting gracefully.")
    exit(0)

def ask_student(prompt):
    for attempt in range(len(groq_keys)):
        try:
            client = get_groq_client()
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                rotate_groq_key()
            else:
                raise
    print("[Rate Limit] All Groq keys exhausted. Exiting gracefully.")
    exit(0)

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

def generate_topic(level, avg_score, total):
    level_desc = LEVELS[level]
    memory_summary = get_memory_summary() if MEMORY_ENABLED else ""
    prompt = f"""You are an expert Python teacher designing a curriculum.
Student level: {level}/10. Average score: {round(avg_score*100)}%. Tasks completed: {total}.
Level focus: {level_desc}.
Memory of past lessons: {memory_summary}
Generate ONE specific coding topic. Avoid topics already covered. Return ONLY the topic name."""
    return ask_ai(prompt, max_tokens=100)

def generate_task(topic, level, avg_score):
    level_desc = LEVELS[level]
    difficulty = "straightforward" if avg_score < 0.5 else "moderately challenging" if avg_score < 0.8 else "advanced"
    prompt = f"""You are an expert Python teacher.
Create ONE specific {difficulty} coding task for a student at level {level}/10.
Topic: {topic}
Level focus: {level_desc}
The task should reflect actual production code patterns.
Return ONLY the task description."""
    return ask_ai(prompt, max_tokens=400)

def evaluate(prompt, output, level):
    eval_prompt = f"""You are an expert Python teacher evaluating a level {level}/10 student.
Task: {prompt}
Student output: {output}
Evaluate on correctness, code quality, best practices, completeness.
Provide detailed corrections.
End with exactly: SCORE: X (where X is 0-10)"""
    correction = ask_ai(eval_prompt, max_tokens=1024)
    try:
        score_line = [l for l in correction.split("\n") if "SCORE:" in l][-1]
        score = int(score_line.split("SCORE:")[-1].strip().split()[0]) / 10
    except:
        score = 1 if "error" not in output.lower() else 0
    return correction, score

def store(prompt, output, correction, score, level, topic):
    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {"prompt": prompt, "student_output": output, "teacher_correction": correction, "evaluation_score": score, "level": level, "topic": topic}
    with open(DATASET_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")

def run():
    print("[AAES] Intelligent run started - 3 Groq keys rotating!")
    total, avg_score, level = get_stats()
    print(f"[Stats] Total: {total} | Avg Score: {round(avg_score*100)}% | Level: {level}/10")
    try:
        print(f"[Teacher] Generating topic for level {level}...")
        topic = generate_topic(level, avg_score, total)
        print(f"[Teacher] Topic: {topic}")
        task = generate_task(topic, level, avg_score)
        print(f"[Teacher] Task generated.")
        output = ask_student(task)
        print(f"[Student] Response received.")
        correction, score = evaluate(task, output, level)
        store(task, output, correction, score, level, topic)
        add_topic(topic, score)
        total_new = total + 1
        print(f"[Dataset] Total: {total_new} | Score: {round(score*10)}/10 | Level: {level}/10")
        print(f"[Memory] Topic saved: {topic}")
        if score >= 0.8:
            print(f"[Progress] Student performing well at level {level}!")
        else:
            print(f"[Progress] Student needs more practice at level {level}.")
        print("[AAES] Run complete!")
    except Exception as e:
        if "429" in str(e) or "rate_limit" in str(e).lower():
            print("[Rate Limit] Exiting gracefully.")
            exit(0)
        print(f"[ERROR] {e}")
        raise

if __name__ == "__main__":
    for i in range(10):
        print(f"\n[AAES] Starting run {i+1} of 10...")
        run()
