from typing import Dict, Any
from .base import BaseModelProvider
from .openai_compatible import OpenAICompatibleProvider
from .gigachat_provider import GigaChatProvider
from .yandexgpt_provider import YandexGPTProvider


class ModelFactory:
    """Фабрика для создания провайдеров моделей"""
    
    @staticmethod
    def create_provider(config: Dict[str, Any]) -> BaseModelProvider:
        """Создание провайдера по конфигурации"""
        provider_type = config.get("provider", "openai_compatible")
        name = config.get("name", "default")
        
        if provider_type == "openai_compatible":
            return OpenAICompatibleProvider(name, config)
        elif provider_type == "gigachat":
            return GigaChatProvider(name, config)
        elif provider_type == "yandexgpt":
            return YandexGPTProvider(name, config)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    @staticmethod
    def create_from_config_list(configs: list) -> Dict[str, BaseModelProvider]:
        """Создание всех провайдеров из списка конфигураций"""
        providers = {}
        for config in configs:
            try:
                provider = ModelFactory.create_provider(config)
                providers[provider.name] = provider
            except Exception as e:
                print(f"Failed to create provider {config.get('name', 'unknown')}: {e}")
        return providers
