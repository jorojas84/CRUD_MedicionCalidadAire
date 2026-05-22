"""Pruebas unitarias para EstacionRepository y EstacionAmbiental."""

import pytest
from pathlib import Path
import json
from src.models.estacion_ambiental import (
    EstacionAmbiental,
    EstacionValidationError,
    DuplicateEstacionError,
)
from src.repositories.estacion_repository import EstacionRepository
from src.exceptions.custom_exceptions import RegistroNoEncontradoError


def test_crear_estacion_valida(tmp_path):
    """Crear una estación ambiental válida y verificar persistencia."""
    archivo_json = tmp_path / "estaciones.json"
    repo = EstacionRepository(str(archivo_json))
    
    estacion = EstacionAmbiental(
        id_estacion="EST001",
        nombre="Estación Centro",
        municipio="Bogotá",
        tipo_estacion="Fija",
        estado="Activa"
    )
    
    repo.crear(estacion)
    
    encontrada = repo.buscar("EST001")
    assert encontrada is not None
    assert encontrada.nombre == "Estación Centro"
    assert encontrada.estado == "Activa"


def test_rechazar_estacion_sin_id(tmp_path):
    """Rechazar creación de estación sin id_estacion."""
    archivo_json = tmp_path / "estaciones.json"
    repo = EstacionRepository(str(archivo_json))
    
    with pytest.raises(EstacionValidationError):
        EstacionAmbiental(
            id_estacion="",
            nombre="Estación Centro",
            municipio="Bogotá",
            tipo_estacion="Fija",
            estado="Activa"
        )


def test_rechazar_estacion_sin_nombre(tmp_path):
    """Rechazar creación de estación sin nombre."""
    archivo_json = tmp_path / "estaciones.json"
    repo = EstacionRepository(str(archivo_json))
    
    with pytest.raises(EstacionValidationError):
        EstacionAmbiental(
            id_estacion="EST001",
            nombre="",
            municipio="Bogotá",
            tipo_estacion="Fija",
            estado="Activa"
        )


def test_rechazar_estacion_sin_municipio(tmp_path):
    """Rechazar creación de estación sin municipio."""
    archivo_json = tmp_path / "estaciones.json"
    repo = EstacionRepository(str(archivo_json))
    
    with pytest.raises(EstacionValidationError):
        EstacionAmbiental(
            id_estacion="EST001",
            nombre="Estación Centro",
            municipio="",
            tipo_estacion="Fija",
            estado="Activa"
        )


def test_rechazar_estado_invalido(tmp_path):
    """Rechazar estado que no esté en ESTADOS_VALIDOS."""
    archivo_json = tmp_path / "estaciones.json"
    repo = EstacionRepository(str(archivo_json))
    
    with pytest.raises(EstacionValidationError):
        EstacionAmbiental(
            id_estacion="EST001",
            nombre="Estación Centro",
            municipio="Bogotá",
            tipo_estacion="Fija",
            estado="Suspendida"
        )


def test_rechazar_estacion_duplicada(tmp_path):
    """Rechazar creación de estación con id duplicado."""
    archivo_json = tmp_path / "estaciones.json"
    repo = EstacionRepository(str(archivo_json))
    
    estacion1 = EstacionAmbiental(
        id_estacion="EST001",
        nombre="Estación Centro",
        municipio="Bogotá",
        tipo_estacion="Fija",
        estado="Activa"
    )
    repo.crear(estacion1)
    
    with pytest.raises(DuplicateEstacionError):
        estacion2 = EstacionAmbiental(
            id_estacion="EST001",
            nombre="Estación Norte",
            municipio="Bogotá",
            tipo_estacion="Fija",
            estado="Activa"
        )
        repo.crear(estacion2)


def test_listar_estaciones(tmp_path):
    """Listar todas las estaciones guardadas."""
    archivo_json = tmp_path / "estaciones.json"
    repo = EstacionRepository(str(archivo_json))
    
    estacion1 = EstacionAmbiental(
        id_estacion="EST001",
        nombre="Estación Centro",
        municipio="Bogotá",
        tipo_estacion="Fija",
        estado="Activa"
    )
    estacion2 = EstacionAmbiental(
        id_estacion="EST002",
        nombre="Estación Sur",
        municipio="Bogotá",
        tipo_estacion="Móvil",
        estado="Activa"
    )
    
    repo.crear(estacion1)
    repo.crear(estacion2)
    
    estaciones = repo.listar()
    assert len(estaciones) == 2
    assert isinstance(estaciones[0], EstacionAmbiental)
    assert isinstance(estaciones[1], EstacionAmbiental)


def test_buscar_estacion_existente(tmp_path):
    """Buscar estación existente y no existente."""
    archivo_json = tmp_path / "estaciones.json"
    repo = EstacionRepository(str(archivo_json))
    
    estacion = EstacionAmbiental(
        id_estacion="EST001",
        nombre="Estación Centro",
        municipio="Bogotá",
        tipo_estacion="Fija",
        estado="Activa"
    )
    repo.crear(estacion)
    
    encontrada = repo.buscar("EST001")
    assert encontrada is not None
    assert encontrada.id_estacion == "EST001"
    
    no_encontrada = repo.buscar("NOEXISTE")
    assert no_encontrada is None


def test_actualizar_estacion(tmp_path):
    """Actualizar datos de una estación existente."""
    archivo_json = tmp_path / "estaciones.json"
    repo = EstacionRepository(str(archivo_json))
    
    estacion = EstacionAmbiental(
        id_estacion="EST001",
        nombre="Estación Centro",
        municipio="Bogotá",
        tipo_estacion="Fija",
        estado="Activa"
    )
    repo.crear(estacion)
    
    estacion_actualizada = EstacionAmbiental(
        id_estacion="EST001",
        nombre="Estación Centro Modificada",
        municipio="Bogotá",
        tipo_estacion="Fija",
        estado="Inactiva"
    )
    repo.actualizar(estacion_actualizada)
    
    encontrada = repo.buscar("EST001")
    assert encontrada.nombre == "Estación Centro Modificada"
    assert encontrada.estado == "Inactiva"


def test_eliminar_estacion(tmp_path):
    """Eliminar una estación existente."""
    archivo_json = tmp_path / "estaciones.json"
    repo = EstacionRepository(str(archivo_json))
    
    estacion = EstacionAmbiental(
        id_estacion="EST001",
        nombre="Estación Centro",
        municipio="Bogotá",
        tipo_estacion="Fija",
        estado="Activa"
    )
    repo.crear(estacion)
    
    repo.eliminar("EST001")
    
    encontrada = repo.buscar("EST001")
    assert encontrada is None
