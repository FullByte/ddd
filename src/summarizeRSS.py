import os
import feedparser
from openai import OpenAI
from dotenv import load_dotenv
import yaml
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

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
role = load_yaml("roles/newsanchor2.yaml")  # Load system role
prompt_template = load_yaml("prompts/createNews.yaml")  # Load prompt

# Verify
print("RSS_FEED_URL:", os.getenv("RSS_FEED_URL"))
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))


# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_summary(summary_text):
    """
    Extrahiert den Inhalt des title-Attributs aus einer Zusammenfassung,
    oder gibt den Originaltext zurück, wenn kein title gefunden wird.
    """
    # Regex, um den Inhalt von title="..."> zu finden
    match = re.search(r'title="([^"]+)"', summary_text)
    if match:
        return match.group(1)  # Gibt den Inhalt von title="..." zurück
    return summary_text  # Gibt den Originaltext zurück, wenn kein title gefunden wird


def fetch_article_content(url):
    """
    Ruft den HTML-Inhalt der Seite ab und extrahiert den Haupttext mit BeautifulSoup.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Suche gezielt nach dem Artikelbereich
        article_tag = soup.find('div', class_='article-content')
        if article_tag:
            # Extrahiere alle <p>-Tags innerhalb des Artikels
            paragraphs = article_tag.find_all('div')
            article_content = " ".join([p.get_text() for p in paragraphs])
        else:
            print(f"Kein Artikelinhalt gefunden auf: {url}")
            return "Artikelinhalt konnte nicht extrahiert werden."
        #print(article_content[:2000])
        return article_content[:2000]  # Beschränke auf die ersten 1000 Zeichen
    except requests.RequestException as e:
        print(f"Fehler beim Abrufen des Artikels: {url}\n{e}")
        return "Artikel konnte nicht abgerufen werden."

def rss_feed_abrufen(feed_url, max_entries=10):
    # RSS-Feed abrufen
    feed = feedparser.parse(feed_url)
    nachrichten = []

    for eintrag in feed.entries[:max_entries]:  # Nur max_entries iterieren
        print(f"Verarbeite Artikel: {eintrag.title} - {eintrag.link}")
        artikel_text = fetch_article_content(eintrag.link)  # Abrufen des Artikels
        bereinigte_beschreibung = extract_summary(eintrag.summary) # Zusammenfassung bereinigen
        #artikel_summary = summarize_article(artikel_text)  # Summarize the article
        nachrichten.append({
            "titel": eintrag.title,
            "beschreibung": bereinigte_beschreibung,
            "link": eintrag.link,
            "artikel_text": artikel_text,  # Fügt den abgerufenen Text hinzu
            #"artikel_summary": artikel_summary  # Add summarized text
        })
    #print(nachrichten)
    # Truncate to the first `max_entries`
    return nachrichten

def nachrichtensendung_generieren(nachrichten):
    # prompt = "Erstelle eine komplette Nachrichtensendung mit den folgenden Elementen:\n\n"
    current_date = datetime.now().strftime("%Y-%m-%d")
    day_period = get_day_period()
    prompt = f"Es ist aktuell {day_period}, am , {current_date}.\n\n"
    prompt += prompt_template["content"] + "\n\n"
    for index, nachricht in enumerate(nachrichten, 1):
        prompt += (
            f"Nachricht {index}:\n"
            f"Titel: {nachricht['titel']}\n"
            f"Zusammenfassung: {nachricht['beschreibung']}\n"
            #f"Zusammenfassung: {nachricht['artikel_summary']}\n"
            #f"Link: {nachricht['link']}\n"
            f"Artikeltext: {nachricht['artikel_text'][:600]}\n\n"
        )
        print(prompt)
        

    # ChatGPT Aufruf
    response = client.chat.completions.create(
        model="gpt-4",  # Adjust model as necessary
        messages=[
            {"role": "system", "content": role["content"]},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

def summarize_article(text, max_tokens=100):
    """
    Summarizes the given text using OpenAI's API.
    Falls back to truncation if the API is unavailable.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes articles."},
                {"role": "user", "content": f"Summarize the following text in 10 sentences:\n\n{text}"}
            ],
            max_tokens=max_tokens,
            temperature=0.5
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"Fehler beim Zusammenfassen des Artikels: {e}")
        # Fallback to truncation
        return text[:max_tokens * 4]  # Approximation: 1 token = ~4 characters
    
def save_result(result_content, file_name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H%M%S")
    result_file = os.path.join(script_dir, "outputs", "results", "news", timestamp + "_" + file_name)
    with open(result_file, "w") as file:
        file.write(result_content)
        
def save_rss_results(nachrichten):
    for index, nachricht in enumerate(nachrichten, 1):
        file_name = f"rss_article_{index}.txt"
        save_result(
            result_content=f"Titel: {nachricht['titel']}\nZusammenfassung: {nachricht['beschreibung']}\nText: {nachricht['artikel_text']}\n\nLink: {nachricht['link']}\n",
            file_name=file_name
        )

def get_day_period():
    """
    Bestimmt die Tageszeit basierend auf der aktuellen Uhrzeit.
    """
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Morgen" 
    elif 12 <= hour < 17:
        return "Nachmittag"  
    elif 17 <= hour < 22:
        return "Abend"  
    else:
        return "Nacht" 

def main():
    feed_url = os.getenv("RSS_FEED_URL")
    max_entries = 5  # Limit to the first 5 entries
    nachrichten = rss_feed_abrufen(feed_url, max_entries)

    if nachrichten:
        sendung = nachrichten
        save_rss_results(nachrichten)
        sendung = nachrichtensendung_generieren(nachrichten)
        save_result(sendung, "news")
        print("\n--- Nachrichtensendung ---\n")
        print(sendung)

    else:
        print("Keine Nachrichten gefunden.")

if __name__ == "__main__":
    main()