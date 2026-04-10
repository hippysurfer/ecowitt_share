"""Constants for Ecowitt Share integration."""

DOMAIN = "ecowitt_share"

# Base URLs
BASE_URL = "https://www.ecowitt.net"
DEVICE_LIST_URL = f"{BASE_URL}/index/get_device_list"
DEVICE_DATA_URL = f"{BASE_URL}/index/home"

DEFAULT_SCAN_INTERVAL = 60  # seconds

CONF_AUTHORIZE = "authorize"

# Actual JSON structure returned by /index/home (confirmed via diagnostic):
#
# data.<group>.data.<sensor_key>.value
#
# Groups and keys:
#   temp        → tempf, humidity, drew_temp, sendible_temp, vpd
#   tempin      → tempinf, humidityin, drew_tempin, sendible_tempin
#   pressure    → baromrelin, baromabsin
#   wind        → windspeedmph, windgustmph, winddir   (speed/gust in mph!)
#   rain_piezo  → rrain_piezo, drain_piezo, hrain_piezo, wrain_piezo,
#                 mrain_piezo, yrain_piezo, erain_piezo, last24hrain_piezo
#   so_uv       → solarradiation, uv
#   ch_lds1     → air_ch1  (LDS water level / distance sensor)
#
# Quirks to handle:
#   - Pressure values arrive as comma-formatted strings e.g. "1,012.2"
#   - Wind speed/gust arrive in mph → converted to m/s (* 0.44704)
#   - ch_lds1 distance arrives as comma-formatted e.g. "1,938"

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    UnitOfTemperature,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfIrradiance,
    UnitOfVolumetricFlux,
    DEGREE,
    UnitOfLength,
)

# Each tuple: (json_path, friendly_name, unit, device_class, state_class, icon, transform)
#
# transform values:
#   None          – plain float conversion
#   "mph_to_ms"   – multiply by 0.44704 after float conversion
#   "strip_commas"– remove thousands-separator commas before float conversion

SENSOR_DESCRIPTIONS = [
    # ── Outdoor ──────────────────────────────────────────────────────────────
    (
        "temp.data.tempf.value",
        "Outdoor Temperature",
        UnitOfTemperature.CELSIUS,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        None,
        None,
    ),
    (
        "temp.data.humidity.value",
        "Outdoor Humidity",
        PERCENTAGE,
        SensorDeviceClass.HUMIDITY,
        SensorStateClass.MEASUREMENT,
        None,
        None,
    ),
    (
        "temp.data.drew_temp.value",
        "Dew Point",
        UnitOfTemperature.CELSIUS,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        "mdi:thermometer-water",
        None,
    ),
    (
        "temp.data.sendible_temp.value",
        "Feels Like",
        UnitOfTemperature.CELSIUS,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        "mdi:thermometer",
        None,
    ),
    (
        "temp.data.vpd.value",
        "Vapour Pressure Deficit",
        "kPa",
        SensorDeviceClass.PRESSURE,
        SensorStateClass.MEASUREMENT,
        "mdi:water-percent",
        None,
    ),
    # ── Indoor ───────────────────────────────────────────────────────────────
    (
        "tempin.data.tempinf.value",
        "Indoor Temperature",
        UnitOfTemperature.CELSIUS,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        None,
        None,
    ),
    (
        "tempin.data.humidityin.value",
        "Indoor Humidity",
        PERCENTAGE,
        SensorDeviceClass.HUMIDITY,
        SensorStateClass.MEASUREMENT,
        None,
        None,
    ),
    (
        "tempin.data.drew_tempin.value",
        "Indoor Dew Point",
        UnitOfTemperature.CELSIUS,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        "mdi:thermometer-water",
        None,
    ),
    (
        "tempin.data.sendible_tempin.value",
        "Indoor Feels Like",
        UnitOfTemperature.CELSIUS,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        "mdi:thermometer",
        None,
    ),
    # ── Pressure ─────────────────────────────────────────────────────────────
    # Values arrive as "1,012.2" — thousands comma must be stripped
    (
        "pressure.data.baromrelin.value",
        "Relative Pressure",
        UnitOfPressure.HPA,
        SensorDeviceClass.PRESSURE,
        SensorStateClass.MEASUREMENT,
        None,
        "strip_commas",
    ),
    (
        "pressure.data.baromabsin.value",
        "Absolute Pressure",
        UnitOfPressure.HPA,
        SensorDeviceClass.PRESSURE,
        SensorStateClass.MEASUREMENT,
        None,
        "strip_commas",
    ),
    # ── Wind ─────────────────────────────────────────────────────────────────
    # windspeedmph / windgustmph arrive in mph → converted to m/s
    (
        "wind.data.windspeedmph.value",
        "Wind Speed",
        UnitOfSpeed.METERS_PER_SECOND,
        SensorDeviceClass.WIND_SPEED,
        SensorStateClass.MEASUREMENT,
        None,
        "mph_to_ms",
    ),
    (
        "wind.data.windgustmph.value",
        "Wind Gust",
        UnitOfSpeed.METERS_PER_SECOND,
        SensorDeviceClass.WIND_SPEED,
        SensorStateClass.MEASUREMENT,
        "mdi:weather-windy",
        "mph_to_ms",
    ),
    (
        "wind.data.winddir.value",
        "Wind Direction",
        DEGREE,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:compass-rose",
        None,
    ),
    (
        "wind.data.winddir.avg10m",
        "Wind Direction 10 min avg",
        DEGREE,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:compass",
        None,
    ),
    # ── Rainfall (Piezo) ─────────────────────────────────────────────────────
    (
        "rain_piezo.data.rrain_piezo.value",
        "Rain Rate",
        UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR,
        SensorDeviceClass.PRECIPITATION_INTENSITY,
        SensorStateClass.MEASUREMENT,
        None,
        None,
    ),
    (
        "rain_piezo.data.drain_piezo.value",
        "Daily Rainfall",
        "mm",
        SensorDeviceClass.PRECIPITATION,
        SensorStateClass.TOTAL_INCREASING,
        None,
        None,
    ),
    (
        "rain_piezo.data.hrain_piezo.value",
        "Hourly Rainfall",
        "mm",
        SensorDeviceClass.PRECIPITATION,
        SensorStateClass.MEASUREMENT,
        None,
        None,
    ),
    (
        "rain_piezo.data.erain_piezo.value",
        "Event Rainfall",
        "mm",
        SensorDeviceClass.PRECIPITATION,
        SensorStateClass.MEASUREMENT,
        None,
        None,
    ),
    (
        "rain_piezo.data.last24hrain_piezo.value",
        "Rainfall Last 24h",
        "mm",
        SensorDeviceClass.PRECIPITATION,
        SensorStateClass.MEASUREMENT,
        None,
        None,
    ),
    (
        "rain_piezo.data.wrain_piezo.value",
        "Weekly Rainfall",
        "mm",
        SensorDeviceClass.PRECIPITATION,
        SensorStateClass.TOTAL_INCREASING,
        None,
        None,
    ),
    (
        "rain_piezo.data.mrain_piezo.value",
        "Monthly Rainfall",
        "mm",
        SensorDeviceClass.PRECIPITATION,
        SensorStateClass.TOTAL_INCREASING,
        None,
        None,
    ),
    (
        "rain_piezo.data.yrain_piezo.value",
        "Yearly Rainfall",
        "mm",
        SensorDeviceClass.PRECIPITATION,
        SensorStateClass.TOTAL_INCREASING,
        None,
        None,
    ),
    # ── Solar & UV ───────────────────────────────────────────────────────────
    (
        "so_uv.data.solarradiation.value",
        "Solar Radiation",
        UnitOfIrradiance.WATTS_PER_SQUARE_METER,
        SensorDeviceClass.IRRADIANCE,
        SensorStateClass.MEASUREMENT,
        None,
        None,
    ),
    (
        "so_uv.data.uv.value",
        "UV Index",
        "UV index",
        SensorDeviceClass.UV_INDEX,
        SensorStateClass.MEASUREMENT,
        None,
        None,
    ),
    # ── LDS Water Level / Distance Sensor (ch_lds1) ──────────────────────────
    # air_ch1 = distance from sensor head down to water surface (mm)
    # Value arrives comma-formatted e.g. "1,938"
    (
        "ch_lds1.data.air_ch1.value",
        "LDS CH1 Distance",
        UnitOfLength.MILLIMETERS,
        SensorDeviceClass.DISTANCE,
        SensorStateClass.MEASUREMENT,
        "mdi:waves",
        "strip_commas",
    ),
]
