import os
import feedparser
import openai
from dotenv import load_dotenv

# Load environment variables from .secrets file
load_dotenv()

# Set the OpenAI API key directly
openai.api_key = os.getenv("OPENAI_API_KEY")

def rss_feed_abrufen(feed_url):
    # RSS-Feed abrufen
    feed = feedparser.parse(feed_url)
    nachrichten = []

    for eintrag in feed.entries:
        nachrichten.append({
            "titel": eintrag.title,
            "beschreibung": eintrag.summary,
            "link": eintrag.link
        })
    return nachrichten

def nachrichtensendung_generieren(nachrichten):
    # Construct a custom prompt for the RSS feed content
    prompt = "Hier sind die neuesten Nachrichten:\n\n"
    
    for index, nachricht in enumerate(nachrichten, 1):
        prompt += f"{index}. {nachricht['titel']}\n{nachricht['beschreibung']}\nLink: {nachricht['link']}\n\n"
    
    return prompt.strip()

def main():
    feed_url = os.getenv("RSS_FEED_URL")
    nachrichten = rss_feed_abrufen(feed_url)

    if nachrichten:
        sendung = nachrichtensendung_generieren(nachrichten)
        print("\n--- Nachrichtensendung ---\n")
        print(sendung)
    else:
        print("Keine Nachrichten gefunden.")

if __name__ == "__main__":
    main()