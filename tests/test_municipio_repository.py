"""Pruebas unitarias para el modulo Municipio (Actividad 7)."""

import pytest

from src.controllers.municipio_controller import MunicipioController
from src.exceptions.municipio_exceptions import (
    DatosMunicipioInvalidosError,
    MunicipioNoEncontradoError,
    ReglaNegocioMunicipioError,
)
from src.repositories.municipio_repository import MunicipioRepository


def _controller_temporal(tmp_path):
    repo = MunicipioRepository(data_file=tmp_path / "municipios_test.json")
    return MunicipioController(repo)


def test_1_crear_municipio_valido(tmp_path):
    controller = _controller_temporal(tmp_path)
    creado = controller.crear_municipio("MUN001", "Medellin", "Antioquia", "Andina", "Activo")
    assert creado.id_municipio == "MUN001"


def test_2_rechazar_municipio_sin_id(tmp_path):
    controller = _controller_temporal(tmp_path)
    with pytest.raises(DatosMunicipioInvalidosError):
        controller.crear_municipio("", "Medellin", "Antioquia", "Andina", "Activo")


def test_3_rechazar_municipio_sin_nombre(tmp_path):
    controller = _controller_temporal(tmp_path)
    with pytest.raises(DatosMunicipioInvalidosError):
        controller.crear_municipio("MUN001", "", "Antioquia", "Andina", "Activo")


def test_4_rechazar_municipio_sin_departamento(tmp_path):
    controller = _controller_temporal(tmp_path)
    with pytest.raises(DatosMunicipioInvalidosError):
        controller.crear_municipio("MUN001", "Medellin", "", "Andina", "Activo")


def test_5_rechazar_municipio_sin_region(tmp_path):
    controller = _controller_temporal(tmp_path)
    with pytest.raises(DatosMunicipioInvalidosError):
        controller.crear_municipio("MUN001", "Medellin", "Antioquia", "", "Activo")


def test_6_rechazar_estado_invalido(tmp_path):
    controller = _controller_temporal(tmp_path)
    with pytest.raises(DatosMunicipioInvalidosError):
        controller.crear_municipio("MUN001", "Medellin", "Antioquia", "Andina", "Pendiente")


def test_7_rechazar_municipio_duplicado(tmp_path):
    controller = _controller_temporal(tmp_path)
    controller.crear_municipio("MUN001", "Medellin", "Antioquia", "Andina", "Activo")
    with pytest.raises(ReglaNegocioMunicipioError):
        controller.crear_municipio("MUN001", "Bello", "Antioquia", "Andina", "Inactivo")


def test_8_buscar_municipio_existente(tmp_path):
    controller = _controller_temporal(tmp_path)
    controller.crear_municipio("MUN001", "Medellin", "Antioquia", "Andina", "Activo")
    encontrado = controller.buscar_municipio("MUN001")
    assert encontrado.nombre == "Medellin"


def test_9_actualizar_municipio(tmp_path):
    controller = _controller_temporal(tmp_path)
    controller.crear_municipio("MUN001", "Medellin", "Antioquia", "Andina", "Activo")
    actualizado = controller.actualizar_municipio(
        "MUN001", "Medellin", "Antioquia", "Andina", "Inactivo"
    )
    assert actualizado.estado == "Inactivo"


def test_10_eliminar_municipio(tmp_path):
    controller = _controller_temporal(tmp_path)
    controller.crear_municipio("MUN001", "Medellin", "Antioquia", "Andina", "Inactivo")
    assert controller.eliminar_municipio("MUN001") is True
    with pytest.raises(MunicipioNoEncontradoError):
        controller.buscar_municipio("MUN001")
