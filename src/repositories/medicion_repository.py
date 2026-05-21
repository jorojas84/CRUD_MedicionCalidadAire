"""Persistencia de mediciones en un archivo JSON.

Sigue el patron Repository: oculta el medio de almacenamiento detras de
una interfaz (`IMedicionRepository`) para que el resto del sistema (en
particular el Controller de MVC) dependa de la abstraccion y no del
mecanismo concreto de persistencia (DIP).
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path

from src.exceptions.custom_exceptions import (
    ArchivoInvalidoError,
    DatoInvalidoError,
    RegistroDuplicadoError,
    RegistroNoEncontradoError,
)
from src.models.medicion import Medicion
from src.models.medicion_calidad_aire import MedicionCalidadAirePM


# Registro de tipos concretos de medicion soportados al deserializar.
# Para sumar un contaminante nuevo (CO, SO2, NO2, O3...) basta con
# registrarlo aqui sin tocar el resto del repositorio (OCP).
_TIPOS_MEDICION: dict[str, type[Medicion]] = {
    "PM": MedicionCalidadAirePM,
}


def _deserializar_medicion(item: dict) -> Medicion:
    """Crea la subclase concreta de `Medicion` que corresponda al dict."""
    # Compatibilidad: si el JSON no trae `tipo`, lo inferimos por sus campos.
    tipo = item.get("tipo")
    if not tipo and "diametro_aerodinamico" in item:
        tipo = "PM"
    cls = _TIPOS_MEDICION.get(tipo) if tipo else None
    if cls is None:
        raise ArchivoInvalidoError(f"Tipo de medicion desconocido: {tipo!r}")
    return cls.from_dict(item)


class IMedicionRepository(ABC):
    """Contrato CRUD que debe cumplir cualquier implementacion de persistencia.

    El Controller depende de esta interfaz, no de una implementacion
    concreta (DIP), lo que permite intercambiar el backend (JSON, SQLite,
    HTTP, en memoria para tests...) sin modificar las capas superiores.
    """

    @abstractmethod
    def crear_medicion(self, medicion: Medicion) -> Medicion: ...

    @abstractmethod
    def listar_mediciones(self) -> list[Medicion]: ...

    @abstractmethod
    def buscar_medicion_por_id(self, medicion_id: str) -> Medicion | None: ...

    @abstractmethod
    def actualizar_medicion(self, medicion: Medicion) -> Medicion: ...

    @abstractmethod
    def eliminar_medicion(self, medicion_id: str) -> bool: ...


class MedicionRepository(IMedicionRepository):
    """Implementacion del repositorio sobre un archivo JSON local."""

    _RUTA_POR_DEFECTO: Path = (
        Path(__file__).resolve().parents[2] / "data" / "mediciones.json"
    )

    def __init__(self, data_file: str | Path | None = None) -> None:
        self._data_file = Path(data_file) if data_file else self._RUTA_POR_DEFECTO
        self._asegurar_archivo()

    # ── operaciones del repositorio ──────────────────────────────────
    def crear_medicion(self, medicion: Medicion) -> Medicion:
        if self.buscar_medicion_por_id(medicion.id) is not None:
            raise RegistroDuplicadoError(
                f"Ya existe una medicion con id {medicion.id}"
            )
        data = self._leer_json()
        data.append(medicion.to_dict())
        self._guardar_json(data)
        return medicion

    def listar_mediciones(self) -> list[Medicion]:
        return [_deserializar_medicion(item) for item in self._leer_json()]

    def buscar_medicion_por_id(self, medicion_id: str) -> Medicion | None:
        for item in self._leer_json():
            if item.get("id") == medicion_id:
                return _deserializar_medicion(item)
        return None

    def actualizar_medicion(self, medicion: Medicion) -> Medicion:
        data = self._leer_json()
        for idx, item in enumerate(data):
            if item.get("id") == medicion.id:
                data[idx] = medicion.to_dict()
                self._guardar_json(data)
                return medicion
        raise RegistroNoEncontradoError(
            f"No se encontro medicion con id {medicion.id}"
        )

    def eliminar_medicion(self, medicion_id: str) -> bool:
        """Elimina la medicion solo si su origen lo permite (regla del modelo)."""
        medicion = self.buscar_medicion_por_id(medicion_id)
        if medicion is None:
            raise RegistroNoEncontradoError(
                f"No se encontro medicion con id {medicion_id}"
            )
        if not medicion.es_eliminable():
            raise DatoInvalidoError(
                "Solo se pueden eliminar mediciones MANUALES. "
                f"Origen: {medicion.origen}"
            )
        data = [
            item for item in self._leer_json()
            if item.get("id") != medicion_id
        ]
        self._guardar_json(data)
        return True

    # ── E/S del archivo JSON (detalle de implementacion) ─────────────
    def _asegurar_archivo(self) -> None:
        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self._data_file.exists():
            self._guardar_json([])

    def _leer_json(self) -> list[dict]:
        try:
            with self._data_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
        return data if isinstance(data, list) else []

    def _guardar_json(self, data: list[dict]) -> None:
        with self._data_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
