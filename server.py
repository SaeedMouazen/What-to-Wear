import json
import socket
import sqlite3
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from flask import Flask, jsonify, request

from database import Database

app = Flask(__name__)
db = Database()

# Temperature limits used by the input checks (in °C).
LOWEST_TEMP = -10
HIGHEST_TEMP = 55

# Free weather forecast service (no account or key needed): https://open-meteo.com
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# City name -> (latitude, longitude)
CITIES = {
    "Riyadh": (24.69, 46.72),
    "Jeddah": (21.49, 39.19),
    "Madinah": (24.47, 39.61),
    "Abha": (18.22, 42.51),
    "Dammam": (26.43, 50.10),
}


# ---------- helper functions ----------

def check_number(text, label, low, high):
    """Turn text into a whole number between low and high, or raise ValueError."""
    text = text.strip()
    if text == "":
        raise ValueError(f"{label} is required.")
    try:
        number = int(text)
    except ValueError:
        raise ValueError(f"{label} must be a whole number.")
    if number < low or number > high:
        raise ValueError(f"{label} must be between {low} and {high}.")
    return number


def read_clothing_form():
    """Read and check the fields sent by Tkinter. Raise ValueError if something is wrong."""
    name = request.form.get("name", "").strip()
    if name == "":
        raise ValueError("Name is required.")
    if len(name) > 40:
        raise ValueError("Name must be 40 characters or fewer.")
    min_temp = check_number(request.form.get("min_temp", ""), "Min temperature", LOWEST_TEMP, HIGHEST_TEMP)
    max_temp = check_number(request.form.get("max_temp", ""), "Max temperature", LOWEST_TEMP, HIGHEST_TEMP)
    if min_temp > max_temp:
        raise ValueError("Min temperature cannot be higher than max temperature.")
    return name, min_temp, max_temp


def forecast_feels_like(city, hour):
    """Ask the weather service for today's "feels like" temperature in this city at this hour."""
    latitude, longitude = CITIES[city]
    query = urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "apparent_temperature",
        "timezone": "Asia/Riyadh",
        "forecast_days": 1,
    })
    with urlopen(WEATHER_URL + "?" + query, timeout=3) as reply:
        data = json.loads(reply.read().decode("utf-8"))
    # The list has 24 values: one for each hour of today, starting at 00:00.
    return round(data["hourly"]["apparent_temperature"][hour])


# ---------- routes ----------

@app.route("/clothes")
def list_clothes():
    return jsonify(db.get_all())


@app.route("/clothes/add", methods=["POST"])
def add_clothing():
    try:
        name, min_temp, max_temp = read_clothing_form()
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    new_id = db.add(name, min_temp, max_temp)
    return jsonify({"message": f"Saved: {name}", "id": new_id}), 201


@app.route("/clothes/<int:item_id>/edit", methods=["POST"])
def edit_clothing(item_id):
    try:
        name, min_temp, max_temp = read_clothing_form()
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    if not db.update(item_id, name, min_temp, max_temp):
        return jsonify({"error": f"Item {item_id} was not found. It may have been deleted."}), 404
    return jsonify({"message": f"Updated: {name}"})


@app.route("/clothes/<int:item_id>/delete", methods=["POST"])
def delete_clothing(item_id):
    if not db.delete(item_id):
        return jsonify({"error": f"Item {item_id} was not found. It may have been deleted."}), 404
    return jsonify({"message": "Item deleted."})


@app.route("/suggest")
def suggest():
    city = request.args.get("city", "")
    typed_temp = request.args.get("temp", "").strip()

    # 1. Check the input.
    try:
        hour = check_number(request.args.get("hour", ""), "Hour", 0, 23)
        if typed_temp == "" and city not in CITIES:
            raise ValueError("Choose a city from the list.")
        if typed_temp != "":
            felt = check_number(typed_temp, "Temperature", LOWEST_TEMP, HIGHEST_TEMP)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    # 2. No typed temperature: get it from the weather forecast.
    source = "typed"
    if typed_temp == "":
        source = "forecast"
        try:
            felt = forecast_feels_like(city, hour)
        except (URLError, socket.timeout, ValueError, KeyError, IndexError):
            return jsonify({"error": "Couldn't get the weather forecast. Check your internet, "
                                     "or type the temperature yourself."}), 503

    # 3. Find the clothes that suit this temperature.
    return jsonify({
        "source": source,
        "city": city,
        "hour": hour,
        "feels_like": felt,
        "clothes": db.get_for_temperature(felt),
    })


@app.errorhandler(sqlite3.Error)
def database_error(error):
    return jsonify({"error": "Database error. Please try again."}), 500


if __name__ == "__main__":
    app.run(port=5050)