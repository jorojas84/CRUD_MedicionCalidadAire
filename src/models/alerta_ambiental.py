"""Modelo de la entidad AlertaAmbiental."""

from src.exceptions.custom_exceptions import DatoInvalidoError


class AlertaAmbiental:
    """Representa una alerta ambiental registrada en el sistema."""

    NIVELES_VALIDOS = {"Bajo", "Medio", "Alto"}
    ESTADOS_VALIDOS = {"Activa", "Cerrada"}

    def __init__(self, id_alerta, id_medicion, nivel, descripcion, fecha, estado):
        self.id_alerta = (id_alerta or "").strip()
        self.id_medicion = (id_medicion or "").strip()
        self.nivel = (nivel or "").strip()
        self.descripcion = (descripcion or "").strip()
        self.fecha = (fecha or "").strip()
        self.estado = (estado or "").strip()

        self._validar_datos()
        self._aplicar_regla_nivel_alto()

    def _validar_datos(self):
        """Valida los datos obligatorios y valores permitidos."""
        if not self.id_alerta:
            raise DatoInvalidoError("id_alerta no puede estar vacio")

        if not self.id_medicion:
            raise DatoInvalidoError("id_medicion no puede estar vacio")

        if self.nivel not in self.NIVELES_VALIDOS:
            raise DatoInvalidoError("nivel debe ser Bajo, Medio o Alto")

        if not self.descripcion:
            raise DatoInvalidoError("descripcion no puede estar vacia")

        if self.estado not in self.ESTADOS_VALIDOS:
            raise DatoInvalidoError("estado debe ser Activa o Cerrada")

    def _aplicar_regla_nivel_alto(self):
        """Si el nivel es Alto, el estado siempre debe ser Activa."""
        if self.nivel == "Alto":
            self.estado = "Activa"

    def to_dict(self):
        """Convierte el objeto en diccionario para persistencia."""
        return {
            "id_alerta": self.id_alerta,
            "id_medicion": self.id_medicion,
            "nivel": self.nivel,
            "descripcion": self.descripcion,
            "fecha": self.fecha,
            "estado": self.estado,
        }

    @classmethod
    def from_dict(cls, data):
        """Crea una instancia desde un diccionario."""
        return cls(
            id_alerta=data.get("id_alerta", ""),
            id_medicion=data.get("id_medicion", ""),
            nivel=data.get("nivel", ""),
            descripcion=data.get("descripcion", ""),
            fecha=data.get("fecha", ""),
            estado=data.get("estado", ""),
        )
