import os
from datetime import datetime
import httpx
from dotenv import load_dotenv

# Aktuelle Zeit und Datum
now = datetime.now()

script_dir = os.path.dirname(os.path.abspath(__file__))

def load_yaml(file_name):
    file_path = os.path.join(script_dir, file_name)
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
def load_env(file_name):
    file_path = os.path.join(script_dir, file_name)
    load_dotenv(file_path)

load_env(".env") # Load env
load_env(".secrets") # Load secrets
def tts_with_instructions(
    input_text: str,
    instructions: str = "",
    voice: str = "coral",
    model: str = "gpt-4o-mini-tts",
    response_format: str = "mp3",
    out_filename: str = None,
):
    """
    Nutzt die OpenAI TTS-API direkt per HTTP, inkl. instructions-Parameter.
    Speichert das Ergebnis als Audiodatei.

    :param input_text: Der zu sprechende Text.
    :param instructions: Zusätzliche Sprach-/Stil-Anweisungen.
    :param voice: Stimme (z.B. coral, onyx, nova, echo, ...).
    :param model: TTS-Modell (z.B. gpt-4o-mini-tts).
    :param response_format: "mp3" oder "wav".
    :param out_filename: Dateiname zum Speichern (inkl. Endung, optional).
    """
    
    api_key = os.getenv("OPENAI_API_KEY")
    print("OPENAI_API_KEY:", api_key)
    
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "input": input_text,
        "voice": voice,
        "instructions": instructions,
        "response_format": response_format
    }

    if not out_filename:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        out_filename = f"output_{timestamp}.{response_format}"

    with httpx.stream("POST", url, headers=headers, json=data, timeout=120.0) as response:
        response.raise_for_status()
        with open(out_filename, "wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
    print(f"Audio gespeichert als {out_filename}")
    return out_filename

def save_result(result_content, file_name):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    result_file = os.path.join(os.path.dirname(__file__), "outputs", "results", "news", f"{timestamp}_{file_name}")
    os.makedirs(os.path.dirname(result_file), exist_ok=True)
    with open(result_file, "w") as file:
        file.write(result_content)

if __name__ == "__main__":
    input_text = (
        "Yo, Leute! Hier ist Mad Dog die Morgenlatte, euer Hauptlieferant für radioaktives "
        "Entertainment und absolut irre News! Wir sind live aus dem Ödland – wo der Sand weht, "
        "die Mutanten pfeifen und niemand fragt, warum ich keine Hose trage. Aber genug von meinen "
        "Beinkleidern, lasst uns zu den wirklich wichtigen Dingen kommen, den News!"
    )
    instructions = (
        "Sprich laut, wild, rockig und mit viel Energie. "
        "Roll das R nicht und bring zwischendurch kurze Ausraster und Lacher ein!"
    )

    tts_with_instructions(
        input_text=input_text,
        instructions=instructions,
        voice="ash",
        model="gpt-4o-mini-tts",
        response_format="mp3",
        out_filename="output.mp3"
    )