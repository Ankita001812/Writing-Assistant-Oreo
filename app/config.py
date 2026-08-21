import os

class Settings:
    """
    Centralised place to read environment variables.
    Nothing else in the app should call os.environ directly —
    that way, if we rename a variable, we only change it here.
    """
    ai_api_key: str = os.environ.get("AI_API_KEY", "")
    ai_model: str = os.environ.get("AI_MODEL", "claude-sonnet-4-6")
    port: int = int(os.environ.get("PORT", 8000))
    max_text_length: int = 2000

settings = Settings()