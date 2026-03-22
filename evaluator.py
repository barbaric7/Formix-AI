from llm_engine import ask_model

# MAX SPEED MODE: Only use one highly accurate, non-rate-limited model
PRIMARY_MODEL = "openai/gpt-4o-mini"

def get_final_answer(question, options, user_data):
    api_key = user_data.get("openrouter_api_key", "").strip()

    if not api_key:
        print("❌ ERROR: OpenRouter API Key is missing! Please save it in the Profile Settings.")
        return options[0]

    print(f"⚡ Fast-Solving with {PRIMARY_MODEL.split('/')[1]}...")
    
    # Make a single, fast API call
    answer = ask_model(PRIMARY_MODEL, question, options, api_key)
    
    if answer:
        return answer
    else:
        print("⚠️ Model failed to respond. Defaulting to first option.")
        return options[0]