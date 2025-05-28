"""Config flow for IPTV Media Source."""

import voluptuous as vol
import logging
import aiohttp

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_SOURCE_TYPE,
    CONF_COUNTRY_CODE,
    CONF_M3U_URL,
    CONF_FRIENDLY_NAME,
    CONF_FLAG_URL,  # Import new constant
    SOURCE_IPTV_ORG,
    SOURCE_CUSTOM_URL,
    IPTV_ORG_COUNTRIES_URL,
    IPTV_ORG_STREAMS_BASE_URL,
    IPTV_ORG_FLAGS_BASE_URL,  # Import new constant
)

_LOGGER = logging.getLogger(__name__)


# --- Helper for Flag Emojis ---
def get_flag_emoji(country_code: str) -> str:
    """Convert a two-letter country code to a flag emoji string."""
    if len(country_code) == 2:
        code_upper = country_code.upper()
        # Regional Indicator Symbol Letters A-Z are U+1F1E6 to U+1F1FF
        try:
            return (
                chr(ord(code_upper[0]) - ord("A") + 0x1F1E6)
                + chr(ord(code_upper[1]) - ord("A") + 0x1F1E6)
                + " "
            )
        except ValueError:  # Non A-Z char
            return ""
    return ""


# --- Schema Steps ---
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SOURCE_TYPE, default=SOURCE_IPTV_ORG): vol.In(
            {
                SOURCE_IPTV_ORG: "Select from IPTV.org list",
                SOURCE_CUSTOM_URL: "Provide custom M3U8 URL",
            }
        )
    }
)

STEP_CUSTOM_URL_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_M3U_URL): str,
        vol.Optional(CONF_FRIENDLY_NAME, default="Custom IPTV"): str,
    }
)


async def fetch_iptv_org_data(session: aiohttp.ClientSession) -> tuple[dict, dict]:
    """
    Fetch country list for display (with flags) and raw data for config.
    Returns:
        - countries_for_display: { "us": "🇺🇸 United States (US)" }
        - countries_raw_data:    { "us": {"name": "United States", "code_upper": "US"} }
    """
    countries_for_display = {}
    countries_raw_data = {}
    try:
        _LOGGER.debug(f"Fetching countries from: {IPTV_ORG_COUNTRIES_URL}")
        async with session.get(IPTV_ORG_COUNTRIES_URL) as response:
            response.raise_for_status()
            data = await response.json()  # List of country objects
            for country_info in data:
                country_code_upper = country_info.get("code")  # e.g., "US"
                country_name_raw = country_info.get("name")  # e.g., "United States"

                if country_code_upper and country_name_raw:
                    country_code_lower = country_code_upper.lower()
                    flag_emoji = get_flag_emoji(country_code_upper)
                    countries_for_display[country_code_lower] = (
                        f"{flag_emoji}{country_name_raw} "  # ({country_code_upper})"
                    )
                    countries_raw_data[country_code_lower] = {
                        "name": country_name_raw,
                        "code_upper": country_code_upper,
                    }
            _LOGGER.debug(f"Fetched {len(countries_for_display)} countries")
            # Sort by the display name (which includes flag and country name)
            sorted_countries_for_display = dict(
                sorted(countries_for_display.items(), key=lambda item: item[1])
            )
            return sorted_countries_for_display, countries_raw_data
    except aiohttp.ClientError as err:
        _LOGGER.error(f"Error fetching IPTV.org countries: {err}")
        return {"error": "Could not fetch country list"}, {}
    except Exception as err:
        _LOGGER.error(f"Unexpected error fetching IPTV.org countries: {err}")
        return {"error": "Unexpected error fetching country list"}, {}


class IPTVMediaSourceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for IPTV Media Source."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize the config flow."""
        self.user_input = {}
        self.iptv_org_countries_display = {}  # For dropdown
        self.iptv_org_countries_data = {}  # For processing selection

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        self.user_input.update(user_input)

        if user_input[CONF_SOURCE_TYPE] == SOURCE_IPTV_ORG:
            return await self.async_step_select_country()
        elif user_input[CONF_SOURCE_TYPE] == SOURCE_CUSTOM_URL:
            return await self.async_step_custom_url()

        return self.async_abort(reason="unknown_source_type")

    async def async_step_select_country(self, user_input=None):
        """Handle the step to select a country from IPTV.org."""
        if not self.iptv_org_countries_display:  # Check if already fetched
            session = async_get_clientsession(self.hass)
            display_data, raw_data = await fetch_iptv_org_data(session)
            if "error" in display_data:
                _LOGGER.warning(
                    "Failed to fetch or no countries found from IPTV.org API."
                )
                return self.async_abort(reason="cannot_connect_iptv_org")
            self.iptv_org_countries_display = display_data
            self.iptv_org_countries_data = raw_data

        if not self.iptv_org_countries_display:  # Still no countries
            return self.async_show_form(  # Show form with error
                step_id="select_country",
                # No data schema means it will just show description and errors
                errors={"base": "no_countries_found"},
            )

        if user_input is None:
            country_schema = vol.Schema(
                {
                    vol.Required(CONF_COUNTRY_CODE): vol.In(
                        self.iptv_org_countries_display
                    )
                }
            )
            return self.async_show_form(
                step_id="select_country", data_schema=country_schema
            )

        selected_country_code_lower = user_input[CONF_COUNTRY_CODE]  # e.g., "us"
        country_data = self.iptv_org_countries_data.get(selected_country_code_lower)

        if not country_data:
            _LOGGER.error(
                f"Selected country code '{selected_country_code_lower}' not found in processed data."
            )
            return self.async_abort(
                reason="unknown_error"
            )  # Should not happen if list is correct

        country_name_for_entry = country_data["name"]  # Raw name without emoji

        m3u_url = f"{IPTV_ORG_STREAMS_BASE_URL}{selected_country_code_lower}.m3u"
        # Construct flag URL using lowercase country code
        flag_image_url = f"{IPTV_ORG_FLAGS_BASE_URL}{selected_country_code_lower.upper()}/flat/64.png"

        final_data = {
            CONF_SOURCE_TYPE: SOURCE_IPTV_ORG,
            CONF_M3U_URL: m3u_url,
            CONF_FRIENDLY_NAME: f"IPTV.org - {country_name_for_entry}",  # Name without emoji
            CONF_COUNTRY_CODE: selected_country_code_lower,
            CONF_FLAG_URL: flag_image_url,  # Store the flag image URL
        }

        entry_title = f"IPTV.org - {country_name_for_entry}"

        await self.async_set_unique_id(f"iptv_org_{selected_country_code_lower}")
        self._abort_if_unique_id_configured(
            updates=final_data
        )  # Pass updates for existing entry

        _LOGGER.info(
            f"Configuring IPTV.org for {country_name_for_entry} with URL: {m3u_url}"
        )
        return self.async_create_entry(title=entry_title, data=final_data)

    async def async_step_custom_url(self, user_input=None):
        """Handle the step to provide a custom M3U URL."""
        errors = {}
        if user_input is None:
            return self.async_show_form(
                step_id="custom_url", data_schema=STEP_CUSTOM_URL_SCHEMA
            )

        custom_m3u_url = user_input[CONF_M3U_URL]
        if not custom_m3u_url.lower().endswith((".m3u", ".m3u8")):
            errors[CONF_M3U_URL] = "invalid_m3u_url"

        if errors:
            return self.async_show_form(
                step_id="custom_url", data_schema=STEP_CUSTOM_URL_SCHEMA, errors=errors
            )

        friendly_name = user_input.get(CONF_FRIENDLY_NAME, "Custom IPTV")
        final_data = {
            CONF_SOURCE_TYPE: SOURCE_CUSTOM_URL,
            CONF_M3U_URL: custom_m3u_url,
            CONF_FRIENDLY_NAME: friendly_name,
            CONF_FLAG_URL: None,  # No flag URL for custom entries
        }

        await self.async_set_unique_id(f"custom_{hash(custom_m3u_url)}")
        self._abort_if_unique_id_configured(updates=final_data)

        _LOGGER.info(f"Configuring custom IPTV with URL: {custom_m3u_url}")
        return self.async_create_entry(title=friendly_name, data=final_data)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for IPTV Media Source."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry
        self.current_data = dict(config_entry.data)

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}
        if user_input is not None:
            updated_data = self.current_data.copy()
            # Only allow friendly name and m3u_url (if custom) to be changed here
            updated_data[CONF_FRIENDLY_NAME] = user_input[CONF_FRIENDLY_NAME]

            if self.current_data.get(CONF_SOURCE_TYPE) == SOURCE_CUSTOM_URL:
                updated_data[CONF_M3U_URL] = user_input[CONF_M3U_URL]
                if not updated_data[CONF_M3U_URL].lower().endswith((".m3u", ".m3u8")):
                    errors["base"] = "invalid_m3u_url_format"

            if not errors:
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=updated_data
                )
                _LOGGER.info(f"IPTV Media Source {self.config_entry.title} updated.")
                return self.async_create_entry(title="", data={})

        # Build schema based on source type
        schema_dict = {
            vol.Required(
                CONF_FRIENDLY_NAME, default=self.current_data.get(CONF_FRIENDLY_NAME)
            ): str,
        }
        if self.current_data.get(CONF_SOURCE_TYPE) == SOURCE_CUSTOM_URL:
            schema_dict[
                vol.Required(CONF_M3U_URL, default=self.current_data.get(CONF_M3U_URL))
            ] = str
        else:  # For IPTV.org, M3U URL is not editable here.
            schema_dict[vol.Disabled(CONF_M3U_URL)] = self.current_data.get(
                CONF_M3U_URL
            )

        options_schema = vol.Schema(schema_dict)

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
        )
