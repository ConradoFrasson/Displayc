# data_provider.py
import random

class DataProvider:
    def __init__(self):
        self.rpm = 1000
        self.speed = 100
        self.soc = 0.95
        self.power_delta = 1.3
        self.battery_temp = 20.0
        self.engine_temp = 20.0
        self.accelerator = 80
        self.brake = 10
        self.tyre_data = {
            'FL': {'temp': 50.0, 'pressure': 10}, 'FR': {'temp': 50.0, 'pressure': 10},
            'RL': {'temp': 50.0, 'pressure': 10}, 'RR': {'temp': 50.0, 'pressure': 10}
        }
        self.lap_data = { "best": "1:25:123", "previous": "1:25:123", "current": "1:25:123" }
        self.faults = {"bms": False, "inverter": False, "battery": False, "engine": False}
        self.mode = "Endurance Mode"
        self._rpm_direction = 1
        self.battery_capacity_kwh = 85.0

    def update(self):
        # Simulação de RPM e Velocidade
        if self._rpm_direction == 1:
            self.rpm += random.randint(150, 250)
            if self.rpm > 11800: self._rpm_direction = -1
        else:
            self.rpm -= random.randint(300, 400)
            if self.rpm < 1000: self._rpm_direction = 1
        self.speed = int((self.rpm / 12000) * 180)

        # Simulação de Pedais e Delta de Potência
        if self._rpm_direction == 1 and self.rpm > 1500:
            self.accelerator = int((self.rpm / 12000) * 100)
            self.brake = 0
            self.power_delta = - (10 + (self.rpm / 12000) * 50)
        else:
            self.accelerator = 0
            self.brake = int(random.uniform(0.2, 0.8) * 100)
            self.power_delta = (5 + (self.speed / 180) * 15)

        # Atualização do SOC
        soc_delta = self.power_delta / self.battery_capacity_kwh
        self.soc += (soc_delta / 500)
        self.soc = max(0.0, min(1.0, self.soc))

        # Atualização das Temperaturas
        self.battery_temp = 20 + (1 - self.soc) * 40 + (self.speed / 180) * 20
        self.engine_temp = 20 + (self.rpm / 12000) * 90
        
        # Simulação dos Pneus
        for key in self.tyre_data:
            self.tyre_data[key]['temp'] += random.uniform(-0.1, 0.2)
            self.tyre_data[key]['temp'] = max(40, min(100, self.tyre_data[key]['temp']))

        # Simulação de Falhas (mais provável de acontecer)
        if random.random() < 0.005: self.faults["bms"] = not self.faults["bms"]
        if random.random() < 0.005: self.faults["inverter"] = not self.faults["inverter"]