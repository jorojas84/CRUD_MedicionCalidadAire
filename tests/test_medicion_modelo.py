"""Pruebas unitarias para el modelo MedicionCalidadAire (clasificacion ICA y validaciones)."""

from datetime import datetime

import pytest

from src.exceptions.custom_exceptions import DatoInvalidoError
from src.models.medicion_calidad_aire import MedicionCalidadAire, MedicionCalidadAirePM


def _pm(**overrides) -> MedicionCalidadAirePM:
    data = {
        "id": "M001",
        "codigo_dane_municipio": "05001",
        "id_estacion": "EST-MED-01",
        "fecha": datetime(2026, 5, 20, 10, 0),
        "diametro_aerodinamico": "PM10",
        "medicion": 42.5,
        "origen": MedicionCalidadAire.MANUAL,
    }
    data.update(overrides)
    return MedicionCalidadAirePM(**data)


def test_1_pm10_nivel_buena():
    assert _pm(diametro_aerodinamico="PM10", medicion=40.0).nivel == "Buena"


def test_2_pm10_nivel_aceptable():
    assert _pm(diametro_aerodinamico="PM10", medicion=120.0).nivel == "Aceptable"


def test_3_pm10_nivel_peligrosa():
    assert _pm(diametro_aerodinamico="PM10", medicion=800.0).nivel == "Peligrosa"


def test_4_pm25_puntos_corte_distintos():
    # 30 µg/m³ en PM2.5 ya es Aceptable; el mismo valor en PM10 seria Buena.
    assert _pm(diametro_aerodinamico="PM2.5", medicion=30.0).nivel == "Aceptable"
    assert _pm(diametro_aerodinamico="PM10", medicion=30.0).nivel == "Buena"


def test_5_rechazar_diametro_invalido():
    with pytest.raises(DatoInvalidoError):
        _pm(diametro_aerodinamico="PM5")


def test_6_rechazar_medicion_negativa():
    with pytest.raises(DatoInvalidoError):
        _pm(medicion=-1.0)


def test_7_rechazar_origen_invalido():
    with pytest.raises(DatoInvalidoError):
        _pm(origen="DESCONOCIDO")


def test_8_rechazar_id_vacio():
    with pytest.raises(DatoInvalidoError):
        _pm(id="")


def test_9_to_dict_incluye_tipo_y_diametro():
    datos = _pm().to_dict()
    assert datos["tipo"] == "PM"
    assert datos["diametro_aerodinamico"] == "PM10"
    assert datos["nivel"] == "Buena"


def test_10_es_eliminable_solo_manuales():
    assert _pm(origen=MedicionCalidadAire.MANUAL).es_eliminable() is True
    assert _pm(origen=MedicionCalidadAire.AUTO).es_eliminable() is False
