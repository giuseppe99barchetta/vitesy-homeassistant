import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import DATETIME

from .const import DOMAIN
from .coordinator import VitesyCoordinator
from .sensor_base import FridgeSensor
_LOGGER = logging.getLogger(__name__)

class FridgeFilterSensor(FridgeSensor):

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.DATETIME

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"FridgeFilterCleaning{self.device_id}-{self.sensor_id}"

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        return DATETIME

    @property
    def native_value(self) -> int | float:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        return self.sensor.get('due_date', None)

    @property
    def state_class(self) -> str | None:
        """Return state class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-state-classes
        return SensorStateClass.MEASUREMENT
    