"""Configuration management for NotaBene."""
from pathlib import Path
from typing import Any

import yaml


class Config:
    """Configuration manager for NotaBene."""

    def __init__(self, config_path: str | Path | None = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to YAML configuration file.
                        If None, uses default config.
        """
        self.config_path = Path(config_path) if config_path else None
        self._config: dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from file or use defaults."""
        if self.config_path and self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        else:
            # Default configuration
            self._config = self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """
        Get default configuration.

        Returns:
            Default configuration dictionary
        """
        home = Path.home()
        notabene_dir = home / ".notabene"

        return {
            "database": {
                "path": str(notabene_dir / "notabene.db"),
            },
            "storage": {
                "pdf_directory": str(notabene_dir / "pdfs"),
            },
            "extraction": {
                "pdf": {
                    "max_pages_for_abstract": 3,
                    "abstract_keywords": ["abstract", "résumé", "summary"],
                },
                "web": {
                    "timeout": 30,
                    "user_agent": "NotaBene/0.1.0",
                },
            },
            "search": {
                "max_results": 50,
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key (supports dot notation, e.g., 'database.path')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self, path: str | Path | None = None):
        """
        Save configuration to file.

        Args:
            path: Path to save configuration. If None, uses config_path.
        """
        save_path = Path(path) if path else self.config_path

        if save_path is None:
            raise ValueError("No path specified for saving configuration")

        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, "w", encoding="utf-8") as f:
            yaml.dump(self._config, f, default_flow_style=False, indent=2)

    @property
    def db_path(self) -> Path:
        """Get database path."""
        return Path(self.get("database.path"))

    @property
    def pdf_directory(self) -> Path:
        """Get PDF storage directory."""
        return Path(self.get("storage.pdf_directory"))


# Global config instance
_config_instance: Config | None = None


def init_config(config_path: str | Path | None = None) -> Config:
    """
    Initialize global configuration.

    Args:
        config_path: Path to configuration file

    Returns:
        Config instance
    """
    global _config_instance
    _config_instance = Config(config_path)
    return _config_instance


def get_config() -> Config:
    """
    Get global configuration instance.

    Returns:
        Config instance

    Raises:
        RuntimeError: If config not initialized
    """
    if _config_instance is None:
        # Auto-initialize with defaults if not done
        return init_config()
    return _config_instance
