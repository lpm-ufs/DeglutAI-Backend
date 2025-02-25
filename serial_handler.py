# serial_handler.py
import asyncio
import serial
import serial.tools.list_ports

class SerialHandler:
    def __init__(self):
        self.ser = None

    async def find_arduino(self):
        while True:
            ports = list(serial.tools.list_ports.comports())
            for port in ports:
                if 'Arduino' in port.description:
                    print(f"Arduino encontrado na porta {port.device}")
                    return port.device
            print("Arduino não encontrado. Tentando novamente em 5 segundos...")
            await asyncio.sleep(5)

    async def initialize_serial_connection(self):
        arduino_port = await self.find_arduino()
        try:
            self.ser = serial.Serial(arduino_port, 115200)
            print(f"Porta serial {arduino_port} aberta com sucesso.")
        except serial.SerialException:
            print(f"Erro ao abrir a porta serial {arduino_port}. Tentando novamente...")
            await asyncio.sleep(5)
            await self.initialize_serial_connection()

    async def read_serial_data(self, process_data_callback):
        if self.ser:
            while True:
                if self.ser.in_waiting > 0:
                    serial_data = self.ser.readline().decode('utf-8').strip()
                    process_data_callback(serial_data)
                await asyncio.sleep(0.1)
