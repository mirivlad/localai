#!/usr/bin/env python3
"""
Runner для запуска интерфейсов
Использование:
    python -m interfaces.run_interface --type cli
    python -m interfaces.run_interface --type telegram --token YOUR_TOKEN
    python -m interfaces.run_interface --type web
"""
import argparse
import asyncio
import sys


async def run_cli():
    from interfaces.cli import CLIInterface
    cli = CLIInterface()
    cli.run()


async def run_telegram(token: str):
    from interfaces.telegram_bot import TelegramInterface
    import logging
    
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    bot = TelegramInterface(token=token)
    await bot.start()


async def run_web(port: int = 8080):
    from interfaces.web_ui import WebUIInterface
    import uvicorn
    
    ui = WebUIInterface(port=port)
    config = uvicorn.Config(ui.app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    await server.serve()


def main():
    parser = argparse.ArgumentParser(description="Run Local AI Agent Interface")
    parser.add_argument("--type", choices=["cli", "telegram", "web"], 
                        default="cli", help="Type of interface to run")
    parser.add_argument("--token", help="Telegram bot token")
    parser.add_argument("--port", type=int, default=8080, help="Port for Web UI")
    parser.add_argument("--api-url", default="http://localhost:8000", 
                        help="API URL")
    
    args = parser.parse_args()
    
    if args.type == "cli":
        asyncio.run(run_cli())
    elif args.type == "telegram":
        if not args.token:
            print("Error: --token required for Telegram bot")
            sys.exit(1)
        asyncio.run(run_telegram(args.token))
    elif args.type == "web":
        asyncio.run(run_web(args.port))


if __name__ == "__main__":
    main()
