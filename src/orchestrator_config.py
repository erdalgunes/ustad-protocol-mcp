"""Configuration management for the Sequential Thinking Orchestrator.
Provides environment-based configuration with sensible defaults.
"""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class OrchestratorConfig:
    """Main configuration for the orchestrator"""

    # Model selection
    default_model: str = "local"
    fallback_model: str = "local"
    enable_gpt5: bool = False
    enable_o3: bool = False
    enable_deepseek: bool = False

    # Performance
    max_thinking_time: int = 30  # seconds
    max_reasoning_tokens: int = 4000
    cache_responses: bool = True
    cache_ttl: int = 300  # 5 minutes

    # Security
    require_api_keys: bool = False
    sanitize_inputs: bool = True
    log_api_calls: bool = True
    mask_sensitive_data: bool = True

    # Rate limiting
    rate_limit_enabled: bool = True
    requests_per_minute: int = 20
    requests_per_hour: int = 100
    requests_per_day: int = 1000

    # Cost management
    cost_tracking_enabled: bool = True
    max_cost_per_request: float = 0.10
    max_cost_per_hour: float = 1.00
    max_cost_per_day: float = 10.00
    cost_warning_threshold: float = 0.80

    # CBT/HiTOP features
    enable_reality_testing: bool = True
    enable_bias_detection: bool = True
    enable_maintenance_factors: bool = True
    enable_dimensional_assessment: bool = True

    # Development
    debug_mode: bool = False
    verbose_logging: bool = False
    save_reasoning_chains: bool = False

    @classmethod
    def from_env(cls) -> "OrchestratorConfig":
        """Load configuration from environment variables"""
        config = cls()

        # Override with environment variables
        env_mappings = {
            "ORCHESTRATOR_DEFAULT_MODEL": "default_model",
            "ORCHESTRATOR_ENABLE_GPT5": "enable_gpt5",
            "ORCHESTRATOR_ENABLE_O3": "enable_o3",
            "ORCHESTRATOR_MAX_THINKING_TIME": "max_thinking_time",
            "ORCHESTRATOR_MAX_REASONING_TOKENS": "max_reasoning_tokens",
            "ORCHESTRATOR_CACHE_RESPONSES": "cache_responses",
            "ORCHESTRATOR_RATE_LIMIT_ENABLED": "rate_limit_enabled",
            "ORCHESTRATOR_REQUESTS_PER_MINUTE": "requests_per_minute",
            "ORCHESTRATOR_REQUESTS_PER_HOUR": "requests_per_hour",
            "ORCHESTRATOR_COST_TRACKING_ENABLED": "cost_tracking_enabled",
            "ORCHESTRATOR_MAX_COST_PER_REQUEST": "max_cost_per_request",
            "ORCHESTRATOR_MAX_COST_PER_DAY": "max_cost_per_day",
            "ORCHESTRATOR_DEBUG_MODE": "debug_mode",
            "ORCHESTRATOR_VERBOSE_LOGGING": "verbose_logging",
        }

        for env_key, attr_name in env_mappings.items():
            if env_key in os.environ:
                value = os.environ[env_key]
                current_type = type(getattr(config, attr_name))

                # Type conversion using isinstance
                current_value = getattr(config, attr_name)
                if isinstance(current_value, bool):
                    setattr(config, attr_name, value.lower() in ("true", "1", "yes"))
                elif isinstance(current_value, int):
                    setattr(config, attr_name, int(value))
                elif isinstance(current_value, float):
                    setattr(config, attr_name, float(value))
                else:
                    setattr(config, attr_name, value)

        return config

    @classmethod
    def from_file(cls, path: str) -> "OrchestratorConfig":
        """Load configuration from JSON file"""
        config_path = Path(path)
        if not config_path.exists():
            return cls()

        with Path(config_path).open() as f:
            data = json.load(f)

        return cls(**data)

    def save_to_file(self, path: str):
        """Save configuration to JSON file"""
        config_path = Path(path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with Path(config_path).open("w") as f:
            json.dump(asdict(self), f, indent=2)

    def validate(self) -> tuple[bool, list[str]]:
        """Validate configuration settings"""
        errors = []

        # Validate rate limits
        if self.rate_limit_enabled:
            if self.requests_per_minute <= 0:
                errors.append("requests_per_minute must be positive")
            if self.requests_per_hour <= 0:
                errors.append("requests_per_hour must be positive")
            if self.requests_per_day <= 0:
                errors.append("requests_per_day must be positive")

            # Logical consistency
            if self.requests_per_minute * 60 < self.requests_per_hour:
                errors.append("requests_per_minute * 60 should be >= requests_per_hour")
            if self.requests_per_hour * 24 < self.requests_per_day:
                errors.append("requests_per_hour * 24 should be >= requests_per_day")

        # Validate costs
        if self.cost_tracking_enabled:
            if self.max_cost_per_request <= 0:
                errors.append("max_cost_per_request must be positive")
            if self.max_cost_per_hour <= 0:
                errors.append("max_cost_per_hour must be positive")
            if self.max_cost_per_day <= 0:
                errors.append("max_cost_per_day must be positive")
            if not 0 < self.cost_warning_threshold <= 1:
                errors.append("cost_warning_threshold must be between 0 and 1")

        # Validate model configuration
        valid_models = ["local", "gpt-5", "gpt-5-thinking", "o3", "deepseek-r1"]
        if self.default_model not in valid_models:
            errors.append(f"default_model must be one of {valid_models}")
        if self.fallback_model not in valid_models:
            errors.append(f"fallback_model must be one of {valid_models}")

        # Validate performance settings
        if self.max_thinking_time <= 0:
            errors.append("max_thinking_time must be positive")
        if self.max_reasoning_tokens <= 0:
            errors.append("max_reasoning_tokens must be positive")
        if self.cache_ttl < 0:
            errors.append("cache_ttl must be non-negative")

        return len(errors) == 0, errors

    def get_model_config(self, model: str) -> dict[str, Any]:
        """Get configuration specific to a model"""
        configs = {
            "local": {"max_tokens": 4000, "temperature": 0.7, "timeout": 10},
            "gpt-5": {
                "max_tokens": self.max_reasoning_tokens,
                "temperature": 0.7,
                "timeout": self.max_thinking_time,
                "reasoning_effort": "medium",
            },
            "gpt-5-thinking": {
                "max_tokens": self.max_reasoning_tokens * 2,
                "temperature": 0.7,
                "timeout": self.max_thinking_time,
                "reasoning_effort": "high",
            },
            "o3": {
                "max_tokens": self.max_reasoning_tokens,
                "temperature": 0.5,
                "timeout": self.max_thinking_time,
            },
            "deepseek-r1": {
                "max_tokens": self.max_reasoning_tokens,
                "temperature": 0.7,
                "timeout": self.max_thinking_time,
            },
        }

        return configs.get(model, configs["local"])

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def __str__(self) -> str:
        """String representation"""
        return json.dumps(self.to_dict(), indent=2)


class ConfigManager:
    """Manages configuration with multiple sources"""

    def __init__(self):
        self.config: OrchestratorConfig | None = None
        self._load_config()

    def _load_config(self):
        """Load configuration from multiple sources in priority order"""
        # 1. Start with defaults
        self.config = OrchestratorConfig()

        # 2. Override with config file if exists
        config_locations = [
            Path.home() / ".orchestrator" / "config.json",
            Path.cwd() / "orchestrator.config.json",
            Path.cwd() / ".orchestrator.json",
        ]

        for location in config_locations:
            if location.exists():
                try:
                    self.config = OrchestratorConfig.from_file(str(location))
                    break
                except Exception:
                    # Continue with defaults if file is invalid
                    # This is intentional - we want to use defaults if config file has errors
                    continue

        # 3. Override with environment variables (highest priority)
        env_config = OrchestratorConfig.from_env()
        # Merge env config with existing
        for key, value in asdict(env_config).items():
            if os.environ.get(f"ORCHESTRATOR_{key.upper()}"):
                setattr(self.config, key, value)

        # 4. Validate final configuration
        valid, errors = self.config.validate()
        if not valid:
            error_msg = f"Invalid configuration: {', '.join(errors)}"
            raise ValueError(error_msg)

    def get(self) -> OrchestratorConfig:
        """Get current configuration"""
        if not self.config:
            self._load_config()
        return self.config

    def reload(self):
        """Reload configuration from sources"""
        self._load_config()

    def set(self, key: str, value: Any):
        """Set a configuration value"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
        else:
            error_msg = f"Unknown configuration key: {key}"
            raise ValueError(error_msg)

    def save(self, path: str | None = None):
        """Save current configuration to file"""
        if not path:
            path = str(Path.home() / ".orchestrator" / "config.json")
        self.config.save_to_file(path)


# Global config manager instance
config_manager = ConfigManager()


def get_config() -> OrchestratorConfig:
    """Get global configuration"""
    return config_manager.get()


def reload_config():
    """Reload configuration from sources"""
    config_manager.reload()


def set_config(key: str, value: Any):
    """Set a configuration value"""
    config_manager.set(key, value)
