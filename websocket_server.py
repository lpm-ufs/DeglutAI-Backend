# websocket_server.py
import asyncio
import websockets
import json

class WebSocketServer:
    def __init__(self, data_manager, serial_handler):
        self.data_manager = data_manager
        self.serial_handler = serial_handler
        self.clients = set()

    async def handle_websocket(self, websocket):
        self.clients.add(websocket)
        try:
            async for message in websocket:
                message_data = json.loads(message)

                if message_data.get('action') == 'set-paciente-data':
                    self.data_manager.latest_paciente_data = {
                        "nome": message_data.get('nome'),
                        "dataNascimento": message_data.get('dataNascimento'),
                        "doenca": message_data.get('doenca'),
                        "comentarios": message_data.get('comentarios'),
                        "sexo": message_data.get('sexo')
                    }
                    self.data_manager.save_patient_data()
                    print(f'Dados do paciente atualizados: {self.data_manager.latest_paciente_data}')
                    await websocket.send(json.dumps({"status": 200, "message": "Dados do paciente atualizados com sucesso."}))

                elif message_data.get('action') == 'start-recording':
                    self.data_manager.is_recording = True
                    print(f'Gravação iniciada')
                    await websocket.send(json.dumps({"status": 200, "message": "Gravação iniciada com sucesso."}))

                elif message_data.get('action') == 'start-calibration':
                    print("🔄 Iniciando calibração do MPU6050...")
                    await self.data_manager.calibrar_mpu(self.serial_handler) 
                    print("✅ Calibração concluída")

                elif message_data.get('action') == 'stop-recording':
                    self.data_manager.is_recording = False
                    print('Gravação parada')
                    await websocket.send(json.dumps({"status": 200, "message": "Gravação parada com sucesso."}))

                elif message_data.get('action') == 'enviar-dados':
                    print("Dados enviados com sucesso.")
                    await websocket.send(json.dumps({"status": 200, "message": "Dados enviados com sucesso."}))

        except websockets.ConnectionClosed:
            print('Cliente WebSocket desconectado.')
        finally:
            self.clients.remove(websocket)

    async def start_server(self):
        async with websockets.serve(self.handle_websocket, 'localhost', 8080):
            print('Servidor WebSocket rodando em ws://localhost:8080')
            await asyncio.Future()