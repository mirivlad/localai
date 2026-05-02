# Local AI Agent

Локальная агентная платформа с поддержкой мультимодельности и мультиагентности.

## Установка

1. Создать виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

3. Настроить конфигурацию:
```bash
cp config/.env.example config/.env
# Отредактируйте config/.env под свои нужды
```

## Запуск

### Через скрипт управления:
```bash
./scripts/manage.sh start    # Запуск
./scripts/manage.sh stop     # Остановка
./scripts/manage.sh restart  # Перезапуск
./scripts/manage.sh status   # Статус
./scripts/manage.sh logs     # Показать логи
```

### Как systemd сервис:

1. Скопировать unit файл:
```bash
sudo cp scripts/local-ai-agent.service /etc/systemd/system/
```

2. Отредактировать файл (при необходимости изменить пути и пользователя):
```bash
sudo nano /etc/systemd/system/local-ai-agent.service
```

3. Включить и запустить сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl enable local-ai-agent
sudo systemctl start local-ai-agent
```

4. Проверить статус:
```bash
sudo systemctl status local-ai-agent
```

## API Endpoints

- `GET /` - проверка статуса
- `POST /chat` - чат (JSON ответ)
- `POST /chat/stream` - чат (streaming)
- `POST /voice` - голосовые сообщения
- `GET /health` - health check

## Структура проекта

```
project/
├── api/           # FastAPI приложение
├── orchestrator/  # Оркестратор (роутер, контекст, исполнение)
├── agents/        # Субагенты (Chat, Code, Operator, etc.)
├── tools/         # Инструменты (shell, filesystem, browser)
├── memory/        # Слои памяти (short-term, vector, behavioral)
├── models/        # Модели и провайдеры
├── voice/         # STT/TTS
├── interfaces/    # Telegram, Web UI, CLI
├── config/        # Конфигурационные файлы
└── scripts/       # Скрипты управления
```

## TODO

- [ ] STEP 2: Model Manager + OpenAI-compatible client
- [ ] STEP 3: Router
- [ ] STEP 4: Subagents
- [ ] STEP 5: Tools
- [ ] STEP 6: Memory
- [ ] STEP 7: Behavioral memory
- [ ] STEP 8: Execution loop
- [ ] STEP 9: Voice
- [ ] STEP 10: Interfaces
