import requests

# Request for Las Vegas
response = requests.get(
    "http://localhost:8002/forecast",
    params={"lat": 36.1147, "lon":  -115.2015, "date": "2026-08-10"},
)

if response.status_code == 200:
    data = response.json()
    print(data["temp_max_f"], data["temp_min_f"])
else:
    print(response.json()["error"])