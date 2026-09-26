from __future__ import annotations

from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'CivicPulse'
    environment: str = 'development'
    log_level: str = 'INFO'
    database_url: str = 'postgresql+psycopg://civicpulse:civicpulse@postgres:5432/civicpulse'
    redis_url: str = 'redis://redis:6379/0'
    triage_provider: str = 'simulated'
    groq_api_key: str | None = Field(default=None, alias='GROQ_API_KEY')
    groq_base_url: str = 'https://api.groq.com/openai/v1'
    groq_model: str = 'openai/gpt-oss-20b'
    ollama_url: str = 'http://ollama:11434'
    ollama_model: str = 'llama3.2:1b'
    request_timeout_seconds: float = Field(default=10.0, gt=0, le=10.0)
    trusted_proxy_cidrs: str = '127.0.0.1/32'
    triage_cache_ttl_seconds: int = 86400
    stats_cache_ttl_seconds: int = 30
    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 60
    simulated_failure_mode: str = 'none'

    @field_validator('trusted_proxy_cidrs')
    @classmethod
    def validate_trusted_proxy_cidrs(cls, value: str) -> str:
        from ipaddress import ip_network

        for cidr in (item.strip() for item in value.split(',') if item.strip()):
            ip_network(cidr)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
