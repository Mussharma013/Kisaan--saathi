import requests
import os

# Placeholder for your OpenWeatherMap API key (or IMD if accessible)
# API_KEY = os.environ.get("OPENWEATHER_API_KEY") # Store in .env
API_KEY = "592a88aefc717397705d60f599ad55da" # Replace with your actual key

def get_current_weather(location):
    """Fetches current weather data for a given location."""
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': location,
        'appid': API_KEY,
        'units': 'metric' # Celsius
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if data['cod'] == 200:
            return {
                'temperature': data['main']['temp'],
                'condition': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed']
            }
        else:
            print(f"Weather API error: {data.get('message', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching current weather: {e}")
        return None

def get_weather_forecast(location):
    """Fetches 5-day weather forecast data for a given location."""
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': location,
        'appid': API_KEY,
        'units': 'metric',
        'cnt': 40 # 5 days / 3-hour intervals = 40
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        if data['cod'] == '200': # Note: '200' as string for forecast API
            forecast_list = []
            # Aggregate data per day (taking one measurement per day for simplicity)
            daily_data = {}
            for item in data['list']:
                date = item['dt_txt'].split(' ')[0] # YYYY-MM-DD
                if date not in daily_data:
                    daily_data[date] = {
                        'min_temp': item['main']['temp_min'],
                        'max_temp': item['main']['temp_max'],
                        'conditions': []
                    }
                daily_data[date]['min_temp'] = min(daily_data[date]['min_temp'], item['main']['temp_min'])
                daily_data[date]['max_temp'] = max(daily_data[date]['max_temp'], item['main']['temp_max'])
                daily_data[date]['conditions'].append(item['weather'][0]['description'])

            for date, values in daily_data.items():
                forecast_list.append({
                    'date': date,
                    'temp_high': round(values['max_temp'], 1),
                    'temp_low': round(values['min_temp'], 1),
                    'condition': ", ".join(list(set(values['conditions']))) # Unique conditions
                })
            return forecast_list[:5] # Return for next 5 days
        else:
            print(f"Forecast API error: {data.get('message', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather forecast: {e}")
        return None

# Example usage (for testing this module directly)
if __name__ == '__main__':
    current = get_current_weather('Varanasi')
    if current:
        print(f"Current weather in Varanasi: {current}")
    forecast = get_weather_forecast('Varanasi')
    if forecast:
        print(f"5-day forecast for Varanasi: {forecast}")