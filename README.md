# Local AI Agent

Локальная агентная платформа с поддержкой мультимодельности, мультиагентности и инструментов. Система может работать с локальными моделями (через LM Studio / llama.cpp) и облачными провайдерами (OpenAI, OpenRouter, GigaChat, YandexGPT).

## 📋 Содержание

1. [Что нужно скачать](#1-что-нужно-скачать)
2. [Установка](#2-установка)
3. [Настройка провайдеров](#3-настройка-провайдеров)
4. [Запуск локальных моделей (LM Studio)](#4-запуск-локальных-моделей-lm-studio)
5. [Подключение GigaChat](#5-подключение-gigachat)
6. [Подключение YandexGPT](#6-подключение-yandexgpt)
7. [Запуск системы](#7-запуск-системы)
8. [Интерфейсы](#8-интерфейсы)
9. [Голосовые функции](#9-голосовые-функции)
10. [Проверка работы](#10-проверка-работы)
11. [Структура проекта](#11-структура-проекта)

---

## 1. Что нужно скачать

### Обязательно:
- **Python 3.10+** — [python.org](https://python.org)
- **Git** — [git-scm.com](https://git-scm.com)

### Для локальных моделей (опционально):
- **LM Studio** (рекомендуется для новичков) — [lmstudio.ai](https://lmstudio.ai)
  - Позволяет скачивать и запускать модели одним кликом
  - Автоматически создает OpenAI-совместимый API

### Для голосовых функций (опционально):
- **Piper TTS** — устанавливается через pip (см. ниже)
- **Whisper** — скачивается автоматически при первом использовании

---

## 2. Установка

### Клонирование репозитория:
```bash
git clone https://git.mirv.top/mirivlad/local_ai.git
cd local_ai
```

### Создание виртуального окружения:
```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Установка зависимостей:
```bash
pip install -r requirements.txt
```

> **Примечание:** Для голосовых функций (Whisper, TTS) могут потребоваться дополнительные библиотеки. Они установятся автоматически с `requirements.txt`.

---

## 3. Настройка провайдеров

Система поддерживает два способа настройки провайдеров:

### Способ 1: Через переменные окружения (`.env`)

Создайте файл `config/.env`:

```bash
cp config/.env.example config/.env  # Если есть пример
# Или создайте вручную
nano config/.env
```

Пример содержимого `config/.env`:

```bash
# ========== OpenAI ==========
OPENAI_API_KEY=sk-your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_DEFAULT_MODEL=gpt-3.5-turbo

# ========== OpenRouter ==========
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=deepseek/deepseek-chat

# ========== Локальная модель (LM Studio / llama.cpp) ==========
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
LOCAL_LLM_API_KEY=sk-no-key-required
LOCAL_LLM_DEFAULT_MODEL=local-model

# ========== Telegram бот (опционально) ==========
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# ========== Порядок fallback (если модель недоступна) ==========
FALLBACK_CHAIN=local_llm,openrouter,openai
```

### Способ 2: Через YAML файл (`providers.yaml`)

Создайте файл `config/providers.yaml`:

```yaml
providers:
  - name: "openai"
    provider: "openai_compatible"
    base_url: "https://api.openai.com/v1"
    api_key: "sk-your-openai-key"
    default_model: "gpt-3.5-turbo"

  - name: "openrouter"
    provider: "openai_compatible"
    base_url: "https://openrouter.ai/api/v1"
    api_key: "sk-or-v1-..."
    default_model: "deepseek/deepseek-chat"

  - name: "local_llm"
    provider: "openai_compatible"
    base_url: "http://localhost:1234/v1"
    api_key: "sk-no-key-required"
    default_model: "local-model"

fallback_chain: ["local_llm", "openrouter", "openai"]
```

> **Приоритет:** Сначала проверяются переменные окружения, затем YAML файл.

---

## 4. Запуск локальных моделей (LM Studio)

LM Studio — самый простой способ запустить локальные модели.

### Шаг 1: Установка LM Studio
Скачайте и установите с [lmstudio.ai](https://lmstudio.ai)

### Шаг 2: Скачивание модели
1. Откройте LM Studio
2. Перейдите в раздел "Discover" (лупа)
3. Найдите модель (рекомендую: `Mistral 7B Instruct`, `Llama 3 8B`)
4. Нажмите "Download"

### Шаг 3: Запуск сервера
1. Перейдите во вкладку "Developer" (скобки `</>`)
2. Выберите скачанную модель в выпадающем списке
3. Нажмите "Start Server"
4. Сервер запустится на `http://localhost:1234/v1`

### Шаг 4: Настройка в конфиге
В `config/.env` пропишите:

```bash
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
LOCAL_LLM_API_KEY=sk-no-key-required  # LM Studio не требует ключ
LOCAL_LLM_DEFAULT_MODEL= mistral-7b-instruct  # Имя модели (любое)
```

### Шаг 5: Проверка
```bash
curl http://localhost:1234/v1/models
```

---

## 5. Подключение GigaChat

### Шаг 1: Получение доступов
1. Зарегистрируйтесь в [GigaChat](https://developers.sber.ru/gigachat)
2. Создайте приложение в личном кабинете
3. Получите `CLIENT_ID` и `CLIENT_SECRET`

### Шаг 2: Установка библиотеки
```bash
pip install gigachat
```

### Шаг 3: Настройка
В `config/.env` добавьте:

```bash
GIGACHAT_CLIENT_ID=your-client-id
GIGACHAT_CLIENT_SECRET=your-client-secret
GIGACHAT_PROFILE=default  # Или имя вашего профиля
GIGACHAT_MODEL=GigaChat-Pro  # Или GigaChat, GigaChat-Max
```

В `config/providers.yaml` добавьте:

```yaml
  - name: "gigachat"
    provider: "gigachat"
    client_id: "${GIGACHAT_CLIENT_ID}"
    client_secret: "${GIGACHAT_CLIENT_SECRET}"
    model: "GigaChat-Pro"
```

---

## 6. Подключение YandexGPT

### Шаг 1: Получение доступов
1. Зарегистрирутесь в [Yandex Cloud](https://cloud.yandex.ru)
2. Создайте сервисный аккаунт
3. Получите `API_KEY` и `FOLDER_ID`

### Шаг 2: Установка библиотеки
```bash
pip install yandexcloud
```

### Шаг 3: Настройка
В `config/.env` добавьте:

```bash
YANDEX_FOLDER_ID=your-folder-id
YANDEX_API_KEY=your-api-key
YANDEX_GPT_MODEL=yandexgpt-lite  # Или yandexgpt, yandexgpt-large
```

В `config/providers.yaml` добавьте:

```yaml
  - name: "yandexgpt"
    provider: "yandexgpt"
    folder_id: "${YANDEX_FOLDER_ID}"
    api_key: "${YANDEX_API_KEY}"
    model: "yandexgpt-lite"
```

---

## 7. Запуск системы

### Запуск API сервера

**Способ 1: Через скрипт управления**
```bash
./scripts/manage.sh start    # Запуск
./scripts/manage.sh stop     # Остановка
./scripts/manage.sh restart  # Перезапуск
./scripts/manage.sh status   # Статус
./scripts/manage.sh logs     # Показать логи
```

**Способ 2: Напрямую через uvicorn**
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Способ 3: Как systemd сервис**
```bash
# Копирование unit файла
sudo cp scripts/local-ai-agent.service /etc/systemd/system/

# Редактирование (при необходимости изменить пути и пользователя)
sudo nano /etc/systemd/system/local-ai-agent.service

# Запуск
sudo systemctl daemon-reload
sudo systemctl enable local-ai-agent
sudo systemctl start local-ai-agent

# Проверка статуса
sudo systemctl status local-ai-agent
```

---

## 8. Интерфейсы

Система поддерживает несколько интерфейсов:

### CLI (командная строка)
```bash
python -m interfaces.run_interface --type cli
```
- Вводите сообщения в консоль
- Команда `new` — новая сессия
- Команда `exit` или `quit` — выход

### Telegram бот
```bash
python -m interfaces.run_interface --type telegram --token YOUR_BOT_TOKEN
```
- Получите токен у [@BotFather](https://t.me/BotFather)
- Укажите токен в команде или в `config/.env` как `TELEGRAM_BOT_TOKEN`
- Команды бота: `/start`, `/new`

### Web UI (браузер)
```bash
python -m interfaces.run_interface --type web --port 8080
```
- Откройте в браузере: `http://localhost:8080`
- Простой чат интерфейс для тестирования

---

## 9. Голосовые функции

### Настройка STT (Speech-to-Text)
Используется Whisper (локально или через API):

- **Локально:** Модель скачается автоматически при первом запуске
- **Облако (OpenAI API):** Укажите `OPENAI_API_KEY` в `.env`

### Настройка TTS (Text-to-Speech)
Два варианта:

**Piper TTS (быстрый, локальный):**
```bash
pip install piper-tts
# Piper будет использоваться по умолчанию
```

**Coqui TTS (качественный, локальный):**
```bash
pip install TTS
# Потребуется скачивание моделей при первом запуске
```

### Использование в интерфейсах
Пока голосовые функции доступны через API эндпоинт `/voice`. Интеграция с Telegram и Web UI появится в следующих обновлениях.

---

## 10. Проверка работы

### Проверка статуса API:
```bash
curl http://localhost:8000/
```

### Тест чата:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "content": "Привет! Как дела?"}'
```

### Получение списка провайдеров:
```bash
curl http://localhost:8000/providers
```

### Health check:
```bash
curl http://localhost:8000/health
```

---

## 11. Структура проекта

```
local_ai/
├── api/                # FastAPI приложение (эндпоинты)
├── orchestrator/       # Оркестратор (роутер, контекст, исполнение)
│   ├── router.py       # Маршрутизация запросов (LLM classifier)
│   ├── context_builder.py  # Сбор контекста
│   ├── execution_manager.py  # Multi-step reasoning loop
│   └── state_tracker.py   # Логирование состояний
├── agents/            # Субагенты (Chat, Code, Operator, etc.)
│   ├── base.py        # Базовый класс агента
│   ├── chat_agent.py  # Диалоговый агент
│   ├── code_agent.py  # Кодовый агент
│   └── factory.py     # Фабрика агентов
├── tools/             # Инструменты (shell, filesystem, browser)
│   ├── base.py        # Базовый класс инструмента
│   ├── shell.py       # Выполнение команд
│   ├── filesystem.py  # Работа с файлами
│   └── factory.py     # Фабрика инструментов
├── memory/            # Слои памяти
│   ├── short_term.py  # Краткосрочная память
│   ├── vector.py      # Векторная память (FAISS)
│   └── behavioral.py  # Поведенческая память (скоринг)
├── models/            # Модели и провайдеры
│   ├── base.py        # Базовый класс провайдера
│   ├── openai_compatible.py  # OpenAI-совместимые провайдеры
│   └── manager.py     # Менеджер моделей (выбор, fallback)
├── voice/             # STT/TTS
│   ├── stt.py         # Whisper STT
│   ├── tts.py         # Piper/Coqui TTS
│   └── pipeline.py    # Голосовой пайплайн
├── interfaces/        # Интерфейсы (Telegram, Web UI, CLI)
│   ├── base.py        # Базовый класс интерфейса
│   ├── cli.py         # CLI интерфейс
│   ├── telegram_bot.py  # Telegram бот
│   ├── web_ui.py      # Web интерфейс
│   └── run_interface.py  # Запускатор интерфейсов
├── config/            # Конфигурационные файлы
│   ├── loader.py      # Загрузчик конфигурации
│   └── providers.yaml.example  # Пример конфигурации
├── scripts/           # Скрипты управления
│   └── manage.sh      # Скрипт управления сервисом
├── requirements.txt   # Зависимости Python
├── task_list          # Список задач (прогресс)
├── TASK.md            # Детальное описание задач
├── ARCHITECTURE.md    # Архитектура системы
└── README.md          # Этот файл
```

---

## 📝 TODO

- [x] STEP 1: FastAPI base
- [x] STEP 2: Model Manager + OpenAI-compatible client
- [x] STEP 3: Router
- [x] STEP 4: Subagents
- [x] STEP 5: Tools
- [x] STEP 6: Memory
- [x] STEP 7: Behavioral memory
- [x] STEP 8: Execution loop (multi-step, timeout)
- [x] STEP 9: Interfaces (CLI, Telegram, Web UI)
- [x] STEP 10: Voice (STT Whisper, TTS Piper/Coqui)
- [ ] Интеграция Voice в Interfaces
- [ ] Native провайдеры (GigaChat, YandexGPT) - в процессе
- [ ] Browser tool (playwright)
- [ ] Доработка Web UI

---

## 📄 Лицензия

MIT License (или укажите вашу)

## 🤝 Вклад

Pull requests приветствуются! Пожалуйста, сначала обсудите изменения через Issues.

## 📧 Контакты

- Git: [git.mirv.top/mirivlad/local_ai](https://git.mirv.top/mirivlad/local_ai)
