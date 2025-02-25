# data_manager.py
import json
import os
import csv
import numpy as np
import asyncio  # Importe asyncio para usar await

class DataManager:
    def __init__(self, csv_filename='dados_sensores.csv', json_filename='dados_paciente.json'):
        self.csv_path = os.path.join(os.getcwd(), csv_filename)
        self.json_path = os.path.join(os.getcwd(), json_filename)
        self.latest_paciente_data = self.load_patient_data()
        self.is_recording = False
        self.is_calibrating = False
        self.csv_writer = None
        self.file_stream = None
        self.ax_offset = 0.0
        self.ay_offset = 0.0
        self.az_offset = 0.0

    def load_patient_data(self):
        if os.path.exists(self.json_path):
            with open(self.json_path, 'r', encoding='utf-8') as json_file:
                try:
                    return json.load(json_file)
                except json.JSONDecodeError:
                    print('Erro ao ler os dados do paciente.')
        return {}

    def save_patient_data(self):
        with open(self.json_path, 'w', encoding='utf-8') as json_file:
            json.dump(self.latest_paciente_data, json_file, ensure_ascii=False, indent=4)

    def process_serial_data(self, data):
        try:
            values = data.split(',')
            if len(values) == 4:
                tempo, ax, ay, az = map(float, values)
                
                # Aplica os offsets de calibração
                ax_corrigido = ax - self.ax_offset
                ay_corrigido = ay - self.ay_offset
                az_corrigido = az - self.az_offset

                sensor_data = {
                    "tempo": tempo,
                    "ax": ax_corrigido,
                    "ay": ay_corrigido,
                    "az": az_corrigido,
                    "paciente": self.latest_paciente_data
                }
                
                if self.is_recording:
                    self.save_to_csv(sensor_data)
                    self.save_to_json(sensor_data)
                return sensor_data
        except ValueError as error:
            print(f'Erro ao processar os dados: {error}')
        return None

    def save_to_csv(self, sensor_data):
        if self.file_stream is None:
            self.file_stream = open(self.csv_path, 'a', newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.file_stream)
            self.csv_writer.writerow(['tempo', 'ax', 'ay', 'az', 'paciente'])

        self.csv_writer.writerow([sensor_data['tempo'], sensor_data['ax'], sensor_data['ay'], sensor_data['az'], sensor_data['paciente']])
        print(f'Dados gravados no CSV: {sensor_data}')

    def save_to_json(self, sensor_data):
        json_file_path = os.path.join(os.getcwd(), 'dados_sensores.json')
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                all_data = json.load(json_file)
        else:
            all_data = {}

        timestamp = sensor_data["tempo"]
        if timestamp not in all_data:
            all_data[timestamp] = []

        all_data[timestamp].append(sensor_data)

        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(all_data, json_file, ensure_ascii=False, indent=4)

    async def calibrar_mpu(self, serial_handler):
        """Coleta dados do MPU6050 para calcular os offsets iniciais."""
        print("⚙️ Iniciando calibração do MPU6050...")
        self.is_calibrating = True
        
        ax_list, ay_list, az_list = [], [], []
        
        # Limpa o buffer serial antes de iniciar a calibração
        serial_handler.ser.reset_input_buffer()

        for _ in range(100):  # Coleta 100 amostras para calibração
            if serial_handler.ser.in_waiting > 0:
                linha = serial_handler.ser.readline().decode().strip()
                print(linha)
                try:
                    tempo, ax, ay, az = map(float, linha.split(","))
                    ax_list.append(ax)
                    ay_list.append(ay)
                    az_list.append(az)
                except ValueError:
                    continue  # Ignora leituras inválidas
            await asyncio.sleep(0.1)  # Respeita o delay de 100 ms entre as leituras
        
        # Calcula os offsets médios
        self.ax_offset = np.mean(ax_list)
        self.ay_offset = np.mean(ay_list)
        self.az_offset = np.mean(az_list) - 1.0  # Ajuste para compensar gravidade
        
        print(f"✅ Calibração concluída!\nOffsets -> X: {self.ax_offset:.5f}, Y: {self.ay_offset:.5f}, Z: {self.az_offset:.5f}")
        self.is_calibrating = False