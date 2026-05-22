"""Prueba temporal para validar persistencia JSON de estaciones."""

from __future__ import annotations

from src.models.estacion_ambiental import EstacionAmbiental
from src.repositories.estacion_repository import EstacionRepository


def test_guardado_temporal_estacion_json(tmp_path, capsys) -> None:
    """Guarda una estacion en un JSON temporal y confirma el resultado."""
    repo = EstacionRepository(data_file=tmp_path / "estaciones.json")
    estacion = EstacionAmbiental(
        id_estacion="EST-TEMP-001",
        nombre="Estacion Temporal",
        municipio="Bogota",
        tipo_estacion="Urbana",
        estado="Activa",
    )

    repo.crear(estacion)
    guardada = repo.buscar("EST-TEMP-001")

    assert guardada is not None
    assert guardada.id_estacion == "EST-TEMP-001"
    print("Guardado exitoso en estaciones.json")

    salida = capsys.readouterr()
    assert "Guardado exitoso en estaciones.json" in salida.out