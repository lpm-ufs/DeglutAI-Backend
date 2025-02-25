# main.py
import asyncio
from serial_handler import SerialHandler
from data_manager import DataManager
from websocket_server import WebSocketServer

async def main():
    data_manager = DataManager()
    serial_handler = SerialHandler()
    websocket_server = WebSocketServer(data_manager, serial_handler)

    await serial_handler.initialize_serial_connection()
    
    tasks = [
        asyncio.create_task(websocket_server.start_server()),
        asyncio.create_task(serial_handler.read_serial_data(data_manager.process_serial_data))
    ]

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())