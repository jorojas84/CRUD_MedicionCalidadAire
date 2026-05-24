"""Controlador de Municipio para coordinar modelo y repositorio."""

from src.exceptions.municipio_exceptions import (
    DatosMunicipioInvalidosError,
    MunicipioNoEncontradoError,
    ReglaNegocioMunicipioError,
)
from src.models.municipio import Municipio
from src.repositories.municipio_repository import MunicipioRepository


from src.services.email_service import EmailService

class MunicipioControllerNotificador:
    """
    Implementa el patrón GoF Decorator.
    Envuelve el MunicipioController original para añadir notificaciones.
    """

    def __init__(self, controlador_base):
        self._controlador_base = controlador_base
        self._email_service = EmailService()

    def crear_municipio(self, id_municipio, nombre, departamento, region, estado):
        municipio = self._controlador_base.crear_municipio(
            id_municipio, nombre, departamento, region, estado
        )
        
        mensaje = f"Se ha registrado exitosamente el municipio {nombre} ({id_municipio})."
        self._email_service.enviar_notificacion("Inserción", mensaje)
        
        return municipio

    def actualizar_municipio(self, id_municipio, nombre, departamento, region, estado):
        municipio = self._controlador_base.actualizar_municipio(
            id_municipio, nombre, departamento, region, estado
        )
        
        mensaje = f"Se han modificado los datos del municipio {nombre} ({id_municipio})."
        self._email_service.enviar_notificacion("Modificación", mensaje)
        
        return municipio

    def listar_municipios(self):
        return self._controlador_base.listar_municipios()

    def buscar_municipio(self, id_municipio):
        return self._controlador_base.buscar_municipio(id_municipio)

    def eliminar_municipio(self, id_municipio):
        return self._controlador_base.eliminar_municipio(id_municipio)