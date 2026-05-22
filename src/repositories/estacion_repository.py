"""Repositorio para la persistencia de estaciones ambientales en JSON."""

import json
import os
import tempfile
from pathlib import Path

from src.exceptions.custom_exceptions import (
    ArchivoInvalidoError,
    RegistroNoEncontradoError,
)
from src.models.estacion_ambiental import (
    DuplicateEstacionError,
    EstacionAmbiental,
)


class EstacionRepository:
    """Gestiona el CRUD de estaciones usando un archivo JSON local."""

    _RUTA_POR_DEFECTO: Path = (
        Path(__file__).resolve().parents[2] / "data" / "estaciones.json"
    )

    def __init__(self, data_file: str | Path | None = None) -> None:
        self._data_file = Path(data_file) if data_file else self._RUTA_POR_DEFECTO
        self._asegurar_archivo()

    def crear(self, estacion: EstacionAmbiental) -> EstacionAmbiental:
        """Guarda una estacion nueva evitando IDs repetidos."""
        if self.buscar(estacion.id_estacion) is not None:
            raise DuplicateEstacionError(
                f"Ya existe una estacion con id {estacion.id_estacion}"
            )

        data = self._leer_json()
        data.append(estacion.to_dict())
        self._guardar_json(data)
        return estacion

    def listar(self) -> list[EstacionAmbiental]:
        """Retorna todas las estaciones guardadas."""
        return [EstacionAmbiental.from_dict(item) for item in self._leer_json()]

    def buscar(self, id_estacion: str) -> EstacionAmbiental | None:
        """Busca una estacion por su identificador."""
        for item in self._leer_json():
            if item.get("id_estacion") == id_estacion:
                return EstacionAmbiental.from_dict(item)
        return None

    def actualizar(self, estacion_actualizada: EstacionAmbiental) -> EstacionAmbiental:
        """Reemplaza una estacion existente por ID."""
        data = self._leer_json()
        for indice, item in enumerate(data):
            if item.get("id_estacion") == estacion_actualizada.id_estacion:
                data[indice] = estacion_actualizada.to_dict()
                self._guardar_json(data)
                return estacion_actualizada

        raise RegistroNoEncontradoError(
            f"No se encontro estacion con id {estacion_actualizada.id_estacion}"
        )

    def eliminar(self, id_estacion: str) -> bool:
        """Elimina una estacion por su ID."""
        data = self._leer_json()
        filtradas = [item for item in data if item.get("id_estacion") != id_estacion]

        if len(filtradas) == len(data):
            raise RegistroNoEncontradoError(
                f"No se encontro estacion con id {id_estacion}"
            )

        self._guardar_json(filtradas)
        return True

    def _asegurar_archivo(self) -> None:
        """Crea carpeta y archivo si no existen."""
        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self._data_file.exists():
            self._guardar_json([])

    def _leer_json(self) -> list[dict]:
        """Lee la lista de estaciones desde JSON."""
        try:
            with self._data_file.open("r", encoding="utf-8") as archivo:
                data = json.load(archivo)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

        if not isinstance(data, list):
            raise ArchivoInvalidoError("El archivo de estaciones debe contener una lista")

        return data

    def _guardar_json(self, data: list[dict]) -> None:
        """Guarda el contenido usando escritura atomica."""
        self._data_file.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=self._data_file.parent,
            suffix=".tmp",
        ) as temporal:
            json.dump(data, temporal, indent=4, ensure_ascii=False)
            temporal.flush()
            os.fsync(temporal.fileno())
            ruta_temporal = Path(temporal.name)

        os.replace(ruta_temporal, self._data_file)