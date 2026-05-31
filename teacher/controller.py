# teacher/controller.py
from pathlib import Path
import json
import os
import requests
from groq import Groq

STUDENT_API_URL = "https://brianageko1--aaes-student-generate.modal.run"

class TeacherController:
    def __init__(self):
        self.datasets_path = Path("datasets/training_data.jsonl")
        self.checkpoints_path = Path("checkpoints/")
        self.logs_path = Path("logs/")
        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])

    def assign_task(self, prompt: str):
        print(f"[Teacher] Assigning task to Student: {prompt}")
        response = requests.post(
            f"{STUDENT_API_URL}/generate",
            json={"prompt": prompt},
            headers={"ngrok-skip-browser-warning": "true"}
        )
        student_output = response.json()["response"]
        print(f"[Student] Response received.")
        return student_output

    def evaluate_student(self, prompt: str, student_output: str):
        print("[Teacher] Evaluating student output...")
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Python teacher. Evaluate the student's code, identify any issues, and provide a corrected version with explanation."
                },
                {
                    "role": "user",
                    "content": f"Task: {prompt}\n\nStudent output:\n{student_output}\n\nEvaluate this code and provide corrections if needed."
                }
            ]
        )
        correction = response.choices[0].message.content
        score = 1 if "error" not in student_output.lower() else 0
        print(f"[Teacher] Evaluation complete. Score: {score}")
        return correction, score

    def store_result(self, prompt: str, student_output: str, correction: str, score: int):
        record = {
            "prompt": prompt,
            "student_output": student_output,
            "teacher_correction": correction,
            "evaluation_score": score
        }
        with open(self.datasets_path, "a") as f:
            f.write(json.dumps(record) + "\n")
        print("[Teacher] Stored result in dataset.")

if __name__ == "__main__":
    teacher = TeacherController()
    prompt = "Write a Python function to multiply two numbers."
    student_output = teacher.assign_task(prompt)
    print(f"\n[Student Output]\n{student_output}")
    correction, score = teacher.evaluate_student(prompt, student_output)
    print(f"\n[Teacher Correction]\n{correction}")
    teacher.store_result(prompt, student_output, correction, score)