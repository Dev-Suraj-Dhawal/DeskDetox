"""Open data tools for DeskDetox.

Provides local geolocation, Open-Meteo weather forecasting,
and OpenStreetMap Overpass nature/greenspace discovery.
"""

from typing import Any, Dict, List, Optional
import requests
import geocoder


# Mapping of WMO Weather interpretation codes (WW) to human descriptions
WMO_WEATHER_CODES: Dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    62: "Moderate rain",
    63: "Heavy rain",
    65: "Very heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_location() -> Dict[str, Any]:
    """Get the user's current city, latitude, and longitude based on their IP address."""
    # 1. Try geocoder IP lookup
    try:
        g = geocoder.ip("me")
        if g.ok and g.latlng and len(g.latlng) == 2:
            lat, lon = g.latlng
            city = g.city or g.state or "Local Area"
            return {
                "city": city,
                "latitude": round(lat, 4),
                "longitude": round(lon, 4),
                "region": g.state or "",
                "country": g.country or "",
                "source": "geocoder",
            }
    except Exception:
        pass

    # 2. Fallback to free ip-api.com
    try:
        resp = requests.get("http://ip-api.com/json/", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                return {
                    "city": data.get("city", "Local Area"),
                    "latitude": round(float(data.get("lat", 0.0)), 4),
                    "longitude": round(float(data.get("lon", 0.0)), 4),
                    "region": data.get("regionName", ""),
                    "country": data.get("country", ""),
                    "source": "ip-api",
                }
    except Exception:
        pass

    # 3. Safe fallback default (e.g., Central Park / NYC) if completely offline
    return {
        "city": "New York (Default Fallback)",
        "latitude": 40.785091,
        "longitude": -73.968285,
        "region": "New York",
        "country": "US",
        "source": "default_fallback",
        "note": "Could not detect IP location automatically; using default coordinates.",
    }


def get_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Fetch current weather metrics from the free Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "apparent_temperature",
            "is_day",
            "weather_code",
            "wind_speed_10m",
        ],
        "timezone": "auto",
    }

    try:
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})

        weather_code = current.get("weather_code", 0)
        temp_c = current.get("temperature_2m")
        temp_f = round(temp_c * 9 / 5 + 32, 1) if temp_c is not None else None
        feels_like_c = current.get("apparent_temperature")
        feels_like_f = round(feels_like_c * 9 / 5 + 32, 1) if feels_like_c is not None else None
        is_day = bool(current.get("is_day", 1))
        wind_speed = current.get("wind_speed_10m")

        condition = WMO_WEATHER_CODES.get(weather_code, "Pleasant outdoor weather")

        return {
            "temperature_c": temp_c,
            "temperature_f": temp_f,
            "feels_like_c": feels_like_c,
            "feels_like_f": feels_like_f,
            "condition": condition,
            "is_daylight": is_day,
            "daylight_status": "Daytime ☀️" if is_day else "Nighttime 🌙",
            "wind_speed_kmh": wind_speed,
            "status": "success",
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Failed to retrieve weather data: {exc}",
            "condition": "Mild outdoor weather",
            "temperature_c": 18.0,
            "temperature_f": 64.4,
            "is_daylight": True,
            "daylight_status": "Daytime ☀️",
        }


def get_nearby_nature(lat: float, lon: float, radius: int = 1500) -> Dict[str, Any]:
    """Query OpenStreetMap Overpass API for nearby parks, trails, gardens, and green spaces."""
    overpass_endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ]

    query = f"""
    [out:json][timeout:15];
    (
      node["leisure"="park"](around:{radius},{lat},{lon});
      way["leisure"="park"](around:{radius},{lat},{lon});
      node["leisure"="nature_reserve"](around:{radius},{lat},{lon});
      way["leisure"="nature_reserve"](around:{radius},{lat},{lon});
      node["leisure"="garden"](around:{radius},{lat},{lon});
      way["leisure"="garden"](around:{radius},{lat},{lon});
      node["tourism"="viewpoint"](around:{radius},{lat},{lon});
      way["highway"="path"](around:{radius},{lat},{lon});
      node["natural"="water"](around:{radius},{lat},{lon});
      way["natural"="water"](around:{radius},{lat},{lon});
    );
    out tags 20;
    """

    for endpoint in overpass_endpoints:
        try:
            resp = requests.post(
                endpoint,
                data={"data": query},
                headers={"User-Agent": "DeskDetox/1.0 (Hackathon Touch Grass Project)"},
                timeout=12,
            )
            if resp.status_code == 200:
                data = resp.json()
                elements = data.get("elements", [])
                places: List[Dict[str, str]] = []
                seen_names = set()

                for el in elements:
                    tags = el.get("tags", {})
                    name = tags.get("name")
                    if name and name not in seen_names:
                        seen_names.add(name)
                        place_type = (
                            tags.get("leisure")
                            or tags.get("tourism")
                            or tags.get("natural")
                            or tags.get("highway")
                            or "green space"
                        )
                        places.append({
                            "name": name,
                            "type": place_type.replace("_", " ").title(),
                        })

                if places:
                    return {
                        "count": len(places),
                        "radius_meters": radius,
                        "green_spaces": places[:8],
                        "status": "success",
                    }
                else:
                    return {
                        "count": 0,
                        "radius_meters": radius,
                        "green_spaces": [],
                        "note": (
                            f"No officially named parks found within {radius}m on OpenStreetMap, "
                            "but local neighborhood sidewalks, tree-lined streets, or open skies are available."
                        ),
                        "status": "success",
                    }
        except Exception:
            continue

    return {
        "count": 1,
        "radius_meters": radius,
        "green_spaces": [
            {"name": "Nearest Neighborhood Park or Tree Canopy", "type": "Park / Green Path"}
        ],
        "note": "Overpass API temporarily congested. Advise the user to find the closest trees or open outdoor space.",
        "status": "fallback",
    }


def get_air_quality(lat: float, lon: float) -> Dict[str, Any]:
    """Fetch real-time air quality (AQI) and UV Index from Open-Meteo."""
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["us_aqi", "pm2_5", "uv_index"]
    }
    
    try:
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})
        
        aqi = current.get("us_aqi", 0)
        uv = current.get("uv_index", 0)
        
        aqi_warning = "Hazardous" if aqi > 100 else "Safe"
        uv_warning = "High (Needs Shade)" if uv > 6 else "Safe"

        return {
            "aqi": aqi,
            "aqi_status": aqi_warning,
            "pm2_5_ug_m3": current.get("pm2_5", "Unknown"),
            "uv_index": uv,
            "uv_status": uv_warning,
            "status": "success"
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Failed to retrieve air quality data: {exc}",
            "aqi_status": "Unknown",
            "uv_status": "Unknown"
        }