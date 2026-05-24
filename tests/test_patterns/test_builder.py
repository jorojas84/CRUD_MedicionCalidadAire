import pytest

from src.patterns.builder.reporte_alerta_builder import ReporteAlertaBuilder


def test_builder_construye_reporte_completo():
    reporte = (
        ReporteAlertaBuilder()
        .con_id_alerta("ALT-001")
        .con_municipio("Bogota")
        .con_nivel("Alto")
        .con_descripcion("Evento de contaminacion")
        .agregar_medicion({"pm25": 150})
        .agregar_recomendacion("Reducir actividades al aire libre")
        .construir()
    )

    assert reporte.id_alerta == "ALT-001"
    assert reporte.nivel == "Alto"
    assert len(reporte.mediciones) == 1


def test_builder_valida_error_por_nivel_invalido():
    with pytest.raises(ValueError):
        ReporteAlertaBuilder().con_nivel("Critico")
