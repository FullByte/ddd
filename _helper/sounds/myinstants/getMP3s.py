import os
import re
import shutil
import requests
from bs4 import BeautifulSoup

# The base URL
base_url = "https://www.myinstants.com"

# Output directory for MP3 files
output_dir = "mp3s"
os.makedirs(output_dir, exist_ok=True)

# Move existing MP3s in the project root into the output directory with unique names
for entry in os.listdir("."):
    if entry.lower().endswith(".mp3") and os.path.isfile(entry):
        src_path = os.path.join(".", entry)
        dest_name = entry
        stem, ext = os.path.splitext(dest_name)
        dest_path = os.path.join(output_dir, dest_name)
        suffix = 1
        while os.path.exists(dest_path):
            dest_name = f"{stem}_{suffix}{ext}"
            dest_path = os.path.join(output_dir, dest_name)
            suffix += 1
        shutil.move(src_path, dest_path)
        print(f"Verschoben: {entry} -> {dest_name}")

def sanitize_filename(name: str) -> str:
    # Replace invalid Windows filename characters
    return re.sub(r'[<>:"/\\|?*]', "_", name)


# Read the HTML content from the file
input_file = "input.html"
with open(input_file, "r", encoding="utf-8") as file:
    html_content = file.read()

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Find all MP3 URLs using regex in the onclick attributes
mp3_urls = set()
for button in soup.find_all("button", onclick=True):
    match = re.search(r"'(/media/sounds/[^']+\.mp3)'", button["onclick"])
    if match:
        mp3_urls.add(base_url + match.group(1))

print(f"Gefundene MP3-Links: {len(mp3_urls)}")

new_downloads = 0
skipped = 0

# Download the MP3 files into the output directory, skip if exists
for url in sorted(mp3_urls):
    filename = sanitize_filename(url.split("/")[-1])
    dest_path = os.path.join(output_dir, filename)
    if os.path.exists(dest_path):
        skipped += 1
        continue
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Fehler beim Download: {url} -> {e}")
        continue
    with open(dest_path, "wb") as f:
        f.write(response.content)
    new_downloads += 1
    print(f"Downloaded: {filename}")

# Build list file and print summary
mp3_files = [f for f in os.listdir(output_dir) if f.lower().endswith(".mp3")]
mp3_files.sort()
total_size_bytes = 0
for f in mp3_files:
    total_size_bytes += os.path.getsize(os.path.join(output_dir, f))

with open("mp3s.txt", "w", encoding="utf-8") as out:
    for f in mp3_files:
        size = os.path.getsize(os.path.join(output_dir, f))
        out.write(f"{f}\t{size}\n")

total_size_mb = total_size_bytes / (1024 * 1024)
print(f"Neue Downloads: {new_downloads}, Übersprungen: {skipped}")
print(f"Gesamt: {len(mp3_files)} Dateien, Größe: {total_size_mb:.1f} MB")
print("Dateiliste gespeichert in: mp3s.txt")
