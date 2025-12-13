import pytest
from unittest.mock import patch, MagicMock
from data_sources.meteoblue import MeteoBlueSource


def test_init_requires_api_key():
    with pytest.raises(ValueError):
        MeteoBlueSource(api_key="")


def test_current_weather_success():
    src = MeteoBlueSource(api_key="TESTKEY")
    fake_resp = MagicMock()
    fake_resp.json.return_value = {
        "data_1h": [
            {
                "temperature": 20.1,
                "relative_humidity": 60,
                "precipitation": 0.0,
                "wind_speed": 5.0,
                "wind_direction": 180,
                "pressure_msl": 1012,
            }
        ]
    }

    with patch.object(src, "_make_request", return_value=fake_resp):
        data = src.get_current_weather(6.245, -75.5715)
        assert data["source"] == "MeteoBlue"
        assert data["location"]["lat"] == 6.245
        assert data["temperature"] == 20.1
        assert data["humidity"] == 60


def test_forecast_success():
    src = MeteoBlueSource(api_key="TESTKEY")
    fake_resp = MagicMock()
    fake_resp.json.return_value = {"any": "payload"}

    with patch.object(src, "_make_request", return_value=fake_resp):
        data = src.get_forecast(6.245, -75.5715, days=5)
        assert data["forecast_days"] == 5
        assert data["raw_data"]["any"] == "payload"


def test_meteogram_image_download():
    src = MeteoBlueSource(api_key="TESTKEY")
    content = b"PNGDATA"
    with patch("data_sources.meteoblue.requests.get") as mget:
        mresp = MagicMock()
        mresp.content = content
        mresp.raise_for_status = MagicMock()
        mget.return_value = mresp
        out = src.get_meteogram_image(6.245, -75.5715, location_name="Medellin")
        assert out == content
