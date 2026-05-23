"""Tests del controller: orquestacion entre modelo, repos y view."""

from datetime import datetime

from src.controllers.medicion_calidad_aire_controller import MedicionController
from src.models.estacion_ambiental import EstacionAmbiental
from src.models.medicion_calidad_aire import (
    MedicionCalidadAire,
    MedicionCalidadAirePM,
)
from src.repositories.estacion_repository import EstacionRepository
from src.repositories.medicion_calidad_aire_repository import MedicionRepository
from src.views.medicion_calidad_aire_view import MedicionView


def _repos_temporales(tmp_path) -> tuple[MedicionRepository, EstacionRepository]:
    return (
        MedicionRepository(data_file=tmp_path / "mediciones_test.json"),
        EstacionRepository(data_file=tmp_path / "estaciones_test.json"),
    )


def _estacion(id_estacion: str = "EST-001", municipio: str = "11001") -> EstacionAmbiental:
    return EstacionAmbiental(
        id_estacion=id_estacion,
        nombre="Estacion de prueba",
        municipio=municipio,
        tipo_estacion="Fija",
        estado="Activa",
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


class _FakeView(MedicionView):
    def __init__(self):
        self.mensajes: list[str] = []
        self.errores: list[str] = []

    def show_message(self, msg):
        self.mensajes.append(msg)

    def show_error(self, msg):
        self.errores.append(msg)

    def show_mediciones(self, _mediciones):
        pass


def _item_sensor(**overrides) -> dict:
    base = {
        "tipo": "PM",
        "id": "s-001",
        "codigo_dane_municipio": "76001",
        "id_estacion": "EST-SUR",
        "fecha": "2026-05-20T10:00:00",
        "diametro_aerodinamico": MedicionCalidadAirePM.PM10,
        "medicion": 50,
    }
    base.update(overrides)
    return base


# ── CRUD via controller ──────────────────────────────────────────────────────

def test_crear_fuerza_origen_manual(tmp_path):
    repo, estaciones = _repos_temporales(tmp_path)
    estaciones.crear(_estacion("EST-001"))
    ctrl = MedicionController(repo, _FakeView(), estacion_repository=estaciones)
    ctrl.crear_medicion(
        tipo="PM",
        id="m-001", codigo_dane_municipio="11001", id_estacion="EST-001",
        fecha=datetime(2026, 5, 20, 8, 0), medicion=10,
        diametro_aerodinamico=MedicionCalidadAirePM.PM10,
    )
    m = repo.buscar_medicion_por_id("m-001")
    assert m is not None
    assert m.origen == MedicionCalidadAire.MANUAL


def test_crear_rechaza_estacion_inexistente(tmp_path):
    repo, estaciones = _repos_temporales(tmp_path)
    view = _FakeView()
    ctrl = MedicionController(repo, view, estacion_repository=estaciones)
    ctrl.crear_medicion(
        tipo="PM",
        id="m-001", codigo_dane_municipio="11001", id_estacion="EST-XYZ",
        fecha=datetime(2026, 5, 20, 8, 0), medicion=10,
        diametro_aerodinamico=MedicionCalidadAirePM.PM10,
    )
    assert any("EST-XYZ" in e for e in view.errores)
    assert repo.buscar_medicion_por_id("m-001") is None


def test_actualizar_manual_permitido(tmp_path):
    repo, estaciones = _repos_temporales(tmp_path)
    estaciones.crear(_estacion("EST-001"))
    ctrl = MedicionController(repo, _FakeView(), estacion_repository=estaciones)
    repo.crear_medicion(_medicion_base(origen=MedicionCalidadAire.MANUAL))

    ctrl.actualizar_medicion("m-001", medicion=200)

    m = repo.buscar_medicion_por_id("m-001")
    assert m is not None
    assert m.medicion == 200
    assert m.origen == MedicionCalidadAire.MANUAL


# ── inmutabilidad de las mediciones del sensor ───────────────────────────────

def test_actualizar_sensor_bloqueado(tmp_path):
    repo, estaciones = _repos_temporales(tmp_path)
    estaciones.crear(_estacion("EST-001"))
    view = _FakeView()
    ctrl = MedicionController(repo, view, estacion_repository=estaciones)
    repo.crear_medicion(_medicion_base(origen=MedicionCalidadAire.AUTO))

    ctrl.actualizar_medicion("m-001", medicion=200, codigo_dane_municipio="00000")

    assert "inmutables" in view.errores[0]
    m = repo.buscar_medicion_por_id("m-001")
    assert m is not None
    assert m.medicion == 120.5
    assert m.codigo_dane_municipio == "11001"


def test_eliminar_sensor_reporta_error(tmp_path):
    repo, estaciones = _repos_temporales(tmp_path)
    view = _FakeView()
    ctrl = MedicionController(repo, view, estacion_repository=estaciones)
    repo.crear_medicion(_medicion_base(origen=MedicionCalidadAire.AUTO))

    ctrl.eliminar_medicion("m-001")

    assert view.errores
    assert repo.buscar_medicion_por_id("m-001") is not None


# ── sincronizacion con sensor ────────────────────────────────────────────────

def test_sincronizar_agrega_nuevas(tmp_path):
    repo, estaciones = _repos_temporales(tmp_path)
    ctrl = MedicionController(repo, _FakeView(), estacion_repository=estaciones)
    ctrl.sincronizar_sensor([_item_sensor()])
    m = repo.buscar_medicion_por_id("s-001")
    assert m is not None
    assert m.origen == MedicionCalidadAire.AUTO


def test_sincronizar_autorregistra_estacion_desconocida(tmp_path):
    # Cuando llega una estacion que no esta en el catalogo, el controller
    # la crea con placeholders en vez de fallar. La medicion se guarda
    # normalmente y la estacion queda lista para que un operador la
    # complete despues.
    repo, estaciones = _repos_temporales(tmp_path)
    ctrl = MedicionController(repo, _FakeView(), estacion_repository=estaciones)

    ctrl.sincronizar_sensor([_item_sensor(id_estacion="EST-NUEVA")])

    e = estaciones.buscar("EST-NUEVA")
    assert e is not None
    assert e.nombre == "(autorregistrada)"
    assert e.tipo_estacion == "Desconocido"
    assert repo.buscar_medicion_por_id("s-001") is not None


def test_sincronizar_no_sobreescribe_manual(tmp_path):
    repo, estaciones = _repos_temporales(tmp_path)
    estaciones.crear(_estacion("EST-001"))
    view = _FakeView()
    ctrl = MedicionController(repo, view, estacion_repository=estaciones)
    repo.crear_medicion(_medicion_base(medicion=10, origen=MedicionCalidadAire.MANUAL))

    ctrl.sincronizar_sensor([_item_sensor(
        id="m-001", medicion=999,
        codigo_dane_municipio="11001", id_estacion="EST-001",
    )])

    m = repo.buscar_medicion_por_id("m-001")
    assert m is not None
    assert m.medicion == 10
    assert m.origen == MedicionCalidadAire.MANUAL


# ── manejo de errores ───────────────────────────────────────────────────────

def test_actualizar_inexistente_reporta_error(tmp_path):
    repo, estaciones = _repos_temporales(tmp_path)
    view = _FakeView()
    ctrl = MedicionController(repo, view, estacion_repository=estaciones)
    ctrl.actualizar_medicion("no-existe", medicion=50)
    assert view.errores == ["No existe medicion con id no-existe"]


def test_tipo_desconocido_reportado(tmp_path):
    repo, estaciones = _repos_temporales(tmp_path)
    view = _FakeView()
    ctrl = MedicionController(repo, view, estacion_repository=estaciones)
    ctrl.crear_medicion(
        tipo="CO",
        id="m-998", codigo_dane_municipio="11001", id_estacion="EST-001",
        fecha=datetime(2026, 5, 20, 8, 0), medicion=10,
    )
    assert any("desconocido" in e for e in view.errores)
    assert repo.buscar_medicion_por_id("m-998") is None
