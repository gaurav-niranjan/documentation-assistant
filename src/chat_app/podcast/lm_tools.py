from dotenv import load_dotenv
from openai import OpenAI
import os
import re
import requests
from bs4 import BeautifulSoup
import json
from google import genai
import base64

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client()

def read_webpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text()
    return text

def search_web(query):
    response = requests.get(
        "https://serpapi.com/search.json",
        params={
            "q": query,
            "engine": "google",
            "api_key": os.getenv("SERPAPI_API_KEY"),
        },
        timeout=20,
    )
    data = response.json()

    if "error" in data :
        return f'Search failed: {data["error"]}'

    results = []
    for item in data.get("organic_results", [])[:5]:
        results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet"),
        })
    return results

def create_audio(script):
    audio_filename = "podcast.wav"
    style_instruction = (
        "Persona: You are a newscaster. "
        "Delivery: Crisp and articulate, with measured pacing. "
        "Tone: Objective and neutral, confident and authoritative, conversational yet formal."
    )

    interaction = client.interactions.create(
        model = "gemini-3.8-flash-tts",
        input = [{
            "type": "user_input",
            "content": [{
                "type": "text",
                "text": script,
                "annotations": [{
                    "type": "speech_metadata",
                    "style": style_instruction,
                }]
            }]
        }],
        response_format={"type": "audio"},
        generation_config={
            "speech_config": [
                {"voice": "Charon"}
            ]
        },
    )
    with open(audio_filename, "wb") as f:
        f.write(base64.b64decode(interaction.output_audio.data))

    return True


