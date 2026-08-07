from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/forecast")
def forecast():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    date = request.args.get("date")

    # Validate inputs and Error Handling to be updated by Eitan

    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "start_date": date,
            "end_date": date,
            "daily": ["temperature_2m_max", "temperature_2m_min"],
            "temperature_unit": "fahrenheit",
            "timezone": "auto",
        },
    )
    
    daily = response.json()["daily"]

    return jsonify({
        "temp_max_f": daily["temperature_2m_max"][0],
        "temp_min_f": daily["temperature_2m_min"][0],
    })

from datetime import date, datetime
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def error_response(status_code, error, message):
    return jsonify({
        "error": error,
        "message": message,
    }), status_code


def validate_coordinates(lat, lon):
    if lat is None or lon is None:
        return "Parameters 'lat' and 'lon' are required."

    try:
        latitude = float(lat)
        longitude = float(lon)
    except ValueError:
        return "Parameters 'lat' and 'lon' must be numeric."

    if not -90 <= latitude <= 90:
        return "Parameter 'lat' must be between -90 and 90."

    if not -180 <= longitude <= 180:
        return "Parameter 'lon' must be between -180 and 180."

    return None


def validate_date(date_string):
    if date_string is None:
        return "Parameter 'date' is required."

    try:
        requested_date = datetime.strptime(
            date_string,
            "%Y-%m-%d"
        ).date()
    except ValueError:
        return "Parameter 'date' must use YYYY-MM-DD format."

    if requested_date < date.today():
        return "Historical dates are not supported."

    return None


@app.route("/forecast")
def forecast():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    requested_date = request.args.get("date")

    coordinate_error = validate_coordinates(lat, lon)
    if coordinate_error:
        return error_response(
            400,
            "invalid_coordinates",
            coordinate_error,
        )

    date_error = validate_date(requested_date)
    if date_error:
        return error_response(
            400,
            "invalid_date",
            date_error,
        )

    try:
        response = requests.get(
            OPEN_METEO_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "start_date": requested_date,
                "end_date": requested_date,
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                ],
                "temperature_unit": "fahrenheit",
                "timezone": "auto",
            },
            timeout=5,
        )
    except requests.RequestException:
        return error_response(
            502,
            "weather_provider_unavailable",
            "The weather provider could not be reached.",
        )

    if response.status_code != 200:
        return error_response(
            400,
            "unsupported_date",
            "The requested date is outside the supported forecast range.",
        )

    try:
        daily = response.json()["daily"]
        temp_max = daily["temperature_2m_max"][0]
        temp_min = daily["temperature_2m_min"][0]
    except (KeyError, IndexError, TypeError, ValueError):
        return error_response(
            502,
            "invalid_provider_response",
            "The weather provider returned an unexpected response.",
        )

    return jsonify({
        "temp_max_f": temp_max,
        "temp_min_f": temp_min,
    })

if __name__ == "__main__":
    app.run(port=8002)
