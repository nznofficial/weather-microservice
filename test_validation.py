import requests
from unittest.mock import patch

from app import app


def test_missing_latitude():
    client = app.test_client()

    response = client.get(
        "/forecast?lon=-115.2015&date=2026-08-10"
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "invalid_coordinates"


def test_invalid_latitude():
    client = app.test_client()

    response = client.get(
        "/forecast?lat=abc&lon=-115.2015&date=2026-08-10"
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "invalid_coordinates"


def test_out_of_range_coordinate():
    client = app.test_client()

    response = client.get(
        "/forecast?lat=100&lon=-115.2015&date=2026-08-10"
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "invalid_coordinates"


def test_invalid_date_format():
    client = app.test_client()

    response = client.get(
        "/forecast?lat=36.1147&lon=-115.2015&date=August-10"
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "invalid_date"


@patch("app.requests.get")
def test_unsupported_forecast_date(mock_get):
    mock_get.return_value.status_code = 400

    client = app.test_client()

    response = client.get(
        "/forecast?lat=36.1147&lon=-115.2015&date=2099-01-01"
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "unsupported_date"


@patch("app.requests.get")
def test_provider_failure(mock_get):
    mock_get.side_effect = requests.RequestException()

    client = app.test_client()

    response = client.get(
        "/forecast?lat=36.1147&lon=-115.2015&date=2026-08-10"
    )

    assert response.status_code == 502
    assert (
        response.get_json()["error"]
        == "weather_provider_unavailable"
    )
