from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import re

# API Configuration
client = OpenAI(
    api_key=""  # Replace with your actual API key
)

messages = []
website_content = ""

def scrape_website(url):
    """
    Scrapes the website content from the given URL
    Returns: Extracted text content from the website
    """
    try:
        print(f"\n[INFO] Fetching content from: {url}")
        
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract text content
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up text - remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit content to avoid token limits (approximately 3000 words)
        words = text.split()
        if len(words) > 3000:
            text = ' '.join(words[:3000])
        
        print(f"[SUCCESS] Extracted {len(words)} words from the website")
        return text
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch website: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        return None

def initialize_chatbot_with_context(website_data):
    """
    Initializes the chatbot with website context
    """
    global messages
    
    system_message = {
        "role": "system",
        "content": f"""You are a helpful assistant with knowledge about a specific website. 
        Use the following website content to answer user questions accurately:
        
        WEBSITE CONTENT:
        {website_data}
        
        Instructions:
        - Answer questions based on the website content provided
        - If the answer is not in the website content, politely inform the user
        - Be concise and helpful
        - Provide specific information from the website when relevant"""
    }
    
    messages.append(system_message)
    print("[INFO] Chatbot initialized with website context")

def completion(message):
    """
    Sends user message to ChatGPT and gets response
    """
    global messages
    
    messages.append({
        "role": "user",
        "content": message
    })

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="gpt-4o",
            temperature=0.7,
            max_tokens=500
        )
        
        response_content = chat_completion.choices[0].message.content
        
        assistant_message = {
            "role": "assistant",
            "content": response_content
        }
        messages.append(assistant_message)
        
        # Print response only once
        print(f"\nJarvis: {response_content}\n")
        
    except Exception as e:
        print(f"[ERROR] API call failed: {e}")

def main():
    """
    Main function to run the chatbot
    """
    global website_content
    
    print("=" * 60)
    print("CHATBOT WITH WEB SCRAPING - CONSOLE APPLICATION")
    print("=" * 60)
    
    # Step 1: Get website URL from user
    website_url = input("\nEnter the website URL to scrape (or press Enter for default): ").strip()
    
    # Use default URL if none provided
    if not website_url:
        website_url = "https://botpenguin.com/"
        print(f"Using default URL: {website_url}")
    
    # Step 2: Scrape website content
    website_content = scrape_website(website_url)
    
    if not website_content:
        print("[ERROR] Failed to scrape website. Exiting...")
        return
    
    # Step 3: Initialize chatbot with website context
    initialize_chatbot_with_context(website_content)
    
    # Step 4: Start conversation loop
    print("\n" + "=" * 60)
    print("Jarvis: Hi! I am Jarvis. I have analyzed the website.")
    print("Ask me anything about it! (Type 'exit' or 'quit' to end)")
    print("=" * 60 + "\n")
    
    while True:
        user_question = input("You: ").strip()
        
        if not user_question:
            continue
            
        if user_question.lower() in ['exit', 'quit', 'bye']:
            print("\nJarvis: Goodbye! Have a great day!\n")
            break
        
        completion(user_question)

if __name__ == "__main__":
    main()
    