import sqlite3

from flask import Flask, jsonify, request

from database import Database

app = Flask(__name__)
db = Database()

# Temperature limits used by the input checks (in °C).
LOWEST_TEMP = -10
HIGHEST_TEMP = 55


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


def feels_like(temp, hour, hours_out):
    """Night and long time outside make it feel colder."""
    result = temp
    if hour >= 18 or hour < 6:
        result = result - 3
    if hours_out >= 3:
        result = result - 2
    return result


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
    try:
        temp = check_number(request.args.get("temp", ""), "Temperature", LOWEST_TEMP, HIGHEST_TEMP)
        hour = check_number(request.args.get("hour", ""), "Hour", 0, 23)
        hours_out = check_number(request.args.get("hours", ""), "Hours outside", 1, 24)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    felt = feels_like(temp, hour, hours_out)
    return jsonify({"feels_like": felt, "clothes": db.get_for_temperature(felt)})


@app.errorhandler(sqlite3.Error)
def database_error(error):
    return jsonify({"error": "Database error. Please try again."}), 500


if __name__ == "__main__":
    app.run(port=5050)