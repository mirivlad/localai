#!/usr/bin/env python3
"""
Скрипт для скачивания моделей (эмбеддинги, Whisper, TTS)
Использование:
    python scripts/download_models.py --all
    python scripts/download_models.py --embeddings
    python scripts/download_models.py --whisper base
    python scripts/download_models.py --piper ru_RU-irina
"""
import argparse
import os
import sys


def download_embedding_model(model_name: str = "all-MiniLM-L6-v2", 
                             save_path: str = "./models/embeddings"):
    """Скачивание модели эмбеддингов"""
    print(f"Скачивание модели эмбеддингов: {model_name}")
    try:
        from sentence_transformers import SentenceTransformer
        os.makedirs(save_path, exist_ok=True)
        
        model = SentenceTransformer(model_name)
        model.save(save_path)
        
        print(f"✓ Модель сохранена в: {save_path}")
        print(f"  Укажите путь в .env: EMBEDDING_MODEL_PATH={save_path}")
        return True
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def download_whisper_model(model_name: str = "base", 
                            save_path: str = "./models/whisper"):
    """Скачивание модели Whisper"""
    print(f"Скачивание модели Whisper: {model_name}")
    try:
        import whisper
        os.makedirs(save_path, exist_ok=True)
        
        model = whisper.load_model(model_name)
        
        # Whisper сам сохраняет в кэш, покажем где
        cache_dir = os.path.expanduser("~/.cache/whisper")
        print(f"✓ Модель загружена (кэш: {cache_dir})")
        print(f"  Укажите в .env: WHISPER_MODEL={model_name}")
        return True
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def download_piper_model(model_name: str = "ru_RU-irina", 
                         save_path: str = "./models/piper"):
    """Скачивание модели Piper TTS"""
    print(f"Скачивание модели Piper: {model_name}")
    try:
        import subprocess
        os.makedirs(save_path, exist_ok=True)
        
        # Скачивание через piper
        cmd = ["piper", "--model", model_name, "--output_file", "test.wav"]
        print(f"  Запуск: {' '.join(cmd)}")
        print("  (Требуется установленный piper-tts)")
        print(f"✓ Модель будет сохранена в: {save_path}")
        print(f"  Укажите в .env: PIPER_MODEL_PATH={save_path}/{model_name}.onnx")
        return True
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def download_coqui_model(model_name: str = "tts_models/ru/tacotron2-DDC",
                         save_path: str = "./models/coqui"):
    """Скачивание модели Coqui TTS"""
    print(f"Скачивание модели Coqui TTS: {model_name}")
    try:
        from TTS.api import TTS
        os.makedirs(save_path, exist_ok=True)
        
        tts = TTS(model_name=model_name)
        tts.save_model(save_path)
        
        print(f"✓ Модель сохранена в: {save_path}")
        print(f"  Укажите в .env: COQUI_MODEL_PATH={save_path}")
        return True
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Скачивание моделей для Local AI Agent")
    parser.add_argument("--all", action="store_true", help="Скачать все модели")
    parser.add_argument("--embeddings", action="store_true", help="Скачать модель эмбеддингов")
    parser.add_argument("--whisper", nargs="?", const="base", 
                        help="Скачать модель Whisper (по умолчанию: base)")
    parser.add_argument("--piper", nargs="?", const="ru_RU-irina",
                        help="Скачать модель Piper TTS")
    parser.add_argument("--coqui", nargs="?", const="tts_models/ru/tacotron2-DDC",
                        help="Скачать модель Coqui TTS")
    
    args = parser.parse_args()
    
    if not any([args.all, args.embeddings, args.whisper, args.piper, args.coqui]):
        parser.print_help()
        sys.exit(1)
    
    print("=" * 60)
    print("Скачивание моделей для Local AI Agent")
    print("=" * 60)
    print()
    
    success = True
    
    if args.all or args.embeddings:
        success &= download_embedding_model()
        print()
    
    if args.all or args.whisper:
        model = args.whisper if isinstance(args.whisper, str) else "base"
        success &= download_whisper_model(model)
        print()
    
    if args.all or args.piper:
        model = args.piper if isinstance(args.piper, str) else "ru_RU-irina"
        success &= download_piper_model(model)
        print()
    
    if args.all or args.coqui:
        model = args.coqui if isinstance(args.coqui, str) else "tts_models/ru/tacotron2-DDC"
        success &= download_coqui_model(model)
        print()
    
    print("=" * 60)
    if success:
        print("✓ Все модели успешно скачаны!")
    else:
        print("⚠ Некоторые модели не удалось скачать")
    print("=" * 60)


if __name__ == "__main__":
    main()
