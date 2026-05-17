from src.exceptions.custom_exceptions import DatoInvalidoError, RegistroNoEncontradoError
from src.models.alerta_ambiental import AlertaAmbiental
from src.repositories.alerta_repository import AlertaRepository


def _repo_temporal(tmp_path):
    return AlertaRepository(data_file=tmp_path / "alertas_test.json")


def _alerta_base(**overrides):
    datos = {
        "id_alerta": "ALT001",
        "id_medicion": "MED001",
        "nivel": "Medio",
        "descripcion": "Contaminacion moderada",
        "fecha": "2026-05-04",
        "estado": "Activa",
    }
    datos.update(overrides)
    return AlertaAmbiental(**datos)


def test_1_crear_alerta_valida(tmp_path):
    repo = _repo_temporal(tmp_path)
    alerta = _alerta_base()
    creada = repo.crear_alerta(alerta)
    assert creada.id_alerta == "ALT001"
    assert len(repo.listar_alertas()) == 1


def test_2_rechazar_alerta_sin_id():
    try:
        _alerta_base(id_alerta="")
        assert False
    except DatoInvalidoError:
        assert True


def test_3_rechazar_alerta_sin_medicion():
    try:
        _alerta_base(id_medicion="")
        assert False
    except DatoInvalidoError:
        assert True


def test_4_rechazar_alerta_sin_descripcion():
    try:
        _alerta_base(descripcion="")
        assert False
    except DatoInvalidoError:
        assert True


def test_5_rechazar_nivel_invalido():
    try:
        _alerta_base(nivel="Critico")
        assert False
    except DatoInvalidoError:
        assert True


def test_6_rechazar_estado_invalido():
    try:
        _alerta_base(estado="Pendiente")
        assert False
    except DatoInvalidoError:
        assert True


def test_7_buscar_alerta_existente(tmp_path):
    repo = _repo_temporal(tmp_path)
    repo.crear_alerta(_alerta_base())
    encontrada = repo.buscar_alerta_por_id("ALT001")
    assert encontrada is not None
    assert encontrada.id_medicion == "MED001"


def test_8_actualizar_descripcion(tmp_path):
    repo = _repo_temporal(tmp_path)
    repo.crear_alerta(_alerta_base())
    actualizada = _alerta_base(descripcion="Descripcion actualizada")
    repo.actualizar_alerta("ALT001", actualizada)
    assert repo.buscar_alerta_por_id("ALT001").descripcion == "Descripcion actualizada"


def test_9_eliminar_alerta(tmp_path):
    repo = _repo_temporal(tmp_path)
    repo.crear_alerta(_alerta_base())
    repo.eliminar_alerta("ALT001")
    assert repo.buscar_alerta_por_id("ALT001") is None


def test_10_nivel_alto_queda_activa(tmp_path):
    repo = _repo_temporal(tmp_path)
    alerta = _alerta_base(nivel="Alto", estado="Cerrada")
    repo.crear_alerta(alerta)
    guardada = repo.buscar_alerta_por_id("ALT001")
    assert guardada.estado == "Activa"
