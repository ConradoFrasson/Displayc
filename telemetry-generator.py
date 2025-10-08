import numpy as np
import time
import random
from datetime import datetime, timedelta

class TelemetryGenerator:
    """Generates realistic racing car telemetry data"""
    
    def __init__(self):
        self.start_time = time.time()
        self.lap_start_time = time.time()
        self.current_lap = 1
        self.best_lap_time = None
        self.previous_lap_time = None
        
        # Base values for realistic simulation
        self.base_speed = 120
        self.base_rpm = 8000
        self.base_tire_temp = 85
        self.base_tire_pressure = 2.3
        self.base_battery_temp = 45
        self.base_motor_temp = 75
        self.base_soc = 85
        
        # Simulation state
        self.throttle_position = 0.5
        self.brake_position = 0.0
        self.steering_angle = 0.0
        
    def generate_tire_data(self):
        """Generate tire pressure and temperature data for all four wheels"""
        # Simulate tire wear and heating during racing
        elapsed = time.time() - self.start_time
        wear_factor = min(elapsed / 3600, 0.3)  # Up to 30% wear over an hour
        
        tires = {}
        for position in ['FL', 'FR', 'RL', 'RR']:
            # Different wear patterns for different tire positions
            if position in ['FL', 'FR']:  # Front tires work harder
                temp_variation = random.uniform(-5, 15)
                pressure_variation = random.uniform(-0.1, 0.05)
            else:  # Rear tires
                temp_variation = random.uniform(-3, 10)
                pressure_variation = random.uniform(-0.05, 0.03)
            
            temperature = self.base_tire_temp + temp_variation + (wear_factor * 20)
            pressure = self.base_tire_pressure + pressure_variation - (wear_factor * 0.2)
            
            # Add some dynamic variation based on throttle/brake
            if self.throttle_position > 0.7:
                temperature += random.uniform(2, 8)
            if self.brake_position > 0.5:
                temperature += random.uniform(3, 10)
            
            tires[position] = {
                'temperature': max(20, min(120, temperature)),
                'pressure': max(1.8, min(2.8, pressure))
            }
            
        return tires
    
    def generate_engine_data(self):
        """Generate RPM and speed data"""
        # Simulate realistic racing engine behavior
        current_time = time.time()
        
        # Create some variation in driving pattern
        pattern = np.sin((current_time - self.start_time) * 0.5) * 0.3 + 0.7
        self.throttle_position = max(0.2, min(1.0, pattern + random.uniform(-0.2, 0.2)))
        
        # RPM based on throttle position and gear simulation
        gear_factor = random.choice([0.6, 0.7, 0.8, 0.9, 1.0, 1.1])  # Simulate different gears
        rpm = self.base_rpm * self.throttle_position * gear_factor
        rpm += random.uniform(-200, 200)  # Add some noise
        rpm = max(1000, min(12000, rpm))
        
        # Speed calculation with some realism
        speed = (rpm / 11000) * 220  # Max speed around 220 km/h at redline
        speed += random.uniform(-5, 5)  # Add variation
        speed = max(0, min(250, speed))
        
        return {
            'rpm': int(rpm),
            'speed': int(speed),
            'throttle_position': self.throttle_position
        }
    
    def generate_thermal_data(self):
        """Generate battery and motor temperature data"""
        # Thermal buildup over time with cooling effects
        elapsed = time.time() - self.start_time
        thermal_buildup = min(elapsed / 1800, 0.4)  # Build up over 30 minutes
        
        # Battery temperature (affected by discharge rate)
        battery_load_factor = self.throttle_position * 0.5
        battery_temp = self.base_battery_temp + (thermal_buildup * 25) + (battery_load_factor * 10)
        battery_temp += random.uniform(-2, 3)
        battery_temp = max(20, min(80, battery_temp))
        
        # Motor temperature (affected by RPM and throttle)
        motor_load_factor = self.throttle_position * 0.7
        motor_temp = self.base_motor_temp + (thermal_buildup * 35) + (motor_load_factor * 15)
        motor_temp += random.uniform(-3, 5)
        motor_temp = max(25, min(110, motor_temp))
        
        return {
            'battery_temp': battery_temp,
            'motor_temp': motor_temp
        }
    
    def generate_power_data(self):
        """Generate SOC and power consumption data"""
        # SOC decreases over time based on usage
        elapsed = time.time() - self.start_time
        consumption_rate = self.throttle_position * 0.8 + 0.2  # Base consumption + throttle
        
        # Calculate SOC decrease (roughly 1% per minute of hard driving)
        soc_decrease = (elapsed / 60) * (consumption_rate / 100) * 100
        current_soc = max(5, self.base_soc - soc_decrease)
        
        # Power consumption in kW (negative means consuming)
        power_consumption = -(self.throttle_position * 45 + random.uniform(5, 15))
        
        return {
            'soc': current_soc,
            'power_kw': power_consumption
        }
    
    def generate_lap_times(self):
        """Generate lap timing data"""
        current_time = time.time()
        current_lap_time = current_time - self.lap_start_time
        
        # Simulate lap completion (roughly every 90-120 seconds)
        if current_lap_time > random.uniform(90, 120):
            self.previous_lap_time = current_lap_time
            if self.best_lap_time is None or current_lap_time < self.best_lap_time:
                self.best_lap_time = current_lap_time
            self.lap_start_time = current_time
            self.current_lap += 1
        
        return {
            'current_lap_time': current_lap_time,
            'best_lap_time': self.best_lap_time,
            'previous_lap_time': self.previous_lap_time,
            'current_lap': self.current_lap
        }
    
    def generate_status_indicators(self):
        """Generate status LED indicators"""
        # Simulate various car systems status
        indicators = []
        
        # Temperature warnings
        thermal_data = self.generate_thermal_data()
        if thermal_data['battery_temp'] > 60:
            indicators.append({'color': 'yellow', 'status': 'Battery Temp Warning'})
        if thermal_data['battery_temp'] > 70:
            indicators.append({'color': 'red', 'status': 'Battery Overtemp'})
        if thermal_data['motor_temp'] > 90:
            indicators.append({'color': 'yellow', 'status': 'Motor Temp Warning'})
        if thermal_data['motor_temp'] > 100:
            indicators.append({'color': 'red', 'status': 'Motor Overtemp'})
        
        # Tire pressure warnings
        tire_data = self.generate_tire_data()
        for pos, data in tire_data.items():
            if data['pressure'] < 2.0:
                indicators.append({'color': 'yellow', 'status': f'{pos} Low Pressure'})
            if data['temperature'] > 100:
                indicators.append({'color': 'red', 'status': f'{pos} Overheated'})
        
        # Power warnings
        power_data = self.generate_power_data()
        if power_data['soc'] < 20:
            indicators.append({'color': 'yellow', 'status': 'Low Battery'})
        if power_data['soc'] < 10:
            indicators.append({'color': 'red', 'status': 'Critical Battery'})
        
        # Add some normal status indicators
        while len(indicators) < 20:  # Fill up the indicator bar
            indicators.append({'color': 'green', 'status': 'System OK'})
        
        return indicators[:20]  # Return exactly 20 indicators
    
    def get_all_telemetry(self):
        """Get complete telemetry package"""
        return {
            'tires': self.generate_tire_data(),
            'engine': self.generate_engine_data(),
            'thermal': self.generate_thermal_data(),
            'power': self.generate_power_data(),
            'lap_times': self.generate_lap_times(),
            'status_indicators': self.generate_status_indicators(),
            'timestamp': datetime.now()
        }
