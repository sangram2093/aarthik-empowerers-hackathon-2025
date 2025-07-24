from datetime import datetime
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
import requests
from typing import Dict, List, Any

INDIAN_CROP_DATABASE = {
    # ... (The comprehensive database from the previous step remains unchanged) ...
    # Cereals
    "rice": [20, 37, 1000, ["kharif", "zaid"]], "wheat": [10, 25, 500, ["rabi"]],
    "maize": [21, 30, 600, ["kharif", "rabi", "zaid"]], "jowar (Sorghum)": [25, 35, 400, ["kharif", "rabi"]],
    "bajra (Pearl Millet)": [25, 35, 250, ["kharif"]], "ragi (Finger Millet)": [20, 30, 500, ["kharif"]],
    "barley": [12, 20, 300, ["rabi"]],
    # Pulses
    "chana (Chickpea)": [15, 25, 400, ["rabi"]], "tur (Arhar/Pigeon Pea)": [25, 35, 600, ["kharif"]],
    "moong (Green Gram)": [25, 35, 300, ["kharif", "zaid"]], "urad (Black Gram)": [25, 35, 650, ["kharif"]],
    "masur (Lentil)": [15, 25, 300, ["rabi"]],
    # Oilseeds
    "groundnut": [25, 35, 500, ["kharif", "rabi"]], "mustard": [10, 25, 350, ["rabi"]],
    "soybean": [25, 32, 600, ["kharif"]], "sunflower": [20, 28, 500, ["rabi", "zaid"]],
    "sesame": [25, 30, 400, ["kharif"]],
    # Vegetables
    "potato": [15, 25, 500, ["rabi", "kharif"]], "onion": [13, 28, 650, ["rabi", "kharif"]],
    "tomato": [21, 29, 600, ["rabi", "zaid"]], "brinjal (Eggplant)": [22, 32, 600, ["kharif", "zaid"]],
    "chilli": [20, 30, 600, ["kharif", "zaid"]], "okra (Lady's Finger)": [25, 35, 700, ["kharif", "zaid"]],
    # Fruits & Horticulture
    "mango": [24, 30, 750, ["horticulture"]], "banana": [15, 35, 1200, ["horticulture"]],
    "guava": [23, 28, 1000, ["horticulture"]], "papaya": [21, 33, 1000, ["horticulture"]],
    "pomegranate": [25, 35, 500, ["horticulture"]], "citrus (Orange/Lemon)": [13, 35, 800, ["horticulture"]],
    # Cash Crops
    "sugarcane": [21, 30, 750, ["cash_crop"]], "cotton": [21, 35, 500, ["cash_crop", "kharif"]],
    "jute": [24, 35, 1500, ["cash_crop", "kharif"]], "turmeric": [20, 30, 1500, ["cash_crop", "kharif"]],
    "ginger": [20, 28, 1300, ["cash_crop", "kharif"]],
    # Plantation
    "tea": [20, 30, 1500, ["plantation"]], "coffee": [15, 28, 1500, ["plantation"]],
}

def get_geolocation_data(location: str):
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    resp = requests.get(geo_url, params={"name": location, "count": 1})
    data = resp.json()
    if not data.get("results"):
        return {"error": f"Could not find location: {location}"}
    loc = data["results"][0]
    return {"lat": loc["latitude"], "lng": loc["longitude"], "name": loc["name"]}

def get_current_weather(lat: float, lng: float):
    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lng,
        "current_weather": True,
        "hourly": "precipitation,temperature_2m,relative_humidity_2m,windspeed_10m",
        "timezone": "auto",
    }
    resp = requests.get(weather_url, params=params).json()
    return resp.get("current_weather", {})
def get_micro_climate(lat: float, lng: float):
    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lng,
        "hourly": "precipitation,relative_humidity_2m",
        "current_weather": True,
        "timezone": "auto",
    }
    resp = requests.get(weather_url, params=params).json()
    hourly = resp.get("hourly", {})
    precipitation = hourly.get("precipitation", [0])[0]
    humidity = hourly.get("relative_humidity_2m", [0])[0]
    return {"precipitation": precipitation, "humidity": humidity}

def get_extreme_events(lat: float, lng: float):
    current = get_current_weather(lat, lng)
    weathercode = current.get("weathercode", 0)
    extreme_map = {95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe Thunderstorm"}
    alerts = []
    if weathercode in extreme_map:
        alerts.append(extreme_map[weathercode])
    return {"alerts": alerts}

def get_environmental_data(latitude: float, longitude: float) -> Dict[str, Any]:
    # This tool remains unchanged
    print(f"TOOL: `get_environmental_data` called for Lat: {latitude}, Lon: {longitude}")
    try:
        weather_url = "https://api.open-meteo.com/v1/forecast"
        params = {"latitude": latitude, "longitude": longitude, "current": ["temperature_2m", "relative_humidity_2m", "precipitation"], "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"], "timezone": "Asia/Kolkata", "past_days": 365}
        response = requests.get(weather_url, params=params)
        response.raise_for_status()
        weather_data = response.json()
        historical_precip = sum(weather_data['daily']['precipitation_sum'])
        avg_temp = (sum(weather_data['daily']['temperature_2m_max']) + sum(weather_data['daily']['temperature_2m_min'])) / (len(weather_data['daily']['temperature_2m_max']) * 2)
        climate = {"average_annual_temperature_celsius": round(avg_temp, 2), "annual_rainfall_mm": round(historical_precip, 2), "humidity_percent": weather_data['current']['relative_humidity_2m']}
        water = {"water_abundance": "High" if climate['annual_rainfall_mm'] > 1200 else "Medium" if climate['annual_rainfall_mm'] > 600 else "Low", "irrigation_need": "Low" if climate['annual_rainfall_mm'] > 1200 else "Medium" if climate['annual_rainfall_mm'] > 600 else "High", "primary_water_sources": "Likely rain-fed, supplemented by groundwater (wells/borewells) and canals."}
        return {"climate": climate, "water": water}
    except Exception as e: return {"error": f"An unexpected error during environmental data fetch: {e}"}

def get_indian_crop_recommendations(climate: Dict[str, Any]) -> Dict[str, List[str]]:
    # This tool remains unchanged
    print(f"TOOL: `get_indian_crop_recommendations` called")
    recommendations = {"kharif": [], "rabi": [], "zaid": [], "horticulture": [], "cash_crop": [], "plantation": []}
    avg_temp = climate['average_annual_temperature_celsius']
    rainfall = climate['annual_rainfall_mm']
    for crop, reqs in INDIAN_CROP_DATABASE.items():
        min_temp, max_temp, min_rain, seasons = reqs
        if min_temp <= avg_temp <= max_temp and rainfall >= min_rain:
            for season in seasons:
                if season in recommendations: recommendations[season].append(crop)
    for key in recommendations.copy():
        recommendations[key] = sorted(list(set(recommendations[key])))
        if not recommendations[key]: del recommendations[key]
    return recommendations

def get_livestock_recommendations(state: str, climate: Dict[str, Any], water: Dict[str, Any]) -> Dict[str, str]:
    # This tool remains unchanged
    print(f"TOOL: `get_livestock_recommendations` called for state: '{state}'")
    suggestions = {}
    suggestions["Poultry (Broilers and Layers)"] = "Highly profitable and adaptable to various climates with proper housing. A great source of secondary income."
    if climate['annual_rainfall_mm'] < 800: suggestions["Goat Farming"] = "Goats are highly resilient, require less water than cattle, and are well-suited for semi-arid and arid regions. They are excellent for small-scale farmers."
    if water['water_abundance'] in ['Medium', 'High']:
        state_breeds = {"Maharashtra": "Khillari (draught), Deoni (dairy)", "Punjab": "Sahiwal (dairy)", "Gujarat": "Gir (dairy)", "Uttar Pradesh": "Gangartiri (dairy)", "Rajasthan": "Tharparkar, Rathi (dairy)"}
        breed_suggestion = state_breeds.get(state, "local crossbred varieties like Holstein-Friesian (HF) or Jersey crosses")
        suggestions["Dairy Cattle"] = f"Suitable due to medium to high water availability. Focus on locally adapted breeds like {breed_suggestion} for better productivity and disease resistance."
    coastal_states = ["Maharashtra", "Gujarat", "Kerala", "Tamil Nadu", "Andhra Pradesh", "Odisha", "West Bengal", "Goa", "Karnataka"]
    if water['water_abundance'] == 'High' or state in coastal_states: suggestions["Aquaculture/Fisheries"] = "Excellent potential in areas with high water abundance or in coastal regions. Farm ponds can be used for freshwater fish like Catla and Rohu."
    return suggestions

def get_recommendations_for_current_season(all_crops: Dict[str, List[str]], current_season: str) -> Dict[str, any]:
    """
    Filters the general crop list to provide recommendations for the current season.
    
    Args:
        all_crops: The complete dictionary of suitable crops for all seasons.
        current_season: The name of the current season (e.g., 'kharif').
        
    Returns:
        A dictionary containing the current season and its specific crop recommendations.
    """
    print(f"TOOL: `get_recommendations_for_current_season` called for '{current_season}'")
    
    seasonal_crops = all_crops.get(current_season, [])
    
    if not seasonal_crops:
        return {
            "current_season_name": current_season,
            "timely_recommendations": [],
            "note": "The main sowing window for this season may have passed or conditions are not ideal for its typical crops. Focus on other recommendations."
        }
        
    return {
        "current_season_name": current_season,
        "timely_recommendations": seasonal_crops,
        "note": f"These are the most suitable crops for the ongoing {current_season} season. Sowing should be planned immediately."
    }

def get_current_season():
    current_month = datetime.now().month
    season = 'kharif'
    if 6 <= current_month <= 9:
        season = 'kharif'
    elif 10 <= current_month <= 1 or current_month == 2 : # Oct-Feb
        season = 'rabi'
    else: # Mar-May
        season = 'zaid'
    return season


prompt = f"""
Only give output in json format.
    You are an expert-level Indian Agricultural Feasibility agent. Your task is to provide a comprehensive, structured analysis for a given Indian location, with a special focus on the current season.

    If query is in Hindi or other regional languages , answer in the same regional language
    
    The current season is determined using `get_current_season`.

    Follow these steps meticulously:
    1.  Use `get_geolocation_data` for the user's query. If not in India, stop and report.
    2.  Use the coordinates with `get_environmental_data` to get climate/water data.
    3.  Call `get_indian_crop_recommendations` to get a list of all potentially suitable crops.
    4.  **Crucially, now call the `get_recommendations_for_current_season` tool. Pass the full crop list and the current season to it.** This will give you the most timely advice.
    5.  Call `get_livestock_recommendations` for integrated farming options.
    6.  Finally, compile all collected information into a single JSON object. The JSON must have top-level keys: 'location_details', 'current_season_analysis', 'environmental_analysis', 'all_season_crop_recommendations', and 'integrated_farming_suggestions'. The 'current_season_analysis' MUST be at the top.
    
    Execute the plan and return only the final JSON object.
    """

root_agent = Agent(
    name="agricultural_agent",
    model="gemini-2.0-flash",
    description="You are an expert-level Indian Agricultural Feasibility agent. Your task is to provide a comprehensive, structured analysis for a given Indian location, with a special focus on the current season. Only give output in JSON format.",
    instruction=prompt,
    tools=[get_geolocation_data, get_current_season, get_environmental_data, get_indian_crop_recommendations, get_livestock_recommendations, get_recommendations_for_current_season]
    )


async def run_agricultural_agent(query: str):
    """
    Runs the agricultural agent on the given query and returns the result.
    """
    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name,
        session_id=1234567890,  # Use a fixed session ID for simplicity
        user_id="temp",
    )
    context = UserContent(parts=[Part(text=query)])
    result = await runner.run(
        session_id=1234567890,  # Use a fixed session ID for simplicity
        new_message=context,
        user_id="temp",
    )
    return result