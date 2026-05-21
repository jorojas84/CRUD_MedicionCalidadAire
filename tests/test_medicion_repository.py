"""Tests del repositorio: CRUD y persistencia en JSON.

El Repository es la unica capa que conoce el medio de almacenamiento
(en este caso un archivo JSON). Probamos su contrato CRUD contra un
archivo temporal (fixture `tmp_path` de pytest), de modo que cada test
arranca limpio y nunca toca la data real del proyecto.

La unica regla de dominio que vive aqui es "solo las mediciones MANUAL
son eliminables"; el resto se prueba en el modelo o el controller.
"""

from datetime import datetime

import pytest

from src.exceptions.custom_exceptions import (
    DatoInvalidoError,
    RegistroDuplicadoError,
)
from src.models.medicion import Medicion
from src.models.medicion_calidad_aire import MedicionCalidadAirePM
from src.repositories.medicion_repository import MedicionRepository


def _repo_temporal(tmp_path) -> MedicionRepository:
    """Repositorio sobre un archivo nuevo y vacio por test.

    `tmp_path` es una fixture incorporada de pytest: crea un directorio
    temporal unico por test y lo borra al terminar. Eso garantiza que
    los tests son independientes entre si.
    """
    return MedicionRepository(data_file=tmp_path / "mediciones_test.json")


def _medicion_base(**overrides) -> MedicionCalidadAirePM:
    """Medicion PM por defecto; `overrides` cambia solo lo que importa."""
    datos = {
        "id": "m-001",
        "municipio": "Bogota",
        "estacion": "Estacion Centro",
        "fecha": datetime(2026, 5, 18, 8, 15),
        "diametro_aerodinamico": MedicionCalidadAirePM.PM10,
        "medicion": 120.5,
        "origen": Medicion.AUTO,
    }
    datos.update(overrides)
    return MedicionCalidadAirePM(**datos)


# ── CRUD basico ─────────────────────────────────────────────────────────────

def test_crear_y_buscar(tmp_path):
    # Persistencia ida y vuelta: lo que se guarda se puede recuperar.
    repo = _repo_temporal(tmp_path)
    repo.crear_medicion(_medicion_base())
    m = repo.buscar_medicion_por_id("m-001")
    assert m is not None
    assert m.municipio == "Bogota"


def test_actualizar_persiste_cambios(tmp_path):
    # El repo reemplaza el registro y los cambios sobreviven al releerse.
    repo = _repo_temporal(tmp_path)
    repo.crear_medicion(_medicion_base(medicion=10, origen=Medicion.MANUAL))
    repo.actualizar_medicion(
        _medicion_base(medicion=200, origen=Medicion.MANUAL)
    )
    m = repo.buscar_medicion_por_id("m-001")
    assert m is not None
    assert m.medicion == 200


def test_listar_devuelve_subclase_correcta(tmp_path):
    # El repo no devuelve dicts: reconstruye la subclase concreta de
    # `Medicion` segun el campo `tipo` del JSON. Eso es lo que permite
    # que las capas superiores trabajen polimorficamente.
    repo = _repo_temporal(tmp_path)
    repo.crear_medicion(_medicion_base())
    [m] = repo.listar_mediciones()
    assert isinstance(m, MedicionCalidadAirePM)


# ── reglas que vienen del repositorio ───────────────────────────────────────

def test_crear_rechaza_id_duplicado(tmp_path):
    # El `id` identifica univocamente una medicion: no puede repetirse.
    repo = _repo_temporal(tmp_path)
    repo.crear_medicion(_medicion_base())
    with pytest.raises(RegistroDuplicadoError):
        repo.crear_medicion(_medicion_base())


def test_eliminar_sensor_falla(tmp_path):
    # Las mediciones AUTO (origen sensor) son inmutables: ni se editan
    # ni se eliminan, ni siquiera desde el repo.
    repo = _repo_temporal(tmp_path)
    repo.crear_medicion(_medicion_base(origen=Medicion.AUTO))
    with pytest.raises(DatoInvalidoError):
        repo.eliminar_medicion("m-001")


def test_eliminar_manual_funciona(tmp_path):
    # En cambio una medicion MANUAL si puede borrarse (la creo el usuario).
    repo = _repo_temporal(tmp_path)
    repo.crear_medicion(_medicion_base(origen=Medicion.MANUAL))
    repo.eliminar_medicion("m-001")
    assert repo.buscar_medicion_por_id("m-001") is None
