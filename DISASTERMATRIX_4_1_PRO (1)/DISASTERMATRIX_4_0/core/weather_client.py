import requests

CITY_COORDS = {
    "Chennai": (13.0827,80.2707),
    "Puducherry": (11.9416,79.8083),
    "Tiruchirappalli": (10.7905,78.7047)
}

def fetch_weather(city):
    """Open-Meteo current model/API context. Not a certified rain-gauge observation."""
    lat,lon=CITY_COORDS[city]
    url="https://api.open-meteo.com/v1/forecast"
    params={"latitude":lat,"longitude":lon,"current":"temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m",
            "timezone":"Asia/Kolkata"}
    response=requests.get(url,params=params,timeout=8)
    response.raise_for_status()
    data=response.json().get("current",{})
    return data
