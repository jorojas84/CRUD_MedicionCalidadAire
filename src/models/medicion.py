from datetime import datetime
from typing import ClassVar

from src.exceptions.custom_exceptions import DatoInvalidoError


class Medicion:
    """Representa una medicion de calidad de aire registrada en una estacion."""

    PM10: ClassVar[str] = "PM10"
    PM25: ClassVar[str] = "PM2.5"
    PM1: ClassVar[str] = "PM1"
    PST: ClassVar[str] = "PST"
    DIAMETROS_VALIDOS: ClassVar[tuple] = (PM10, PM25, PM1, PST)

    SANO: ClassVar[str] = "Sano"
    MODERADO: ClassVar[str] = "Moderado"
    PELIGROSO: ClassVar[str] = "Peligroso"
    PENDIENTE: ClassVar[str] = "Pendiente"

    MANUAL: ClassVar[str] = "MANUAL"
    SENSOR: ClassVar[str] = "SENSOR"
    ORIGENES_VALIDOS: ClassVar[tuple] = (MANUAL, SENSOR)

    # Umbrales OMS / Colombia Res. 2254 de 2017 (µg/m³, promedio 24h)
    _UMBRALES: ClassVar[dict] = {
        PM10: (54,  154),
        PM25: (12,  35.4),
        PM1:  (10,  25),
        PST:  (100, 260),
    }

    def __init__(
        self,
        id: str,
        municipio: str,
        estacion: str,
        fecha: datetime,
        diametro_aerodinamico: str,
        medicion: float,
        origen: str = SENSOR,
    ) -> None:
        self.id = id
        self.municipio = municipio
        self.estacion = estacion
        self.fecha = fecha
        self.diametro_aerodinamico = diametro_aerodinamico
        self.medicion = medicion
        self.origen = origen
        self._validar_datos()
        # nivel se asigna despues de validar porque depende de diametro y medicion
        self.nivel = self._calcular_nivel()

    def _validar_datos(self) -> None:
        if not self.id:
            raise DatoInvalidoError("id no puede estar vacio")
        if not self.municipio:
            raise DatoInvalidoError("municipio no puede estar vacio")
        if not self.estacion:
            raise DatoInvalidoError("estacion no puede estar vacia")
        if not self.fecha:
            raise DatoInvalidoError("fecha no puede estar vacia")
        if not isinstance(self.fecha, datetime):
            raise DatoInvalidoError("fecha debe ser datetime")
        if self.medicion is None:
            raise DatoInvalidoError("medicion no puede estar vacia")
        if not isinstance(self.medicion, (int, float)):
            raise DatoInvalidoError("medicion debe ser numerica")
        if self.medicion <= 0:
            raise DatoInvalidoError("medicion debe ser positiva")
        if self.diametro_aerodinamico not in self.DIAMETROS_VALIDOS:
            raise DatoInvalidoError(
                f"Diametro aerodinamico invalido: {self.diametro_aerodinamico}. "
                f"Validos: {self.DIAMETROS_VALIDOS}"
            )
        if self.origen not in self.ORIGENES_VALIDOS:
            raise DatoInvalidoError(
                f"Origen invalido: {self.origen}. Validos: {self.ORIGENES_VALIDOS}"
            )

    def _calcular_nivel(self) -> str:
        """Clasifica la medicion segun umbrales OMS / Res. 2254 de 2017."""
        lim_sano, lim_moderado = self._UMBRALES[self.diametro_aerodinamico]
        if self.medicion <= lim_sano:
            return self.SANO
        if self.medicion <= lim_moderado:
            return self.MODERADO
        return self.PELIGROSO

    def es_eliminable(self) -> bool:
        """Solo las mediciones manuales pueden eliminarse."""
        return self.origen == self.MANUAL

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "municipio": self.municipio,
            "estacion": self.estacion,
            "fecha": self.fecha.isoformat(),
            "diametro_aerodinamico": self.diametro_aerodinamico,
            "medicion": self.medicion,
            "nivel": self.nivel,
            "origen": self.origen,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Medicion":
        # nivel no se restaura: se calcula siempre desde medicion y diametro.
        return cls(
            id=data["id"],
            municipio=data["municipio"],
            estacion=data["estacion"],
            fecha=datetime.fromisoformat(data["fecha"]),
            diametro_aerodinamico=data["diametro_aerodinamico"],
            medicion=float(data["medicion"]),
            origen=data.get("origen", cls.SENSOR),
        )
