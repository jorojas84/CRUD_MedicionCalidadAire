"""Repositorio JSON para CRUD de mediciones de calidad del aire."""

import json
from pathlib import Path

from src.exceptions.custom_exceptions import RegistroDuplicadoError, RegistroNoEncontradoError
from src.models.medicion_calidad_aire import MedicionCalidadAire


class MedicionCalidadAireRepository:
    """Gestiona persistencia de mediciones en JSON."""

    def __init__(self, data_file=None):
        default_path = Path(__file__).resolve().parents[2] / "data" / "mediciones.json"
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

    def crear(self, medicion):
        if self.buscar_por_id(medicion.id_medicion):
            raise RegistroDuplicadoError(f"Ya existe una medicion con id {medicion.id_medicion}")
        data = self._leer_json()
        data.append(medicion.to_dict())
        self._guardar_json(data)
        return medicion

    def listar(self):
        return [MedicionCalidadAire.from_dict(item) for item in self._leer_json()]

    def buscar_por_id(self, id_medicion):
        for item in self._leer_json():
            if item.get("id_medicion") == id_medicion:
                return MedicionCalidadAire.from_dict(item)
        return None

    def actualizar(self, id_medicion, medicion_actualizada):
        data = self._leer_json()
        for index, item in enumerate(data):
            if item.get("id_medicion") == id_medicion:
                data[index] = medicion_actualizada.to_dict()
                self._guardar_json(data)
                return medicion_actualizada
        raise RegistroNoEncontradoError(f"No se encontro medicion con id {id_medicion}")

    def eliminar(self, id_medicion):
        data = self._leer_json()
        filtradas = [item for item in data if item.get("id_medicion") != id_medicion]
        if len(filtradas) == len(data):
            raise RegistroNoEncontradoError(f"No se encontro medicion con id {id_medicion}")
        self._guardar_json(filtradas)
        return True
