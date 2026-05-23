"""Modelo de mediciones de calidad del aire (Res. 2254 de 2017).

Clase base abstracta del dominio. Antes existia una `Medicion` generica
encima, pensando en otros tipos de medicion (ruido, agua...). El
observatorio solo trabaja con calidad del aire, asi que se colapso esa
jerarquia: la base ahora es directamente `MedicionCalidadAire` y cada
contaminante criterio (PM10/PM2.5, CO, SO2, NO2, O3...) se modela como
una subclase concreta. Si en el futuro hace falta medir otro dominio,
se extraera una clase base entonces (YAGNI hasta ese momento).
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import ClassVar

from src.exceptions.custom_exceptions import DatoInvalidoError


class MedicionCalidadAire(ABC):
    """Lectura de un contaminante criterio tomada en una estacion.

    Define la identidad y los datos comunes (id, municipio, estacion,
    fecha, valor, origen) y la clasificacion ICA comun a todos los
    contaminantes. Delega en las subclases solo los puntos de corte
    propios de cada contaminante (OCP: agregar uno nuevo no obliga a
    modificar esta clase).
    """

    # Origen del dato
    PENDIENTE: ClassVar[str] = "Pendiente"
    MANUAL: ClassVar[str] = "MANUAL"
    AUTO: ClassVar[str] = "AUTOMATICO"
    ORIGENES_VALIDOS: ClassVar[tuple] = (MANUAL, AUTO)

    # Categorias del Indice de Calidad del Aire (Res. 2254/2017, Tabla 6)
    # https://www.minambiente.gov.co/wp-content/uploads/2021/10/Resolucion-2254-de-2017.pdf
    BUENA: ClassVar[str] = "Buena"
    ACEPTABLE: ClassVar[str] = "Aceptable"
    DANINA_SENSIBLES: ClassVar[str] = "Daniña a la salud de grupos sensibles"
    DANINA: ClassVar[str] = "Daniña a la salud"
    MUY_DANINA: ClassVar[str] = "Muy daniña a la salud"
    PELIGROSA: ClassVar[str] = "Peligrosa"

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

    # ── acceso de solo lectura ───────────────────────────────────────
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

    # ── validacion de invariantes ────────────────────────────────────
    def _validar_datos(self) -> None:
        if not self._id:
            raise DatoInvalidoError("id no puede estar vacio")
        if not self._codigo_dane_municipio:
            raise DatoInvalidoError("codigo_dane_municipio no puede estar vacio")
        if not self._id_estacion:
            raise DatoInvalidoError("id_estacion no puede estar vacio")
        if not isinstance(self._fecha, datetime):
            raise DatoInvalidoError("fecha debe ser datetime")
        if self._medicion is None or not isinstance(self._medicion, (int, float)):
            raise DatoInvalidoError("medicion debe ser numerica")
        if self._medicion <= 0:
            raise DatoInvalidoError("medicion debe ser positiva")
        if self._origen not in self.ORIGENES_VALIDOS:
            raise DatoInvalidoError(
                f"Origen invalido: {self._origen}. "
                f"Validos: {self.ORIGENES_VALIDOS}"
            )

    # ── contrato que deben cumplir las subclases ─────────────────────
    @property
    @abstractmethod
    def _puntos_corte(self) -> list[tuple[float, str]]:
        """Puntos de corte ICA del contaminante.

        Lista ordenada de `(limite_superior, categoria_ICA)`.
        """

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> "MedicionCalidadAire":
        """Reconstruye una instancia desde su representacion serializada."""

    # ── derivados comunes a toda subclase ────────────────────────────
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
        """Solo las mediciones manuales pueden eliminarse del repositorio."""
        return self._origen == self.MANUAL

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "codigo_dane_municipio": self._codigo_dane_municipio,
            "id_estacion": self._id_estacion,
            "fecha": self._fecha.isoformat(),
            "medicion": self._medicion,
            "nivel": self.nivel,
            "origen": self._origen,
            "observacion": self.observacion,
        }


class MedicionCalidadAirePM(MedicionCalidadAire):
    """Material particulado PM10 y PM2.5 (promedio 24h)."""

    PM10: ClassVar[str] = "PM10"
    PM25: ClassVar[str] = "PM2.5"
    DIAMETROS_VALIDOS: ClassVar[tuple] = (PM10, PM25)

    # Puntos de corte del ICA — Res. 2254/2017 Tabla 6 (µg/m³, 24h).
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
        # Se asigna antes del super().__init__ porque _validar_datos
        # (invocado al final del __init__ base) ya lo necesita.
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
