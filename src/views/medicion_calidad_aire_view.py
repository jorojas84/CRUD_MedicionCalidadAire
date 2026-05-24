"""Vista de consola para mediciones (capa V del patron MVC).

Unica capa que interactua con el usuario: muestra resultados y recoge
entradas. No accede al repositorio ni contiene reglas de dominio.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Iterable, Optional

from src.models.medicion_calidad_aire import MedicionCalidadAire
from src.repositories.estacion_repository import EstacionRepository
from src.repositories.municipio_repository import MunicipioRepository

if TYPE_CHECKING:
    from src.controllers.medicion_calidad_aire_controller import MedicionController


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
            print("5. Recalcular niveles")
            print("6. Volver")
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
                self.controller.calcular_niveles_pendientes()
            elif opcion == "6":
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
        tipo = self.pedir_opcion("Tipo", ["PM"])
        if tipo is None:
            return
        medicion_id = self.pedir_texto("ID medicion")
        if not medicion_id:
            return self.show_error("ID es obligatorio.")
        codigo_dane = self.pedir_texto("Codigo DANE municipio")
        if not codigo_dane:
            return self.show_error("Codigo DANE es obligatorio.")
        if MunicipioRepository().buscar_por_id(codigo_dane) is None:
            return self.show_error(f"Municipio con codigo DANE {codigo_dane!r} no existe.")
        id_estacion = self.pedir_texto("ID estacion")
        if not id_estacion:
            return self.show_error("ID estacion es obligatorio.")
        if EstacionRepository().buscar(id_estacion) is None:
            return self.show_error(f"Estacion {id_estacion!r} no existe.")
        fecha = self.pedir_fecha("Fecha")
        if fecha is None:
            return self.show_error("Fecha requerida.")
        valor = self.pedir_numero("Valor de medicion")
        if valor is None:
            return self.show_error("Valor requerido.")

        extra = {}
        if tipo == "PM":
            diametro = self.pedir_opcion("Diametro aerodinamico", ["PM10", "PM2.5"])
            if diametro is None:
                return
            extra["diametro_aerodinamico"] = diametro

        self.controller.crear_medicion(
            tipo, medicion_id, codigo_dane, id_estacion, fecha, valor, **extra
        )

    def _accion_actualizar(self) -> None:
        medicion_id = self.pedir_texto("ID medicion a actualizar")
        if not medicion_id:
            return
        print("(Deje vacio cualquier campo que no desee modificar)")
        self.controller.actualizar_medicion(
            medicion_id,
            codigo_dane_municipio=self.pedir_texto("Nuevo codigo DANE", opcional=True),
            id_estacion=self.pedir_texto("Nuevo ID estacion", opcional=True),
            fecha=self.pedir_fecha("Nueva fecha"),
            medicion=self.pedir_numero("Nuevo valor"),
        )

    def _accion_eliminar(self) -> None:
        medicion_id = self.pedir_texto("ID medicion a eliminar")
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

    # ── prompts de entrada ───────────────────────────────────────────
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
