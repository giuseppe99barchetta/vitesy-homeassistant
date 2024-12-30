import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import PERCENTAGE

from .const import DOMAIN
from .coordinator import VitesyCoordinator

_LOGGER = logging.getLogger(__name__)

class FridgeSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a sensor."""

    def __init__(self, coordinator: VitesyCoordinator, device: dict, sensor: dict) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.device = device
        self.sensor = sensor
        
        self.device_id = device.get('id')
        self.sensor_id = sensor.get('id')

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.device = self.coordinator.get_device_by_id(self.device_id)
        _LOGGER.debug("_handle_coordinator_update Device: %s", self.device)
        self.sensor = self.coordinator.get_sensor_by_id(self.device_id, self.sensor_id)
        _LOGGER.debug("_handle_coordinator_update Sensor: %s", self.sensor)
        self.async_write_ha_state()

    @property
    def device_class(self) -> str:
        raise NotImplementedError("Device class not implemented")

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        # Identifiers are what group entities into the same device.
        # If your device is created elsewhere, you can just specify the indentifiers parameter.
        # If your device connects via another device, add via_device parameter with the indentifiers of that device.
        return DeviceInfo(
            name=f"Shelfy{self.device_id}",
            manufacturer="Vitesy",
            model="Shelfy",
            sw_version=self.device.get('firmware_version'),
            identifiers={
                (
                    DOMAIN,
                    self.device_id
                )
            },
        )

    @property
    def name(self) -> str:
            """Return the name of the sensor."""
            return f"FridgeBattery{self.device_id}-{self.sensor_id}"

    @property
    def native_unit_of_measurement(self) -> str | None:
            """Return unit of temperature."""
            return PERCENTAGE

    @property
    def native_value(self) -> int | float:
        raise NotImplementedError("Native value not implemented")
    @property
    def state_class(self) -> str | None:
        raise NotImplementedError("State class not implemented")

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-{self.device_id}-{self.sensor_id}"

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        attrs = {}
        attrs["extra_info"] = self.sensor
        return attrs