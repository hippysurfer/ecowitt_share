#!/usr/bin/env python3
"""
Ecowitt Share Diagnostic Script
================================
Run this script to reveal the exact JSON structure returned by the
Ecowitt /index/home endpoint for your station.

Usage:
    python3 ecowitt_diagnose.py D2H86Q

It will:
1. Fetch the device list to get your device_id
2. Fetch the live data endpoint
3. Print the full JSON response, nicely formatted
4. Print a suggested SENSOR_PATH mapping for the HA integration
"""

import sys
import json
import urllib.request
import urllib.error

BASE_URL = "https://www.ecowitt.net"


def fetch(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def flatten(obj, prefix=""):
    """Recursively flatten a JSON object to dot-paths and values."""
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            results.extend(flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            results.extend(flatten(v, f"{prefix}[{i}]"))
    else:
        results.append((prefix, obj))
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ecowitt_diagnose.py <AUTHORIZE_CODE>")
        print("Example: python3 ecowitt_diagnose.py D2H86Q")
        sys.exit(1)

    authorize = sys.argv[1].strip()
    print(f"\n{'='*60}")
    print(f"Ecowitt Share Diagnostic — authorize: {authorize}")
    print(f"{'='*60}\n")

    # Step 1: get device list
    print("Step 1: Fetching device list...")
    try:
        device_data = fetch(f"{BASE_URL}/index/get_device_list?authorize={authorize}")
    except Exception as e:
        print(f"  ERROR: {e}")
        sys.exit(1)

    print(f"  Response: {json.dumps(device_data, indent=2)}\n")

    if device_data.get("errcode") != "0":
        print(f"  ERROR: {device_data.get('errmsg', 'Unknown error')}")
        sys.exit(1)

    devices = device_data.get("list", [])
    if not devices:
        print("  ERROR: No devices found.")
        sys.exit(1)

    device = devices[0]
    device_id = device["device_id"]
    print(f"  Found device: '{device.get('name')}' (id: {device_id})\n")

    # Step 2: fetch live data
    print("Step 2: Fetching live sensor data...")
    url = f"{BASE_URL}/index/home?device_id={device_id}&authorize={authorize}"
    print(f"  URL: {url}\n")

    try:
        live_data = fetch(url)
    except Exception as e:
        print(f"  ERROR: {e}")
        sys.exit(1)

    print("Full JSON response:")
    print("-" * 60)
    print(json.dumps(live_data, indent=2))
    print("-" * 60)

    # Step 3: flatten all paths
    print("\nAll data paths (for integration mapping):")
    print("-" * 60)
    paths = flatten(live_data)
    for path, value in paths:
        print(f"  {path:<55} = {repr(value)}")

    # Step 4: verify confirmed sensor paths and transforms
    print("\n" + "=" * 60)
    print("Sensor path verification (confirmed against real data):")
    print("=" * 60)

    MPH_TO_MS = 0.44704

    # (json_path, friendly_name, unit, transform)
    # transform: None = plain float, "mph_to_ms" = *0.44704, "strip_commas" = remove , then float
    CONFIRMED_SENSORS = [
        ("temp.data.tempf.value",                "Outdoor Temperature",       "°C",    None),
        ("temp.data.humidity.value",             "Outdoor Humidity",          "%",     None),
        ("temp.data.drew_temp.value",            "Dew Point",                 "°C",    None),
        ("temp.data.sendible_temp.value",        "Feels Like",                "°C",    None),
        ("temp.data.vpd.value",                  "Vapour Pressure Deficit",   "kPa",   None),
        ("tempin.data.tempinf.value",            "Indoor Temperature",        "°C",    None),
        ("tempin.data.humidityin.value",         "Indoor Humidity",           "%",     None),
        ("tempin.data.drew_tempin.value",        "Indoor Dew Point",          "°C",    None),
        ("tempin.data.sendible_tempin.value",    "Indoor Feels Like",         "°C",    None),
        ("pressure.data.baromrelin.value",       "Relative Pressure",         "hPa",   "strip_commas"),
        ("pressure.data.baromabsin.value",       "Absolute Pressure",         "hPa",   "strip_commas"),
        ("wind.data.windspeedmph.value",         "Wind Speed",                "m/s",   "mph_to_ms"),
        ("wind.data.windgustmph.value",          "Wind Gust",                 "m/s",   "mph_to_ms"),
        ("wind.data.winddir.value",              "Wind Direction",            "°",     None),
        ("wind.data.winddir.avg10m",             "Wind Direction 10 min avg", "°",     None),
        ("rain_piezo.data.rrain_piezo.value",    "Rain Rate",                 "mm/hr", None),
        ("rain_piezo.data.drain_piezo.value",    "Daily Rainfall",            "mm",    None),
        ("rain_piezo.data.hrain_piezo.value",    "Hourly Rainfall",           "mm",    None),
        ("rain_piezo.data.erain_piezo.value",    "Event Rainfall",            "mm",    None),
        ("rain_piezo.data.last24hrain_piezo.value", "Rainfall Last 24h",      "mm",    None),
        ("rain_piezo.data.wrain_piezo.value",    "Weekly Rainfall",           "mm",    None),
        ("rain_piezo.data.mrain_piezo.value",    "Monthly Rainfall",          "mm",    None),
        ("rain_piezo.data.yrain_piezo.value",    "Yearly Rainfall",           "mm",    None),
        ("so_uv.data.solarradiation.value",      "Solar Radiation",           "W/m²",  None),
        ("so_uv.data.uv.value",                  "UV Index",                  "",      None),
        ("ch_lds1.data.air_ch1.value",           "LDS CH1 Distance",          "mm",    "strip_commas"),
    ]

    def get_nested(data, path):
        current = data
        for key in path.split("."):
            if not isinstance(current, dict):
                return None
            current = current.get(key)
            if current is None:
                return None
        return current

    def apply_transform(raw, transform):
        if raw is None:
            return None
        try:
            if transform == "strip_commas":
                return round(float(str(raw).replace(",", "")), 4)
            elif transform == "mph_to_ms":
                return round(float(raw) * MPH_TO_MS, 2)
            else:
                return float(raw)
        except (ValueError, TypeError):
            return raw

    data = live_data.get("data", live_data)

    passed = 0
    failed = 0
    missing = 0

    print(f"\n  {'Sensor':<28} {'Path':<45} {'Result'}")
    print(f"  {'-'*28} {'-'*45} {'-'*25}")
    for path, name, unit, transform in CONFIRMED_SENSORS:
        raw = get_nested(data, path)
        if raw is None:
            status = "✗  NOT FOUND"
            missing += 1
        else:
            value = apply_transform(raw, transform)
            note = f" (raw: {repr(raw)})" if transform else ""
            status = f"✓  {value} {unit}{note}"
            passed += 1

        print(f"  {name:<28} {path:<45} {status}")

    print(f"\n  Results: {passed} passed, {missing} not found, {failed} errors")
    if missing:
        print("  Sensors marked ✗ are not present on this station (hardware not fitted).")
    else:
        print("  All sensors found — integration should work without changes.")
    print()


if __name__ == "__main__":
    main()