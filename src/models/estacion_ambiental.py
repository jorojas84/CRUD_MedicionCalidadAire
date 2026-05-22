"""Modelo de la entidad EstacionAmbiental."""


class EstacionAmbiental:
    """Representa una estacion ambiental."""

    def __init__(self, id_estacion, nombre, municipio, tipo_estacion, estado):
        # Datos de la estacion
        self.id_estacion = (id_estacion or "").strip()
        self.nombre = (nombre or "").strip()
        self.municipio = (municipio or "").strip()
        self.tipo_estacion = (tipo_estacion or "").strip()
        self.estado = (estado or "").strip()

    def to_dict(self):
        """Convierte el objeto a diccionario."""
        return {
            "id_estacion": self.id_estacion,
            "nombre": self.nombre,
            "municipio": self.municipio,
            "tipo_estacion": self.tipo_estacion,
            "estado": self.estado,
        }

    @classmethod
    def from_dict(cls, data):
        """Crea una estacion desde un diccionario."""
        return cls(
            id_estacion=data.get("id_estacion", ""),
            nombre=data.get("nombre", ""),
            municipio=data.get("municipio", ""),
            tipo_estacion=data.get("tipo_estacion", ""),
            estado=data.get("estado", ""),
        )