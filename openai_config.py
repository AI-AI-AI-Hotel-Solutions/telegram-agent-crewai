import os
import openai

def setup_openai():
    openai.api_key = os.getenv("OPENAI_API_KEY") or "SUA_CHAVE_OPENAI"

