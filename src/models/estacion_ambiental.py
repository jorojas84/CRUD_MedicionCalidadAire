"""Modelo de la entidad EstacionAmbiental."""

from __future__ import annotations

from typing import Any, ClassVar


class EstacionError(ValueError):
    """Error base del modelo de estacion."""


class EstacionValidationError(EstacionError):
    """Error para datos invalidos de estacion."""


class DuplicateEstacionError(EstacionError):
    """Error para IDs de estacion duplicados."""


class EstacionAmbiental:
    """Representa una estacion ambiental."""

    ESTADOS_VALIDOS: ClassVar[set[str]] = {"Activa", "Inactiva"}

    def __init__(
        self,
        id_estacion: str,
        nombre: str,
        municipio: str,
        tipo_estacion: str,
        estado: str,
    ) -> None:
        self.id_estacion: str = self._normalizar(id_estacion)
        self.nombre: str = self._normalizar(nombre)
        self.municipio: str = self._normalizar(municipio)
        self.tipo_estacion: str = self._normalizar(tipo_estacion)
        self.estado: str = self._normalizar(estado)
        self._validar()

    @staticmethod
    def _normalizar(valor: str | None) -> str:
        return (valor or "").strip()

    def _validar(self) -> None:
        if not self.id_estacion:
            raise EstacionValidationError("id_estacion es obligatorio")
        if not self.nombre:
            raise EstacionValidationError("nombre es obligatorio")
        if not self.municipio:
            raise EstacionValidationError("municipio es obligatorio")
        if self.estado not in self.ESTADOS_VALIDOS:
            raise EstacionValidationError(
                "estado debe ser exactamente 'Activa' o 'Inactiva'"
            )

    def to_dict(self) -> dict[str, str]:
        return {
            "id_estacion": self.id_estacion,
            "nombre": self.nombre,
            "municipio": self.municipio,
            "tipo_estacion": self.tipo_estacion,
            "estado": self.estado,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EstacionAmbiental":
        if not isinstance(data, dict):
            raise EstacionValidationError("data debe ser un diccionario")

        return cls(
            id_estacion=data.get("id_estacion", ""),
            nombre=data.get("nombre", ""),
            municipio=data.get("municipio", ""),
            tipo_estacion=data.get("tipo_estacion", ""),
            estado=data.get("estado", ""),
        )
