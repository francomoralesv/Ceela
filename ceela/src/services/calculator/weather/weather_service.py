import json
import os

from fastapi import HTTPException
import requests

from src.models.entity.weather_data import WeatherMetadata


def get_weather_data_from_coord_one(db, latitude, longitude, zone=None):
    print('[INFO] Getting weather data from coordinates')
    try:
        weather_data = get_weather_data_from_coord(db, latitude, longitude, zone)
        if not weather_data:
            raise HTTPException(status_code=404, detail="No se encontraron datos meteorológicos para las coordenadas proporcionadas")
        return weather_data[0]
    except Exception as e:
        print(f"Error al obtener datos meteorológicos: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener datos meteorológicos")

def get_weather_geocoding(latitude,longitude):
    print(f"[INFO] Run reverse geocoding for latitude: {latitude}, longitude: {longitude}")
    url = f'https://places.geo.{os.getenv('AWS_REGION')}.amazonaws.com/v2/reverse-geocode'
    headers = {
        'Content-Type': 'application/json',
    }
    params = {
        'key': os.getenv('PLACES_API_KEY')
    }
    data = {
        'QueryPosition': [longitude,latitude]
    }

    try:
        response = requests.post(url, headers=headers,
                                 params=params, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error in reverse geocoding request: {e}")
        raise HTTPException(
            status_code=500, detail="Error communicating with Places API")
    result = response.json()
    print('[INFO] Reverse geocoding complete', result)
    if result is None and len(result["ResultItems"]) <= 0:
        raise Exception("Error in reverse geocoding response")
    
    place = result["ResultItems"][0]
    address = place.get("Address", {})
    country = address.get("Country", {}).get(
        "Code3", "").lower().replace(' ', '_')
    city = address.get("Locality", "").lower().replace(' ', '_')
    district = address.get("SubRegion", "").get("Name").lower().replace(' ', '_')
    print(f"[INFO] Geocoding results - Country: {country}, City: {city}, District: {district}")
    return country, city, district

def get_weather_data_from_coord(db, latitude,longitude, zone=None):
    """
    Get the thermal zone based on latitude and longitude using AWS Places API 
    and search matching weather data.
    """

    country, city, district = get_weather_geocoding(latitude, longitude)
    print(
        f"[INFO]Geocoding results - Country: {country}, City: {city}, District: {district}")

    query = db.query(WeatherMetadata)
    if country:
        query = query.filter(WeatherMetadata.country == country)
    if city:
        query = query.filter(WeatherMetadata.city == city)
    if district:
        query = query.filter(WeatherMetadata.district == district)
    if zone:
        query = query.filter(WeatherMetadata.zone == zone)
    weather_data = query.order_by(WeatherMetadata.created_at.desc()).all()
    return weather_data