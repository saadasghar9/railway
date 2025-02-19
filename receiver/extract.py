import requests
from bs4 import BeautifulSoup
import os

def fetch_and_save_content(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get the title for the filename
            title = soup.title.string if soup.title else "unknown_title"
            # Sanitize filename to remove special characters
            filename = ''.join(e for e in title if e.isalnum() or e.isspace()).strip()[:50] + ".html"
            
            # Determine where to save the file
            save_path = os.path.join(os.getcwd(), filename)
            
            # Write the content to a file
            with open(save_path, 'w', encoding='utf-8') as file:
                file.write(response.text)
            
            print(f"Content saved to {save_path}")
        else:
            print(f"Failed to retrieve content, status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

# Main loop for user input
while True:
    url = input("Enter a URL (or 'exit' to quit): ").strip()
    if url.lower() == 'exit':
        break
    if not url.startswith('http'):
        url = 'http://' + url  # Add protocol if not specified
    fetch_and_save_content(url)

print("Program ended.")