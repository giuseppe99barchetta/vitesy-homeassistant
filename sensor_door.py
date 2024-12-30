import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import UnitOfTime

from .coordinator import VitesyCoordinator
from .sensor_base import FridgeSensor

_LOGGER = logging.getLogger(__name__)

class FridgeDoorSensor(FridgeSensor):

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.DURATION

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"FridgeDoor{self.device_id}-{self.sensor_id}"

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        return UnitOfTime.SECONDS

    @property
    def native_value(self) -> int | float:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        return float(self.sensor.get('value', {}).get('avg', None))

    @property
    def state_class(self) -> str | None:
        """Return state class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-state-classes
        return SensorStateClass.MEASUREMENT