"""
Configuration management for TripGenie
"""
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """Central configuration"""
    
    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    AMADEUS_API_KEY: str = os.getenv("AMADEUS_API_KEY", "")
    AMADEUS_API_SECRET: str = os.getenv("AMADEUS_API_SECRET", "")
    
    # Model Configuration
    PRIMARY_MODEL: str = os.getenv("PRIMARY_MODEL", "claude-sonnet-4-20250514")
    SECONDARY_MODEL: str = os.getenv("SECONDARY_MODEL", "claude-sonnet-4-20250514")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.0"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4000"))
    
    # System Configuration
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "true").lower() == "true"
    
    # Cost Tracking (per 1M tokens)
    CLAUDE_SONNET_INPUT_COST: float = 3.0  # $3 per 1M input tokens
    CLAUDE_SONNET_OUTPUT_COST: float = 15.0  # $15 per 1M output tokens
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set")
        return True

config = Config()
