from typing import Dict, Optional, Callable
from pythonbot.providers.base import BaseProvider


class ProviderRegistry:
    def __init__(self):
        self._factories: Dict[str, Callable[[], BaseProvider]] = {}
        self._instances: Dict[str, BaseProvider] = {}
        self.active_provider: Optional[str] = None

    def register(self, name: str, factory: Callable[[], BaseProvider]) -> None:
        """Register a provider factory (callable that returns a BaseProvider instance)."""
        self._factories[name] = factory

    def register_instance(self, name: str, instance: BaseProvider) -> None:
        """Register a pre-created provider instance directly."""
        self._instances[name] = instance
        # Also register a dummy factory so set_active/has checks work
        self._factories[name] = lambda: instance

    def get_provider(self, name: str) -> Optional[BaseProvider]:
        """Get provider by name, instantiating lazily if needed."""
        if name not in self._instances and name in self._factories:
            self._instances[name] = self._factories[name]()
        return self._instances.get(name)

    def set_active(self, name: str) -> bool:
        if name in self._factories:
            self.active_provider = name
            return True
        return False

    def list_providers(self) -> list[str]:
        return list(self._factories.keys())


# Global registry instance
registry = ProviderRegistry()
