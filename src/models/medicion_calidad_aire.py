"""Modelo de mediciones de calidad del aire (Res. 2254 de 2017).

Define la entidad base abstracta `MedicionCalidadAire` y una subclase
concreta por contaminante criterio. Cada subclase aporta sus propios
puntos de corte ICA; la base se encarga de la validacion comun y de
clasificar el nivel a partir del valor medido.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import ClassVar

from src.exceptions.custom_exceptions import DatoInvalidoError


class MedicionCalidadAire(ABC):
    """Lectura de un contaminante tomada en una estacion."""

    # Origen del dato
    PENDIENTE: ClassVar[str] = "Pendiente"
    MANUAL: ClassVar[str] = "MANUAL"
    AUTO: ClassVar[str] = "AUTOMATICO"
    ORIGENES_VALIDOS: ClassVar[tuple] = (MANUAL, AUTO)

    # Categorias ICA (Res. 2254/2017, Tabla 6).
    BUENA: ClassVar[str] = "Buena"
    ACEPTABLE: ClassVar[str] = "Aceptable"
    DANINA_SENSIBLES: ClassVar[str] = "Daniña a la salud de grupos sensibles"
    DANINA: ClassVar[str] = "Daniña a la salud"
    MUY_DANINA: ClassVar[str] = "Muy daniña a la salud"
    PELIGROSA: ClassVar[str] = "Peligrosa"

    # Identificador del contaminante (lo sobrescribe cada subclase).
    TIPO: ClassVar[str] = ""

    def __init__(
        self,
        id: str,
        codigo_dane_municipio: str,
        id_estacion: str,
        fecha: datetime,
        medicion: float,
        origen: str = AUTO,
    ) -> None:
        self._id = id
        self._codigo_dane_municipio = codigo_dane_municipio
        self._id_estacion = id_estacion
        self._fecha = fecha
        self._medicion = medicion
        self._origen = origen
        self._validar_datos()

    @property
    def id(self) -> str:
        return self._id

    @property
    def codigo_dane_municipio(self) -> str:
        return self._codigo_dane_municipio

    @property
    def id_estacion(self) -> str:
        return self._id_estacion

    @property
    def fecha(self) -> datetime:
        return self._fecha

    @property
    def medicion(self) -> float:
        return self._medicion

    @property
    def origen(self) -> str:
        return self._origen

    def _validar_datos(self) -> None:
        if not self._id:
            raise DatoInvalidoError("id no puede estar vacio")
        if not self._codigo_dane_municipio:
            raise DatoInvalidoError("codigo_dane_municipio no puede estar vacio")
        if not self._id_estacion:
            raise DatoInvalidoError("id_estacion no puede estar vacio")
        if not isinstance(self._fecha, datetime):
            raise DatoInvalidoError("fecha debe ser datetime")
        if not isinstance(self._medicion, (int, float)):
            raise DatoInvalidoError("medicion debe ser numerica")
        if self._medicion <= 0:
            raise DatoInvalidoError("medicion debe ser positiva")
        if self._origen not in self.ORIGENES_VALIDOS:
            raise DatoInvalidoError(
                f"Origen invalido: {self._origen}. "
                f"Validos: {self.ORIGENES_VALIDOS}"
            )

    @property
    @abstractmethod
    def _puntos_corte(self) -> list[tuple[float, str]]:
        """Lista ordenada de (limite_superior, categoria_ICA)."""

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> "MedicionCalidadAire":
        """Reconstruye una instancia desde su forma serializada."""

    @property
    def nivel(self) -> str:
        """Categoria ICA correspondiente al valor medido."""
        for limite, categoria in self._puntos_corte:
            if self._medicion <= limite:
                return categoria
        return self.PELIGROSA

    @property
    def observacion(self) -> str:
        if self._origen == self.MANUAL:
            return "Medicion agregada manualmente"
        return ""

    def es_eliminable(self) -> bool:
        """Las mediciones automaticas son inmutables; solo se borran las manuales."""
        return self._origen == self.MANUAL

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "codigo_dane_municipio": self._codigo_dane_municipio,
            "id_estacion": self._id_estacion,
            "fecha": self._fecha.isoformat(),
            "tipo": type(self).TIPO,
            "medicion": self._medicion,
            "nivel": self.nivel,
            "origen": self._origen,
            "observacion": self.observacion,
        }


class MedicionCalidadAirePM(MedicionCalidadAire):
    """Material particulado PM10 y PM2.5 (promedio 24h)."""

    TIPO: ClassVar[str] = "PM"
    PM10: ClassVar[str] = "PM10"
    PM25: ClassVar[str] = "PM2.5"
    DIAMETROS_VALIDOS: ClassVar[tuple] = (PM10, PM25)

    # Puntos de corte ICA por diametro (Res. 2254/2017, Tabla 6, µg/m³).
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
        codigo_dane_municipio: str,
        id_estacion: str,
        fecha: datetime,
        diametro_aerodinamico: str,
        medicion: float,
        origen: str = MedicionCalidadAire.AUTO,
    ) -> None:
        # Se asigna antes del super().__init__ porque _validar_datos lo necesita.
        self._diametro_aerodinamico = diametro_aerodinamico
        super().__init__(
            id, codigo_dane_municipio, id_estacion, fecha, medicion, origen
        )

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
        return cls(
            id=data["id"],
            codigo_dane_municipio=data["codigo_dane_municipio"],
            id_estacion=data["id_estacion"],
            fecha=datetime.fromisoformat(data["fecha"]),
            diametro_aerodinamico=data["diametro_aerodinamico"],
            medicion=float(data["medicion"]),
            origen=data.get("origen", cls.AUTO),
        )
