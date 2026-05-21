"""Tests del controller: orquestacion entre modelo, repo y view.

El Controller es la capa que coordina los tres componentes: recibe la
intencion del usuario, llama al repositorio para persistir y le pide a
la vista que comunique el resultado. No prueba reglas de dominio
(eso es del modelo) ni persistencia (eso es del repo); prueba que la
coordinacion sea correcta y que las reglas criticas del negocio
(inmutabilidad de AUTO, proteccion de MANUAL) se cumplan.
"""

from datetime import datetime

from src.controllers.medicion_controller import MedicionController
from src.models.medicion import Medicion
from src.models.medicion_calidad_aire import MedicionCalidadAirePM
from src.repositories.medicion_repository import MedicionRepository
from src.views.medicion_view import MedicionView


def _repo_temporal(tmp_path) -> MedicionRepository:
    # `tmp_path` es una fixture de pytest: directorio temporal unico por
    # test que se borra al terminar. Asegura aislamiento entre tests.
    return MedicionRepository(data_file=tmp_path / "mediciones_test.json")


def _medicion_base(**overrides) -> MedicionCalidadAirePM:
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


class _FakeView(MedicionView):
    """Doble de prueba que captura llamadas a la vista sin imprimir.

    Asi los tests pueden verificar que el controller le hablo a la vista
    correctamente sin ensuciar el stdout durante la corrida.
    """

    def __init__(self):
        self.mensajes: list[str] = []
        self.errores: list[str] = []

    def show_message(self, msg):
        self.mensajes.append(msg)

    def show_error(self, msg):
        self.errores.append(msg)

    def show_mediciones(self, _mediciones):
        # No nos interesa el listado en estos tests: stub no-op.
        pass


def _item_sensor(**overrides) -> dict:
    base = {
        "tipo": "PM",
        "id": "s-001",
        "municipio": "Cali",
        "estacion": "Sur",
        "fecha": "2026-05-20T10:00:00",
        "diametro_aerodinamico": MedicionCalidadAirePM.PM10,
        "medicion": 50,
    }
    base.update(overrides)
    return base


# ── CRUD via controller ──────────────────────────────────────────────────────

def test_crear_fuerza_origen_manual(tmp_path):
    # Aunque el caller no especifique origen, el controller siempre
    # marca como MANUAL lo que viene del usuario. Asi nadie puede
    # "inyectar" datos haciendose pasar por el sensor.
    repo = _repo_temporal(tmp_path)
    ctrl = MedicionController(repo, _FakeView())
    ctrl.crear_medicion(
        tipo="PM",
        id="m-001", municipio="Bogota", estacion="Centro",
        fecha=datetime(2026, 5, 20, 8, 0), medicion=10,
        diametro_aerodinamico=MedicionCalidadAirePM.PM10,
    )
    m = repo.buscar_medicion_por_id("m-001")
    assert m is not None
    assert m.origen == Medicion.MANUAL


def test_actualizar_manual_permitido(tmp_path):
    # Las mediciones MANUAL si se pueden corregir (las creo el usuario).
    # El origen debe preservarse: no se "convierte" en AUTO al editar.
    repo = _repo_temporal(tmp_path)
    ctrl = MedicionController(repo, _FakeView())
    repo.crear_medicion(_medicion_base(origen=Medicion.MANUAL))

    ctrl.actualizar_medicion("m-001", medicion=200)

    m = repo.buscar_medicion_por_id("m-001")
    assert m is not None
    assert m.medicion == 200
    assert m.origen == Medicion.MANUAL  # se preserva


# ── inmutabilidad de las mediciones del sensor ───────────────────────────────

def test_actualizar_sensor_bloqueado(tmp_path):
    # Regla critica del negocio: lo que vino del sensor es intocable.
    # Aunque se intenten cambiar varios campos a la vez, NINGUNO debe
    # quedar modificado en disco.
    repo = _repo_temporal(tmp_path)
    view = _FakeView()
    ctrl = MedicionController(repo, view)
    repo.crear_medicion(_medicion_base(origen=Medicion.AUTO))

    ctrl.actualizar_medicion("m-001", medicion=200, municipio="Hackeado")

    assert "inmutables" in view.errores[0]
    m = repo.buscar_medicion_por_id("m-001")
    assert m is not None
    assert m.medicion == 120.5      # no cambio
    assert m.municipio == "Bogota"  # tampoco


def test_eliminar_sensor_reporta_error(tmp_path):
    # Misma regla pero para borrado: el controller avisa a la vista y
    # deja la medicion intacta en el repositorio.
    repo = _repo_temporal(tmp_path)
    view = _FakeView()
    ctrl = MedicionController(repo, view)
    repo.crear_medicion(_medicion_base(origen=Medicion.AUTO))

    ctrl.eliminar_medicion("m-001")

    assert view.errores
    assert repo.buscar_medicion_por_id("m-001") is not None


# ── sincronizacion con sensor ────────────────────────────────────────────────

def test_sincronizar_agrega_nuevas(tmp_path):
    # Items con un id que el repo no conoce se agregan como AUTO
    # (vienen del sensor).
    repo = _repo_temporal(tmp_path)
    ctrl = MedicionController(repo, _FakeView())
    ctrl.sincronizar_sensor([_item_sensor()])
    m = repo.buscar_medicion_por_id("s-001")
    assert m is not None
    assert m.origen == Medicion.AUTO


def test_sincronizar_no_sobreescribe_manual(tmp_path):
    # Caso critico: si el sensor manda un id que ya existe como MANUAL,
    # NO debe pisar el valor manual. La prioridad es del usuario.
    repo = _repo_temporal(tmp_path)
    view = _FakeView()
    ctrl = MedicionController(repo, view)
    repo.crear_medicion(_medicion_base(medicion=10, origen=Medicion.MANUAL))

    ctrl.sincronizar_sensor([_item_sensor(id="m-001", medicion=999)])

    m = repo.buscar_medicion_por_id("m-001")
    assert m is not None
    assert m.medicion == 10
    assert m.origen == Medicion.MANUAL


# ── manejo de errores: nunca propagar excepciones a quien llame ──────────────

def test_actualizar_inexistente_reporta_error(tmp_path):
    # Si la medicion no existe, el controller lo comunica via la view
    # en vez de hacer crashear la app con una excepcion sin atrapar.
    view = _FakeView()
    ctrl = MedicionController(_repo_temporal(tmp_path), view)
    ctrl.actualizar_medicion("no-existe", medicion=50)
    assert view.errores == ["No existe medicion con id no-existe"]


def test_tipo_desconocido_reportado(tmp_path):
    # El controller usa un registry de tipos (PM, y a futuro CO/SO2...).
    # Si se pide crear un contaminante no registrado, avisa y no guarda.
    repo = _repo_temporal(tmp_path)
    view = _FakeView()
    ctrl = MedicionController(repo, view)
    ctrl.crear_medicion(
        tipo="CO",
        id="m-998", municipio="X", estacion="Y",
        fecha=datetime(2026, 5, 20, 8, 0), medicion=10,
    )
    assert any("desconocido" in e for e in view.errores)
    assert repo.buscar_medicion_por_id("m-998") is None
