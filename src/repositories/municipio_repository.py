"""Repositorio JSON para CRUD de Municipios."""

import json
from pathlib import Path

from src.models.municipio import Municipio


class MunicipioRepository:
    """Gestiona persistencia de municipios en archivo JSON."""

    def __init__(self, data_file=None):
        default_path = Path(__file__).resolve().parents[2] / "data" / "municipios.json"
        self.data_file = Path(data_file) if data_file else default_path
        self._asegurar_archivo()

    def _asegurar_archivo(self):
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._guardar_json([])

    def _leer_json(self):
        try:
            with self.data_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _guardar_json(self, data):
        with self.data_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def crear(self, municipio):
        data = self._leer_json()
        data.append(municipio.to_dict())
        self._guardar_json(data)
        return municipio

    def listar(self):
        return [Municipio.from_dict(item) for item in self._leer_json()]

    def buscar_por_id(self, id_municipio):
        for item in self._leer_json():
            if item.get("id_municipio") == id_municipio:
                return Municipio.from_dict(item)
        return None

    def actualizar(self, id_municipio, municipio_actualizado):
        data = self._leer_json()
        for index, item in enumerate(data):
            if item.get("id_municipio") == id_municipio:
                data[index] = municipio_actualizado.to_dict()
                self._guardar_json(data)
                return municipio_actualizado
        return None

    def eliminar(self, id_municipio):
        data = self._leer_json()
        filtrados = [item for item in data if item.get("id_municipio") != id_municipio]
        if len(filtrados) == len(data):
            return False
        self._guardar_json(filtrados)
        return True
