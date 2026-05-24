"""Persistencia de mediciones en un archivo JSON local."""

import json
from abc import ABC, abstractmethod
from pathlib import Path

from src.exceptions.custom_exceptions import (
    ArchivoInvalidoError,
    DatoInvalidoError,
    RegistroDuplicadoError,
    RegistroNoEncontradoError,
)
from src.factories.medicion_factory import MedicionFactory
from src.models.medicion_calidad_aire import MedicionCalidadAire


def _deserializar_medicion(item: dict) -> MedicionCalidadAire:
    """Reconstruye una medicion desde un dict del JSON."""
    try:
        return MedicionFactory.desde_dict(item)
    except DatoInvalidoError as e:
        raise ArchivoInvalidoError(str(e)) from e


class IMedicionRepository(ABC):
    """Contrato CRUD para la persistencia de mediciones."""

    @abstractmethod
    def crear_medicion(self, medicion: MedicionCalidadAire) -> MedicionCalidadAire: ...

    @abstractmethod
    def listar_mediciones(self) -> list[MedicionCalidadAire]: ...

    @abstractmethod
    def buscar_medicion_por_id(self, medicion_id: str) -> MedicionCalidadAire | None: ...

    @abstractmethod
    def actualizar_medicion(self, medicion: MedicionCalidadAire) -> MedicionCalidadAire: ...

    @abstractmethod
    def eliminar_medicion(self, medicion_id: str) -> bool: ...


class MedicionRepository(IMedicionRepository):
    """Repositorio respaldado por un archivo JSON en `data/mediciones.json`."""

    _RUTA_POR_DEFECTO: Path = (
        Path(__file__).resolve().parents[2] / "data" / "mediciones.json"
    )

    def __init__(self, data_file: str | Path | None = None) -> None:
        self._data_file = Path(data_file) if data_file else self._RUTA_POR_DEFECTO
        self._asegurar_archivo()

    def crear_medicion(self, medicion: MedicionCalidadAire) -> MedicionCalidadAire:
        if self.buscar_medicion_por_id(medicion.id) is not None:
            raise RegistroDuplicadoError(
                f"Ya existe una medicion con id {medicion.id}"
            )
        data = self._leer_json()
        data.append(medicion.to_dict())
        self._guardar_json(data)
        return medicion

    def listar_mediciones(self) -> list[MedicionCalidadAire]:
        return [_deserializar_medicion(item) for item in self._leer_json()]

    def buscar_medicion_por_id(self, medicion_id: str) -> MedicionCalidadAire | None:
        for item in self._leer_json():
            if item.get("id") == medicion_id:
                return _deserializar_medicion(item)
        return None

    def actualizar_medicion(self, medicion: MedicionCalidadAire) -> MedicionCalidadAire:
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
        """Elimina la medicion solo si su origen lo permite."""
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
        data = [item for item in self._leer_json() if item.get("id") != medicion_id]
        self._guardar_json(data)
        return True

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
