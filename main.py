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