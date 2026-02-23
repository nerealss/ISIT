import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import requests
import threading

class WeatherExpertSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Экспертная система погоды")
        self.root.geometry("650x600")
        self.root.resizable(False, False)
        
        self.cities = {
            "Макеевка": {"lat": 48.0478, "lon": 37.9258},
            "Донецк": {"lat": 48.0159, "lon": 37.8028},
            "Ростов": {"lat": 47.2225, "lon": 39.7189},
            "Москва": {"lat": 55.7558, "lon": 37.6173},
            "Санкт-Петербург": {"lat": 59.9343, "lon": 30.3351}
        }
        
        self.knowledge_base = self.init_knowledge_base()
        self.setup_ui()
        self.update_time()
        
        self.root.mainloop()
    
    def init_knowledge_base(self):
        return {
            "Макеевка": {
                "temperature": -7,
                "apparent_temp": -7,
                "humidity": 60,
                "wind_speed": 5,
                "pressure": 1013,
                "precipitation": 0.0,
                "condition": "ЯСНО",
                "condition_ru": "Ясно"
            },
            "Донецк": {
                "temperature": -5,
                "apparent_temp": -6,
                "humidity": 65,
                "wind_speed": 7,
                "pressure": 1012,
                "precipitation": 0.0,
                "condition": "ЯСНО",
                "condition_ru": "Ясно"
            },
            "Ростов": {
                "temperature": 0,
                "apparent_temp": -2,
                "humidity": 70,
                "wind_speed": 10,
                "pressure": 1015,
                "precipitation": 0.5,
                "condition": "ОБЛАЧНО",
                "condition_ru": "Облачно"
            },
            "Москва": {
                "temperature": -10,
                "apparent_temp": -12,
                "humidity": 80,
                "wind_speed": 3,
                "pressure": 1008,
                "precipitation": 0.0,
                "condition": "СНЕГ",
                "condition_ru": "Снег"
            },
            "Санкт-Петербург": {
                "temperature": -8,
                "apparent_temp": -10,
                "humidity": 75,
                "wind_speed": 8,
                "pressure": 1010,
                "precipitation": 1.2,
                "condition": "ДОЖДЬ",
                "condition_ru": "Дождь"
            }
        }
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="Экспертная система погоды", 
                               font=('Arial', 18, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(main_frame, text="Машина вывода реляционного типа", 
                                  font=('Arial', 10))
        subtitle_label.pack()
        
        city_frame = ttk.Frame(main_frame)
        city_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(city_frame, text="Выберите город:", font=('Arial', 11)).pack(side=tk.LEFT)
        
        self.city_combo = ttk.Combobox(city_frame, values=list(self.cities.keys()), 
                                       state="readonly", width=20, font=('Arial', 11))
        self.city_combo.pack(side=tk.LEFT, padx=10)
        self.city_combo.set("Макеевка")
        self.city_combo.bind('<<ComboboxSelected>>', self.on_city_selected)
        
        ttk.Button(city_frame, text="Обновить", command=self.fetch_weather_data, 
                  width=12).pack(side=tk.LEFT, padx=5)
        
        self.weather_frame = ttk.LabelFrame(main_frame, text="", padding="15")
        self.weather_frame.pack(fill=tk.BOTH, expand=True)
        
        self.display_weather("Макеевка")
    
    def display_weather(self, city):
        for widget in self.weather_frame.winfo_children():
            widget.destroy()
        
        data = self.knowledge_base.get(city, {})
        if not data:
            return
        
        city_header = ttk.Frame(self.weather_frame)
        city_header.pack(fill=tk.X)
        
        city_label = ttk.Label(city_header, text=city, font=('Arial', 16, 'bold'))
        city_label.pack(side=tk.LEFT)
        
        condition_label = ttk.Label(city_header, text=data['condition'], 
                                   font=('Arial', 16, 'bold'), foreground='#0066CC')
        condition_label.pack(side=tk.RIGHT)
        
        ttk.Separator(self.weather_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        params_frame = ttk.Frame(self.weather_frame)
        params_frame.pack(fill=tk.BOTH, expand=True)
        
        params_frame.columnconfigure(0, weight=1)
        params_frame.columnconfigure(1, weight=1)
        params_frame.columnconfigure(2, weight=1)
        
        self.add_parameter(params_frame, 0, 0, "Температура", 
                          f"{data['temperature']}°C", 
                          self.evaluate_temperature(data['temperature']))
        
        self.add_parameter(params_frame, 0, 1, "Ощущается как", 
                          f"{data['apparent_temp']}°C", 
                          self.evaluate_temperature(data['apparent_temp']))
        
        self.add_parameter(params_frame, 1, 0, "Влажность", 
                          f"{data['humidity']}%", 
                          self.evaluate_humidity(data['humidity']))
        
        wind_speed_kmh = data['wind_speed'] * 3.6
        self.add_parameter(params_frame, 1, 1, "Ветер", 
                          f"{wind_speed_kmh:.1f} км/ч", 
                          self.evaluate_wind(data['wind_speed']))
        
        self.add_parameter(params_frame, 2, 0, "Давление", 
                          f"{data['pressure']} гПа", 
                          self.evaluate_pressure(data['pressure']))
        
        self.add_parameter(params_frame, 2, 1, "Осадки", 
                          f"{data['precipitation']:.1f} мм", 
                          self.evaluate_precipitation(data['precipitation']))
        
        ttk.Separator(self.weather_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        time_str = datetime.now().strftime("%H:%M:%S")
        time_label = ttk.Label(self.weather_frame, 
                              text=f"Данные для {city} обновлены: {time_str}",
                              font=('Arial', 9), foreground='gray')
        time_label.pack()
    
    def add_parameter(self, parent, row, col, title, value, evaluation):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        ttk.Label(frame, text=title, font=('Arial', 10, 'bold')).pack()
        ttk.Label(frame, text=value, font=('Arial', 14)).pack(pady=5)
        
        if "Холодно" in evaluation or "Сильный" in evaluation or "Высокая" in evaluation:
            color = '#0066CC'
        elif "Нормальная" in evaluation or "Умеренный" in evaluation:
            color = '#009900'
        else:
            color = '#666666'
        
        ttk.Label(frame, text=evaluation, font=('Arial', 9), foreground=color).pack()
    
    def evaluate_temperature(self, temp):
        if temp < -10:
            return "Очень холодно"
        elif -10 <= temp < 0:
            return "Холодно"
        elif 0 <= temp < 15:
            return "Прохладно"
        else:
            return "Тепло"
    
    def evaluate_wind(self, wind_speed):
        if wind_speed < 2:
            return "Слабый"
        elif 2 <= wind_speed < 8:
            return "Умеренный"
        else:
            return "Сильный"
    
    def evaluate_precipitation(self, precip):
        if precip == 0:
            return "Нет или слабые"
        elif 0 < precip <= 5:
            return "Умеренные"
        else:
            return "Сильные"
    
    def evaluate_humidity(self, humidity):
        if humidity < 40:
            return "Низкая"
        elif 40 <= humidity < 70:
            return "Нормальная"
        else:
            return "Высокая"
    
    def evaluate_pressure(self, pressure):
        if pressure < 1000:
            return "Низкое"
        elif 1000 <= pressure < 1020:
            return "Нормальное"
        else:
            return "Высокое"
    
    def get_weather_condition(self, weather_code):
        conditions = {
            0: "ЯСНО",
            1: "ЯСНО",
            2: "ОБЛАЧНО",
            3: "ОБЛАЧНО",
            45: "ТУМАН",
            51: "ДОЖДЬ",
            61: "ДОЖДЬ",
            71: "СНЕГ",
            95: "ГРОЗА"
        }
        return conditions.get(weather_code, "НЕИЗВЕСТНО")
    
    def on_city_selected(self, event):
        city = self.city_combo.get()
        if city:
            self.display_weather(city)
    
    def fetch_weather_data(self):
        city = self.city_combo.get()
        if not city:
            messagebox.showwarning("Предупреждение", "Выберите город")
            return
        
        self.weather_frame.config(text="Загрузка...")
        
        thread = threading.Thread(target=self.fetch_weather_thread, args=(city,))
        thread.daemon = True
        thread.start()
    
    def fetch_weather_thread(self, city):
        try:
            coords = self.cities[city]
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "current_weather": "true",
                "hourly": "temperature_2m,relativehumidity_2m,pressure_msl,precipitation",
                "timezone": "auto"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                current = data.get("current_weather", {})
                hourly = data.get("hourly", {})
                
                temp = current.get("temperature", 0)
                wind_speed = current.get("windspeed", 0)
                weather_code = current.get("weathercode", 0)
                
                humidity = 60
                pressure = 1013
                precipitation = 0
                
                if hourly:
                    if "relativehumidity_2m" in hourly and hourly["relativehumidity_2m"]:
                        humidity = hourly["relativehumidity_2m"][0]
                    if "pressure_msl" in hourly and hourly["pressure_msl"]:
                        pressure = hourly["pressure_msl"][0]
                    if "precipitation" in hourly and hourly["precipitation"]:
                        precipitation = hourly["precipitation"][0]
                
                condition = self.get_weather_condition(weather_code)
                
                condition_ru_map = {
                    "ЯСНО": "Ясно",
                    "ОБЛАЧНО": "Облачно",
                    "ТУМАН": "Туман",
                    "ДОЖДЬ": "Дождь",
                    "СНЕГ": "Снег",
                    "ГРОЗА": "Гроза",
                    "НЕИЗВЕСТНО": "Неизвестно"
                }
                
                self.knowledge_base[city] = {
                    "temperature": temp,
                    "apparent_temp": temp - 2 if wind_speed > 5 else temp,
                    "humidity": humidity,
                    "wind_speed": wind_speed,
                    "pressure": pressure,
                    "precipitation": precipitation,
                    "condition": condition,
                    "condition_ru": condition_ru_map.get(condition, "Неизвестно")
                }
                
                self.root.after(0, lambda: self.display_weather(city))
            else:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка API: {response.status_code}"))
                
        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка сети: {str(e)}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка: {str(e)}"))
    
    def update_time(self):
        if hasattr(self, 'weather_frame') and self.city_combo.get():
            city = self.city_combo.get()
            if city and city in self.knowledge_base:
                time_str = datetime.now().strftime("%H:%M:%S")
                
                for widget in self.weather_frame.winfo_children():
                    if isinstance(widget, ttk.Label) and "обновлены" in widget.cget("text"):
                        widget.config(text=f"Данные для {city} обновлены: {time_str}")
                        break
        
        self.root.after(1000, self.update_time)

if __name__ == "__main__":
    app = WeatherExpertSystem()