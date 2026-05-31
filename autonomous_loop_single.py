import os
import json
import random
from pathlib import Path
from groq import Groq

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

def generate_topic(level, avg_score, total):
    level_desc = LEVELS[level]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are an expert Python teacher designing a curriculum.
Your student is at level """ + str(level) + """ out of 10.
Recent average score: """ + str(round(avg_score * 100)) + """%.
Total tasks completed: """ + str(total) + """.
Generate ONE specific coding topic that is appropriate for this level.
The topic should be slightly challenging but achievable.
Return ONLY the topic name, nothing else."""
            },
            {
                "role": "user",
                "content": f"Generate one specific Python coding topic for level {level}: {level_desc}"
            }
        ],
        max_tokens=100
    )
    return response.choices[0].message.content.strip()

def generate_task(topic, level, avg_score):
    difficulty = "straightforward" if avg_score < 0.5 else "moderately challenging" if avg_score < 0.8 else "advanced"
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"""You are an expert Python teacher.
Create ONE specific {difficulty} coding task for a student at level {level} out of 10.
The task should be detailed, practical, and build real skills.
Return ONLY the task description, nothing else."""
            },
            {
                "role": "user",
                "content": f"Create a {difficulty} Python coding task about: {topic}"
            }
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

def evaluate(prompt, output, level):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"""You are an expert Python teacher evaluating a level {level} student.
Score the code from 0 to 10 based on:
- Correctness
- Code quality
- Best practices
- Completeness
Be detailed in your corrections.
End your response with exactly: SCORE: X (where X is 0-10)"""
            },
            {
                "role": "user",
                "content": f"Task: {prompt}\n\nStudent output:\n{output}\n\nEvaluate and provide corrections."
            }
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
    record = {
        "prompt": prompt,
        "student_output": output,
        "teacher_correction": correction,
        "evaluation_score": score,
        "level": level,
        "topic": topic,
    }
    with open(DATASET_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")

def run():
    print("[AAES] Intelligent run started!")
    total, avg_score, level = get_stats()
    print(f"[Stats] Total: {total} | Avg Score: {round(avg_score*100)}% | Level: {level}/10")

    try:
        topic = generate_topic(level, avg_score, total)
        print(f"[Teacher] Topic: {topic}")

        task = generate_task(topic, level, avg_score)
        print(f"[Teacher] Task generated.")

        output = get_student_response(task)
        print(f"[Student] Response received.")

        correction, score = evaluate(task, output, level)
        store(task, output, correction, score, level, topic)

        total_new = total + 1
        print(f"[Dataset] Total: {total_new} | Score: {round(score*10)}/10 | Level: {level}/10")

        if score >= 0.8:
            print(f"[Progress] Student performing well at level {level}!")
        else:
            print(f"[Progress] Student needs more practice at level {level}.")

        print("[AAES] Run complete!")

    except Exception as e:
        print(f"[ERROR] {e}")
        raise

if __name__ == "__main__":
    run()
