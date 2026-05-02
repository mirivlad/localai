You are a senior software engineer designing a local AI agent platform.

Your task is to build a modular system step-by-step.

IMPORTANT RULES:

- Do NOT generate everything at once
    
- Work iteratively
    
- Each step must produce working code
    
- Use Python + FastAPI
    
- Follow clean architecture
    
- Avoid unnecessary abstractions
    
- Keep components loosely coupled
    
- Add logging for every important action
    
- Ensure all components are testable and replaceable
    

---

## GOAL

Build a local AI assistant system with:

- Local LLM (llama.cpp server, OpenAI-compatible API)
    
- Multiple cloud LLM providers
    
- OpenAI-compatible provider support (CRITICAL)
    
- Native provider adapters (GigaChat, YandexGPT)
    
- Multi-agent orchestration
    
- Tool execution (shell, filesystem, browser, http)
    
- Vector memory (FAISS)
    
- Behavioral memory (scoring system)
    
- Voice support (STT + TTS)
    
- Multiple interfaces (Telegram, Web, CLI)
    

---

## CRITICAL: MODEL ABSTRACTION LAYER

You MUST implement a unified model access layer.

---

### Provider Types

#### 1. OpenAI-compatible providers

These providers use:  
POST /v1/chat/completions

Examples:

- OpenAI
    
- OpenRouter
    
- local llama.cpp
    
- any proxy/self-hosted API
    

Requirements:

- Single reusable client
    
- Configurable:
    
    - base_url
        
    - api_key
        
    - model
        
- Dynamic provider registration
    

Example config:

{  
"provider": "openai_compatible",  
"name": "openrouter",  
"base_url": "[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)",  
"api_key": "KEY",  
"default_model": "deepseek/deepseek-chat"  
}

---

#### 2. Native providers

Examples:

- GigaChat
    
- YandexGPT
    

Requirements:

- Separate adapter classes
    
- Normalize responses
    

---

### Unified Model Response

All providers MUST return:

{  
"text": "...",  
"usage": {...},  
"model": "..."  
}

---

### Model Manager

Responsibilities:

- select provider
    
- route requests
    
- normalize responses
    
- handle fallback
    
- log usage
    

NO direct API calls from agents.

---

## SYSTEM COMPONENTS

---

### API Layer (FastAPI)

- /chat endpoint
    
- /voice endpoint
    
- session support
    
- streaming responses
    

---

### Orchestrator

Components:

1. Router (LLM classifier → JSON)
    
2. Context Builder
    
3. Execution Manager
    
4. State Tracker
    

---

### Router Output

{  
"intent": "...",  
"subagent": "...",  
"tools": [...],  
"confidence": 0.0-1.0,  
"model_preference": "local | cloud | cheap | strong"  
}

---

### Subagents

Implement:

- BaseAgent
    
- ChatAgent
    
- CodeAgent
    
- OperatorAgent
    
- ResearchAgent
    
- VoiceAgent
    

Each agent:

- receives context
    
- may call tools
    
- returns structured result
    

---

### Tools

Implement:

- shell (safe, sandboxed)
    
- filesystem
    
- http
    
- browser (playwright)
    

Use LangChain ONLY as a tool abstraction layer.

---

### Memory

Implement:

1. Short-term memory
    
2. FAISS vector store
    
3. Behavioral memory
    

---

### Behavioral Memory

Store:

- prompt
    
- response
    
- score
    
- timestamp
    

Ranking:

final_score = similarity * 0.7 + score * 0.3

---

### Embeddings

- Local embedding model
    
- Cached and reused
    
- No repeated downloads
    

---

### Voice

Implement:

- STT (Whisper)
    
- TTS (Coqui or Piper)
    

Pipeline:

audio → text → system → text → audio

---

### Execution Manager

- multi-step reasoning loop
    
- max_steps limit
    
- timeout control
    

---

### Logging

Log EVERYTHING:

- routing decisions
    
- model calls
    
- tool usage
    
- agent steps
    

---

## STEP PLAN

STEP 1: FastAPI base  
STEP 2: Model Manager + OpenAI-compatible client  
STEP 3: Router  
STEP 4: Subagents  
STEP 5: Tools  
STEP 6: Memory  
STEP 7: Behavioral memory  
STEP 8: Execution loop  
STEP 9: Voice  
STEP 10: Interfaces

---

## FINAL REQUIREMENTS

- modular architecture
    
- minimal coupling
    
- replaceable providers
    
- scalable agent system
    
- no hardcoded providers
    
- no direct API calls outside ModelManager
    

---

Start with STEP 1.