from fastmcp import FastMCP
from statistics import mean
import operator
from duckduckgo_search import DDGS
import requests
import json

mcp = FastMCP("echo-server", version="2025-03-26")

@mcp.tool(description="Echo text back with optional casing tweaks")
def echo(text: str, upper: bool = False) -> str:
    """Return the submitted text."""
    return text.upper() if upper else text

@mcp.tool
def word_count(text: str) -> int:
    """Count characters separated by whitespace."""
    return len(text.split())

@mcp.tool
def math(a: float, b: float, op: str) -> float:
    """Perform mathematical operations. Operator can be: +, -, *, /, //, %, **"""
    ops = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '//': operator.floordiv,
        '%': operator.mod,
        '**': operator.pow
    }

    if op not in ops:
        raise ValueError(f"Invalid operator: {op}. Use: +, -, *, /, //, %, **")

    return ops[op](a, b)

@mcp.tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo."""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))

    output = []
    for result in results:
        output.append(f"Title: {result['title']}\nURL: {result['href']}\nSnippet: {result['body']}\n")

    return "\n".join(output)

@mcp.tool
def get_weather(location: str) -> str:
    """Get live weather updates for a location. Provide city name or 'latitude,longitude'."""
    # First, geocode the location using DuckDuckGo
    try:
        # Try to parse as lat,lon
        if ',' in location:
            parts = location.split(',')
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
        else:
            # Use geocoding API to get coordinates
            geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json"
            geo_response = requests.get(geocode_url, timeout=10)
            geo_response.raise_for_status()
            geo_data = geo_response.json()

            if not geo_data.get('results'):
                return f"Could not find location: {location}"

            result = geo_data['results'][0]
            lat = result['latitude']
            lon = result['longitude']
            location_name = result['name']
            country = result.get('country', '')
            location_display = f"{location_name}, {country}" if country else location_name

        # Get weather data from Open-Meteo
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m&temperature_unit=celsius&wind_speed_unit=kmh"
        weather_response = requests.get(weather_url, timeout=10)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        current = weather_data['current']

        # Weather code interpretation
        weather_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            77: "Snow grains", 80: "Slight rain showers", 81: "Moderate rain showers",
            82: "Violent rain showers", 85: "Slight snow showers", 86: "Heavy snow showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
        }

        weather_desc = weather_codes.get(current['weather_code'], "Unknown")

        if ',' in location:
            location_display = f"Coordinates ({lat}, {lon})"

        output = f"""Weather for {location_display}:
Temperature: {current['temperature_2m']}°C (feels like {current['apparent_temperature']}°C)
Conditions: {weather_desc}
Humidity: {current['relative_humidity_2m']}%
Wind Speed: {current['wind_speed_10m']} km/h
Precipitation: {current['precipitation']} mm
Last updated: {current['time']}"""

        return output

    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {str(e)}"
    except (KeyError, ValueError) as e:
        return f"Error parsing weather data: {str(e)}"

if __name__ == "__main__":
    mcp.run()  # Use stdio transport for gateway integration
