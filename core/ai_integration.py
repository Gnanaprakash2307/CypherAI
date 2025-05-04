import requests
from config.settings import GEMINI_API_KEY  # Replace with your API key


def fetch_news():
    # Fetch news from Gemini or any other news API
    url = "https://api.gemini.com/news"  # Modify this URL for the actual Gemini endpoint
    response = requests.get(url, headers={"Authorization": f"Bearer {GEMINI_API_KEY}"})

    if response.status_code == 200:
        news = response.json()
        headlines = [f"{news_item['headline']}" for news_item in news['articles'][:5]]
        return "\n".join(headlines)
    else:
        return "Failed to fetch news."


def generate_response(query):
    # Simulate AI response (you can use Gemini API or any AI model)
    url = "https://api.gemini.com/query"  # Modify this URL for Gemini or other endpoint
    response = requests.post(url, json={"query": query}, headers={"Authorization": f"Bearer {GEMINI_API_KEY}"})

    if response.status_code == 200:
        data = response.json()
        return data['response']  # Assuming the AI returns a 'response' field
    else:
        return "AI Error: Unable to process the request."
