"""Pruebas unitarias para MedicionController."""

from datetime import datetime

import pytest

from src.controllers.medicion_calidad_aire_controller import MedicionController
from src.models.estacion_ambiental import EstacionAmbiental
from src.models.medicion_calidad_aire import MedicionCalidadAire
from src.repositories.estacion_repository import EstacionRepository
from src.repositories.medicion_calidad_aire_repository import MedicionRepository


class _VistaStub:
    """Vista de prueba que captura los mensajes y errores emitidos."""

    def __init__(self):
        self.mensajes: list[str] = []
        self.errores: list[str] = []
        self.listados: list[list] = []

    def show_message(self, mensaje: str) -> None:
        self.mensajes.append(mensaje)

    def show_error(self, mensaje: str) -> None:
        self.errores.append(mensaje)

    def show_mediciones(self, mediciones) -> None:
        self.listados.append(list(mediciones))


@pytest.fixture
def contexto(tmp_path):
    """Controller + dependencias preparadas con una estacion valida."""
    estaciones = EstacionRepository(tmp_path / "estaciones.json")
    estaciones.crear(EstacionAmbiental(
        id_estacion="EST-MED-01",
        nombre="Centro",
        municipio="05001",
        tipo_estacion="Fija",
        estado="Activa",
    ))
    mediciones = MedicionRepository(data_file=tmp_path / "mediciones.json")
    vista = _VistaStub()
    controller = MedicionController(mediciones, vista, estacion_repository=estaciones)
    return controller, mediciones, vista


def test_1_crear_medicion_manual_exitosa(contexto):
    controller, repo, vista = contexto
    controller.crear_medicion(
        "PM", "M001", "05001", "EST-MED-01",
        datetime(2026, 5, 20, 10, 0), 42.5,
        diametro_aerodinamico="PM10",
    )
    assert repo.buscar_medicion_por_id("M001") is not None
    assert any("creada manualmente" in m for m in vista.mensajes)


def test_2_crear_falla_si_estacion_no_existe(contexto):
    controller, repo, vista = contexto
    controller.crear_medicion(
        "PM", "M001", "05001", "EST-INEXISTENTE",
        datetime(2026, 5, 20), 42.5,
        diametro_aerodinamico="PM10",
    )
    assert repo.buscar_medicion_por_id("M001") is None
    assert any("no existe" in e for e in vista.errores)


def test_3_crear_falla_con_tipo_desconocido(contexto):
    controller, repo, vista = contexto
    controller.crear_medicion(
        "OZONO", "M001", "05001", "EST-MED-01",
        datetime(2026, 5, 20), 42.5,
    )
    assert repo.buscar_medicion_por_id("M001") is None
    assert any("desconocido" in e for e in vista.errores)


def test_4_crear_falla_con_valor_negativo(contexto):
    controller, repo, vista = contexto
    controller.crear_medicion(
        "PM", "M001", "05001", "EST-MED-01",
        datetime(2026, 5, 20), -5.0,
        diametro_aerodinamico="PM10",
    )
    assert repo.buscar_medicion_por_id("M001") is None
    assert vista.errores  # se reporto el error


def test_5_actualizar_medicion_manual(contexto):
    controller, repo, vista = contexto
    controller.crear_medicion(
        "PM", "M001", "05001", "EST-MED-01",
        datetime(2026, 5, 20), 42.5,
        diametro_aerodinamico="PM10",
    )
    controller.actualizar_medicion("M001", medicion=130.0)
    encontrada = repo.buscar_medicion_por_id("M001")
    assert encontrada.medicion == 130.0
    assert encontrada.nivel == "Aceptable"


def test_6_no_actualizar_medicion_automatica(contexto):
    controller, repo, vista = contexto
    from src.models.medicion_calidad_aire import MedicionCalidadAirePM
    repo.crear_medicion(MedicionCalidadAirePM(
        id="A001", codigo_dane_municipio="05001", id_estacion="EST-MED-01",
        fecha=datetime(2026, 5, 20), diametro_aerodinamico="PM10",
        medicion=42.5, origen=MedicionCalidadAire.AUTO,
    ))
    controller.actualizar_medicion("A001", medicion=999.0)
    assert repo.buscar_medicion_por_id("A001").medicion == 42.5
    assert any("inmutable" in e.lower() for e in vista.errores)


def test_7_actualizar_inexistente_reporta_error(contexto):
    controller, _, vista = contexto
    controller.actualizar_medicion("X999", medicion=10.0)
    assert any("no existe" in e.lower() for e in vista.errores)


def test_8_eliminar_medicion_manual(contexto):
    controller, repo, vista = contexto
    controller.crear_medicion(
        "PM", "M001", "05001", "EST-MED-01",
        datetime(2026, 5, 20), 42.5,
        diametro_aerodinamico="PM10",
    )
    controller.eliminar_medicion("M001")
    assert repo.buscar_medicion_por_id("M001") is None


def test_9_listar_mediciones(contexto):
    controller, _, vista = contexto
    controller.crear_medicion(
        "PM", "M001", "05001", "EST-MED-01",
        datetime(2026, 5, 20), 42.5,
        diametro_aerodinamico="PM10",
    )
    controller.listar_mediciones()
    assert len(vista.listados) == 1
    assert len(vista.listados[0]) == 1


def test_10_sincronizar_sensor_no_pisa_manuales(contexto):
    controller, repo, vista = contexto
    controller.crear_medicion(
        "PM", "M001", "05001", "EST-MED-01",
        datetime(2026, 5, 20), 42.5,
        diametro_aerodinamico="PM10",
    )
    controller.sincronizar_sensor([{
        "tipo": "PM",
        "id": "M001",  # mismo id que la manual
        "codigo_dane_municipio": "05001",
        "id_estacion": "EST-MED-01",
        "fecha": "2026-05-21T10:00",
        "medicion": 999.0,
        "diametro_aerodinamico": "PM10",
    }])
    # La medicion manual no debe ser sobrescrita.
    assert repo.buscar_medicion_por_id("M001").medicion == 42.5
