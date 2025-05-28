"""Constants for the IPTV Media Source integration."""

DOMAIN = "iptv_media_source"

# Configuration keys
CONF_SOURCE_TYPE = "source_type"
CONF_COUNTRY_CODE = "country_code"
CONF_M3U_URL = "m3u_url"
CONF_FRIENDLY_NAME = "friendly_name"
CONF_FLAG_URL = "flag_url"

# Source types
SOURCE_IPTV_ORG = "iptv_org"
SOURCE_CUSTOM_URL = "custom_url"

# API URLs
IPTV_ORG_API_BASE_URL = "https://iptv-org.github.io/api"
IPTV_ORG_COUNTRIES_URL = f"{IPTV_ORG_API_BASE_URL}/countries.json"

IPTV_ORG_FLAGS_BASE_URL = "https://flagsapi.com/"
IPTV_ORG_STREAMS_BASE_URL = (
    "https://iptv-org.github.io/iptv/countries/"  # e.g., /us.m3u
)
