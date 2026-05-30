# student/student.py
import anthropic
import os

class StudentModel:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_code(self, prompt: str) -> str:
        message = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text

if __name__ == "__main__":
    student = StudentModel(api_key=os.environ["ANTHROPIC_API_KEY"])
    output = student.generate_code("Write a Python function to add two numbers.")
    print(output)