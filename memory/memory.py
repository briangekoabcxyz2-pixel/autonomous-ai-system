# memory/memory.py
import chromadb
from pathlib import Path

class MemorySystem:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="memory/chroma_db")
        self.collection = self.client.get_or_create_collection("teacher_memory")

    def store(self, prompt: str, student_output: str, correction: str, score: int):
        self.collection.add(
            documents=[correction],
            metadatas=[{
                "prompt": prompt,
                "student_output": student_output,
                "score": score
            }],
            ids=[f"record_{self.collection.count()}"]
        )
        print("[Memory] Stored result in ChromaDB.")

    def retrieve(self, query: str, n=3):
        results = self.collection.query(
            query_texts=[query],
            n_results=n
        )
        print(f"[Memory] Retrieved {len(results['documents'][0])} relevant memories.")
        return results

if __name__ == "__main__":
    memory = MemorySystem()
    memory.store(
        prompt="Write a function to add two numbers.",
        student_output="def add(a, b): return a + b",
        correction="Add docstring and input validation.",
        score=1
    )
    results = memory.retrieve("function to add numbers")
    print(results)