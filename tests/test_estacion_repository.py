"""Pruebas unitarias para EstacionRepository y EstacionAmbiental."""

import pytest

from src.models.estacion_ambiental import DuplicateEstacionError, EstacionAmbiental, EstacionValidationError
from src.repositories.estacion_repository import EstacionRepository


def test_1_crear_estacion_valida(tmp_path):
    repo = EstacionRepository(tmp_path / "estaciones.json")
    estacion = EstacionAmbiental("EST001", "Estacion Centro", "Bogota", "Fija", "Activa")
    repo.crear(estacion)
    encontrada = repo.buscar("EST001")
    assert encontrada is not None
    assert encontrada.nombre == "Estacion Centro"


def test_2_rechazar_estacion_sin_id(tmp_path):
    _ = EstacionRepository(tmp_path / "estaciones.json")
    with pytest.raises(EstacionValidationError):
        EstacionAmbiental("", "Estacion Centro", "Bogota", "Fija", "Activa")


def test_3_rechazar_estacion_sin_nombre(tmp_path):
    _ = EstacionRepository(tmp_path / "estaciones.json")
    with pytest.raises(EstacionValidationError):
        EstacionAmbiental("EST001", "", "Bogota", "Fija", "Activa")


def test_4_rechazar_estacion_sin_municipio(tmp_path):
    _ = EstacionRepository(tmp_path / "estaciones.json")
    with pytest.raises(EstacionValidationError):
        EstacionAmbiental("EST001", "Estacion Centro", "", "Fija", "Activa")


def test_5_rechazar_estado_invalido(tmp_path):
    _ = EstacionRepository(tmp_path / "estaciones.json")
    with pytest.raises(EstacionValidationError):
        EstacionAmbiental("EST001", "Estacion Centro", "Bogota", "Fija", "Suspendida")


def test_6_rechazar_estacion_duplicada(tmp_path):
    repo = EstacionRepository(tmp_path / "estaciones.json")
    repo.crear(EstacionAmbiental("EST001", "Estacion Centro", "Bogota", "Fija", "Activa"))
    with pytest.raises(DuplicateEstacionError):
        repo.crear(EstacionAmbiental("EST001", "Estacion Norte", "Bogota", "Movil", "Activa"))


def test_7_listar_estaciones(tmp_path):
    repo = EstacionRepository(tmp_path / "estaciones.json")
    repo.crear(EstacionAmbiental("EST001", "Centro", "Bogota", "Fija", "Activa"))
    repo.crear(EstacionAmbiental("EST002", "Sur", "Bogota", "Movil", "Activa"))
    estaciones = repo.listar()
    assert len(estaciones) == 2


def test_8_buscar_estacion_existente(tmp_path):
    repo = EstacionRepository(tmp_path / "estaciones.json")
    repo.crear(EstacionAmbiental("EST001", "Centro", "Bogota", "Fija", "Activa"))
    encontrada = repo.buscar("EST001")
    assert encontrada is not None
    assert encontrada.id_estacion == "EST001"


def test_9_actualizar_estacion(tmp_path):
    repo = EstacionRepository(tmp_path / "estaciones.json")
    repo.crear(EstacionAmbiental("EST001", "Centro", "Bogota", "Fija", "Activa"))
    repo.actualizar(EstacionAmbiental("EST001", "Centro Modificada", "Bogota", "Fija", "Inactiva"))
    encontrada = repo.buscar("EST001")
    assert encontrada.nombre == "Centro Modificada"
    assert encontrada.estado == "Inactiva"


def test_10_eliminar_estacion(tmp_path):
    repo = EstacionRepository(tmp_path / "estaciones.json")
    repo.crear(EstacionAmbiental("EST001", "Centro", "Bogota", "Fija", "Activa"))
    repo.eliminar("EST001")
    assert repo.buscar("EST001") is None
