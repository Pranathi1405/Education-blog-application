import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

model_name = "EleutherAI/gpt-neo-125M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

def get_answer(user_question, course_title):
    prompt = f"""You are the expert author of the course "{course_title}".
Always respond clearly, concisely, and informatively to student questions. Use only 4 lines.

User: {user_question}
AI (Author):"""

    output = generator(prompt, max_new_tokens=80, do_sample=True, temperature=0.7)[0]['generated_text']
    answer = output.split("AI (Author):")[-1].strip().split("\n")[:4]  # Get max 4 lines
    return "\n".join(answer)
