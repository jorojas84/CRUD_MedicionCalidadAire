"""Tests del repositorio: CRUD y persistencia en JSON."""

from datetime import datetime

import pytest

from src.exceptions.custom_exceptions import (
    DatoInvalidoError,
    RegistroDuplicadoError,
)
from src.models.medicion_calidad_aire import (
    MedicionCalidadAire,
    MedicionCalidadAirePM,
)
from src.repositories.medicion_calidad_aire_repository import MedicionRepository


def _repo_temporal(tmp_path) -> MedicionRepository:
    return MedicionRepository(data_file=tmp_path / "mediciones_test.json")


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


# ── CRUD basico ─────────────────────────────────────────────────────────────

def test_crear_y_buscar(tmp_path):
    repo = _repo_temporal(tmp_path)
    repo.crear_medicion(_medicion_base())
    m = repo.buscar_medicion_por_id("m-001")
    assert m is not None
    assert m.codigo_dane_municipio == "11001"


def test_actualizar_persiste_cambios(tmp_path):
    repo = _repo_temporal(tmp_path)
    repo.crear_medicion(_medicion_base(medicion=10, origen=MedicionCalidadAire.MANUAL))
    repo.actualizar_medicion(
        _medicion_base(medicion=200, origen=MedicionCalidadAire.MANUAL)
    )
    m = repo.buscar_medicion_por_id("m-001")
    assert m is not None
    assert m.medicion == 200


def test_listar_devuelve_subclase_correcta(tmp_path):
    repo = _repo_temporal(tmp_path)
    repo.crear_medicion(_medicion_base())
    [m] = repo.listar_mediciones()
    assert isinstance(m, MedicionCalidadAirePM)


# ── reglas que vienen del repositorio ───────────────────────────────────────

def test_crear_rechaza_id_duplicado(tmp_path):
    repo = _repo_temporal(tmp_path)
    repo.crear_medicion(_medicion_base())
    with pytest.raises(RegistroDuplicadoError):
        repo.crear_medicion(_medicion_base())


def test_eliminar_sensor_falla(tmp_path):
    repo = _repo_temporal(tmp_path)
    repo.crear_medicion(_medicion_base(origen=MedicionCalidadAire.AUTO))
    with pytest.raises(DatoInvalidoError):
        repo.eliminar_medicion("m-001")


def test_eliminar_manual_funciona(tmp_path):
    repo = _repo_temporal(tmp_path)
    repo.crear_medicion(_medicion_base(origen=MedicionCalidadAire.MANUAL))
    repo.eliminar_medicion("m-001")
    assert repo.buscar_medicion_por_id("m-001") is None
