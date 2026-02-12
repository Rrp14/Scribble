import os

from google import genai

from src.ai.utils import content_hash
from src.data.redis_client import redis_client
from src.ai.prompts import SUMMARIZE_PROMPT, GRAMMAR_PROMPT

# Initialize the new Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

import json
from google.genai import types

CACHE_TTL = 60 * 10


async def summarize_notes(content: str) -> dict:
    key = f"ai:summary:{content_hash(content)}"

    # 1. Check Cache
    cached = redis_client.get(key)
    if cached:
        # Decode bytes from Redis and parse JSON
        return {"cached": True, "result": json.loads(cached.decode())}

    prompt = SUMMARIZE_PROMPT.format(content=content)

    config = types.GenerateContentConfig(
        response_mime_type="application/json"
    )

    # 2. Call Gemini API
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash-lite",  # Note: Verify your model version name
        contents=prompt,
        config=config
    )

    # 3. Extract and Validate Text
    try:
        # Use .text property to get the generated string
        ai_text = response.text
        parsed_result = json.loads(ai_text)
    except (json.JSONDecodeError, AttributeError):
        raise ValueError("AI returned invalid JSON")

    # 4. Cache the raw text (must be a string/bytes for Redis)
    redis_client.setex(key, CACHE_TTL, ai_text)

    return {"cached": False, "result": parsed_result}


async def grammar_check(content: str) -> dict:

    key=f"ai:grammar:{content_hash(content)}"

    cached=redis_client.get(key)

    if cached:
        return {"cached":True,"result":json.loads(cached.decode())}

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
        ai_text=response.text
        parsed_result=json.loads(ai_text)
    except (json.JSONDecodeError, AttributeError):
        raise ValueError("AI returned invalid JSON")

    redis_client.setex(key,CACHE_TTL,ai_text)

    return {"cached":False,"result":parsed_result}
