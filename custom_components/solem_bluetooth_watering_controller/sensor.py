"""Sensor setup for our Integration.

Here we use a different method to define some of our entity classes.
As, in our example, so much is common, we use our base entity class to define
many properties, then our base sensor class to define the property to get the
value of the sensor.

As such, for all our other sensor types, we can just set the _attr_ value to
keep our code small and easily readable.  You can do this for all entity properties(attributes)
if you so wish, or mix and match to suit.
"""

from dataclasses import dataclass
import logging
from datetime import datetime
import pytz

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfTemperature,
    UnitOfPrecipitationDepth,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MyConfigEntry
from .base import SolemBaseEntity
from .coordinator import SolemCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class SensorTypeClass:
    """Class for holding sensor type to sensor class."""

    device_type: str
    state_field: str
    sensor_class: object


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Sensors."""
    # This gets the data update coordinator from the config entry runtime data as specified in your __init__.py
    coordinator: SolemCoordinator = config_entry.runtime_data.coordinator

    # ----------------------------------------------------------------------------
    # Here we enumerate the sensors in your data value from your
    # DataUpdateCoordinator and add an instance of your sensor class to a list
    # for each one.
    # This maybe different in your specific case, depending on how your data is
    # structured
    # ----------------------------------------------------------------------------

    sensor_types = [
        SensorTypeClass("STATE_SENSOR", "state", StateSensor),
        SensorTypeClass("NEXT_SCHEDULE_SENSOR", "state", NextScheduleSensor),
        SensorTypeClass("LAST_SPRINKLE_SENSOR", "state", LastSprinkleSensor),
        SensorTypeClass("LAST_RAIN_SENSOR", "state", LastRainSensor),
        SensorTypeClass("RAIN_TIME_TODAY_SENSOR", "state", TotalRainTimeSensor),
        SensorTypeClass("TOTAL_WATER_CONSUMPTION_SENSOR", "state", TotalWaterConsumptionSensor),
        SensorTypeClass("TOTAL_AMOUNT_RAIN_TODAY", "state", TotalAmountRainSensor),
        SensorTypeClass("TOTAL_FORECASTED_RAIN_TODAY", "state", TotalForecastedRainSensor),
    ]

    sensors = []

    for sensor_type in sensor_types:
        sensors.extend(
            [
                sensor_type.sensor_class(coordinator, device, sensor_type.state_field)
                for device in coordinator.data
                if device.get("device_type") == sensor_type.device_type
            ]
        )

    # Now create the sensors.
    async_add_entities(sensors)


class StateSensor(SolemBaseEntity, SensorEntity):
    """Class to handle temperature sensors.

    This inherits the SolemBaseSensor and so uses all the properties and methods
    from that class and then overrides specific attributes relevant to this sensor type.
    """

    @property
    def native_value(self) -> int | float | str:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        return self.coordinator.get_device_parameter(self.device_id, self.parameter)

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        attrs = {}
        if self.coordinator.controller.device_name == "Controller Status":
            attrs["schedule"] = self.coordinator.schedule
            attrs["num_stations"] = self.coordinator.num_stations
        return attrs

class NextScheduleSensor(SolemBaseEntity, SensorEntity):
    """Class to handle Next Schedule.

    This inherits the SolemBaseSensor and so uses all the properties and methods
    from that class and then overrides specific attributes relevant to this sensor type.
    """

    _attr_device_class = SensorDeviceClass.TIMESTAMP  # Define como um timestamp

    @property
    def native_value(self) -> datetime | None:
        """Retorna o timestamp da próxima irrigação no formato datetime com timezone."""

        next_schedule = self.coordinator.next_schedule

        if next_schedule:
            try:
                # Certifica-te de que next_schedule é um datetime
                if isinstance(next_schedule, str):
                    next_schedule = datetime.fromisoformat(next_schedule)

                # Garante que tem timezone (Home Assistant exige um datetime aware)
                if next_schedule.tzinfo is None:
                    next_schedule = next_schedule.replace(tzinfo=pytz.UTC)

                return next_schedule  # Retorna datetime correto
            except Exception as e:
                _LOGGER.warning(f"Invalid format for schedule: {next_schedule} - {e}")

        return None

class LastSprinkleSensor(SolemBaseEntity, SensorEntity):
    """Class to handle Next Schedule.

    This inherits the SolemBaseSensor and so uses all the properties and methods
    from that class and then overrides specific attributes relevant to this sensor type.
    """

    _attr_device_class = SensorDeviceClass.TIMESTAMP  # Define como um timestamp

    @property
    def native_value(self) -> datetime | None:
        """Retorna o timestamp da próxima irrigação no formato datetime com timezone."""

        last_sprinkle = self.coordinator.last_sprinkle

        if last_sprinkle:
            try:
                # Certifica-te de que next_schedule é um datetime
                if isinstance(last_sprinkle, str):
                    last_sprinkle = datetime.fromisoformat(last_sprinkle)

                # Garante que tem timezone (Home Assistant exige um datetime aware)
                if last_sprinkle.tzinfo is None:
                    last_sprinkle = last_sprinkle.replace(tzinfo=pytz.UTC)

                return last_sprinkle  # Retorna datetime correto
            except Exception as e:
                _LOGGER.warning(f"Invalid format for last_sprinkle: {last_sprinkle} - {e}")

        return None

class LastRainSensor(SolemBaseEntity, SensorEntity):
    """Class to handle Next Schedule.

    This inherits the SolemBaseSensor and so uses all the properties and methods
    from that class and then overrides specific attributes relevant to this sensor type.
    """

    _attr_device_class = SensorDeviceClass.TIMESTAMP  # Define como um timestamp

    @property
    def native_value(self) -> datetime | None:
        """Retorna o timestamp da próxima irrigação no formato datetime com timezone."""

        last_rain = self.coordinator.last_rain

        if last_rain:
            try:
                # Certifica-te de que next_schedule é um datetime
                if isinstance(last_rain, str):
                    last_rain = datetime.fromisoformat(last_rain)

                # Garante que tem timezone (Home Assistant exige um datetime aware)
                if last_rain.tzinfo is None:
                    last_rain = last_rain.replace(tzinfo=pytz.UTC)

                return last_rain  # Retorna datetime correto
            except Exception as e:
                _LOGGER.warning(f"Invalid format for last_rain: {last_rain} - {e}")

        return None

class TotalRainTimeSensor(SolemBaseEntity, SensorEntity):
    """Sensor that measures the total rain time for today."""

    _attr_state_class = SensorStateClass.TOTAL
    _attr_device_class = SensorDeviceClass.DURATION  # Indica que representa uma duração

    @property
    def native_unit_of_measurement(self) -> str:
        """Retorna uma unidade genérica, pois o valor já está formatado."""
        return "min"

    @property
    def native_value(self) -> int:
        """Retorna o tempo total de chuva em minutos (mantendo o valor numérico)."""
        return self.coordinator.rain_time_today


class TotalAmountRainSensor(SolemBaseEntity, SensorEntity):
    """Sensor that measures ammount of rain for today."""

    _attr_state_class = SensorStateClass.TOTAL
    _attr_device_class = SensorDeviceClass.PRECIPITATION

    @property
    def native_unit_of_measurement(self) -> str:
        """Retorna uma unidade genérica, pois o valor já está formatado."""
        return UnitOfPrecipitationDepth.MILLIMETERS

    @property
    def native_value(self) -> int:
        """Retorna o tempo total de chuva em minutos (mantendo o valor numérico)."""
        return round(self.coordinator.rain_total_amount_today, 2)


class TotalForecastedRainSensor(SolemBaseEntity, SensorEntity):
    """Sensor that identifies ammount forecasted of rain for today."""

    _attr_state_class = SensorStateClass.TOTAL
    _attr_device_class = SensorDeviceClass.PRECIPITATION

    @property
    def native_unit_of_measurement(self) -> str:
        """Retorna uma unidade genérica, pois o valor já está formatado."""
        return UnitOfPrecipitationDepth.MILLIMETERS

    @property
    def native_value(self) -> int:
        """Retorna o tempo total de chuva em minutos (mantendo o valor numérico)."""
        return round(self.coordinator.rain_total_amount_forecasted_today, 2)

class TotalWaterConsumptionSensor(SolemBaseEntity, SensorEntity):
    """Sensor que calcula o consumo total de água com base no tempo de rega."""

    _attr_state_class = SensorStateClass.TOTAL
    _attr_device_class = SensorDeviceClass.WATER
    _attr_native_unit_of_measurement = "L"

    @property
    def native_value(self) -> float:
        """Retorna o total de litros consumidos com base no tempo de rega."""
        # Obtém o tempo total de rega em minutos
        return round(self.coordinator.total_water_consumption, 2)
