import json
import os
from pathlib import Path

# Built-in config defaults
DEFAULT_CONFIGS = {
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", str(Path.home() / "Desktop")]
    },
    "brave_search": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "env": {"BRAVE_API_KEY": ""}
    },
    "playwright": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-playwright"]
    },
    "postgres": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost/db"]
    },
    "sequential_thinking": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": ""}
    }
}

class MCPRegistry:
    def __init__(self):
        from pythonbot.core.config import CONFIG_DIR
        self.config_dir = CONFIG_DIR / "mcp_configs"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.active_clients = {}
        self._init_defaults()

    def _init_defaults(self):
        for name, config in DEFAULT_CONFIGS.items():
            file_path = self.config_dir / f"{name}.json"
            if not file_path.exists():
                with open(file_path, "w") as f:
                    json.dump(config, f, indent=4)

    def list_configs(self):
        configs = []
        for file in self.config_dir.glob("*.json"):
            configs.append(file.stem)
        return configs
        
    def get_config(self, name: str):
        file_path = self.config_dir / f"{name}.json"
        if file_path.exists():
            with open(file_path, "r") as f:
                return json.load(f)
        return None

mcp_registry = MCPRegistry()
