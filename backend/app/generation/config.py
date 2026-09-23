import os


GENERATION_CONFIG = {
    "provider": os.getenv(
        "LLM_PROVIDER",
        "openai",
    ),
    "model": os.getenv(
        "LLM_MODEL",
        "gpt-5.6-luna",
    ),
    "api_key": os.getenv("OPENAI_API_KEY"),
}