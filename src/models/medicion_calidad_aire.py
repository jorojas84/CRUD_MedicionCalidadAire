"""Modelo de la entidad MedicionCalidadAire."""

from src.exceptions.custom_exceptions import DatoInvalidoError


class MedicionCalidadAire:
    """Representa una medicion de calidad del aire."""

    NIVELES_VALIDOS = {"Bajo", "Medio", "Alto"}

    def __init__(self, id_medicion, id_estacion, contaminante, valor, unidad, fecha):
        self.id_medicion = (id_medicion or "").strip()
        self.id_estacion = (id_estacion or "").strip()
        self.contaminante = (contaminante or "").strip()
        self.unidad = (unidad or "").strip()
        self.fecha = (fecha or "").strip()
        self.valor = valor

        self._validar_datos()
        self.nivel = self._calcular_nivel_alerta()

    def _validar_datos(self):
        if not self.id_medicion:
            raise DatoInvalidoError("id_medicion no puede estar vacio")
        if not self.id_estacion:
            raise DatoInvalidoError("id_estacion no puede estar vacio")
        if not self.contaminante:
            raise DatoInvalidoError("contaminante no puede estar vacio")
        if self.valor is None or not isinstance(self.valor, (int, float)):
            raise DatoInvalidoError("valor debe ser numerico")
        if self.valor < 0:
            raise DatoInvalidoError("valor no puede ser negativo")
        if not self.unidad:
            raise DatoInvalidoError("unidad no puede estar vacia")

    def _calcular_nivel_alerta(self):
        if self.valor < 50:
            return "Bajo"
        if self.valor <= 100:
            return "Medio"
        return "Alto"

    def to_dict(self):
        return {
            "id_medicion": self.id_medicion,
            "id_estacion": self.id_estacion,
            "contaminante": self.contaminante,
            "valor": self.valor,
            "unidad": self.unidad,
            "fecha": self.fecha,
            "nivel": self.nivel,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id_medicion=data.get("id_medicion", ""),
            id_estacion=data.get("id_estacion", ""),
            contaminante=data.get("contaminante", ""),
            valor=data.get("valor", 0),
            unidad=data.get("unidad", ""),
            fecha=data.get("fecha", ""),
        )
