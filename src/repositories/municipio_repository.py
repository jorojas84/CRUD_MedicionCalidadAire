import json
import os
from typing import List, Optional
from src.models.municipio import Municipio

class MunicipioRepository:
    def __init__(self, file_path: str = 'data/municipios.json'):
        self.file_path = file_path
        self._asegurar_archivo()

    def _asegurar_archivo(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def obtener_todos(self) -> List[Municipio]:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            return [Municipio.from_dict(d) for d in datos]

    def guardar_todos(self, municipios: List[Municipio]) -> None:
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump([m.to_dict() for m in municipios], f, indent=4)

    def crear(self, municipio: Municipio) -> None:
        municipios = self.obtener_todos()
        municipios.append(municipio)
        self.guardar_todos(municipios)

    def obtener_por_codigo(self, codigo_dane: str) -> Optional[Municipio]:
        municipios = self.obtener_todos()
        for m in municipios:
            if m.codigo_dane == codigo_dane:
                return m
        return None

    def actualizar(self, municipio_actualizado: Municipio) -> bool:
        municipios = self.obtener_todos()
        for i, m in enumerate(municipios):
            if m.codigo_dane == municipio_actualizado.codigo_dane:
                municipios[i] = municipio_actualizado
                self.guardar_todos(municipios)
                return True
        return False

    def eliminar(self, codigo_dane: str) -> bool:
        municipios = self.obtener_todos()
        municipios_filtrados = [m for m in municipios if m.codigo_dane != codigo_dane]
        if len(municipios) != len(municipios_filtrados):
            self.guardar_todos(municipios_filtrados)
            return True
        return False