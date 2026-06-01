import os
import json
from pathlib import Path
from groq import Groq

try:
    from memory_store import get_memory_summary, add_topic
    MEMORY_ENABLED = True
except Exception as e:
    print(f"[Memory] Memory system unavailable: {e}")
    MEMORY_ENABLED = False
    def get_memory_summary(): return ""
    def add_topic(t, s): pass

DATASET_PATH = Path("datasets/training_data.jsonl")
client = Groq(api_key=os.environ["GROQ_API_KEY"])

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
    if avg_score >= 0.8 and total % 50 == 0 and total > 0:
        current_level = min(10, current_level + 1)
    return total, avg_score, current_level

def search_web(query):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a Python expert. Search your knowledge for real world examples and best practices. Return a concise summary of practical production code patterns."},
                {"role": "user", "content": f"Search for current best practices and real world examples for: {query}"}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[Search] Web search failed: {e}")
        return "Focus on practical Python best practices."

def generate_topic(level, avg_score, total):
    level_desc = LEVELS[level]
    memory_summary = get_memory_summary() if MEMORY_ENABLED else ""
    search_results = search_web(f"Python {level_desc} real world examples 2024")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"You are an expert Python teacher. Student is at level {level}/10. Average score: {round(avg_score*100)}%. Tasks completed: {total}. Real world patterns found: {search_results}. Memory of past lessons: {memory_summary}. Generate ONE specific coding topic. Avoid covered topics. Return ONLY the topic name."},
            {"role": "user", "content": f"Generate one specific Python coding topic for level {level}: {level_desc}"}
        ],
        max_tokens=100
    )
    return response.choices[0].message.content.strip(), search_results

def generate_task(topic, level, avg_score, search_results):
    difficulty = "straightforward" if avg_score < 0.5 else "moderately challenging" if avg_score < 0.8 else "advanced"
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"You are an expert Python teacher. Create ONE specific {difficulty} coding task for level {level}/10. Base it on these real world patterns: {search_results}. Return ONLY the task description."},
            {"role": "user", "content": f"Create a {difficulty} Python coding task about: {topic}"}
        ],
        max_tokens=400
    )
    return response.choices[0].message.content.strip()

def get_student_response(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1024
    )
    return response.choices[0].message.content

def evaluate(prompt, output, level, search_results):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"You are an expert Python teacher evaluating a level {level} student. Compare against these real world best practices: {search_results}. Score 0-10 on correctness, code quality, best practices, completeness. End with exactly: SCORE: X"},
            {"role": "user", "content": f"Task: {prompt}\n\nStudent output:\n{output}\n\nEvaluate against real world standards."}
        ],
        max_tokens=1024
    )
    correction = response.choices[0].message.content
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
    print("[AAES] Intelligent run with web search started!")
    total, avg_score, level = get_stats()
    print(f"[Stats] Total: {total} | Avg Score: {round(avg_score*100)}% | Level: {level}/10")
    try:
        print(f"[Teacher] Searching web for level {level} content...")
        topic, search_results = generate_topic(level, avg_score, total)
        print(f"[Teacher] Topic: {topic}")
        task = generate_task(topic, level, avg_score, search_results)
        print(f"[Teacher] Task generated from real world examples.")
        output = get_student_response(task)
        print(f"[Student] Response received.")
        correction, score = evaluate(task, output, level, search_results)
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
            print("[Rate Limit] Daily token limit reached. Exiting gracefully.")
            exit(0)
        print(f"[ERROR] {e}")
        raise

if __name__ == "__main__":
    run()
