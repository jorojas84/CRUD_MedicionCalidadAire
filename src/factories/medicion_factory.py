"""Factory de mediciones de calidad del aire.

Centraliza la relacion `tipo -> clase concreta` para que tanto el
repositorio (al deserializar el JSON) como el controller (al crear una
medicion nueva) usen el mismo registro. Para agregar un contaminante
nuevo basta con registrar su subclase aqui (OCP).
"""

from src.exceptions.custom_exceptions import DatoInvalidoError
from src.models.medicion_calidad_aire import (
    MedicionCalidadAire,
    MedicionCalidadAirePM,
)


class MedicionFactory:
    """Factory unica para mediciones de calidad del aire."""

    _tipos: dict[str, type[MedicionCalidadAire]] = {
        "PM": MedicionCalidadAirePM,
    }

    @classmethod
    def registrar(cls, tipo: str, clase: type[MedicionCalidadAire]) -> None:
        """Registra (o reemplaza) la clase concreta asociada a un tipo."""
        cls._tipos[tipo] = clase

    @classmethod
    def tipos_disponibles(cls) -> list[str]:
        return sorted(cls._tipos)

    @classmethod
    def resolver(cls, tipo: str) -> type[MedicionCalidadAire]:
        """Devuelve la subclase concreta correspondiente al `tipo`."""
        clase = cls._tipos.get(tipo)
        if clase is None:
            raise DatoInvalidoError(
                f"Tipo de medicion desconocido: {tipo!r}. "
                f"Registrados: {cls.tipos_disponibles()}"
            )
        return clase

    @classmethod
    def crear(cls, tipo: str, **datos) -> MedicionCalidadAire:
        """Instancia una medicion a partir de campos sueltos."""
        return cls.resolver(tipo)(**datos)

    @classmethod
    def desde_dict(cls, data: dict) -> MedicionCalidadAire:
        """Reconstruye una medicion desde su forma serializada (JSON)."""
        tipo = data.get("tipo")
        # Compatibilidad: mediciones antiguas sin 'tipo' pero con campo PM.
        if not tipo and "diametro_aerodinamico" in data:
            tipo = "PM"
        if not tipo:
            raise DatoInvalidoError("Item de medicion sin campo 'tipo'")
        return cls.resolver(tipo).from_dict(data)
