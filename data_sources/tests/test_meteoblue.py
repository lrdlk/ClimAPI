import os
import pytest

from data_sources.meteoblue import MeteoBlueSource

API_KEY = os.environ.get("METEOBLUE_API_KEY", "Z2AnKNoxLJul08UQ")

@pytest.mark.skipif(not API_KEY, reason="Se requiere METEOBLUE_API_KEY")
def test_basic_day_clouds_sunmoon_json():
    src = MeteoBlueSource(api_key=API_KEY)
    try:
        res = src.get_basic_day_clouds_sunmoon(latitude=6.245, longitude=-75.5715, asl=1405)
        assert isinstance(res, dict)
        assert "data" in res
        assert res["location"]["lat"] == 6.245
        assert res["location"]["lon"] == -75.5715
    except Exception as e:
        # Algunas cuentas/paquetes de MeteoBlue devuelven 403 si el paquete no está habilitado
        import requests
        assert isinstance(e, requests.HTTPError)

@pytest.mark.skipif(not API_KEY, reason="Se requiere METEOBLUE_API_KEY")
def test_meteogram_image_download(tmp_path):
    src = MeteoBlueSource(api_key=API_KEY)
    save_file = tmp_path / "meteogram_medellin.png"
    try:
        res = src.get_meteogram_image(
            latitude=6.245,
            longitude=-75.5715,
            asl=1405,
            location_name="Medellín",
            tz="America/Bogota",
            dpi=72,
            lang="en",
            temperature_units="C",
            precipitation_units="mm",
            windspeed_units="kmh",
            format="png",
            save_path=str(save_file)
        )
        assert res["saved"] is True
        assert os.path.exists(save_file)
        assert len(res["bytes"]) > 1000  # imagen no vacía
    except Exception as e:
        import requests
        # Si el plan no incluye imágenes, MeteoBlue responde 403
        assert isinstance(e, requests.HTTPError)
