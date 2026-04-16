import requests
from app.config.settings import OLLAMA_URL, OLLAMA_MODEL

def generate_response(prompt: str, temperature: float = 0.2, num_predict: int = 256):

    url = f"{OLLAMA_URL}/api/generate"

    response = requests.post(
        url,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict
            }
        }
    )

    response.raise_for_status()  # 🔥 importante para debug

    return response.json()["response"]