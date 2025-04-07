import os
import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urlparse
import pprint

# Create the folder if it doesn't exist
os.makedirs('website_content', exist_ok=True)

def sanitize_filename(url):
    """
    Create a safe filename from the URL.
    """
    parsed_url = urlparse(url)
    filename = parsed_url.netloc + parsed_url.path  # Use domain and path for filename
    filename = filename.replace('/', '_').replace(':', '_').replace('?', '_').replace('&', '_')  # Sanitize
    if filename.endswith('_'):
        filename = filename[:-1]
    return filename
# Method 1: Basic JSON loading
def load_json_basic(file_path):
    """
    Basic method to load JSON from a file
    """
    with open(file_path, 'r') as file:
        return json.load(file)
    
def scrape_and_generate_json(urls=[]):
    summaries = []  # This will store the summary for each page
    u = load_json_basic("config/school_url.json")
    urls = []
    for school in u:
        for url in school["urls"]:
            # urls.append(url)
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract the text content (adjust this depending on your website's structure)
            text = soup.get_text(separator=' ', strip=True)
            # Sanitize the URL and create a safe filename for the JSON file
            filename =  sanitize_filename(url) + ".json"           
            # Create the data structure for the page content
            page_data = {
                "source_url": url,
                "content": text
            }

            output_dir = "website_content/" + school["school"]
            full_path = os.path.join(output_dir, filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(f"{full_path}", 'w', encoding='utf-8') as json_file:
                json.dump(page_data, json_file, ensure_ascii=False, indent=4)
            # Generate a brief summary (first 500 characters as an example)
            summary = text[:500]  # You can adjust this as needed
            
            # Append the summary data for this page
            summaries.append({
                "page": url,
                "url": url,
                "summary": summary
            })
            
            print(f"Saved content from {url} to {filename}")

            # Save the overall summaries to a JSON file
            with open("website_content/scrape_summary.json", "w", encoding="utf-8") as json_file:
                json.dump(summaries, json_file, ensure_ascii=False, indent=4)
                
            print("Scrape summary saved to 'scrape_summary.json'")
scrape_and_generate_json()
