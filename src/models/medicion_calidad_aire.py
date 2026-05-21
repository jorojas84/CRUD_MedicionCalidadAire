from abc import abstractmethod
from datetime import datetime
from typing import ClassVar

from src.exceptions.custom_exceptions import DatoInvalidoError
from src.models.medicion import Medicion


class MedicionCalidadAire(Medicion):
    """Medicion de calidad del aire segun la Res. 2254 de 2017 (Tabla 6).

    Clase abstracta. Cada contaminante criterio (PM10/PM2.5, CO, SO2,
    NO2, O3...) se implementa como una subclase concreta que declara
    sus propios puntos de corte del ICA. La clasificacion en categorias
    ICA es comun a todas las subclases y vive aqui (OCP: agregar un
    contaminante nuevo no requiere modificar esta clase).
    """

    # Categorias del Indice de Calidad del Aire (Res. 2254 de 2017, Tabla 6).
    BUENA: ClassVar[str] = "Buena"
    ACEPTABLE: ClassVar[str] = "Aceptable"
    DANINA_SENSIBLES: ClassVar[str] = "Daniña a la salud de grupos sensibles"
    DANINA: ClassVar[str] = "Daniña a la salud"
    MUY_DANINA: ClassVar[str] = "Muy daniña a la salud"
    PELIGROSA: ClassVar[str] = "Peligrosa"

    @property
    @abstractmethod
    def _puntos_corte(self) -> list[tuple[float, str]]:
        """Puntos de corte del ICA del contaminante.

        Lista ordenada de tuplas `(limite_superior, categoria_ICA)`.
        """

    @property
    def nivel(self) -> str:
        """Categoria ICA correspondiente al valor medido."""
        for limite, categoria in self._puntos_corte:
            if self.medicion <= limite:
                return categoria
        # Concentraciones por encima del ultimo punto de corte siguen
        # siendo peligrosas segun la regulacion.
        return self.PELIGROSA

    @property
    def observacion(self) -> str:
        if self.origen == self.MANUAL:
            return "Medicion agregada manualmente"
        return ""


class MedicionCalidadAirePM(MedicionCalidadAire):
    """Medicion de material particulado PM10 y PM2.5 (promedio 24h)."""

    PM10: ClassVar[str] = "PM10"
    PM25: ClassVar[str] = "PM2.5"
    DIAMETROS_VALIDOS: ClassVar[tuple] = (PM10, PM25)

    # Puntos de corte del ICA segun Tabla 6 de la Res. 2254 de 2017
    # (concentracion en µg/m³, promedio 24h).
    _PUNTOS_CORTE: ClassVar[dict] = {
        PM10: [
            (54, MedicionCalidadAire.BUENA),
            (154, MedicionCalidadAire.ACEPTABLE),
            (254, MedicionCalidadAire.DANINA_SENSIBLES),
            (354, MedicionCalidadAire.DANINA),
            (424, MedicionCalidadAire.MUY_DANINA),
            (604, MedicionCalidadAire.PELIGROSA),
        ],
        PM25: [
            (12, MedicionCalidadAire.BUENA),
            (37, MedicionCalidadAire.ACEPTABLE),
            (55, MedicionCalidadAire.DANINA_SENSIBLES),
            (150, MedicionCalidadAire.DANINA),
            (250, MedicionCalidadAire.MUY_DANINA),
            (500, MedicionCalidadAire.PELIGROSA),
        ],
    }

    def __init__(
        self,
        id: str,
        municipio: str,
        estacion: str,
        fecha: datetime,
        diametro_aerodinamico: str,
        medicion: float,
        origen: str = Medicion.AUTO,
    ) -> None:
        # Se asigna antes de super().__init__ porque _validar_datos
        # (invocado al final del __init__ base) ya lo necesita.
        self._diametro_aerodinamico = diametro_aerodinamico
        super().__init__(id, municipio, estacion, fecha, medicion, origen)

    @property
    def diametro_aerodinamico(self) -> str:
        return self._diametro_aerodinamico

    def _validar_datos(self) -> None:
        super()._validar_datos()
        if self._diametro_aerodinamico not in self.DIAMETROS_VALIDOS:
            raise DatoInvalidoError(
                f"Diametro aerodinamico invalido: {self._diametro_aerodinamico}. "
                f"Validos: {self.DIAMETROS_VALIDOS}"
            )

    @property
    def _puntos_corte(self) -> list[tuple[float, str]]:
        return self._PUNTOS_CORTE[self._diametro_aerodinamico]

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["diametro_aerodinamico"] = self._diametro_aerodinamico
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "MedicionCalidadAirePM":
        # `nivel` y `observacion` no se restauran: siempre se derivan.
        return cls(
            id=data["id"],
            municipio=data["municipio"],
            estacion=data["estacion"],
            fecha=datetime.fromisoformat(data["fecha"]),
            diametro_aerodinamico=data["diametro_aerodinamico"],
            medicion=float(data["medicion"]),
            origen=data.get("origen", cls.AUTO),
        )
