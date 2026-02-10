import os
import json
from google import genai
from google.genai import types  # Import types for the config
from src.ai.prompts import SUMMARIZE_PROMPT, GRAMMAR_PROMPT

# Initialize the new Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def summarize_notes(content: str) -> dict:
    prompt = SUMMARIZE_PROMPT.format(content=content)

    # Use the proper GenerateContentConfig object to satisfy type checking
    config = types.GenerateContentConfig(
        response_mime_type="application/json"
    )

    # Use .aio for async support in FastAPI
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config
    )

    try:
        return json.loads(response.text)
    except (json.JSONDecodeError, AttributeError):
        raise ValueError("AI returned invalid JSON")

async def grammar_check(content: str) -> dict:
    prompt = GRAMMAR_PROMPT.format(content=content)

    config = types.GenerateContentConfig(
        response_mime_type="application/json"
    )

    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config
    )

    try:
        return json.loads(response.text)
    except (json.JSONDecodeError, AttributeError):
        raise ValueError("AI returned invalid JSON")
