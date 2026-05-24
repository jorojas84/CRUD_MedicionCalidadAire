"""Vista de consola para mediciones (capa V del patron MVC).

Unica capa que interactua con el usuario: muestra resultados y recoge
entradas. No accede al repositorio ni contiene reglas de dominio.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Callable, Iterable, Optional

from src.models.medicion_calidad_aire import MedicionCalidadAire
from src.repositories.estacion_repository import EstacionRepository
from src.repositories.municipio_repository import MunicipioRepository

if TYPE_CHECKING:
    from src.controllers.medicion_calidad_aire_controller import MedicionController


class _OperacionCancelada(Exception):
    """El usuario abortó el prompt escribiendo 'cancelar'."""


class MedicionCalidadAireView:
    """Interfaz de consola para el CRUD de mediciones."""

    def __init__(self, controller: Optional["MedicionController"] = None):
        self.controller: "MedicionController" = controller  # type: ignore[assignment]

    def mostrar_menu(self) -> None:
        self._asegurar_controller()
        while True:
            print("\n--- Menu Mediciones ---")
            print("1. Crear medicion (manual)")
            print("2. Listar mediciones")
            print("3. Actualizar medicion")
            print("4. Eliminar medicion")
            print("5. Volver")
            opcion = input("Seleccione una opcion: ").strip()
            if opcion == "1":
                self._accion_crear()
            elif opcion == "2":
                self.controller.listar_mediciones()
            elif opcion == "3":
                self._accion_actualizar()
            elif opcion == "4":
                self._accion_eliminar()
            elif opcion == "5":
                return
            else:
                self.show_error("Opcion invalida.")

    def _asegurar_controller(self) -> None:
        """Construye el controller con dependencias por defecto si no fue inyectado."""
        if self.controller is not None:
            return
        from src.controllers.medicion_calidad_aire_controller import MedicionController
        from src.repositories.medicion_calidad_aire_repository import MedicionRepository
        self.controller = MedicionController(MedicionRepository(), self)

    # ── acciones del menu ────────────────────────────────────────────
    def _accion_crear(self) -> None:
        print("(Escriba 'cancelar' en cualquier campo para abortar)")
        try:
            tipo = self._pedir_opcion_loop("Tipo", ["PM"])
            medicion_id = self._pedir_id_loop("ID medicion")
            codigo_dane = self._pedir_id_existente_loop(
                "Codigo DANE municipio",
                lambda v: MunicipioRepository().buscar_por_id(v) is not None,
                "Municipio inexistente",
            )
            id_estacion = self._pedir_id_existente_loop(
                "ID estacion",
                lambda v: EstacionRepository().buscar(v) is not None,
                "Estacion inexistente",
            )
            fecha = self._pedir_fecha_loop("Fecha")
            valor = self._pedir_numero_loop("Valor de medicion")
            extra: dict = {}
            if tipo == "PM":
                extra["diametro_aerodinamico"] = self._pedir_opcion_loop(
                    "Diametro aerodinamico", ["PM10", "PM2.5"]
                )
        except _OperacionCancelada:
            self.show_message("Operacion cancelada.")
            return

        self.controller.crear_medicion(
            tipo, medicion_id, codigo_dane, id_estacion, fecha, valor, **extra
        )

    def _accion_actualizar(self) -> None:
        crudo = self.pedir_texto("ID medicion a actualizar")
        medicion_id = self._normalizar_id(crudo)
        if not medicion_id:
            return
        print("(Deje vacio cualquier campo que no desee modificar)")
        codigo_dane = self.pedir_texto("Nuevo codigo DANE", opcional=True)
        id_estacion = self.pedir_texto("Nuevo ID estacion", opcional=True)
        self.controller.actualizar_medicion(
            medicion_id,
            codigo_dane_municipio=self._normalizar_id(codigo_dane),
            id_estacion=self._normalizar_id(id_estacion),
            fecha=self.pedir_fecha("Nueva fecha"),
            medicion=self.pedir_numero("Nuevo valor"),
        )

    def _accion_eliminar(self) -> None:
        medicion_id = self._normalizar_id(self.pedir_texto("ID medicion a eliminar"))
        if medicion_id:
            self.controller.eliminar_medicion(medicion_id)

    # ── salida ───────────────────────────────────────────────────────
    def show_message(self, mensaje: str) -> None:
        print(f"[OK] {mensaje}")

    def show_error(self, mensaje: str) -> None:
        print(f"[ERROR] {mensaje}")

    def show_mediciones(self, mediciones: Iterable[MedicionCalidadAire]) -> None:
        mediciones = list(mediciones)
        if not mediciones:
            print("No hay mediciones registradas.")
            return
        for m in mediciones:
            print(m.to_dict())

    # ── normalizacion ────────────────────────────────────────────────
    @staticmethod
    def _normalizar_id(valor: Optional[str]) -> Optional[str]:
        if valor is None:
            return None
        v = valor.strip().upper()
        return v or None

    @staticmethod
    def _es_cancelar(crudo: str) -> bool:
        return crudo.strip().lower() == "cancelar"

    # ── prompts de entrada (one-shot, usados por actualizar/eliminar) ─
    def pedir_texto(self, etiqueta: str, opcional: bool = False) -> Optional[str]:
        valor = input(f"{etiqueta}: ").strip()
        if not valor:
            return None if opcional else ""
        return valor

    def pedir_numero(self, etiqueta: str) -> Optional[float]:
        crudo = input(f"{etiqueta}: ").strip()
        if not crudo:
            return None
        try:
            return float(crudo)
        except ValueError:
            self.show_error(f"Valor numerico invalido: {crudo!r}")
            return None

    def pedir_fecha(self, etiqueta: str) -> Optional[datetime]:
        crudo = input(f"{etiqueta} (ISO 8601, p. ej. 2026-05-21T10:00): ").strip()
        if not crudo:
            return None
        try:
            return datetime.fromisoformat(crudo)
        except ValueError:
            self.show_error(f"Fecha invalida: {crudo!r}")
            return None

    def pedir_opcion(self, etiqueta: str, opciones: Iterable[str]) -> Optional[str]:
        opciones = list(opciones)
        crudo = input(f"{etiqueta} {opciones}: ").strip()
        if crudo not in opciones:
            self.show_error(f"Opcion invalida: {crudo!r}. Validas: {opciones}")
            return None
        return crudo

    # ── prompts en bucle (reintentan hasta entrada valida o 'cancelar') ─
    def _pedir_id_loop(self, etiqueta: str) -> str:
        while True:
            crudo = input(f"{etiqueta}: ")
            if self._es_cancelar(crudo):
                raise _OperacionCancelada
            valor = self._normalizar_id(crudo)
            if valor:
                return valor
            self.show_error(f"{etiqueta} es obligatorio.")

    def _pedir_id_existente_loop(
        self,
        etiqueta: str,
        existe: Callable[[str], bool],
        mensaje_no_existe: str,
    ) -> str:
        while True:
            valor = self._pedir_id_loop(etiqueta)
            if existe(valor):
                return valor
            self.show_error(f"{mensaje_no_existe}: {valor!r}.")

    def _pedir_numero_loop(self, etiqueta: str) -> float:
        while True:
            crudo = input(f"{etiqueta}: ").strip()
            if self._es_cancelar(crudo):
                raise _OperacionCancelada
            if not crudo:
                self.show_error(f"{etiqueta} es obligatorio.")
                continue
            try:
                return float(crudo)
            except ValueError:
                self.show_error(f"Valor numerico invalido: {crudo!r}")

    def _pedir_fecha_loop(self, etiqueta: str) -> datetime:
        while True:
            crudo = input(
                f"{etiqueta} (ISO 8601, p. ej. 2026-05-21T10:00): "
            ).strip()
            if self._es_cancelar(crudo):
                raise _OperacionCancelada
            if not crudo:
                self.show_error(f"{etiqueta} es obligatoria.")
                continue
            try:
                return datetime.fromisoformat(crudo)
            except ValueError:
                self.show_error(f"Fecha invalida: {crudo!r}")

    def _pedir_opcion_loop(self, etiqueta: str, opciones: Iterable[str]) -> str:
        opciones = list(opciones)
        while True:
            crudo = input(f"{etiqueta} {opciones}: ").strip()
            if self._es_cancelar(crudo):
                raise _OperacionCancelada
            if crudo in opciones:
                return crudo
            self.show_error(
                f"Opcion invalida: {crudo!r}. Validas: {opciones}"
            )
