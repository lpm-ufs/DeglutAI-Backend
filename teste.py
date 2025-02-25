import asyncio
import json

from websocket_server import WebSocketServer

# Simula um WebSocket
class FakeWebSocket:
    async def send(self, message):
        print(f"Mensagem enviada pelo servidor: {message}")

# Simula o DataManager
class DataManager:
    def __init__(self):
        self.latest_paciente_data = {}
        self.is_recording = False

    def save_patient_data(self):
        print("Dados do paciente salvos.")

    async def calibrar_mpu(self, serial_handler):
        print("Simulação de calibração do MPU6050...")

# Simula o SerialHandler
class SerialHandler:
    pass

# Função principal para testar
async def main():
    # Crie uma instância do WebSocketServer com um DataManager e SerialHandler simulados
    data_manager = DataManager()
    serial_handler = SerialHandler()
    server = WebSocketServer(data_manager, serial_handler)

    # Crie um WebSocket falso
    fake_websocket = FakeWebSocket()

    # Simule mensagens recebidas
    messages = [
        json.dumps({"action": "set-paciente-data", "nome": "João", "dataNascimento": "1990-01-01", "doenca": "Gripe", "comentarios": "Nenhum", "sexo": "Masculino"}),
        json.dumps({"action": "start-recording"}),
        json.dumps({"action": "start-calibration"}),
        json.dumps({"action": "stop-recording"}),
        json.dumps({"action": "enviar-dados"}),
    ]

    # Processa cada mensagem
    for message in messages:
        print(f"\nProcessando mensagem: {message}")
        await server.handle_websocket(fake_websocket)

# Execute o teste
asyncio.run(main())