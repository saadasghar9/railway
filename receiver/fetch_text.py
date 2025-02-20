import requests
from bs4 import BeautifulSoup
import os

def fetch_and_save_text(url):
    try:
        # Add headers to ensure compatibility with most sites
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = ' '.join([p.get_text(strip=True) for p in soup.find_all('p')])
            if not page_text:
                page_text = ' '.join(soup.stripped_strings)
            if not page_text:
                raise Exception("No meaningful text extracted from the page")
            
            title = soup.title.string if soup.title else "unknown_title"
            filename = ''.join(c for c in title if c.isalnum() or c.isspace()).strip()[:50] + ".txt"
            save_path = os.path.join(os.path.dirname(__file__), 'downloads', filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as file:
                file.write(page_text)
            
            print(f"Text saved to {save_path}")  # Log the save, but don’t return it
            return page_text  # Return the actual text
        else:
            raise Exception(f"Failed to retrieve content, status code: {response.status_code}")
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch URL: {str(e)}")