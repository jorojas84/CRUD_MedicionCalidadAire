"""Controlador de mediciones (capa C del patron MVC).

Coordina la vista y el repositorio para implementar los casos de uso:
crear/actualizar/eliminar mediciones manuales, listarlas y sincronizar
datos automaticos provenientes de un sensor.
"""

from datetime import datetime
from typing import Optional

from src.exceptions.custom_exceptions import (
    DatoInvalidoError,
    RegistroDuplicadoError,
    RegistroNoEncontradoError,
)
from src.factories.medicion_factory import MedicionFactory
from src.models.estacion_ambiental import (
    DuplicateEstacionError,
    EstacionAmbiental,
)
from src.models.medicion_calidad_aire import MedicionCalidadAire
from src.repositories.estacion_repository import EstacionRepository
from src.repositories.medicion_calidad_aire_repository import IMedicionRepository
from src.views.medicion_calidad_aire_view import MedicionCalidadAireView


class MedicionController:
    """Orquesta los casos de uso del modulo de mediciones."""

    def __init__(
        self,
        repository: IMedicionRepository,
        view: MedicionCalidadAireView,
        estacion_repository: Optional[EstacionRepository] = None,
    ) -> None:
        self.repository = repository
        self.view = view
        self._estaciones = estacion_repository or EstacionRepository()

    def crear_medicion(
        self,
        tipo: str,
        id: str,
        codigo_dane_municipio: str,
        id_estacion: str,
        fecha: datetime,
        medicion: float,
        **extra,
    ) -> None:
        """Registra una medicion MANUAL ingresada por el usuario."""
        if self._estaciones.buscar(id_estacion) is None:
            self.view.show_error(
                f"Estacion {id_estacion!r} no existe. "
                "Registrela antes de crear mediciones manuales."
            )
            return
        try:
            nueva = MedicionFactory.crear(
                tipo,
                id=id,
                codigo_dane_municipio=codigo_dane_municipio,
                id_estacion=id_estacion,
                fecha=fecha,
                medicion=medicion,
                origen=MedicionCalidadAire.MANUAL,
                **extra,
            )
            self.repository.crear_medicion(nueva)
        except (DatoInvalidoError, RegistroDuplicadoError) as e:
            self.view.show_error(str(e))
            return
        self.view.show_message(
            f"Medicion {id} creada manualmente — nivel: {nueva.nivel}"
        )

    def actualizar_medicion(
        self,
        medicion_id: str,
        codigo_dane_municipio: Optional[str] = None,
        id_estacion: Optional[str] = None,
        fecha: Optional[datetime] = None,
        medicion: Optional[float] = None,
        **extra,
    ) -> None:
        """Modifica una medicion MANUAL existente (las AUTO son inmutables)."""
        existente = self.repository.buscar_medicion_por_id(medicion_id)
        if existente is None:
            self.view.show_error(f"No existe medicion con id {medicion_id}")
            return
        if existente.origen == MedicionCalidadAire.AUTO:
            self.view.show_error(
                "Las mediciones automaticas son inmutables. "
                "Solo se pueden editar mediciones MANUALES."
            )
            return
        try:
            datos = existente.to_dict()
            datos["fecha"] = existente.fecha  # preservar datetime, no isoformat
            if codigo_dane_municipio is not None:
                datos["codigo_dane_municipio"] = codigo_dane_municipio
            if id_estacion is not None:
                datos["id_estacion"] = id_estacion
            if fecha is not None:
                datos["fecha"] = fecha
            if medicion is not None:
                datos["medicion"] = medicion
            datos.update(extra)

            actualizada = type(existente)(
                id=medicion_id,
                codigo_dane_municipio=datos["codigo_dane_municipio"],
                id_estacion=datos["id_estacion"],
                fecha=datos["fecha"],
                medicion=datos["medicion"],
                origen=existente.origen,
                **{k: v for k, v in datos.items()
                   if k not in {"id", "codigo_dane_municipio", "id_estacion",
                                "fecha", "medicion", "origen", "nivel",
                                "observacion", "tipo"}},
            )
            self.repository.actualizar_medicion(actualizada)
        except (DatoInvalidoError, RegistroNoEncontradoError) as e:
            self.view.show_error(str(e))
            return
        self.view.show_message(
            f"Medicion {medicion_id} actualizada — nivel: {actualizada.nivel}"
        )

    def eliminar_medicion(self, medicion_id: str) -> None:
        try:
            self.repository.eliminar_medicion(medicion_id)
        except (DatoInvalidoError, RegistroNoEncontradoError) as e:
            self.view.show_error(str(e))
            return
        self.view.show_message(f"Medicion {medicion_id} eliminada")

    def listar_mediciones(self) -> None:
        self.view.show_mediciones(self.repository.listar_mediciones())

    def calcular_niveles_pendientes(self) -> None:
        """Recalcula y reescribe el nivel ICA de todas las mediciones."""
        actualizados = 0
        for medicion in self.repository.listar_mediciones():
            self.repository.actualizar_medicion(medicion)
            actualizados += 1
        if actualizados:
            self.view.show_message(
                f"Niveles recalculados: {actualizados} registro(s) actualizados."
            )

    def sincronizar_sensor(self, items: list[dict]) -> None:
        """Carga datos del sensor sin sobrescribir las mediciones manuales.

        Si el item refiere a una estacion desconocida, la autorregistra
        con datos placeholder para no bloquear la sincronizacion.
        """
        resumen = {"agregadas": 0, "actualizadas": 0, "omitidas": 0,
                   "estaciones_creadas": 0, "errores": 0}
        for raw in items:
            try:
                nueva = self._construir_desde_sensor(raw)
            except (DatoInvalidoError, KeyError, ValueError) as e:
                resumen["errores"] += 1
                self.view.show_error(f"Item del sensor invalido: {e}")
                continue

            if self._autoregistrar_estacion_si_falta(nueva):
                resumen["estaciones_creadas"] += 1

            try:
                existente = self.repository.buscar_medicion_por_id(nueva.id)
                if existente is None:
                    self.repository.crear_medicion(nueva)
                    resumen["agregadas"] += 1
                elif existente.origen == MedicionCalidadAire.MANUAL:
                    resumen["omitidas"] += 1
                else:
                    self.repository.actualizar_medicion(nueva)
                    resumen["actualizadas"] += 1
            except (DatoInvalidoError, RegistroDuplicadoError, RegistroNoEncontradoError) as e:
                resumen["errores"] += 1
                self.view.show_error(str(e))

        self.view.show_message(
            f"Sincronizacion completada — "
            f"agregadas: {resumen['agregadas']}, "
            f"actualizadas: {resumen['actualizadas']}, "
            f"omitidas (manuales protegidas): {resumen['omitidas']}, "
            f"estaciones autorregistradas: {resumen['estaciones_creadas']}, "
            f"errores: {resumen['errores']}"
        )

    def _construir_desde_sensor(self, raw: dict) -> MedicionCalidadAire:
        """Normaliza un item crudo del sensor en una entidad del modelo."""
        datos = {**raw, "origen": MedicionCalidadAire.AUTO}
        datos.pop("nivel", None)
        return MedicionFactory.desde_dict(datos)

    def _autoregistrar_estacion_si_falta(
        self, medicion: MedicionCalidadAire
    ) -> bool:
        """Crea la estacion referenciada si no existe. Devuelve True si la creo."""
        if self._estaciones.buscar(medicion.id_estacion) is not None:
            return False
        try:
            self._estaciones.crear(EstacionAmbiental(
                id_estacion=medicion.id_estacion,
                nombre="(autorregistrada)",
                municipio=medicion.codigo_dane_municipio,
                tipo_estacion="Desconocido",
                estado="Activa",
            ))
            return True
        except DuplicateEstacionError:
            return False
