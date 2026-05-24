"""Pruebas unitarias para MedicionCalidadAireRepository."""

import pytest

from src.exceptions.custom_exceptions import DatoInvalidoError, RegistroDuplicadoError
from src.models.medicion_calidad_aire import MedicionCalidadAire
from src.repositories.medicion_calidad_aire_repository import MedicionCalidadAireRepository


def _repo_temporal(tmp_path):
    return MedicionCalidadAireRepository(data_file=tmp_path / "mediciones_test.json")


def _medicion_base(**overrides):
    data = {
        "id_medicion": "MED001",
        "id_estacion": "EST001",
        "contaminante": "PM2.5",
        "valor": 35.5,
        "unidad": "ug/m3",
        "fecha": "2026-05-24",
    }
    data.update(overrides)
    return MedicionCalidadAire(**data)


def test_1_crear_medicion_valida(tmp_path):
    repo = _repo_temporal(tmp_path)
    creada = repo.crear(_medicion_base())
    assert creada.id_medicion == "MED001"


def test_2_rechazar_medicion_sin_id(tmp_path):
    _ = _repo_temporal(tmp_path)
    with pytest.raises(DatoInvalidoError):
        _medicion_base(id_medicion="")


def test_3_rechazar_medicion_sin_estacion(tmp_path):
    _ = _repo_temporal(tmp_path)
    with pytest.raises(DatoInvalidoError):
        _medicion_base(id_estacion="")


def test_4_rechazar_medicion_sin_contaminante(tmp_path):
    _ = _repo_temporal(tmp_path)
    with pytest.raises(DatoInvalidoError):
        _medicion_base(contaminante="")


def test_5_rechazar_valor_negativo(tmp_path):
    _ = _repo_temporal(tmp_path)
    with pytest.raises(DatoInvalidoError):
        _medicion_base(valor=-1)


def test_6_rechazar_medicion_duplicada(tmp_path):
    repo = _repo_temporal(tmp_path)
    repo.crear(_medicion_base())
    with pytest.raises(RegistroDuplicadoError):
        repo.crear(_medicion_base())


def test_7_buscar_medicion_existente(tmp_path):
    repo = _repo_temporal(tmp_path)
    repo.crear(_medicion_base())
    encontrada = repo.buscar_por_id("MED001")
    assert encontrada is not None


def test_8_actualizar_valor_medicion(tmp_path):
    repo = _repo_temporal(tmp_path)
    repo.crear(_medicion_base())
    actualizada = _medicion_base(valor=120)
    repo.actualizar("MED001", actualizada)
    buscada = repo.buscar_por_id("MED001")
    assert buscada.valor == 120


def test_9_eliminar_medicion(tmp_path):
    repo = _repo_temporal(tmp_path)
    repo.crear(_medicion_base())
    repo.eliminar("MED001")
    assert repo.buscar_por_id("MED001") is None


def test_10_calcular_nivel_alerta(tmp_path):
    _ = _repo_temporal(tmp_path)
    bajo = _medicion_base(valor=30)
    medio = _medicion_base(id_medicion="MED002", valor=75)
    alto = _medicion_base(id_medicion="MED003", valor=150)
    assert bajo.nivel == "Bajo"
    assert medio.nivel == "Medio"
    assert alto.nivel == "Alto"
