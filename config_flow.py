"""Config flow for Vitesy integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_POLLING_INTERVAL,
    DEFAULT_POLLING_INTERVAL,
    MIN_POLLING_INTERVAL,
    MAX_POLLING_INTERVAL,
)
from vitesy.client import VitesyClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_API_KEY,
            description={
                "suggested_value": "",
                "placeholder": "Enter your Vitesy API key"
            }
        ): cv.string,
        vol.Optional(
            CONF_POLLING_INTERVAL,
            default=DEFAULT_POLLING_INTERVAL,
            description={"suffix": "seconds"},
        ): vol.All(
            vol.Coerce(int),
            vol.Range(min=MIN_POLLING_INTERVAL, max=MAX_POLLING_INTERVAL)
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect to Vitesy.

    Args:
        hass: The Home Assistant instance.
        data: The user input data containing the API key.

    Returns:
        Dict containing the title for the config entry.

    Raises:
        CannotConnect: Error connecting to Vitesy API.
        InvalidAuth: Invalid API key.
    """
    api = VitesyClient(data[CONF_API_KEY])
    
    try:
        devices = await hass.async_add_executor_job(api.get_devices)
        if not devices:
            _LOGGER.warning("No Vitesy devices found")
            
    except Exception as err:
        _LOGGER.exception("Unexpected error occurred")
        raise CannotConnect from err
    return {"title": f"Vitesy - {data[CONF_API_KEY]}"}


class VitesyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vitesy integration."""

    VERSION = 1
    _input_data: dict[str, Any]

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return VitesyOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step of the config flow.
        
        Args:
            user_input: Dictionary containing user input. None if form needs to be shown.
            
        Returns:
            The result of the config flow step.
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if "base" not in errors:
                # Validation was successful, so create a unique id for this instance of your integration
                # and create the config entry.
                await self.async_set_unique_id(info.get("title"))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> VitesyOptionsFlowHandler:
        """Get the options flow for this handler.
        
        Args:
            config_entry: The config entry being edited.
            
        Returns:
            The options flow handler.
        """
        return VitesyOptionsFlowHandler(config_entry)


class VitesyOptionsFlowHandler(OptionsFlow):
    """Handle Vitesy options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow.
        
        Args:
            config_entry: The config entry being edited.
        """
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage basic options.
        
        Args:
            user_input: Dictionary containing user input. None if form needs to be shown.
            
        Returns:
            The result of the options flow step.
        """
        if user_input is not None:
            options = self.config_entry.options | user_input
            return self.async_create_entry(title="", data=options)

        # It is recommended to prepopulate options fields with default values if available.
        # These will be the same default values you use on your coordinator for setting variable values
        # if the option has not been set.
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_API_KEY,
                    default=self.options.get(CONF_API_KEY, "xxxx"),
                ): str,
                vol.Optional(
                    CONF_POLLING_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_POLLING_INTERVAL,
                        self.config_entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
                    ),
                    description={"suffix": "seconds"},
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(
                        min=MIN_POLLING_INTERVAL,
                        max=MAX_POLLING_INTERVAL,
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""