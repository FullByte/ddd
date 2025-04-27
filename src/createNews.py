# filepath: /home/manu/Repos/ddd/call_summarizeRSS.py
import sys
import os
import yaml
from datetime import datetime
from dotenv import load_dotenv
from tts_openAI import tts_with_instructions
from summarizeRSS import process_rss_feed
from audio_utils import add_jingles

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

def load_instructions(file_path):
    """
    Lädt die Instructions aus einer Textdatei.
    """
    with open(file_path, 'r') as file:
        return file.read().strip()

# Lade Umgebungsvariablen und YAML-Dateien
load_env(".env")  # Load env
load_env(".secrets")  # Load secrets
role = load_yaml("roles/newsanchor2.yaml")  # Load system role
prompt_template = load_yaml("prompts/createNews.yaml")  # Load prompt

# Verify
feed_url = os.getenv("RSS_FEED_URL")
api_key = os.getenv("OPENAI_API_KEY")
print("RSS_FEED_URL:", feed_url)
print("OPENAI_API_KEY:", api_key)

if __name__ == "__main__":
    # Aufruf der Hauptlogik aus summarizeRSS.py
    result = process_rss_feed()
    if result:
        print("\nNachrichtensendung erfolgreich erstellt\n")
    
    # Lade die Instructions aus der Datei
    instructions_path = os.path.join(script_dir, "tts_vibes", "newsanchor2.txt")
    instructions = load_instructions(instructions_path)
    
    # Erstelle den Pfad für die Ausgabe mit Zeitstempel
    output_dir = os.path.join(script_dir, "outputs", "results", "speech")
    os.makedirs(output_dir, exist_ok=True)  # Stelle sicher, dass der Ordner existiert
    timestamp = now.strftime("%Y-%m-%d_%H%M%S")
    news_output_file = os.path.join(output_dir, f"{timestamp}_news.mp3")
    
    # Übergib die Nachrichtensendung an die TTS-Funktion
    tts_with_instructions(
        input_text=result,
        instructions=instructions,
        voice="ash",
        model="gpt-4o-mini-tts",
        response_format="mp3",
        out_filename=news_output_file
    )
    print(f"Audio gespeichert unter: {news_output_file}")

    # Pfade für Jingles
    intro_jingle_path = os.path.join(script_dir, "input", "jingles", "waa_intro_jingle.m4a")
    outro_jingle_path = os.path.join(script_dir, "input", "jingles", "waa_outro_jingle.m4a")
    final_output_file = os.path.join(output_dir, f"{timestamp}_news_with_jingles.mp3")

    # Füge Jingles hinzu
    add_jingles(news_output_file, intro_jingle_path, outro_jingle_path, final_output_file)