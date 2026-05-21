"""Controlador de mediciones (capa C del patron MVC).

Orquesta los casos de uso del usuario coordinando el Modelo (entidades
`Medicion*`) y la Vista (`MedicionView`), apoyandose en el Repositorio
para persistir. Depende solo de abstracciones:

- `IMedicionRepository` (DIP): el controller no conoce el backend de
  persistencia, solo su contrato CRUD.
- `MedicionView`: el controller no imprime ni formatea, delega en la
  vista. Asi se respeta SRP y se puede sustituir por otra vista (web,
  GUI, tests) sin tocar esta clase.

El controller no contiene reglas de dominio: validaciones, calculo de
nivel ICA, inmutabilidad de mediciones automaticas, etc., viven en el
modelo o en el repositorio. Aqui solo se traduce la intencion del
usuario en llamadas al modelo/repositorio y se reportan los resultados.
"""

from datetime import datetime
from typing import Optional

from src.exceptions.custom_exceptions import (
    DatoInvalidoError,
    RegistroDuplicadoError,
    RegistroNoEncontradoError,
)
from src.models.medicion import Medicion
from src.models.medicion_calidad_aire import (
    MedicionCalidadAire,
    MedicionCalidadAirePM,
)
from src.repositories.medicion_repository import IMedicionRepository
from src.views.medicion_view import MedicionView


_TIPOS_POR_DEFECTO: dict[str, type[MedicionCalidadAire]] = {
    "PM": MedicionCalidadAirePM,
    # Para sumar un contaminante nuevo (CO, SO2, NO2, O3...) basta con
    # registrar su subclase aqui (OCP): no hace falta tocar el controller.
}


class MedicionController:
    """Orquesta los casos de uso sobre mediciones (CRUD + sincronizacion).

    Trabaja contra la abstraccion `MedicionCalidadAire` y resuelve la
    subclase concreta en runtime a partir de un registro inyectado
    (`tipos`). Asi un mismo controller puede manejar varios
    contaminantes a la vez y sumar uno nuevo no requiere modificar esta
    clase (OCP): basta con extender el dict pasado al constructor.
    """

    def __init__(
        self,
        repository: IMedicionRepository,
        view: MedicionView,
        tipos: Optional[dict[str, type[MedicionCalidadAire]]] = None,
    ) -> None:
        self.repository = repository
        self.view = view
        self._tipos = dict(tipos) if tipos is not None else dict(_TIPOS_POR_DEFECTO)

    def _resolver_tipo(self, tipo: str) -> Optional[type[MedicionCalidadAire]]:
        """Devuelve la subclase registrada para `tipo`, o None si no existe."""
        cls = self._tipos.get(tipo)
        if cls is None:
            self.view.show_error(
                f"Tipo de medicion desconocido: {tipo!r}. "
                f"Registrados: {sorted(self._tipos)}"
            )
        return cls

    # ── casos de uso ─────────────────────────────────────────────────
    def crear_medicion(
        self,
        tipo: str,
        id: str,
        municipio: str,
        estacion: str,
        fecha: datetime,
        medicion: float,
        **extra,
    ) -> None:
        """Registra una medicion MANUAL ingresada por el usuario.

        `tipo` selecciona la subclase concreta del registro (`"PM"`,
        `"CO"`...). Los campos especificos del contaminante (p. ej.
        `diametro_aerodinamico="PM2.5"`) viajan por `**extra`.
        """
        cls = self._resolver_tipo(tipo)
        if cls is None:
            return
        try:
            nueva = cls(
                id=id,
                municipio=municipio,
                estacion=estacion,
                fecha=fecha,
                medicion=medicion,
                origen=Medicion.MANUAL,
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
        municipio: Optional[str] = None,
        estacion: Optional[str] = None,
        fecha: Optional[datetime] = None,
        medicion: Optional[float] = None,
        **extra,
    ) -> None:
        """Modifica una medicion MANUAL existente (las AUTO son inmutables).

        Los campos especificos del contaminante (p. ej.
        `diametro_aerodinamico` para PM) viajan en `**extra` y solo se
        aplican si vienen explicitos; en caso contrario se reusan los
        del registro existente via `to_dict()`.
        """
        existente = self.repository.buscar_medicion_por_id(medicion_id)
        if existente is None:
            self.view.show_error(f"No existe medicion con id {medicion_id}")
            return
        if existente.origen == Medicion.AUTO:
            self.view.show_error(
                "Las mediciones del sensor son inmutables. "
                "Solo se pueden editar mediciones MANUALES."
            )
            return
        try:
            datos = existente.to_dict()
            datos["fecha"] = existente.fecha  # preservar datetime, no isoformat
            if municipio is not None:
                datos["municipio"] = municipio
            if estacion is not None:
                datos["estacion"] = estacion
            if fecha is not None:
                datos["fecha"] = fecha
            if medicion is not None:
                datos["medicion"] = medicion
            datos.update(extra)

            actualizada = type(existente)(
                id=medicion_id,
                municipio=datos["municipio"],
                estacion=datos["estacion"],
                fecha=datos["fecha"],
                medicion=datos["medicion"],
                origen=existente.origen,
                **{k: v for k, v in datos.items()
                   if k not in {"id", "municipio", "estacion", "fecha",
                                "medicion", "origen", "nivel", "observacion",
                                "tipo"}},
            )
            self.repository.actualizar_medicion(actualizada)
        except (DatoInvalidoError, RegistroNoEncontradoError) as e:
            self.view.show_error(str(e))
            return
        self.view.show_message(
            f"Medicion {medicion_id} actualizada — nivel: {actualizada.nivel}"
        )

    def eliminar_medicion(self, medicion_id: str) -> None:
        """Borra una medicion (el repositorio aplica la regla de origen)."""
        try:
            self.repository.eliminar_medicion(medicion_id)
        except (DatoInvalidoError, RegistroNoEncontradoError) as e:
            self.view.show_error(str(e))
            return
        self.view.show_message(f"Medicion {medicion_id} eliminada")

    def calcular_niveles_pendientes(self) -> None:
        """Recalcula y persiste el nivel ICA de cada medicion almacenada.

        Util al arrancar la app: los registros sincronizados desde el
        sensor pueden quedar con `nivel: "Pendiente"`. Al re-guardarlos,
        el modelo recalcula la categoria a partir del valor medido.
        """
        actualizados = 0
        for medicion in self.repository.listar_mediciones():
            self.repository.actualizar_medicion(medicion)
            actualizados += 1
        if actualizados:
            self.view.show_message(
                f"Niveles calculados: {actualizados} registro(s) actualizados."
            )

    def sincronizar_sensor(self, items: list[dict]) -> None:
        """Carga datos del sensor sin sobreescribir mediciones manuales.

        Orquesta buscar/crear/actualizar usando solo el CRUD del
        repositorio. No conoce el medio de persistencia.
        """
        resumen = {"agregadas": 0, "actualizadas": 0, "omitidas": 0, "errores": 0}
        for raw in items:
            try:
                nueva = self._construir_desde_sensor(raw)
            except (DatoInvalidoError, KeyError, ValueError) as e:
                resumen["errores"] += 1
                self.view.show_error(f"Item del sensor invalido: {e}")
                continue

            try:
                existente = self.repository.buscar_medicion_por_id(nueva.id)
                if existente is None:
                    self.repository.crear_medicion(nueva)
                    resumen["agregadas"] += 1
                elif existente.origen == Medicion.MANUAL:
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
            f"errores: {resumen['errores']}"
        )

    def listar_mediciones(self) -> None:
        """Muestra todas las mediciones almacenadas."""
        self.view.show_mediciones(self.repository.listar_mediciones())

    # ── helpers privados ─────────────────────────────────────────────
    def _construir_desde_sensor(self, raw: dict) -> Medicion:
        """Normaliza un item crudo del sensor en una entidad del modelo.

        Resuelve la subclase concreta segun el campo `tipo` del item.
        Forza `origen=AUTO` y descarta `nivel` para que sea el modelo
        quien lo derive a partir del valor medido.
        """
        tipo = raw.get("tipo")
        if not tipo:
            raise DatoInvalidoError("Item del sensor sin campo 'tipo'")
        cls = self._tipos.get(tipo)
        if cls is None:
            raise DatoInvalidoError(
                f"Tipo de medicion desconocido: {tipo!r}. "
                f"Registrados: {sorted(self._tipos)}"
            )
        datos = {**raw, "origen": Medicion.AUTO}
        datos.pop("nivel", None)
        return cls.from_dict(datos)
