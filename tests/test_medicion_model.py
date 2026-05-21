"""Tests del modelo: reglas de negocio puro (sin repositorio ni controller).

El modelo es el unico lugar donde viven las reglas de dominio:
clasificacion ICA segun Res. 2254/2017, validaciones de invariantes e
inmutabilidad. Si una regla cambia (por ejemplo un punto de corte), este
es el archivo que debe chillar.
"""

from datetime import datetime

import pytest

from src.exceptions.custom_exceptions import DatoInvalidoError
from src.models.medicion import Medicion
from src.models.medicion_calidad_aire import (
    MedicionCalidadAire,
    MedicionCalidadAirePM,
)


def _medicion_base(**overrides) -> MedicionCalidadAirePM:
    """Crea una medicion PM valida por defecto.

    Permite sobreescribir cualquier campo via `overrides`, asi cada test
    solo necesita declarar lo que le interesa probar.
    """
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


# ── clasificacion ICA (Res. 2254/2017 Tabla 6) ──────────────────────────────
# La tabla define 6 categorias segun la concentracion del contaminante.
# Cada test cubre un caso de frontera para asegurarse de que los cortes
# estan bien implementados.

def test_pm10_buena_en_limite_del_corte():
    # PM10 ≤ 54 µg/m³ debe clasificar como BUENA (limite superior incluido).
    assert _medicion_base(medicion=54).nivel == MedicionCalidadAire.BUENA


def test_pm10_aceptable_apenas_pasa_el_corte():
    # Apenas pasa el corte de 54 → cae en la siguiente categoria.
    assert _medicion_base(medicion=55).nivel == MedicionCalidadAire.ACEPTABLE


def test_pm10_peligrosa_por_encima_del_ultimo_corte():
    # Concentraciones por encima del ultimo punto se clasifican siempre
    # como PELIGROSA (la regla la aplica el modelo en el `else` final).
    assert _medicion_base(medicion=700).nivel == MedicionCalidadAire.PELIGROSA


def test_pm25_usa_su_propia_tabla_de_cortes():
    # PM2.5 es mas fino y mas peligroso: tiene cortes mucho mas estrictos.
    # Con 40 µg/m³ ya cae en DANINA_SENSIBLES (en PM10 seria ACEPTABLE).
    m = _medicion_base(
        diametro_aerodinamico=MedicionCalidadAirePM.PM25,
        medicion=40,
    )
    assert m.nivel == MedicionCalidadAire.DANINA_SENSIBLES


# ── validaciones (invariantes del dominio) ──────────────────────────────────
# El modelo se valida a si mismo en `__init__`. Si el dato viola una
# invariante, debe levantar `DatoInvalidoError` antes de quedar construido.

def test_medicion_negativa_es_invalida():
    # Una concentracion negativa no tiene sentido fisico.
    with pytest.raises(DatoInvalidoError):
        _medicion_base(medicion=-1)


def test_diametro_fuera_de_lista_es_invalido():
    # Solo PM10 y PM2.5 estan en la norma; otros valores se rechazan.
    with pytest.raises(DatoInvalidoError):
        _medicion_base(diametro_aerodinamico="PM5")


# ── inmutabilidad (no hay setters publicos) ─────────────────────────────────

def test_modelo_es_inmutable():
    # Una vez creada, una medicion no muta. Para "modificar" hay que
    # construir otra instancia con los valores nuevos. Esto evita que se
    # alteren datos del sensor o se salte la validacion.
    m = _medicion_base(medicion=50, origen=Medicion.MANUAL)
    with pytest.raises(AttributeError):
        m.medicion = 999  # type: ignore[misc]
