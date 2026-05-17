"""Controlador para operaciones de AlertaAmbiental."""

from src.models.alerta_ambiental import AlertaAmbiental
from src.repositories.alerta_repository import AlertaRepository


class AlertaController:
    """Coordina la logica entre main y el repositorio."""

    def __init__(self, repository=None):
        self.repository = repository or AlertaRepository()

    def crear_alerta(self, id_alerta, id_medicion, nivel, descripcion, fecha, estado):
        alerta = AlertaAmbiental(id_alerta, id_medicion, nivel, descripcion, fecha, estado)
        return self.repository.crear_alerta(alerta)

    def listar_alertas(self):
        return self.repository.listar_alertas()

    def buscar_alerta(self, id_alerta):
        return self.repository.buscar_alerta_por_id(id_alerta)

    def actualizar_alerta(self, id_alerta, id_medicion, nivel, descripcion, fecha, estado):
        alerta = AlertaAmbiental(id_alerta, id_medicion, nivel, descripcion, fecha, estado)
        return self.repository.actualizar_alerta(id_alerta, alerta)

    def eliminar_alerta(self, id_alerta):
        return self.repository.eliminar_alerta(id_alerta)
