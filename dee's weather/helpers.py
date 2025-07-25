import requests

from datetime import datetime
from flask import redirect, render_template, session
from functools import wraps


#openweathermap.org
API_KEY = "f00f280483b4a657dd79a0b81944996f"

# get apology function from finance
def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def get_city_coordinates(city, country_code):
    #Myanmar
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{country_code}&limit=1&appid={API_KEY}" #get the data of only 1 city LIMIT=1
    try:
        response = requests.get(url)
        response.raise_for_status()
        geo_data = response.json() #a list of dict()s

        if geo_data and len(geo_data) > 0:
            return {
                "city" : geo_data[0]["name"],
                "country" : geo_data[0]["country"],
                "lat" : geo_data[0]["lat"],
                "lon" : geo_data[0]["lon"]
            }
        else:
            return None #city not found

    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    return None


#api function based on cs50 finance api call
#built URL -> make request -> parse JSON response to python -> return clean data
def lookup_weather_forecast(lat, lon):
    """look up 5 day weather forecast from OpenWeatherMap API for city"""
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url) # Send HTTP get request to API
        response.raise_for_status() # Raise an error for HTTP error responses
        weather_data = response.json() # Parses JSON response into Python dict()

        # to make dt human readable time #used chatgpt
        second_forecasts = []

        for forecast in weather_data["list"]:

            dt_datetime = datetime.fromtimestamp(forecast["dt"])

            second_forecast = forecast.copy() # copy each original forecast
            second_forecast["formatted_time"] = dt_datetime.strftime("%I:%M %p")  # 12-hour format
            second_forecast["formatted_date"] = dt_datetime.strftime("%A, %B %d")  # Day, Month Date
            second_forecast["formatted_datetime"] = dt_datetime.strftime("%A, %B %d at %I:%M %p")  # Full format
            second_forecasts.append(second_forecast)

        return {
                "city" : weather_data["city"]["name"],
                "country" : weather_data["city"]["country"],
                "sunrise" : datetime.fromtimestamp(weather_data["city"]["sunrise"]).strftime("%I:%M %p"), #Unix timestamps -> need to convert to readable time using datetime
                "sunset" : datetime.fromtimestamp(weather_data["city"]["sunset"]).strftime("%I:%M %p"),
                "fc" : second_forecasts
            }

    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    return None

def daily_min_max_temp(forecasts_list, target_date=None):

    if not forecasts_list:
        return None

    if target_date is None:
        target_date = datetime.now().date() # get today's date w/o time

    today_temps =[]

    for forecast in forecasts_list:
        forecast_date = datetime.fromtimestamp(forecast["dt"]).date() #converts to readable date
        if forecast_date == target_date:
            today_temps.append(forecast["main"]["temp"]) #append all temp having today date

    if today_temps:
        return {
            "min" : min(today_temps),
            "max" : max(today_temps)
        }
    else:
        return {
            "min" : forecasts_list[0]["main"]["temp_min"],
            "max" : forecasts_list[0]["main"]["temp_max"]
        }



