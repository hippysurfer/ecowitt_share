# Ecowitt Share — Home Assistant Custom Integration

**NOTE** - This is a very early prototype. It has been generated almost completely using AI. It almost certainly will not work for you.
 

Adds sensors to Home Assistant from any **publicly shared** Ecowitt weather station — no API key or account required. All you need is the 6-character **authorize code** from the share URL.

## How it works

The integration uses Ecowitt's own undocumented public share API:

1. `GET https://www.ecowitt.net/index/get_device_list?authorize=<CODE>` — resolves the device ID
2. `GET https://www.ecowitt.net/index/home?device_id=<ID>&authorize=<CODE>` — fetches live sensor data

This is the same data shown on the public share page (`ecowitt.net/home/share?authorize=…`).

## Installation

### Via HACS (recommended)
1. In HACS → Integrations → ⋮ → Custom repositories
2. Add the URL of this repo, category **Integration**
3. Install **Ecowitt (Public Share)**
4. Restart Home Assistant

### Manual
1. Copy the `custom_components/ecowitt_share/` folder into your HA `config/custom_components/` directory
2. Restart Home Assistant

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Ecowitt Public Share**
3. Enter the authorize code from your share URL

   Example: for `https://www.ecowitt.net/home/share?authorize=D2H86Q`, enter `D2H86Q`

4. Click **Submit** — HA will validate the code and create the sensors

## Sensors created

All sensors are grouped under a single device named after your weather station.

| Sensor | Unit | Device Class |
|---|---|---|
| Outdoor Temperature | °C | temperature |
| Outdoor Humidity | % | humidity |
| Dew Point | °C | temperature |
| Feels Like | °C | temperature |
| Vapour Pressure Deficit | kPa | pressure |
| Indoor Temperature | °C | temperature |
| Indoor Humidity | % | humidity |
| Indoor Dew Point | °C | temperature |
| Indoor Feels Like | °C | temperature |
| Relative Pressure | hPa | pressure |
| Absolute Pressure | hPa | pressure |
| Wind Speed | m/s | wind_speed |
| Wind Gust | m/s | wind_speed |
| Wind Direction | ° | — |
| Wind Direction 10 min avg | ° | — |
| Rain Rate | mm/h | precipitation_intensity |
| Hourly Rainfall | mm | precipitation |
| Event Rainfall | mm | precipitation |
| Rainfall Last 24h | mm | precipitation |
| Daily Rainfall | mm | precipitation |
| Weekly Rainfall | mm | precipitation |
| Monthly Rainfall | mm | precipitation |
| Yearly Rainfall | mm | precipitation |
| Solar Radiation | W/m² | irradiance |
| UV Index | UV index | uv_index |
| LDS CH1 Distance | mm | distance |

Sensors that are not present in the station's data will show as **unavailable** rather than erroring.

## Notes

- **Polling interval**: 60 seconds (configurable in `const.py` via `DEFAULT_SCAN_INTERVAL`)
- **Data availability**: Only sensors transmitted by your specific station hardware will have values
- **Units**: Values are returned in whatever units your station is configured to use on ecowitt.net — most stations use metric (°C, hPa, mm, m/s)
- This uses an **undocumented** endpoint. It may break if Ecowitt changes their share page internals — but it has been stable for a long time

## Troubleshooting

**"The authorize code was not recognised"** — Double-check the code from your share URL. It is case-sensitive.

**Sensors show as unavailable after setup** — The `/index/home` endpoint returned data but the expected keys were missing. Enable debug logging to inspect the raw response:

```yaml
# configuration.yaml
logger:
  logs:
    custom_components.ecowitt_share: debug
```

Then check the Home Assistant log for a line beginning `Ecowitt raw response:`.
