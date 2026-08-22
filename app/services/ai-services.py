import anthropic
from app.config import settings

class AIServiceError(Exception):
    """Raised when the LLM call fails for any reason."""
    pass

BASE_RULES = """Rules:
- Preserve the original meaning.
- Do not add information that was not provided.
- Do not remove important information.
- Do not unnecessarily rewrite the entire text.
- Maintain the user's original tone where possible.
- Return only the resulting text.
- Do not include explanations or headings."""

# One instruction block per mode. Allow-listed — never built from user input.
MODE_PROMPTS = {
    "grammar": f"""You are an AI writing assistant. Correct grammar, spelling,
punctuation, and minor clarity issues only. Preserve tone and meaning.
{BASE_RULES}""",
    "paraphrase": f"""You are an AI writing assistant. Rewrite the text using
different wording while preserving the original meaning. Do not introduce new
information.
{BASE_RULES}""",
    "formal": f"""You are an AI writing assistant. Rewrite the text in a
professional, formal tone while preserving meaning.
{BASE_RULES}""",
    "polite": f"""You are an AI writing assistant. Rewrite the text so it
sounds respectful and courteous, without being unnecessarily formal.
{BASE_RULES}""",
    "friendly": f"""You are an AI writing assistant. Rewrite the text so it
sounds warm, natural, and approachable. Avoid excessive formality.
{BASE_RULES}""",
    "concise": f"""You are an AI writing assistant. Reduce unnecessary words
while preserving the original meaning.
{BASE_RULES}""",
}

client = anthropic.Anthropic(api_key=settings.ai_api_key)

def improve_text(text: str, mode: str = "grammar") -> str:
    system_prompt = MODE_PROMPTS.get(mode, MODE_PROMPTS["grammar"])
    try:
        response = client.messages.create(
            model=settings.ai_model,
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": text}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        raise AIServiceError(str(e)) from e