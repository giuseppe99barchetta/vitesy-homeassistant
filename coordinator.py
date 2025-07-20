"""Integration 101 Template integration using DataUpdateCoordinator."""

from dataclasses import dataclass
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_API_KEY,
)
from homeassistant.core import DOMAIN, HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from vitesy.client import VitesyClient

from datetime import datetime

_LOGGER = logging.getLogger(__name__)


@dataclass
class VitesyAPIData:
    """Class to hold api data."""

    devices: list


class VitesyCoordinator(DataUpdateCoordinator):

    data: VitesyAPIData

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        # Set variables from values entered in config flow setup
        self.api_key = config_entry.data[CONF_API_KEY]
        self.api_connected = False

        # Initialise DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            # Method to call on every update interval.
            update_method=self.async_update_data,
            # Polling interval. Will only be polled if there are subscribers.
            # Using config option here but you can just use a value.
            update_interval=timedelta(seconds=60),
        )

        # Initialise your api here
        if self.api_key:
            self.api = VitesyClient(api_key=self.api_key)
            self.api_connected = True

    async def async_update_data(self):
        _LOGGER.debug("vitesy async_update_data has been called")
        try:
            devices = await self.hass.async_add_executor_job(self.api.get_devices)
            _LOGGER.debug(f"Devices: {devices}")
            
            for device in devices:
                sensors = []  # spostato dentro il ciclo per resettare per ogni device
                
                data_in = await self.hass.async_add_executor_job(
                    self.api.query_measurements, device["id"], None, None, None, True
                )
                
                if data_in and isinstance(data_in, list) and len(data_in) > 0:
                    for sensor_data in data_in[0].get("sensors_data", []):
                        sensors.append(sensor_data)
                    for status_data in data_in[0].get("status_data", []):
                        sensors.append(status_data)
                else:
                    _LOGGER.warning(f"Nessun dato per dispositivo {device['id']}")
                
                device["sensors"] = sensors
                
                _LOGGER.debug(f"Device {device['id']} sensors: {sensors}")
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
    
        return VitesyAPIData(devices)

    def get_device_by_id(self, device_id: str):
        """Return device by device id."""
        # Called by the binary sensors and sensors to get their updated data from self.data
        try:
            return [
                device for device in self.data.devices if device.get('id') == device_id
            ][0]
        except IndexError:
            return None
        
    def get_sensor_by_id(self, device_id: str, sensor_id: str):
        """Return sensor by sensor id."""
        device = self.get_device_by_id(device_id)
        if device:
            return [
                sensor for sensor in device.get('sensors', []) if sensor.get('id') == sensor_id
            ][0]
        return None
