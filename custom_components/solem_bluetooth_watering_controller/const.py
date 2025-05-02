"""Constants for our integration."""

DOMAIN = "solem_bluetooth_watering_controller"

DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 10
CONTROLLER_MAC_ADDRESS = "controller_mac_address"
NUM_STATIONS = "num_stations"
SPRINKLE_WITH_RAIN = "sprinkle_with_rain"
OPEN_WEATHER_MAP_API_KEY = "open_weather_map_api_key"
SOIL_MOISTURE_SENSOR = "soil_moisture_sensor"
SOIL_MOISTURE_THRESHOLD = "soil_moisture_threshold"
DEFAULT_SOIL_MOISTURE = 40
MAX_SPRINKLES_PER_DAY = 5
MONTHS = [
    "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"
]

CHARACTERISTIC_UUID = "108b0002-eab5-bc09-d0ea-0b8f467ce8ee"
BLUETOOTH_TIMEOUT = "bluetooth_timeout"
BLUETOOTH_MIN_TIMEOUT = 5
BLUETOOTH_DEFAULT_TIMEOUT = 15

OPEN_WEATHER_MAP_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast?units=metric&"
OPEN_WEATHER_MAP_CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather?"
OPEN_WEATHER_MAP_API_CACHE_TIMEOUT = "openweathermap_api_cache_timeout"
OPEN_WEATHER_MAP_API_CACHE_MIN_TIMEOUT = 1
OPEN_WEATHER_MAP_API_CACHE_DEFAULT_TIMEOUT = 5
SOLEM_API_MOCK = "solem_api_mock"