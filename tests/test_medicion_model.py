"""Tests del modelo: reglas de negocio puro (sin repositorio ni controller)."""

from datetime import datetime

import pytest

from src.exceptions.custom_exceptions import DatoInvalidoError
from src.models.medicion_calidad_aire import (
    MedicionCalidadAire,
    MedicionCalidadAirePM,
)


def _medicion_base(**overrides) -> MedicionCalidadAirePM:
    datos = {
        "id": "m-001",
        "codigo_dane_municipio": "11001",
        "id_estacion": "EST-001",
        "fecha": datetime(2026, 5, 18, 8, 15),
        "diametro_aerodinamico": MedicionCalidadAirePM.PM10,
        "medicion": 120.5,
        "origen": MedicionCalidadAire.AUTO,
    }
    datos.update(overrides)
    return MedicionCalidadAirePM(**datos)


# ── clasificacion ICA (Res. 2254/2017 Tabla 6) ──────────────────────────────

def test_pm10_buena_en_limite_del_corte():
    assert _medicion_base(medicion=54).nivel == MedicionCalidadAire.BUENA


def test_pm10_aceptable_apenas_pasa_el_corte():
    assert _medicion_base(medicion=55).nivel == MedicionCalidadAire.ACEPTABLE


def test_pm10_peligrosa_por_encima_del_ultimo_corte():
    assert _medicion_base(medicion=700).nivel == MedicionCalidadAire.PELIGROSA


def test_pm25_usa_su_propia_tabla_de_cortes():
    m = _medicion_base(
        diametro_aerodinamico=MedicionCalidadAirePM.PM25,
        medicion=40,
    )
    assert m.nivel == MedicionCalidadAire.DANINA_SENSIBLES


# ── validaciones ────────────────────────────────────────────────────────────

def test_medicion_negativa_es_invalida():
    with pytest.raises(DatoInvalidoError):
        _medicion_base(medicion=-1)


def test_diametro_fuera_de_lista_es_invalido():
    with pytest.raises(DatoInvalidoError):
        _medicion_base(diametro_aerodinamico="PM5")


# ── inmutabilidad ───────────────────────────────────────────────────────────

def test_modelo_es_inmutable():
    m = _medicion_base(medicion=50, origen=MedicionCalidadAire.MANUAL)
    with pytest.raises(AttributeError):
        m.medicion = 999  # type: ignore[misc]
