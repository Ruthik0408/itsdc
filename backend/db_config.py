import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(BACKEND_DIR / ".env", override=True)


def get_database_settings():
    return {
        "dbname": os.getenv("DB_NAME", "tulip2"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "postgres"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "10")),
    }


def get_sqlalchemy_url():
    settings = get_database_settings()
    user = quote_plus(settings["user"])
    password = quote_plus(settings["password"])
    host = settings["host"]
    port = settings["port"]
    dbname = settings["dbname"]
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"


SUPPORTED_LLM_PROVIDERS = ("vllm", "ollama", "groq")

# Runtime override set from the UI; falls back to LLM_PROVIDER env when unset.
_runtime_llm_provider: str | None = None


def get_llm_provider() -> str:
    if _runtime_llm_provider:
        return _runtime_llm_provider
    return os.getenv("LLM_PROVIDER", "ollama").strip().lower()


def set_llm_provider(provider: str) -> str:
    """Override the active LLM provider for this process (UI toggle)."""
    global _runtime_llm_provider
    normalized = (provider or "").strip().lower()
    if normalized not in SUPPORTED_LLM_PROVIDERS:
        raise ValueError(f"provider must be one of: {', '.join(SUPPORTED_LLM_PROVIDERS)}")
    _runtime_llm_provider = normalized
    return normalized


def is_remote_llm_provider() -> bool:
    return get_llm_provider() == "groq"


def get_llama_settings():
    """Resolve the active LLM client settings.

    Supports three OpenAI-compatible providers selected via LLM_PROVIDER:
    - "groq":   Groq cloud (default model llama-3.1-8b-instant).
    - "vllm":   local/remote vLLM OpenAI-compatible server.
    - "ollama": local Ollama server (the original default).
    """
    if get_llm_provider() == "vllm":
        base_url = os.getenv("VLLM_BASE_URL", "http://10.49.41.5:8002/v1").rstrip("/")
        return {
            "provider": "vllm",
            "base_url": base_url,
            "health_url": os.getenv("VLLM_HEALTH_URL", f"{base_url}/models"),
            "api_key": os.getenv("VLLM_API_KEY", "vllm"),
            "model": os.getenv("VLLM_MODEL", "Qwen3-30B-A3B-Instruct"),
        }

    if get_llm_provider() == "groq":
        base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
        return {
            "provider": "groq",
            "base_url": base_url,
            "health_url": os.getenv("GROQ_HEALTH_URL", f"{base_url}/models"),
            "api_key": os.getenv("GROQ_API_KEY", ""),
            "model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        }

    return {
        "provider": "ollama",
        "base_url": os.getenv("LLAMA_BASE_URL", "http://localhost:11434/v1"),
        "health_url": os.getenv("LLAMA_HEALTH_URL", "http://localhost:11434/api/tags"),
        "api_key": os.getenv("LLAMA_API_KEY", "ollama"),
        "model": os.getenv("LLAMA_MODEL", "llama3"),
    }
