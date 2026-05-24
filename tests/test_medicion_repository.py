"""Pruebas unitarias para MedicionRepository."""

from datetime import datetime

import pytest

from src.exceptions.custom_exceptions import (
    DatoInvalidoError,
    RegistroDuplicadoError,
    RegistroNoEncontradoError,
)
from src.models.medicion_calidad_aire import MedicionCalidadAire, MedicionCalidadAirePM
from src.repositories.medicion_calidad_aire_repository import MedicionRepository


def _repo(tmp_path):
    return MedicionRepository(data_file=tmp_path / "mediciones_test.json")


def _medicion(**overrides) -> MedicionCalidadAirePM:
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


def test_1_crear_y_buscar_medicion(tmp_path):
    repo = _repo(tmp_path)
    repo.crear_medicion(_medicion())
    encontrada = repo.buscar_medicion_por_id("M001")
    assert encontrada is not None
    assert encontrada.medicion == 42.5


def test_2_listar_mediciones(tmp_path):
    repo = _repo(tmp_path)
    repo.crear_medicion(_medicion(id="M001"))
    repo.crear_medicion(_medicion(id="M002", medicion=80.0))
    assert len(repo.listar_mediciones()) == 2


def test_3_rechazar_duplicado(tmp_path):
    repo = _repo(tmp_path)
    repo.crear_medicion(_medicion())
    with pytest.raises(RegistroDuplicadoError):
        repo.crear_medicion(_medicion())


def test_4_actualizar_medicion(tmp_path):
    repo = _repo(tmp_path)
    repo.crear_medicion(_medicion())
    repo.actualizar_medicion(_medicion(medicion=120.0))
    encontrada = repo.buscar_medicion_por_id("M001")
    assert encontrada.medicion == 120.0
    assert encontrada.nivel == "Aceptable"


def test_5_actualizar_inexistente_falla(tmp_path):
    repo = _repo(tmp_path)
    with pytest.raises(RegistroNoEncontradoError):
        repo.actualizar_medicion(_medicion(id="X999"))


def test_6_eliminar_manual(tmp_path):
    repo = _repo(tmp_path)
    repo.crear_medicion(_medicion())
    assert repo.eliminar_medicion("M001") is True
    assert repo.buscar_medicion_por_id("M001") is None


def test_7_no_eliminar_automatica(tmp_path):
    repo = _repo(tmp_path)
    repo.crear_medicion(_medicion(origen=MedicionCalidadAire.AUTO))
    with pytest.raises(DatoInvalidoError):
        repo.eliminar_medicion("M001")


def test_8_eliminar_inexistente_falla(tmp_path):
    repo = _repo(tmp_path)
    with pytest.raises(RegistroNoEncontradoError):
        repo.eliminar_medicion("X999")


def test_9_persistencia_entre_instancias(tmp_path):
    archivo = tmp_path / "mediciones_test.json"
    MedicionRepository(archivo).crear_medicion(_medicion())
    otra = MedicionRepository(archivo)
    assert otra.buscar_medicion_por_id("M001") is not None


def test_10_buscar_inexistente_devuelve_none(tmp_path):
    repo = _repo(tmp_path)
    assert repo.buscar_medicion_por_id("X999") is None
