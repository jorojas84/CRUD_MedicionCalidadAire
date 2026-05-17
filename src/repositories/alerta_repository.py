"""Repositorio para persistencia de alertas en JSON."""

import json
from pathlib import Path

from src.exceptions.custom_exceptions import RegistroDuplicadoError, RegistroNoEncontradoError
from src.models.alerta_ambiental import AlertaAmbiental


class AlertaRepository:
    """Gestiona el CRUD de alertas usando un archivo JSON."""

    def __init__(self, data_file=None):
        default_path = Path(__file__).resolve().parents[2] / "data" / "alertas.json"
        self.data_file = Path(data_file) if data_file else default_path
        self._asegurar_archivo()

    def _asegurar_archivo(self):
        """Crea carpeta/archivo de datos si no existen."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._guardar_json([])

    def _leer_json(self):
        """Lee la lista de alertas desde JSON."""
        try:
            with self.data_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _guardar_json(self, data):
        """Guarda una lista de alertas en JSON."""
        with self.data_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def crear_alerta(self, alerta):
        """Crea una nueva alerta verificando ID unico."""
        if self.buscar_alerta_por_id(alerta.id_alerta):
            raise RegistroDuplicadoError(f"Ya existe una alerta con id {alerta.id_alerta}")

        data = self._leer_json()
        data.append(alerta.to_dict())
        self._guardar_json(data)
        return alerta

    def listar_alertas(self):
        """Retorna todas las alertas del archivo."""
        data = self._leer_json()
        return [AlertaAmbiental.from_dict(item) for item in data]

    def buscar_alerta_por_id(self, id_alerta):
        """Busca una alerta por su identificador."""
        data = self._leer_json()
        for item in data:
            if item.get("id_alerta") == id_alerta:
                return AlertaAmbiental.from_dict(item)
        return None

    def actualizar_alerta(self, id_alerta, nueva_alerta):
        """Actualiza una alerta existente por ID."""
        data = self._leer_json()
        for index, item in enumerate(data):
            if item.get("id_alerta") == id_alerta:
                data[index] = nueva_alerta.to_dict()
                self._guardar_json(data)
                return nueva_alerta
        raise RegistroNoEncontradoError(f"No se encontro alerta con id {id_alerta}")

    def eliminar_alerta(self, id_alerta):
        """Elimina una alerta por ID."""
        data = self._leer_json()
        filtradas = [item for item in data if item.get("id_alerta") != id_alerta]

        if len(filtradas) == len(data):
            raise RegistroNoEncontradoError(f"No se encontro alerta con id {id_alerta}")

        self._guardar_json(filtradas)
        return True
