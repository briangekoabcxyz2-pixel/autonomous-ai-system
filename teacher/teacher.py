import os
import json
from datetime import datetime
from groq import Groq

DATASET_FILE = "datasets/training_data.jsonl"
LOG_FILE = "logs/teacher_logs.json"

class TeacherAI:
    def __init__(self):
        self.client = Groq(
            api_key=os.environ["GROQ_API_KEY"]
        )

        # Current Groq model
        self.model = "llama-3.3-70b-versatile"

    def ask(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert AI software engineering teacher. "
                        "Generate coding tasks, evaluate student answers, "
                        "and create training examples."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=2048
        )

        return response.choices[0].message.content

    def generate_task(self):
        prompt = """
Generate one Python programming exercise.

Requirements:
- Beginner to intermediate difficulty
- Practical coding task
- Clear instructions

Return only the task description.
"""
        return self.ask(prompt)

    def generate_solution(self, task):
        prompt = f"""
Solve the following programming task:

{task}

Return only the Python code.
"""
        return self.ask(prompt)

    def evaluate_student(self, task, student_output):
        prompt = f"""
Task:
{task}

Student Output:
{student_output}

Evaluate correctness.

Return ONLY a number between 0 and 1.
"""
        result = self.ask(prompt)

        try:
            return float(result.strip())
        except:
            return 0.0

    def save_training_example(self, task, solution):
        os.makedirs("datasets", exist_ok=True)

        record = {
            "timestamp": datetime.now().isoformat(),
            "prompt": task,
            "completion": solution
        }

        with open(DATASET_FILE, "a") as f:
            f.write(json.dumps(record) + "\n")

    def log(self, message):
        os.makedirs("logs", exist_ok=True)

        entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message
        }

        logs = []

        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r") as f:
                    logs = json.load(f)
            except:
                logs = []

        logs.append(entry)

        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)

    def run_cycle(self):
        print("\nGenerating task...\n")

        task = self.generate_task()

        print("TASK:")
        print(task)

        print("\nGenerating reference solution...\n")

        solution = self.generate_solution(task)

        print("SOLUTION:")
        print(solution)

        self.save_training_example(task, solution)

        self.log(
            f"Generated training example for task: {task[:100]}"
        )

        print("\nSaved to dataset.")
        print("Logged successfully.")

if __name__ == "__main__":
    teacher = TeacherAI()
    teacher.run_cycle()