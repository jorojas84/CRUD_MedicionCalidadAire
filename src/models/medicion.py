from abc import ABC, abstractmethod
from datetime import datetime
from typing import ClassVar

from src.exceptions.custom_exceptions import DatoInvalidoError


class Medicion(ABC):
    """Lectura ambiental tomada en una estacion de monitoreo.

    Clase base abstracta: define la identidad y los datos comunes a
    cualquier medicion (id, ubicacion, fecha, valor, origen). Delega en
    las subclases la interpretacion del valor (`nivel`) y su descripcion
    (`observacion`), de modo que se puedan agregar nuevos tipos de
    medicion (calidad del aire, ruido, agua...) sin modificar esta clase.
    """

    # Constantes del dominio. No son estado del objeto, por eso van sin
    # prefijo `_` y se exponen como atributos publicos de clase.
    PENDIENTE: ClassVar[str] = "Pendiente"
    MANUAL: ClassVar[str] = "MANUAL"
    AUTO: ClassVar[str] = "AUTOMATICO"
    ORIGENES_VALIDOS: ClassVar[tuple] = (MANUAL, AUTO)

    def __init__(
        self,
        id: str,
        municipio: str,
        estacion: str,
        fecha: datetime,
        medicion: float,
        origen: str = AUTO,
    ) -> None:
        self._id = id
        self._municipio = municipio
        self._estacion = estacion
        self._fecha = fecha
        self._medicion = medicion
        self._origen = origen
        self._validar_datos()

    # ── acceso de solo lectura a los atributos ───────────────────────
    @property
    def id(self) -> str:
        return self._id

    @property
    def municipio(self) -> str:
        return self._municipio

    @property
    def estacion(self) -> str:
        return self._estacion

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
        if not self._municipio:
            raise DatoInvalidoError("municipio no puede estar vacio")
        if not self._estacion:
            raise DatoInvalidoError("estacion no puede estar vacia")
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
    def nivel(self) -> str:
        """Clasificacion del valor segun los criterios propios de la subclase."""

    @property
    @abstractmethod
    def observacion(self) -> str:
        """Texto descriptivo sobre el origen o contexto de la medicion."""

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> "Medicion":
        """Reconstruye una instancia a partir de su representacion serializada."""

    # ── operaciones comunes a todas las mediciones ───────────────────
    def es_eliminable(self) -> bool:
        """Solo las mediciones manuales pueden eliminarse del repositorio."""
        return self._origen == self.MANUAL

    def to_dict(self) -> dict:
        """Serializa la medicion a un dict listo para persistir como JSON."""
        return {
            "id": self._id,
            "municipio": self._municipio,
            "estacion": self._estacion,
            "fecha": self._fecha.isoformat(),
            "medicion": self._medicion,
            "nivel": self.nivel,
            "origen": self._origen,
            "observacion": self.observacion,
        }
