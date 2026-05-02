#!/usr/bin/env python3
"""
Скрипт первоначальной настройки Local AI Agent
- Создание .env из примера
- Скачивание моделей (эмбеддинги, whisper, tts)
- Создание необходимых директорий и БД
"""
import os
import sys
import shutil
from pathlib import Path


def create_env_file():
    """Создание .env файла из примера"""
    env_example = Path("config/.env.example")
    env_file = Path("config/.env")
    
    if env_file.exists():
        print(f"Файл {env_file} уже существует")
        return True
    
    if not env_example.exists():
        print(f"Файл {env_example} не найден")
        return False
    
    try:
        shutil.copy(env_example, env_file)
        print(f"Создан файл {env_file}")
        print(f"  Отредактируйте его: nano {env_file}")
        return True
    except Exception as e:
        print(f"Ошибка создания .env: {e}")
        return False


def create_directories():
    """Создание необходимых директорий"""
    dirs = [
        "./data",
        "./data/embeddings",
        "./data/whisper",
        "./data/piper",
        "./data/coqui",
        "./logs"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"Создана директория: {dir_path}")
    
    return True


def download_embedding_model():
    """Скачивание модели эмбеддингов"""
    print("\nСкачивание модели эмбеддингов...")
    try:
        from sentence_transformers import SentenceTransformer
        
        model_name = "all-MiniLM-L6-v2"
        save_path = "./data/embeddings"
        
        print(f"  Модель: {model_name}")
        print(f"  Сохранение в: {save_path}")
        
        model = SentenceTransformer(model_name)
        model.save(save_path)
        
        print("Модель эмбеддингов скачана и сохранена")
        return True
    except Exception as e:
        print(f"Ошибка скачивания эмбеддингов: {e}")
        return False


def download_whisper_model():
    """Скачивание модели Whisper"""
    print("\nСкачивание модели Whisper (base)...")
    try:
        import whisper
        
        model_name = "base"
        print(f"  Модель: {model_name}")
        print(f"  Кэш: ~/.cache/whisper/")
        
        model = whisper.load_model(model_name)
        
        print("Модель Whisper скачана")
        return True
    except Exception as e:
        print(f"Ошибка скачивания Whisper: {e}")
        return False


def download_piper_model():
    """Подготовка директории для Piper TTS"""
    print("\nПодготовка для Piper TTS...")
    try:
        piper_dir = Path("./data/piper")
        piper_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Директория для Piper: {piper_dir}")
        print(f"  Установите piper: pip install piper-tts")
        print(f"  Модели будут скачиваться при первом использовании")
        return True
    except Exception as e:
        print(f"Ошибка подготовки Piper: {e}")
        return False


def initialize_faiss_index():
    """Инициализация FAISS индекса"""
    print("\nИнициализация векторной БД (FAISS)...")
    try:
        import faiss
        import numpy as np
        from sentence_transformers import SentenceTransformer
        
        # Загрузка модели эмбеддингов
        model_path = "./data/embeddings"
        if Path(model_path).exists():
            model = SentenceTransformer(model_path)
        else:
            model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Создание индекса
        dimension = model.get_sentence_embedding_dimension()
        index = faiss.IndexFlatL2(dimension)
        
        # Сохранение
        index_path = "./data/faiss_index"
        faiss.write_index(index, index_path)
        
        # Сохранение пустого списка документов
        import pickle
        with open(index_path + ".docs", 'wb') as f:
            pickle.dump([], f)
        
        print(f"FAISS индекс создан: {index_path}")
        print(f"  Размерность: {dimension}")
        return True
    except Exception as e:
        print(f"Ошибка инициализации FAISS: {e}")
        return False


def main():
    print("=" * 60)
    print("НАСТРОЙКА LOCAL AI AGENT")
    print("=" * 60)
    print()
    
    # Переход в корневую директорию проекта
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    print(f"Рабочая директория: {script_dir}")
    print()
    
    success = True
    
    # 1. Создание .env
    print("1. Создание .env файла...")
    success = create_env_file() and success
    print()
    
    # 2. Создание директорий
    print("2. Создание директорий...")
    success = create_directories() and success
    print()
    
    # 3. Скачивание эмбеддингов
    print("3. Скачивание модели эмбеддингов...")
    response = input("   Скачать? (y/n) [y]: ").strip().lower()
    if response in ['', 'y', 'yes']:
        success = download_embedding_model() and success
    else:
        print("   Пропущено")
    print()
    
    # 4. Скачивание Whisper
    print("4. Скачивание модели Whisper (base)...")
    response = input("   Скачать? (y/n) [y]: ").strip().lower()
    if response in ['', 'y', 'yes']:
        success = download_whisper_model() and success
    else:
        print("   Пропущено")
    print()
    
    # 5. Подготовка Piper
    print("5. Подготовка Piper TTS...")
    success = download_piper_model() and success
    print()
    
    # 6. Инициализация FAISS
    print("6. Инициализация векторной БД...")
    response = input("   Создать БД? (y/n) [y]: ").strip().lower()
    if response in ['', 'y', 'yes']:
        success = initialize_faiss_index() and success
    else:
        print("   Пропущено")
    print()
    
    # Итог
    print("=" * 60)
    if success:
        print("НАСТРОЙКА ЗАВЕРШЕНА УСПЕШНО!")
        print()
        print("Следующие шаги:")
        print("1. Отредактируйте config/.env (добавьте API ключи)")
        print("2. Запустите API сервер: ./scripts/manage.sh start")
        print("3. Или запустите интерфейс: python -m interfaces.run_interface --type cli")
    else:
        print("НАСТРОЙКА ЗАВЕРШЕНА С ОШИБКАМИ")
        print("   Проверьте вывод выше")
    print("=" * 60)


if __name__ == "__main__":
    main()
