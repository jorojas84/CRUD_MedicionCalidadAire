"""Controlador para operaciones CRUD de MedicionCalidadAire."""

from src.models.medicion_calidad_aire import MedicionCalidadAire
from src.repositories.medicion_calidad_aire_repository import MedicionCalidadAireRepository


class MedicionCalidadAireController:
    """Coordina modelo de mediciones y repositorio."""

    def __init__(self, repository=None):
        self.repository = repository or MedicionCalidadAireRepository()

    def crear_medicion(self, id_medicion, id_estacion, contaminante, valor, unidad, fecha):
        medicion = MedicionCalidadAire(id_medicion, id_estacion, contaminante, valor, unidad, fecha)
        return self.repository.crear(medicion)

    def listar_mediciones(self):
        return self.repository.listar()

    def buscar_medicion(self, id_medicion):
        return self.repository.buscar_por_id(id_medicion)

    def actualizar_medicion(self, id_medicion, id_estacion, contaminante, valor, unidad, fecha):
        medicion = MedicionCalidadAire(id_medicion, id_estacion, contaminante, valor, unidad, fecha)
        return self.repository.actualizar(id_medicion, medicion)

    def eliminar_medicion(self, id_medicion):
        return self.repository.eliminar(id_medicion)
