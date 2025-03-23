"""Number setup for our Integration.

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
from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.restore_state import RestoreEntity

from . import MyConfigEntry
from .base import SolemBaseEntity
from .coordinator import SolemCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class NumberTypeClass:
    """Class for holding sensor type to sensor class."""

    device_type: str
    state_field: str
    number_class: object


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

    number_types = [
        NumberTypeClass("IRRIGATION_DURATION_NUMBER", "value", IrrigationManualDuration),
        NumberTypeClass("WATER_FLOW_NUMBER", "value", IrrigationFlowRate),
    ]

    numbers = []

    for number_type in number_types:
        _LOGGER.debug(number_type)
        numbers.extend(
            [
                number_type.number_class(coordinator, device, number_type.state_field)
                for device in coordinator.data
                if device.get("device_type") == number_type.device_type
            ]
        )

    # Now create the numbers.
    async_add_entities(numbers)


class SolemNumberEntity(SolemBaseEntity, NumberEntity):
    def __init__(
        self, coordinator: SolemCoordinator, device: dict[str, Any], parameter: str
    ) -> None:
        """Initialise entity."""
        super().__init__(coordinator, device, parameter)

    @property
    def entity_category(self):
        return EntityCategory.CONFIG

class IrrigationManualDuration(SolemNumberEntity, RestoreEntity):
    def __init__(self, coordinator: SolemCoordinator, device: dict[str, Any], parameter: str):
        super().__init__(coordinator, device, parameter)
        self._attr_min_value = 1
        self._attr_max_value = 60
        self._attr_native_min_value = 1
        self._attr_native_max_value = 60
        self._attr_step = 1
        self._attr_native_value = self.coordinator.irrigation_manual_duration

    @property
    def native_value(self) -> float | None:
        return self.coordinator.irrigation_manual_duration
        
    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = value
        self.coordinator.irrigation_manual_duration = value
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()

        if last_state and last_state.state not in (None, "unknown", "unavailable"):
            try:
                self._attr_native_value = float(last_state.state)
                self.coordinator.irrigation_manual_duration = float(last_state.state)
            except ValueError:
                _LOGGER.warning(f"Estado inválido restaurado: {last_state.state}")

class IrrigationFlowRate(SolemNumberEntity, RestoreEntity):
    def __init__(self, coordinator: SolemCoordinator, device: dict[str, Any], parameter: str):
        super().__init__(coordinator, device, parameter)
        self._attr_min_value = 0.5
        self._attr_max_value = 30
        self._attr_native_min_value = 0.5
        self._attr_native_max_value = 30
        self._attr_step = 0.5
        self._attr_native_value = self.coordinator.water_flow_rate

    @property
    def native_value(self) -> float | None:
        return self.coordinator.water_flow_rate
        
    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = value
        self.coordinator.water_flow_rate = value
        self.async_write_ha_state()
    
    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()

        if last_state and last_state.state not in (None, "unknown", "unavailable"):
            try:
                self._attr_native_value = float(last_state.state)
                self.coordinator.water_flow_rate = float(last_state.state)
            except ValueError:
                _LOGGER.warning(f"Estado inválido restaurado: {last_state.state}")
