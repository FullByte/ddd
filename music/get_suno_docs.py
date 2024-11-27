import os
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import re

# Define the base URL of the help center
BASE_URL = "https://help.suno.com"

# Directory to save downloaded articles
OUTPUT_DIR = os.path.dirname(__file__) + "/suno_help_articles"

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# Function to fetch and parse a webpage
def fetch_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, "html.parser")
    else:
        print(f"Failed to fetch {url} (Status code: {response.status_code})")
        return None

# Function to extract categories and their links
def get_categories(base_url):
    soup = fetch_page(base_url)
    if not soup:
        return []
    category_links = [
        (a.get_text(strip=True), base_url + a["href"])
        for a in soup.select("a[href^='/en/categories/']")
    ]
    return category_links

# Function to get help articles from a category
def get_articles_from_category(category_url):
    soup = fetch_page(category_url)
    if not soup: 
        return []
    articles = [
        (a.get_text(strip=True), BASE_URL + a["href"])
        for a in soup.select("a[href^='/en/articles/']")
    ]
    return articles

# Function to download an article
def download_article(article_url, category_name, output_dir):
    soup = fetch_page(article_url)
    if soup:
        # Extract the title for naming
        title_tag = soup.find("h1")
        if title_tag:
            title = title_tag.get_text(strip=True).replace("/", "-")
            title = sanitize_filename(title)  # Sanitize the title
        else:
            print(f"Warning: <h1> not found for {article_url}. Using URL as title.")
            title = sanitize_filename(article_url.split("/")[-1])
        
        # Find the content inside <div class="article-content-container ">
        content = soup.find("div", class_="article-content-container")
        
        if content:
            # Ensure category directory exists
            category_dir = os.path.join(output_dir, sanitize_filename(category_name))
            os.makedirs(category_dir, exist_ok=True)

            # Save the article as an HTML file
            filename = os.path.join(category_dir, f"{title}.html")
            with open(filename, "w", encoding="utf-8") as file:
                file.write(str(content))
            print(f"Downloaded: {title} in category: {category_name}")
        else:
            print(f"Error: Content not found for {article_url}. Check if <div class='article-content-container'> exists.")
    else:
        print(f"Error: Failed to parse {article_url}")

def combine_articles_by_category(output_dir):
    """
    Combines all help articles in each category into a single HTML file and deletes individual articles.
    """
    for category_name in os.listdir(output_dir):
        category_path = os.path.join(output_dir, category_name)
        if os.path.isdir(category_path):  # Process only directories
            combined_content = f"<html><head><title>{category_name}</title></head><body>"
            combined_content += f"<h1>{category_name}</h1>"
            
            # Iterate through all HTML files in the category folder
            for article_file in os.listdir(category_path):
                if article_file.endswith(".html"):
                    article_path = os.path.join(category_path, article_file)
                    with open(article_path, "r", encoding="utf-8") as file:
                        article_content = file.read()
                        
                        # Extract and append the article's main content
                        soup = BeautifulSoup(article_content, "html.parser")
                        main_content = soup.find("div", class_="article-content-container")
                        if main_content:
                            combined_content += f"<h2>{os.path.splitext(article_file)[0]}</h2>"
                            combined_content += str(main_content)
                        else:
                            print(f"Warning: Could not find main content in {article_file}")
            
            # Close the combined HTML
            combined_content += "</body></html>"
            
            # Save the combined file in the main folder
            combined_file_path = os.path.join(output_dir, f"{category_name}.html")
            with open(combined_file_path, "w", encoding="utf-8") as combined_file:
                combined_file.write(combined_content)
            
            print(f"Combined articles for category '{category_name}' into {combined_file_path}")
            
            # Delete the individual articles and category folder
            for article_file in os.listdir(category_path):
                os.remove(os.path.join(category_path, article_file))
            os.rmdir(category_path)

# Main script
def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Get all categories
    categories = get_categories(BASE_URL)
    if not categories:
        print("No categories found.")
        return

    # Dictionary to hold articles grouped by category
    category_articles = defaultdict(list)

    # Fetch articles for each category
    for category_name, category_url in categories:
        print(f"Fetching articles for category: {category_name}")
        articles = get_articles_from_category(category_url)
        category_articles[category_name].extend(articles)

    # Download articles
    for category_name, articles in category_articles.items():
        print(f"Downloading {len(articles)} articles for category: {category_name}")
        for article_title, article_url in articles:
            download_article(article_url, category_name, OUTPUT_DIR)

    # Call this function after downloading all articles
    combine_articles_by_category(OUTPUT_DIR)
    
if __name__ == "__main__":
    main()
