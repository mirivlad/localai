from typing import Dict, Any
from .base import BaseModelProvider
from .openai_compatible import OpenAICompatibleProvider


class ModelFactory:
    """Фабрика для создания провайдеров моделей"""
    
    @staticmethod
    def create_provider(config: Dict[str, Any]) -> BaseModelProvider:
        """Создание провайдера по конфигурации"""
        provider_type = config.get("provider", "openai_compatible")
        name = config.get("name", "default")
        
        if provider_type == "openai_compatible":
            return OpenAICompatibleProvider(name, config)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    @staticmethod
    def create_from_config_list(configs: list) -> Dict[str, BaseModelProvider]:
        """Создание всех провайдеров из списка конфигураций"""
        providers = {}
        for config in configs:
            provider = ModelFactory.create_provider(config)
            providers[provider.name] = provider
        return providers
