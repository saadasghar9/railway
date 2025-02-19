import requests
from bs4 import BeautifulSoup
import os

def fetch_and_save_text(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = ' '.join(soup.stripped_strings)  # Join text with spaces, ignoring empty strings
            
            # Use the title for the filename or a default name
            title = soup.title.string if soup.title else "unknown_title"
            filename = ''.join(c for c in title if c.isalnum() or c.isspace()).strip()[:50] + ".txt"
            
            # Save in a specific directory, perhaps in a 'downloads' folder within the app
            save_path = os.path.join(os.path.dirname(__file__), 'downloads', filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)  # Create directory if it doesn't exist
            
            with open(save_path, 'w', encoding='utf-8') as file:
                file.write(page_text)
            
            return f"Text content saved to {save_path}"
        else:
            return f"Failed to retrieve content, status code: {response.status_code}"
    except requests.RequestException as e:
        return f"An error occurred: {e}"