# Project: nat_traversal

## Концепт
Имя проекта: "NATranslate"

Суть: Zero-config P2P туннель через NAT без белого IP.

Стек: Python, FastMCP.

Натranslate - это консольная утилита, которая позволяет создавать прямые P2P соединения между локальными машинами, не требуя ни единой конфигурации или белого IP. Утилита использует FastMCP для организации P2P соединения и обеспечивает приватность данных.

## Правки
Макс, хорош фантазировать, но давайте посмотрим на реальность. Утилита с названием "NATranslate" уже существует в виде библиотеки, но не в виде консольной утилиты. Выглядит как костыль, потому что FastMCP не поддерживает NAT traversal в базовой версии.

Звучит бодро, но в MVP оставим только P2P соединение через FastMCP. Остальное - выкинь.

## Исходники
SLUG: nat_traversal

РЕЗЮМЕ_ДЛЯ_ЧАТА: Новая консольная утилита nat_traversal, которая использует FastMCP для организации P2P соединения между локальными машинами без конфигурации или белого IP. Утилита пока не поддерживает NAT traversal, но это будет добавлено в будущих версиях.

КОД:
```python
import argparse
import asyncio
import dataclasses
import socket
from fastmcp import McpServer, McpClient

@dataclasses.dataclass
class McpConfig:
    port: int = 12345

async def create_mcp_server(config: McpConfig):
    server = McpServer(config.port)
    await server.start()
    print(f"МКП сервер запущен на порте {config.port}")
    return server

async def create_mcp_client(config: McpConfig):
    client = McpClient(config.port)
    await client.connect()
    print(f"МКП клиент подключен к серверу на порте {config.port}")
    return client

async def main():
    parser = argparse.ArgumentParser(description="Новая консольная утилита nat_traversal")
    parser.add_argument("--start-server", action="store_true", help="Запустить МКП сервер")
    parser.add_argument("--start-client", action="store_true", help="Запустить МКП клиент")
    parser.add_argument("--port", type=int, default=12345, help="Порт для МКП сервера и клиента")
    args = parser.parse_args()

    if args.start_server:
        config = McpConfig(port=args.port)
        server = await create_mcp_server(config)
        try:
            await asyncio.Future()  # блокировать поток, пока сервер работает
        finally:
            await server.stop()
            print("МКП сервер остановлен")

    elif args.start_client:
        config = McpConfig(port=args.port)
        client = await create_mcp_client(config)
        try:
            await asyncio.Future()  # блокировать поток, пока клиент работает
        finally:
            await client.disconnect()
            print("МКП клиент отключен")

    else:
        print("Нет выбрано действие")

if __name__ == "__main__":
    asyncio.run(main())
```
