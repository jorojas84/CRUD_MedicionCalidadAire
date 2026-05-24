"""Modelo de la entidad Municipio."""

from src.exceptions.municipio_exceptions import DatosMunicipioInvalidosError


class Municipio:
    """Representa un municipio del sistema."""

    ESTADOS_VALIDOS = {"Activo", "Inactivo"}

    def __init__(self, id_municipio, nombre, departamento, region, estado):
        self.id_municipio = (id_municipio or "").strip()
        self.nombre = (nombre or "").strip()
        self.departamento = (departamento or "").strip()
        self.region = (region or "").strip()
        self.estado = (estado or "").strip()
        self._validar()

    def _validar(self):
        if not self.id_municipio:
            raise DatosMunicipioInvalidosError("id_municipio no puede estar vacio")
        if not self.nombre:
            raise DatosMunicipioInvalidosError("nombre no puede estar vacio")
        if not self.departamento:
            raise DatosMunicipioInvalidosError("departamento no puede estar vacio")
        if not self.region:
            raise DatosMunicipioInvalidosError("region no puede estar vacia")
        if self.estado not in self.ESTADOS_VALIDOS:
            raise DatosMunicipioInvalidosError("estado debe ser Activo o Inactivo")

    def to_dict(self):
        return {
            "id_municipio": self.id_municipio,
            "nombre": self.nombre,
            "departamento": self.departamento,
            "region": self.region,
            "estado": self.estado,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id_municipio=data.get("id_municipio", ""),
            nombre=data.get("nombre", ""),
            departamento=data.get("departamento", ""),
            region=data.get("region", ""),
            estado=data.get("estado", ""),
        )
