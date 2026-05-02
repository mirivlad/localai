# 🧠 ПОЛНАЯ АРХИТЕКТУРА СИСТЕМЫ

## 0. Концепция

Это:

> **локальная агентная платформа (Agent Runtime System)**

Свойства:

- мультимодельность
- мультиагентность
- инструментальность (tools)
- память + адаптация
- мультимодальность (текст + голос)

---

# 🧩 1. Верхний уровень

```
[ Interfaces ]   
   ↓
[ API Gateway ]   
   ↓
[ Orchestrator Core ]
   ↓
[ Subagents ]
   ↓
[ Tools Layer ]
   ↓
[ Memory Layer ]
   ↓
[ Model Layer ]
```

---

# 🌐 2. Interfaces Layer

Поддерживаемые интерфейсы:

- Telegram бот (основной)
- Web UI (дебаг + управление)
- CLI
- Voice input/output

---

## Функции:

- приём сообщений (text / voice)
- преобразование voice → text
- передача в API
- отображение ответа
- опционально: воспроизведение TTS

---

# 🚪 3. API Gateway (FastAPI)

Функции:

- `/chat` endpoint
- `/voice` endpoint
- session management
- streaming responses
- user preferences (voice on/off)

---

## Контракт запроса

```
{  "session_id": "string",  "input_type": "text | voice",  "content": "...",  "metadata": {}}
```

---

# 🧠 4. Orchestrator Core (ЦЕНТР СИСТЕМЫ)

Состоит из:

---

## 4.1 Router (LLM-based classifier)

Использует лёгкую модель через llama.cpp

Выход:

```
{  "intent": "chat | code | action | search | voice",  "subagent": "chat | coder | operator | researcher | voice",  "tools": ["filesystem", "shell"],  "confidence": 0.0-1.0,  "model_preference": "local | cloud | cheap | strong"}
```

---

## 4.2 Context Builder

Собирает:

- short-term history
- релевантную память (vector search)
- behavioral patterns
- system prompt
- user preferences

---

## 4.3 Execution Manager

- запускает субагента
- контролирует:
    - max_steps
    - timeouts
- управляет multi-step reasoning

---

## 4.4 State Tracker

Логирует:

- решения роутера
- вызовы моделей
- вызовы tools
- промежуточные шаги

👉 критично для дебага

---

# 🤖 5. Subagents Layer

Каждый субагент — отдельная логика мышления.

---

## 5.1 ChatAgent

- диалог
- объяснения
- low-cost модель

---

## 5.2 CodeAgent

- генерация кода
- анализ
- фиксы
- tools: filesystem, shell

---

## 5.3 OperatorAgent

- выполнение действий
- автоматизация

---

## 5.4 ResearchAgent

- поиск
- анализ источников

---

## 5.5 VoiceAgent

- координация STT/TTS
- conversational loop

---

## Общий интерфейс:

```
class BaseAgent:    async def run(context) -> AgentResult:        pass
```

---

# 🔧 6. Tools Layer

Реализация через LangChain (только как SDK)

---

## Минимальные tools:

- shell (sandboxed)
- filesystem
- http
- browser (playwright)
- code executor

---

## Требования:

- allowlist команд
- dry-run режим
- логирование

---

# 🧠 7. Memory Layer

---

## 7.1 Short-term

- последние N сообщений

---

## 7.2 Long-term (RAG)

- FAISS
- локальные эмбеддинги

---

## 7.3 Embeddings

Локально:

- sentence-transformers
- или GGUF embedding модели

👉 отдельный сервис, кэширование модели

---

## 7.4 Behavioral Memory

Структура:

```
{  "pattern": "...",  "response": "...",  "score": 0,  "last_used": "timestamp"}
```

Использование:

```
final_score = similarity * 0.7 + score * 0.3
```

---

# ⚙️ 8. Model Layer (КРИТИЧЕСКИЙ СЛОЙ)

---

## 8.1 Local LLM

- llama.cpp (Vulkan backend)

---

## 8.2 OpenAI-compatible Providers

Поддержка:

- OpenAI
- OpenRouter
- любые proxy/self-hosted endpoints
- тот же llama.cpp

---

### Конфиг:

```
{  
	"provider": "openai_compatible",  
	"name": "openrouter",  
	"base_url": "https://openrouter.ai/api/v1",  
	"api_key": "...",  
	"default_model": "deepseek/deepseek-chat"
}
```

---

## 8.3 Native Providers

- GigaChat
- YandexGPT

👉 отдельные адаптеры

---

## 8.4 Model Manager

Функции:

- выбор провайдера
- нормализация API
- fallback
- логирование

---

## Унифицированный ответ:

```
{  "text": "...",  "usage": {...},  "model": "..."}
```

---

# 🔊 9. Voice Layer

---

## STT

- Whisper (локально)

---

## TTS

- Coqui TTS  
    или Piper

---

## Pipeline

```
audio → STT → text → orchestrator → text → TTS → audio
```

---

# 🧱 10. Структура проекта

```
project/
├── api/
├── orchestrator/
├── agents/
├── tools/
├── memory/
├── models/
├── voice/
├── interfaces/
└── config/
```