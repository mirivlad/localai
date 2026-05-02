#!/bin/bash

# Local AI Agent - Management Script
# Usage: ./manage.sh {start|stop|restart|status|logs}

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/logs/app.pid"
LOG_DIR="$PROJECT_DIR/logs"
ACCESS_LOG="$LOG_DIR/access.log"
ERROR_LOG="$LOG_DIR/error.log"
APP_MODULE="api.main:app"
HOST="0.0.0.0"
PORT="8000"
WORKERS="1"

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Создаем директорию для логов если её нет
mkdir -p "$LOG_DIR"

# Проверка зависимостей
check_dependencies() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: python3 не установлен${NC}"
        exit 1
    fi
    if ! command -v uvicorn &> /dev/null; then
        echo -e "${YELLOW}Warning: uvicorn не найден в PATH, используем python -m uvicorn${NC}"
    fi
}

# Проверка, запущен ли процесс
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Запуск проекта
start() {
    if is_running; then
        echo -e "${YELLOW}Проект уже запущен (PID: $(cat $PID_FILE))${NC}"
        return 1
    fi

    echo -e "${GREEN}Запуск Local AI Agent...${NC}"
    
    cd "$PROJECT_DIR"
    
    # Активация виртуального окружения если есть
    if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
        source "$PROJECT_DIR/venv/bin/activate"
    fi
    
    # Запуск uvicorn
    nohup uvicorn "$APP_MODULE" \
        --host "$HOST" \
        --port "$PORT" \
        --workers "$WORKERS" \
        > "$ACCESS_LOG" 2>&1 &
    
    echo $! > "$PID_FILE"
    
    sleep 2
    
    if is_running; then
        echo -e "${GREEN}Проект запущен (PID: $(cat $PID_FILE))${NC}"
        echo -e "API доступно по адресу: ${GREEN}http://$HOST:$PORT${NC}"
    else
        echo -e "${RED}Ошибка запуска. Проверьте логи: $ERROR_LOG${NC}"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Остановка проекта
stop() {
    if ! is_running; then
        echo -e "${YELLOW}Проект не запущен${NC}"
        return 1
    fi

    echo -e "${YELLOW}Остановка Local AI Agent...${NC}"
    
    PID=$(cat "$PID_FILE")
    kill "$PID" 2> /dev/null || true
    
    # Ждем остановки
    for i in {1..10}; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    
    # Принудительная остановка если не остановился
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}Принудительная остановка...${NC}"
        kill -9 "$PID" 2> /dev/null || true
    fi
    
    rm -f "$PID_FILE"
    echo -e "${GREEN}Проект остановлен${NC}"
}

# Перезапуск
restart() {
    echo -e "${YELLOW}Перезапуск Local AI Agent...${NC}"
    stop 2> /dev/null || true
    sleep 2
    start
}

# Статус
status() {
    if is_running; then
        PID=$(cat "$PID_FILE")
        echo -e "${GREEN}Проект запущен${NC}"
        echo -e "PID: $PID"
        echo -e "API: http://$HOST:$PORT"
        echo -e "Логи: $LOG_DIR"
    else
        echo -e "${YELLOW}Проект не запущен${NC}"
    fi
}

# Показать логи
logs() {
    if [ "$1" == "error" ]; then
        tail -f "$ERROR_LOG"
    elif [ "$1" == "access" ]; then
        tail -f "$ACCESS_LOG"
    else
        tail -f "$ACCESS_LOG" "$ERROR_LOG"
    fi
}

# Главное меню
case "$1" in
    start)
        check_dependencies
        start
        ;;
    stop)
        stop
        ;;
    restart)
        check_dependencies
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs "$2"
        ;;
    *)
        echo "Использование: $0 {start|stop|restart|status|logs [error|access]}"
        exit 1
        ;;
esac

exit 0
