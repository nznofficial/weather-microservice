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

app.run(port=8002)
