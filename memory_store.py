import json
from pathlib import Path

MEMORY_PATH = Path("memory/teacher_memory.json")

def load_memory():
    if not MEMORY_PATH.exists():
        return {"topics_covered": [], "weak_areas": [], "total_runs": 0}
    with open(MEMORY_PATH) as f:
        return json.load(f)

def save_memory(memory):
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_PATH, "w") as f:
        json.dump(memory, f, indent=2)

def get_covered_topics():
    memory = load_memory()
    return memory.get("topics_covered", [])

def add_topic(topic, score):
    memory = load_memory()
    memory["topics_covered"].append(topic)
    # keep last 100 topics only
    memory["topics_covered"] = memory["topics_covered"][-100:]
    if score < 0.5:
        memory["weak_areas"].append(topic)
        memory["weak_areas"] = memory["weak_areas"][-20:]
    memory["total_runs"] = memory.get("total_runs", 0) + 1
    save_memory(memory)

def get_memory_summary():
    memory = load_memory()
    topics = memory.get("topics_covered", [])
    weak = memory.get("weak_areas", [])
    total = memory.get("total_runs", 0)
    summary = f"Total runs: {total}. "
    if topics:
        summary += f"Recently covered: {', '.join(topics[-5:])}. "
    if weak:
        summary += f"Weak areas needing review: {', '.join(weak[-3:])}. "
    return summary
