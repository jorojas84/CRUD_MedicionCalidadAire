"""Controlador para operaciones CRUD de EstacionAmbiental."""

from src.models.estacion_ambiental import EstacionAmbiental
from src.repositories.estacion_repository import EstacionRepository


class EstacionController:
    """Coordina modelo de estaciones y repositorio."""

    def __init__(self, repository=None):
        self.repository = repository or EstacionRepository()

    def crear_estacion(self, id_estacion, nombre, municipio, tipo_estacion, estado):
        estacion = EstacionAmbiental(id_estacion, nombre, municipio, tipo_estacion, estado)
        return self.repository.crear(estacion)

    def listar_estaciones(self):
        return self.repository.listar()

    def buscar_estacion(self, id_estacion):
        return self.repository.buscar(id_estacion)

    def actualizar_estacion(self, id_estacion, nombre, municipio, tipo_estacion, estado):
        estacion = EstacionAmbiental(id_estacion, nombre, municipio, tipo_estacion, estado)
        return self.repository.actualizar(estacion)

    def eliminar_estacion(self, id_estacion):
        return self.repository.eliminar(id_estacion)
