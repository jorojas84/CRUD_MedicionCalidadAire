"""Registro central de creadores de mediciones (Factory Method).

`MedicionFactory` mantiene el mapa `tipo -> MedicionCreator` y delega
la instanciacion concreta en el creador correspondiente. Agregar un
contaminante nuevo se reduce a registrar su `MedicionCreator` aqui
(OCP) — ni el repositorio ni el controller cambian.
"""

from src.exceptions.custom_exceptions import DatoInvalidoError
from src.factories.medicion_creator import MedicionCreator, PMCreator
from src.models.medicion_calidad_aire import MedicionCalidadAire


class MedicionFactory:
    """Fachada del registro: traduce un `tipo` al creador concreto."""

    _creators: dict[str, MedicionCreator] = {
        "PM": PMCreator(),
    }

    @classmethod
    def registrar(cls, tipo: str, creator: MedicionCreator) -> None:
        """Registra (o reemplaza) el creador asociado a un tipo."""
        cls._creators[tipo] = creator

    @classmethod
    def tipos_disponibles(cls) -> list[str]:
        return sorted(cls._creators)

    @classmethod
    def resolver(cls, tipo: str) -> MedicionCreator:
        """Devuelve el creador concreto correspondiente al `tipo`."""
        creator = cls._creators.get(tipo)
        if creator is None:
            raise DatoInvalidoError(
                f"Tipo de medicion desconocido: {tipo!r}. "
                f"Registrados: {cls.tipos_disponibles()}"
            )
        return creator

    @classmethod
    def crear(cls, tipo: str, **datos) -> MedicionCalidadAire:
        """Instancia una medicion delegando en el creador del tipo."""
        return cls.resolver(tipo).crear(**datos)

    @classmethod
    def desde_dict(cls, data: dict) -> MedicionCalidadAire:
        """Reconstruye una medicion desde su forma serializada (JSON)."""
        tipo = data.get("tipo")
        # Compatibilidad: mediciones antiguas sin 'tipo' pero con campo PM.
        if not tipo and "diametro_aerodinamico" in data:
            tipo = "PM"
        if not tipo:
            raise DatoInvalidoError("Item de medicion sin campo 'tipo'")
        return cls.resolver(tipo).desde_dict(data)
