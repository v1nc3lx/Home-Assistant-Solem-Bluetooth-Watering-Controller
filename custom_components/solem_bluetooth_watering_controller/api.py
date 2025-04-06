"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""
import logging
import sys
import struct
from homeassistant.core import HomeAssistant, ServiceCall
from tenacity import retry, stop_after_attempt, wait_exponential
from bleak import BleakClient, BleakScanner
from typing import Any
from datetime import datetime, timedelta, timezone
from homeassistant.util.dt import as_local
from homeassistant.util import dt as dt_util
from .const import OPEN_WEATHER_MAP_FORECAST_URL, OPEN_WEATHER_MAP_CURRENT_URL

import aiohttp

_LOGGER = logging.getLogger(__name__)

class SolemAPI:
    """Class for Solem API."""

    def __init__(self, mac_address: str, bluetooth_timeout: int) -> None:
        """Initialise."""
        self.mac_address = mac_address
        self.characteristic_uuid = None
        self.bluetooth_timeout = bluetooth_timeout
        self.mock = False

    async def scan_bluetooth(self):
        devices = await BleakScanner.discover()
        return devices

            
    async def connect(self) -> str:
        """Verify if it's possible to connect to the bluetooth device."""
    
        try:
            return await self.connect_with_retries()
        except Exception as ex:
            _LOGGER.debug(f"Timeout connecting to device after retries!, ex:{ex}")
            raise APIConnectionError("Timeout connecting to device after retries!")


    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def connect_with_retries(self) -> str:
        """Verify if it's possible to connect to the bluetooth device."""
    
        if self.mock == True:
            _LOGGER.debug("Mock=True, Returning from function...")
            return

        devices = await self.scan_bluetooth()
        found_device = False
        for device in devices:
            if device.address.upper() == self.mac_address.upper():
                found_device = True
                break;

        if found_device == False:
            _LOGGER.debug(f"Device not found! Failed connecting!")
            raise APIConnectionError("Device not found! Failed connecting!")

        try:
            async with BleakClient(self.mac_address, timeout=self.bluetooth_timeout) as client:
                if client.is_connected:
                    _LOGGER.debug("Connected: True")
                    services = client.services
                    for service in services:
                        for char in service.characteristics:
                            if 'write' in char.properties:
                                self.characteristic_uuid = char.uuid
                                return
                    raise APIConnectionError("Device isn't suitable!")
                else:
                    _LOGGER.debug("Failed connecting!")
                    raise APIConnectionError("Timeout connecting to api")
        except Exception as ex:
            _LOGGER.debug(f"Failed connecting!, ex:{ex}")
            raise APIConnectionError("Timeout connecting to api")


    async def sprinkle_station_x_for_y_minutes(self, station: int, minutes: int):
        """Sprinkle a specific station for a specified number of minutes """
        try:
            await self.sprinkle_station_x_for_y_minutes_with_retry(station, minutes)
        except Exception as ex:
            _LOGGER.debug(f"Error connecting to Solem device after retries!, ex: {ex}", exc_info=True)
            raise APIConnectionError("Error connecting to Solem device after retries!")

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def sprinkle_station_x_for_y_minutes_with_retry(self, station: int, minutes: int):
        """Function with retries"""
        if self.mock:
            _LOGGER.debug("Mock=True, Returning from function...")
            return

        if self.characteristic_uuid is None:
            await self.connect()

        async with BleakClient(self.mac_address, timeout=self.bluetooth_timeout) as client:
            if client.is_connected:
                _LOGGER.debug("Connected: True")
                _LOGGER.debug(f"writing command: Sprinkle station {station} for {minutes} minutes")

                command = struct.pack(">HBBBH", 0x3105, 0x12, station & 0xFF, 0x00, (minutes * 60) & 0xFFFF)
                await client.write_gatt_char(self.characteristic_uuid, command)

                _LOGGER.debug("Committing")
                commit_command = struct.pack(">BB", 0x3b, 0x00)
                await client.write_gatt_char(self.characteristic_uuid, commit_command)

                _LOGGER.debug("Success")
            else:
                _LOGGER.debug("Failed connecting!")
                raise APIConnectionError("Timeout connecting to API")


    async def stop_manual_sprinkle(self):
        if self.mock == True:
            _LOGGER.debug("Mock=True, Returning from function...")
            return

        try:
            async with BleakClient(self.mac_address, timeout=self.bluetooth_timeout) as client:
                if client.is_connected:
                    _LOGGER.debug("Connected: True")
                    _LOGGER.debug("writing command: Stop manual sprinkle")
                    command = struct.pack(">HBBBH",0x3105,0x15,0x00,0xff,0x0000)
                    await client.write_gatt_char(self.characteristic_uuid, command)
        
                    _LOGGER.debug("committing")
                    command = struct.pack(">BB", 0x3b, 0x00)
                    await client.write_gatt_char(self.characteristic_uuid, command)
        
                    _LOGGER.debug("Success")
                else:
                    _LOGGER.debug("Failed connecting!")
                    raise APIConnectionError("Timeout connecting to api")
        except Exception as ex:
            _LOGGER.debug(f"Failed connecting!, ex:{ex}")
            raise APIConnectionError("Timeout connecting to api")


    async def list_characteristics(self):
        if self.mock == True:
            _LOGGER.debug("Mock=True, Returning from function...")
            return

        try:
            async with BleakClient(self.mac_address, timeout=self.bluetooth_timeout) as client:
                if client.is_connected:
                    _LOGGER.debug("Connected: True")
                    _LOGGER.debug("Listing services")
                    services = client.services
                    for service in services:
                        _LOGGER.info(f"Service: {service.uuid}")
                        for char in service.characteristics:
                            _LOGGER.info(f"  Characteristic: {char.uuid}")
        
                    _LOGGER.debug("Success")
                else:
                    _LOGGER.debug("Failed connecting!")
                    raise APIConnectionError("Timeout connecting to api")
        except Exception as ex:
            _LOGGER.debug(f"Failed connecting!, ex:{ex}")
            raise APIConnectionError("Timeout connecting to api")
    
    async def turn_off_permanent(self):
        if self.mock == True:
            _LOGGER.debug("Mock=True, Returning from function...")
            return

        try:
            async with BleakClient(self.mac_address, timeout=self.bluetooth_timeout) as client:
                if client.is_connected:
                    _LOGGER.debug("Connected: True")
                    _LOGGER.debug("writing command: Turn off permanent")
                    command = struct.pack(">HBBBH", 0x3105, 0xc0, 0x00, 0x00, 0x0000)
                    await client.write_gatt_char(self.characteristic_uuid, command)
                    
                    _LOGGER.debug("committing")
                    command = struct.pack(">BB", 0x3b, 0x00)
                    await client.write_gatt_char(self.characteristic_uuid, command)
        
                    _LOGGER.debug("Success")
                else:
                    _LOGGER.debug("Failed connecting!")
                    raise APIConnectionError("Timeout connecting to api")
        except Exception as ex:
            _LOGGER.debug(f"Failed connecting!, ex:{ex}")
            raise APIConnectionError("Timeout connecting to api")
    
    async def turn_off_x_days(self, days: int):
        if self.mock == True:
            _LOGGER.debug("Mock=True, Returning from function...")
            return

        try:
            async with BleakClient(self.mac_address, timeout=self.bluetooth_timeout) as client:
                if client.is_connected:
                    _LOGGER.debug("Connected: True")
                    _LOGGER.debug("writing command: Turn off permanent")
                    command = struct.pack(">HBBBH", 0x3105, 0xc0, 0x00, days & 0xFF, 0x0000)
                    await client.write_gatt_char(self.characteristic_uuid, command)
                    
                    _LOGGER.debug("committing")
                    command = struct.pack(">BB", 0x3b, 0x00)
                    await client.write_gatt_char(self.characteristic_uuid, command)
        
                    _LOGGER.debug("Success")
                else:
                    _LOGGER.debug("Failed connecting!")
                    raise APIConnectionError("Timeout connecting to api")
        except Exception as ex:
            _LOGGER.debug(f"Failed connecting!, ex:{ex}")
            raise APIConnectionError("Timeout connecting to api")
                
    async def turn_on(self):
        if self.mock == True:
            _LOGGER.debug("Mock=True, Returning from function...")
            return

        try:
            async with BleakClient(self.mac_address, timeout=self.bluetooth_timeout) as client:
                if client.is_connected:
                    _LOGGER.debug("Connected: True")
                    _LOGGER.debug("writing command: Turn on")
                    command = struct.pack(">HBBBH",0x3105,0xa0,0x00,0x01,0x0000)
                    await client.write_gatt_char(self.characteristic_uuid, command)
                    
                    _LOGGER.debug("committing")
                    command = struct.pack(">BB", 0x3b, 0x00)
                    await client.write_gatt_char(self.characteristic_uuid, command)
        
                    _LOGGER.debug("Success")
                else:
                    _LOGGER.debug("Failed connecting!")
                    raise APIConnectionError("Timeout connecting to api")
        except Exception as ex:
            _LOGGER.debug(f"Failed connecting!, ex:{ex}")
            raise APIConnectionError("Timeout connecting to api")


    async def sprinkle_all_stations_for_y_minutes(self, minutes: int):
        if self.mock == True:
            _LOGGER.debug("Mock=True, Returning from function...")
            return

        try:
            async with BleakClient(self.mac_address, timeout=self.bluetooth_timeout) as client:
                if client.is_connected:
                    _LOGGER.debug("Connected: True")
                    _LOGGER.debug(f"writing command: Sprinkle all stations for {minutes} minutes")
                    command = struct.pack(">HBBBH", 0x3105, 0x11, 0x00, 0x00,(minutes * 60) & 0xFFFF)
                    await client.write_gatt_char(self.characteristic_uuid, command)
        
                    _LOGGER.debug("committing")
                    command = struct.pack(">BB", 0x3b, 0x00)
                    await client.write_gatt_char(self.characteristic_uuid, command)
        
                    _LOGGER.debug("Success")
                else:
                    _LOGGER.debug("Failed connecting!")
                    raise APIConnectionError("Timeout connecting to api")
        except Exception as ex:
            _LOGGER.debug(f"Failed connecting!, ex:{ex}")
            raise APIConnectionError("Timeout connecting to api")
            
    async def run_program_x(self, program: int):
        if self.mock == True:
            _LOGGER.debug("Mock=True, Returning from function...")
            return

        try:
            async with BleakClient(self.mac_address, timeout=self.bluetooth_timeout) as client:
                if client.is_connected:
                    _LOGGER.debug("Connected: True")
                    _LOGGER.debug(f"writing command: Run program {program}")
                    command = struct.pack(">HBBBH", 0x3105, 0x14, 0x00, program & 0xFF, 0x0000)
                    await client.write_gatt_char(self.characteristic_uuid, command)
        
                    _LOGGER.debug("committing")
                    command = struct.pack(">BB", 0x3b, 0x00)
                    await client.write_gatt_char(self.characteristic_uuid, command)
        
                    _LOGGER.debug("Success")
                else:
                    _LOGGER.debug("Failed connecting!")
                    raise APIConnectionError("Timeout connecting to api")
        except Exception as ex:
            _LOGGER.debug(f"Failed connecting!, ex:{ex}")
            raise APIConnectionError("Timeout connecting to api")
    

class OpenWeatherMapAPI:
    """Class for OpenWeatherMap API."""

    def __init__(self, api_key: str, latitude: str, longitude: str, timeout: int) -> None:
        """Initialise."""
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self.timeout = timeout
        self._cache_forecast = None
        self._cache_current = None
        self._last_forecast_fetch_time = None
        self.last_forecast_date = datetime.now().date()
        self._last_current_fetch_time = None
        

    async def get_current_weather(self) -> Any:
        now = dt_util.now()  # Usa datetime com timezone
    
        if self._cache_current and self._last_current_fetch_time and now - self._last_current_fetch_time < timedelta(minutes=self.timeout):
            _LOGGER.debug("Returning cached data.")
            return self._cache_current
    
        weather_url = f"{OPEN_WEATHER_MAP_CURRENT_URL}appid={self.api_key}&lat={self.latitude}&lon={self.longitude}"
        _LOGGER.debug("Getting current weather at : %s", weather_url)
    
        async with aiohttp.ClientSession() as session:
            async with session.get(weather_url) as response:
                try:
                    data = await response.json()
                    _LOGGER.debug("Current Weather Data: %s", data)
    
                    if "dt" in data:
                        utc_dt = datetime.fromtimestamp(data["dt"], tz=timezone.utc)
                        local_dt = as_local(utc_dt)
                        data["dt_txt"] = local_dt.strftime('%Y-%m-%d %H:%M:%S')
                        
                        _LOGGER.debug(
                            f"UTC time from API: {utc_dt.strftime('%Y-%m-%d %H:%M:%S')}, "
                            f"Local time after as_local: {local_dt.strftime('%Y-%m-%d %H:%M:%S')}"
                        )
    
                    self._cache_current = data
                    self._last_current_fetch_time = now
                except Exception as ex:
                    _LOGGER.error("Error processing Current Weather data: JSON format invalid!")
                    raise APIConnectionError("Error processing Current Weather data: JSON format invalid!")
    
        return self._cache_current


    async def is_raining(self) -> dict:
        current_weather = await self.get_current_weather()
        
        return {
            "is_raining": "rain" in current_weather,
            "current": current_weather
        }


    async def get_forecast(self) -> list:
        """Obtains and preserves data from 00h till 00h of the next day."""
        now = datetime.now()
    
        # If data is recent returns what is on the cache
        if self._cache_forecast and self._last_forecast_fetch_time and now - self._last_forecast_fetch_time < timedelta(minutes=self.timeout):
            _LOGGER.debug("Returning cached data.")
            return self._cache_forecast
    
        temp_cache = self._cache_forecast.copy() if self._cache_forecast else []
    
        # If it is a new day, resets and preserves the block from 0h to 3h obtained yesterday
        if self.last_forecast_date != now.date():
            _LOGGER.debug(f"Day changed, will get 00h forecast to new day...")
            last_00_03_forecast = None
    
            for forecast in self._cache_forecast:
                forecast_time_str = forecast["dt_txt"]
                forecast_dt = datetime.strptime(forecast_time_str, "%Y-%m-%d %H:%M:%S")
                if forecast_dt.hour == 0:
                    _LOGGER.debug(f"Found 00h block: {forecast_time_str}")
                    last_00_03_forecast = forecast
                    break
    
            self._cache_forecast = []
            self.last_forecast_date = now.date()
    
            if last_00_03_forecast:
                self._cache_forecast.append(last_00_03_forecast)
                _LOGGER.debug(f"Inserting 00h block in new cache: {last_00_03_forecast}")
    
        current_hour = now.hour
        forecast_hours = [h for h in range(0, 21, 3) if h >= current_hour]
        forecast_hours.append(0)
        items = len(forecast_hours)
    
        weather_url = f"{OPEN_WEATHER_MAP_FORECAST_URL}&appid={self.api_key}&lat={self.latitude}&lon={self.longitude}&cnt={items}"
        _LOGGER.debug("Getting forecast at: %s", weather_url)
    
        async with aiohttp.ClientSession() as session:
            async with session.get(weather_url) as response:
                try:
                    data = await response.json()
                    _LOGGER.debug("Forecast Weather Data: %s", data)
    
                    for item in data["list"]:
                        # Mantém dt_txt tal como está (já está em hora local)
                        forecast_time_str = item["dt_txt"]
    
                        _LOGGER.debug(
                            f"Forecast timestamp from API (dt_txt): {forecast_time_str}"
                        )
    
                        existing_index = next(
                            (index for index, forecast in enumerate(self._cache_forecast)
                             if forecast["dt_txt"] == forecast_time_str),
                            None
                        )
    
                        if existing_index is not None:
                            _LOGGER.debug(f"Replacing block for {forecast_time_str}")
                            self._cache_forecast[existing_index] = item
                        else:
                            _LOGGER.debug(f"Appending item {forecast_time_str} to _cache_forecast")
                            self._cache_forecast.append(item)
    
                    self._last_forecast_fetch_time = now
    
                except Exception as ex:
                    _LOGGER.error("Error processing Forecast Weather data: JSON format invalid!", exc_info=True)
    
                    if not self._cache_forecast:
                        self._cache_forecast = temp_cache
    
                    raise APIConnectionError("Error processing Forecast Weather data: JSON format invalid!")
    
        _LOGGER.debug(f"self._cache_forecast={self._cache_forecast}")
        return self._cache_forecast


    async def will_it_rain(self) -> dict:
        """Verifies if it will rain for the rest of the day."""
        forecast = await self.get_forecast()
    
        now = dt_util.now()  # Hora local garantida
        today_str = now.strftime("%Y-%m-%d")
        current_hour = now.hour
    
        block_hours = [h for h in range(0, 21, 3)]
        current_block = max([h for h in block_hours if h <= current_hour])
    
        relevant_forecasts = []
        for item in forecast:
            forecast_time_str = item["dt_txt"]  # já está em hora local
            forecast_date, forecast_hour_minute = forecast_time_str.split(" ")
            forecast_hour, _, _ = forecast_hour_minute.split(":")
            forecast_hour = int(forecast_hour)
    
            if forecast_date == today_str and forecast_hour >= current_block:
                relevant_forecasts.append(item)
    
        will_rain = any(item.get("pop", 0) > 0.50 for item in relevant_forecasts)
    
        return {
            "will_rain": will_rain,
            "forecast": forecast
        }
        

    async def get_total_rain_forecast_for_today(self) -> float:
        """Calculates total amount of rain predicted (mm) for the rest of the day."""
    
        will_it_rain_result = await self.will_it_rain()
        forecasts = will_it_rain_result.get("forecast", [])
    
        now = dt_util.now()
        current_time = now.hour * 60 + now.minute
        today_str = now.strftime("%Y-%m-%d")
        total_rain_mm = 0.0
    
        for item in forecasts:
            forecast_time_str = item["dt_txt"]  # já está em hora local
            forecast_date, forecast_hour_minute = forecast_time_str.split(" ")
            forecast_hour, _, _ = forecast_hour_minute.split(":")
            forecast_hour = int(forecast_hour)
    
            rain_data = item.get("rain", {})
            rain_mm = rain_data.get("3h", 0.0)
    
            # Apenas considera previsões do dia atual
            if forecast_date != today_str:
                continue
    
            forecast_start_minute = forecast_hour * 60
            forecast_end_minute = forecast_start_minute + 180
    
            # Se o bloco já passou, ignorar
            if forecast_end_minute <= current_time:
                continue
    
            # Se estamos dentro do bloco atual, calcular a fração exata de tempo restante
            if forecast_start_minute <= current_time < forecast_end_minute:
                remaining_minutes = forecast_end_minute - current_time
                rain_mm = (remaining_minutes / 180) * rain_mm  # Ajuste proporcional
    
            total_rain_mm += rain_mm
    
        return total_rain_mm


class APIConnectionError(Exception):
    """Exception class for connection error."""
