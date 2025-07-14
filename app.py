import os

from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta

from dotenv import load_dotenv


from helpers import apology, get_city_coordinates, lookup_weather_forecast, daily_min_max_temp

#configure application
app = Flask(__name__)

#configue session (may not need/use this)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



#openweathermap.org
load_dotenv()
API_KEY = os.getenv('API_KEY')
# BASE_URL = "https://api.openweathermap.org/data/2.5"

#don't cach the responses, from finance
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods =["GET", "POST"])
def index():

    # POST - get specific location from user
    if request.method == "POST":

        country = request.form.get("country")
        if not country:
            return apology("invalid country")

        city = request.form.get("city")
        if not city:
            return apology("invalid city")

        city_coordinates = get_city_coordinates(city, country)
        if not city_coordinates:
            return apology("City not found")

        print(f"🔍 DEBUG: Coordinates for {city}: {city_coordinates}")

        city_lat = city_coordinates["lat"]
        city_lon = city_coordinates["lon"]


        print(f"COORDINATES: {city_lat}, {city_lon}")

        forecasts = lookup_weather_forecast(city_lat, city_lon)
        if not forecasts:
            return apology("Could not get weather data")

        print(f"🔍 DEBUG: First forecast temp: {forecasts['fc'][0]['main']['temp']}")
        print(f"🔍 DEBUG: City from API: {forecasts['city']}")

        daily_temps = daily_min_max_temp(forecasts["fc"])
        if not daily_temps:
            return apology("Could not get min/max temp")

        min_temp = daily_temps["min"]
        max_temp = daily_temps["max"]

        # get min/max of each date
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        day3 = today + timedelta(days=2)
        day4 = today + timedelta(days=3)
        day5 = today + timedelta(days=4)

        today_temps =  daily_min_max_temp(forecasts["fc"], today)
        tmr_temps = daily_min_max_temp(forecasts["fc"], tomorrow)
        day3_temps = daily_min_max_temp(forecasts["fc"], day3)
        day4_temps = daily_min_max_temp(forecasts["fc"], day4)
        day5_temps = daily_min_max_temp(forecasts["fc"], day5)




        return render_template("results.html",
        forecasts=forecasts,
        current_page="results",
        min_temp = min_temp,
        max_temp = max_temp,
        today_temps=today_temps,
        tmr_temps=tmr_temps,
        day3_temps=day3_temps,
        day4_temps=day4_temps,
        day5_temps=day5_temps)

    # GET - ask location
    return render_template("index.html", current_page="index")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) # use Render's port or 5000 as backup
    app.run(host='0.0.0.0', port=port, debug=False)
