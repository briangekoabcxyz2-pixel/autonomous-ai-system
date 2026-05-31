import modal

app = modal.App("aaes-student")

image = modal.Image.debian_slim().pip_install(
    "transformers",
    "torch",
    "accelerate",
    "fastapi",
    "huggingface_hub",
)

@app.function(
    gpu="T4",
    image=image,
    timeout=300,
    secrets=[modal.Secret.from_name("huggingface-secret")],
)
@modal.fastapi_endpoint(method="POST")
def generate(item: dict):
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch, os

    model_name = "meta-llama/Llama-3.2-3B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=os.environ["HF_TOKEN"])
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="cuda", token=os.environ["HF_TOKEN"])

    prompt = item["prompt"]
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=200, do_sample=False)
    full = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"response": full[len(prompt):].strip()}
