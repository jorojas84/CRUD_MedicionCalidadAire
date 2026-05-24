"""Controlador de Municipio para coordinar modelo y repositorio."""

from src.exceptions.municipio_exceptions import (
    DatosMunicipioInvalidosError,
    MunicipioNoEncontradoError,
    ReglaNegocioMunicipioError,
)
from src.models.municipio import Municipio
from src.repositories.municipio_repository import MunicipioRepository


class MunicipioController:
    """Implementa logica de negocio de municipios."""

    def __init__(self, repository=None):
        self.repository = repository or MunicipioRepository()

    def crear_municipio(self, id_municipio, nombre, departamento, region, estado):
        existente = self.repository.buscar_por_id(id_municipio)
        if existente is not None:
            raise ReglaNegocioMunicipioError(
                f"No se puede registrar dos veces el municipio {id_municipio}"
            )
        municipio = Municipio(id_municipio, nombre, departamento, region, estado)
        return self.repository.crear(municipio)

    def listar_municipios(self):
        return self.repository.listar()

    def buscar_municipio(self, id_municipio):
        municipio = self.repository.buscar_por_id(id_municipio)
        if municipio is None:
            raise MunicipioNoEncontradoError(
                f"No existe municipio con id {id_municipio}"
            )
        return municipio

    def actualizar_municipio(self, id_municipio, nombre, departamento, region, estado):
        _ = self.buscar_municipio(id_municipio)
        municipio = Municipio(id_municipio, nombre, departamento, region, estado)
        actualizado = self.repository.actualizar(id_municipio, municipio)
        if actualizado is None:
            raise MunicipioNoEncontradoError(
                f"No existe municipio con id {id_municipio}"
            )
        return actualizado

    def eliminar_municipio(self, id_municipio):
        municipio = self.buscar_municipio(id_municipio)
        if municipio.estado == "Activo":
            raise ReglaNegocioMunicipioError(
                "No se puede eliminar un municipio en estado Activo"
            )

        eliminado = self.repository.eliminar(id_municipio)
        if not eliminado:
            raise MunicipioNoEncontradoError(
                f"No existe municipio con id {id_municipio}"
            )
        return True
