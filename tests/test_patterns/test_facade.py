import pytest

from src.patterns.facade.alerta_facade import AlertaFacade
from src.repositories.alerta_repository import AlertaRepository


class ClasificadorAcademico:
    def clasificar_valor(self, valor: float) -> str:
        if valor < 50:
            return "Bajo"
        if valor <= 100:
            return "Medio"
        return "Alto"


class ClasificadorInvalido:
    def clasificar_valor(self, valor: float) -> str:
        return "Critico"


def test_facade_registra_evento_critico_valido(tmp_path):
    repo = AlertaRepository(data_file=tmp_path / "alertas_test.json")
    facade = AlertaFacade(
        alerta_repository=repo,
        clasificador=ClasificadorAcademico(),
    )

    creada = facade.registrar_evento_critico(
        id_alerta="ALT-100",
        id_medicion="MED-100",
        valor=120,
        descripcion="Contaminacion elevada",
        fecha="2026-05-24",
    )

    assert creada.id_alerta == "ALT-100"
    assert creada.estado == "Activa"


def test_facade_rechaza_nivel_invalido_y_no_persiste(tmp_path):
    repo = AlertaRepository(data_file=tmp_path / "alertas_test.json")
    facade = AlertaFacade(
        alerta_repository=repo,
        clasificador=ClasificadorInvalido(),
    )

    with pytest.raises(ValueError):
        facade.registrar_evento_critico(
            id_alerta="ALT-200",
            id_medicion="MED-200",
            valor=10,
            descripcion="Caso invalido",
            fecha="2026-05-24",
        )

    assert repo.listar_alertas() == []
