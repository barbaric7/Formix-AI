from llm_engine import ask_model

PRIMARY_MODEL = "openai/gpt-3.5-turbo"
SECONDARY_MODEL = "meta-llama/llama-3.1-8b-instruct"

def get_final_answer(question, options, user_data):
    # Extract API keys dynamically from the GUI input
    primary_key = user_data.get("primary_api_key")
    secondary_key = user_data.get("secondary_api_key")

    print("Querying Primary Model...")
    primary = ask_model(PRIMARY_MODEL, question, options, primary_key)
    print("Primary:", primary)

    print("Querying Secondary Model...")
    # Using secondary_key if provided, otherwise fallback to primary key
    secondary = ask_model(SECONDARY_MODEL, question, options, secondary_key or primary_key)
    print("Secondary:", secondary)

    if primary and secondary:
        if primary.lower() == secondary.lower():
            print("Agreement reached")
            return primary
        else:
            print("Disagreement — using primary")
            return primary

    return primary or secondary