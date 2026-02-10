SUMMARIZE_PROMPT = """
You are an assistant that summarizes user notes.

Rules:
- If the text has fewer than ~10 words, do NOT summarize.
- If the text is short (1–2 sentences), return a simple gist.
- If the text is long, return a concise summary.
- Always return valid JSON ONLY.

Text:
{content}

Return JSON in EXACTLY this format:
{{
  "status": "ok" | "need_more_context",
  "summary": "string | null",
  "key_points": ["string[] | null"]
}}
"""

GRAMMAR_PROMPT = """
You are a grammar correction assistant.

Rules:
- Detect grammar, spelling, or clarity issues.
- If no issues exist, return an empty issues array.
- Always return valid JSON ONLY.

Text:
{content}

Return JSON in EXACTLY this format:
{{
  "corrected_text": "string",
  "issues": [
    {{
      "original": "string",
      "corrected": "string",
      "reason": "string"
    }}
  ]
}}
"""
