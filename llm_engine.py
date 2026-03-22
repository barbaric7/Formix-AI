import requests

API_URL = "https://openrouter.ai/api/v1/chat/completions"

def ask_model(model, question, options, api_key):
    prompt = f"""
You are solving a multiple choice question.

Question:
{question}

Options:
{chr(10).join(options)}

IMPORTANT:
Return EXACTLY one of the options above.
Copy the option text exactly.
Do NOT explain.
Do NOT rephrase.
Return only the exact option text.
"""
    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30, # Reduced timeout so it doesn't hang forever
        )

        data = response.json()

        # --- NEW: DETAILED ERROR LOGGING ---
        if response.status_code != 200:
            print(f"❌ API HTTP Error {response.status_code}: {response.text}")
            return None

        if "choices" not in data:
            print("❌ Model returned invalid data format:", data)
            return None

        return data["choices"][0]["message"]["content"].strip()
        
    except Exception as e:
        print(f"❌ Network or Connection Error: {e}")
        return None