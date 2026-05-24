"""Creadores de mediciones (patron Factory Method de GoF).

Define la jerarquia paralela a la de productos (`MedicionCalidadAire`):
una clase abstracta `MedicionCreator` declara las operaciones de
creacion y cada creador concreto las implementa para su contaminante.
"""

from abc import ABC, abstractmethod

from src.models.medicion_calidad_aire import (
    MedicionCalidadAire,
    MedicionCalidadAirePM,
)


class MedicionCreator(ABC):
    """Creador abstracto: las subclases deciden que producto instanciar."""

    @abstractmethod
    def crear(self, **datos) -> MedicionCalidadAire:
        """Instancia el producto a partir de campos sueltos."""

    @abstractmethod
    def desde_dict(self, data: dict) -> MedicionCalidadAire:
        """Reconstruye el producto desde su forma serializada."""


class PMCreator(MedicionCreator):
    """Creador concreto para material particulado (PM10 / PM2.5)."""

    def crear(self, **datos) -> MedicionCalidadAire:
        return MedicionCalidadAirePM(**datos)

    def desde_dict(self, data: dict) -> MedicionCalidadAire:
        return MedicionCalidadAirePM.from_dict(data)
