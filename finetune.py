import os
import json
from pathlib import Path
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from trl import SFTTrainer
import torch

DATASET_PATH = Path("datasets/training_data.jsonl")
CHECKPOINT_PATH = Path("checkpoints/latest")

print("[Fine-tune] Starting automatic fine-tuning...")

all_records = []
with open(DATASET_PATH) as f:
    for line in f:
        try:
            all_records.append(json.loads(line))
        except:
            pass

records = all_records[-300:]
print(f"[Fine-tune] Using latest {len(records)} of {len(all_records)} total records")

dataset = Dataset.from_list([
    {"text": f"### Task:\n{r['prompt']}\n\n### Solution:\n{r.get('teacher_correction', r.get('correction', ''))}"}
    for r in records
])

model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
print(f"[Fine-tune] Loading model: {model_name}")

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32,
    device_map="cpu"
)

print("[Fine-tune] Training started...")
trainer = SFTTrainer(
    model=model,
    processing_class=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=512,
    args=TrainingArguments(
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        num_train_epochs=1,
        learning_rate=2e-4,
        fp16=False,
        logging_steps=10,
        output_dir="checkpoints/latest",
        report_to="none",
        save_strategy="no",
    ),
)

trainer.train()
print("[Fine-tune] Training complete!")

CHECKPOINT_PATH.mkdir(parents=True, exist_ok=True)
model.save_pretrained(str(CHECKPOINT_PATH))
tokenizer.save_pretrained(str(CHECKPOINT_PATH))
print("[Fine-tune] Model saved to checkpoints/latest!")
# Compress checkpoint for GitHub storage
import subprocess
if CHECKPOINT_PATH.exists():
    print("[Fine-tune] Compressing checkpoint...")
    subprocess.run(["tar", "-czf", "checkpoints/model.tar.gz", str(CHECKPOINT_PATH)])
    print("[Fine-tune] Saved to checkpoints/model.tar.gz")
