import os
import yaml
from typing import Dict, Any, List
from pathlib import Path


def load_providers_config(config_path: str = None) -> List[Dict[str, Any]]:
    """Загрузка конфигурации провайдеров из YAML или переменных окружения"""
    
    # Если указан путь к YAML файлу
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('providers', [])
    
    # Иначе загружаем из переменных окружения
    providers = []
    
    # OpenAI
    if os.getenv('OPENAI_API_KEY'):
        providers.append({
            'name': 'openai',
            'provider': 'openai_compatible',
            'base_url': os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
            'api_key': os.getenv('OPENAI_API_KEY'),
            'default_model': os.getenv('OPENAI_DEFAULT_MODEL', 'gpt-3.5-turbo')
        })
    
    # OpenRouter
    if os.getenv('OPENROUTER_API_KEY'):
        providers.append({
            'name': 'openrouter',
            'provider': 'openai_compatible',
            'base_url': os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1'),
            'api_key': os.getenv('OPENROUTER_API_KEY'),
            'default_model': os.getenv('OPENROUTER_DEFAULT_MODEL', 'deepseek/deepseek-chat')
        })
    
    # Local LLM (llama.cpp / LM Studio)
    local_url = os.getenv('LOCAL_LLM_BASE_URL')
    if local_url:
        providers.append({
            'name': 'local_llm',
            'provider': 'openai_compatible',
            'base_url': local_url,
            'api_key': os.getenv('LOCAL_LLM_API_KEY', 'sk-no-key-required'),
            'default_model': os.getenv('LOCAL_LLM_DEFAULT_MODEL', 'local-model')
        })
    
    # GigaChat
    gigachat_client_id = os.getenv('GIGACHAT_CLIENT_ID')
    gigachat_client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')
    if gigachat_client_id and gigachat_client_secret:
        providers.append({
            'name': 'gigachat',
            'provider': 'gigachat',
            'client_id': gigachat_client_id,
            'client_secret': gigachat_client_secret,
            'profile': os.getenv('GIGACHAT_PROFILE', 'default'),
            'model': os.getenv('GIGACHAT_MODEL', 'GigaChat-Pro')
        })
    
    # YandexGPT
    yandex_folder_id = os.getenv('YANDEX_FOLDER_ID')
    yandex_api_key = os.getenv('YANDEX_API_KEY')
    if yandex_folder_id and yandex_api_key:
        providers.append({
            'name': 'yandexgpt',
            'provider': 'yandexgpt',
            'folder_id': yandex_folder_id,
            'api_key': yandex_api_key,
            'model': os.getenv('YANDEX_GPT_MODEL', 'yandexgpt-lite')
        })
    
    return providers


def get_fallback_chain() -> List[str]:
    """Получение цепочки fallback из конфигурации"""
    chain = os.getenv('FALLBACK_CHAIN', 'local_llm,openrouter,openai,gigachat,yandexgpt')
    return [x.strip() for x in chain.split(',')]
