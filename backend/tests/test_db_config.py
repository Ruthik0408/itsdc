import db_config


def _reload_with_env(monkeypatch, env):
    # db_config reads os.getenv lazily, so we mutate the environment in place.
    # No importlib.reload: reloading would re-run load_dotenv and repopulate the
    # real .env values, defeating isolation.
    for key in (
        "LLM_PROVIDER",
        "GROQ_API_KEY",
        "GROQ_MODEL",
        "GROQ_BASE_URL",
        "GROQ_HEALTH_URL",
        "LLAMA_BASE_URL",
        "LLAMA_MODEL",
        "LLAMA_API_KEY",
    ):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return db_config


def test_groq_provider_settings(monkeypatch):
    cfg = _reload_with_env(
        monkeypatch,
        {"LLM_PROVIDER": "groq", "GROQ_API_KEY": "gsk_test", "GROQ_MODEL": "llama-3.1-8b-instant"},
    )
    settings = cfg.get_llama_settings()
    assert settings["provider"] == "groq"
    assert settings["base_url"] == "https://api.groq.com/openai/v1"
    assert settings["health_url"].endswith("/models")
    assert settings["api_key"] == "gsk_test"
    assert settings["model"] == "llama-3.1-8b-instant"
    assert cfg.is_remote_llm_provider() is True


def test_ollama_provider_settings(monkeypatch):
    cfg = _reload_with_env(
        monkeypatch,
        {"LLM_PROVIDER": "ollama", "LLAMA_MODEL": "qwen2.5:3b-instruct-q4_0"},
    )
    settings = cfg.get_llama_settings()
    assert settings["provider"] == "ollama"
    assert "11434" in settings["base_url"]
    assert settings["model"] == "qwen2.5:3b-instruct-q4_0"
    assert cfg.is_remote_llm_provider() is False


def test_default_provider_is_ollama(monkeypatch):
    cfg = _reload_with_env(monkeypatch, {})
    assert cfg.get_llm_provider() == "ollama"
    assert cfg.get_llama_settings()["provider"] == "ollama"


def test_runtime_provider_override(monkeypatch):
    cfg = _reload_with_env(monkeypatch, {"LLM_PROVIDER": "ollama", "GROQ_API_KEY": "gsk_test"})
    try:
        assert cfg.get_llm_provider() == "ollama"          # from env
        assert cfg.set_llm_provider("groq") == "groq"        # UI override
        assert cfg.get_llm_provider() == "groq"
        assert cfg.get_llama_settings()["provider"] == "groq"
        assert cfg.set_llm_provider("ollama") == "ollama"
        assert cfg.get_llm_provider() == "ollama"
    finally:
        cfg._runtime_llm_provider = None  # reset shared module state


def test_invalid_provider_rejected(monkeypatch):
    cfg = _reload_with_env(monkeypatch, {})
    with __import__("pytest").raises(ValueError):
        cfg.set_llm_provider("openai")
