"""Pruebas del patron Command para alertas."""

from src.models.alerta_ambiental import AlertaAmbiental
from src.patterns.command.comandos_alerta import CrearAlertaCommand, HistorialComandos
from src.repositories.alerta_repository import AlertaRepository


def _alerta_base(**overrides):
    datos = {
        "id_alerta": "ALT900",
        "id_medicion": "MED900",
        "nivel": "Medio",
        "descripcion": "Prueba command",
        "fecha": "2026-05-24",
        "estado": "Activa",
    }
    datos.update(overrides)
    return AlertaAmbiental(**datos)


def test_command_ejecuta_creacion_de_alerta(tmp_path):
    repo = AlertaRepository(data_file=tmp_path / "alertas_command.json")
    alerta = _alerta_base()
    comando = CrearAlertaCommand(repo, alerta)

    creada = comando.ejecutar()

    assert creada.id_alerta == "ALT900"
    assert repo.buscar_alerta_por_id("ALT900") is not None


def test_command_guarda_historial_de_ejecuciones(tmp_path):
    repo = AlertaRepository(data_file=tmp_path / "alertas_command.json")
    invocador = HistorialComandos()

    comando_1 = CrearAlertaCommand(repo, _alerta_base(id_alerta="ALT901", id_medicion="MED901"))
    comando_2 = CrearAlertaCommand(repo, _alerta_base(id_alerta="ALT902", id_medicion="MED902"))

    invocador.ejecutar(comando_1)
    invocador.ejecutar(comando_2)

    historial = invocador.obtener_historial()
    assert historial == ["CrearAlertaCommand", "CrearAlertaCommand"]
