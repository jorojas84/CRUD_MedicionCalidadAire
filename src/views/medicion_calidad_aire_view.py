"""Vista de consola para mediciones (capa V del patron MVC).

La vista es el unico punto del sistema que interactua con el usuario:
imprime resultados y, opcionalmente, recoge entradas. No contiene
reglas de dominio ni accede al repositorio: solo recibe entidades
`Medicion` (o mensajes simples) desde el controller y las presenta.

Diseño:

- **SRP**: formateo y E/S estan separados (`_formatear_*` arma strings;
  `_print` los emite). Eso hace la vista testeable sin capturar stdout.
- **OCP/polimorfismo**: `show_mediciones` no asume ninguna subclase
  concreta. Itera sobre `Medicion.to_dict()` —que es polimorfico— y
  renderiza los campos comunes en columnas + los campos extra (p. ej.
  `diametro_aerodinamico` de PM) como detalles. Sumar un contaminante
  nuevo no obliga a tocar esta clase.
- **DIP**: el controller depende de esta vista (o de otra equivalente).
  Para una vista web/GUI/tests basta con respetar la misma interfaz
  publica (`show_message`, `show_error`, `show_mediciones`, prompts).
"""

from datetime import datetime
from typing import Iterable, Optional

from src.models.medicion_calidad_aire import MedicionCalidadAire


# Campos comunes a toda `MedicionCalidadAire` (orden en el que se muestran).
# Todo lo que la subclase agregue en `to_dict()` aparece como "detalle".
_CAMPOS_COMUNES: tuple[str, ...] = (
    "id", "codigo_dane_municipio", "id_estacion",
    "fecha", "medicion", "nivel", "origen",
)
# Claves que `to_dict` incluye pero no aportan a la columna "detalles".
_CAMPOS_OMITIDOS_EN_DETALLES: frozenset[str] = frozenset(
    {*_CAMPOS_COMUNES, "observacion", "tipo"}
)


class MedicionView:
    """Adaptador de consola: presenta mediciones e interactua con el usuario."""

    # ── salida: mensajes simples ─────────────────────────────────────
    def show_message(self, mensaje: str) -> None:
        self._print(f"[OK] {mensaje}")

    def show_error(self, mensaje: str) -> None:
        self._print(f"[ERROR] {mensaje}")

    # ── salida: listado polimorfico de mediciones ────────────────────
    def show_mediciones(self, mediciones: Iterable[MedicionCalidadAire]) -> None:
        mediciones = list(mediciones)
        if not mediciones:
            self._print("No hay mediciones registradas.")
            return
        for linea in self._formatear_tabla(mediciones):
            self._print(linea)

    def _formatear_tabla(self, mediciones: list[MedicionCalidadAire]) -> list[str]:
        """Arma el listado tabular (sin imprimir). Aislado para testear."""
        encabezado = (
            f"{'ID':<12} {'COD_DANE':<10} {'ID_ESTACION':<14} "
            f"{'FECHA':<20} {'VALOR':<8} {'NIVEL':<35} "
            f"{'ORIGEN':<11} DETALLES"
        )
        lineas = [encabezado, "-" * len(encabezado)]
        for m in mediciones:
            lineas.append(self._formatear_fila(m))
        return lineas

    def _formatear_fila(self, m: MedicionCalidadAire) -> str:
        datos = m.to_dict()
        detalles = self._formatear_detalles(datos)
        fecha_str = self._formatear_fecha(datos.get("fecha"))
        return (
            f"{str(datos.get('id', '')):<12} "
            f"{str(datos.get('codigo_dane_municipio', '')):<10} "
            f"{str(datos.get('id_estacion', '')):<14} "
            f"{fecha_str:<20} "
            f"{str(datos.get('medicion', '')):<8} "
            f"{str(datos.get('nivel', '')):<35} "
            f"{str(datos.get('origen', '')):<11} "
            f"{detalles}"
        )

    def _formatear_detalles(self, datos: dict) -> str:
        """Resume los campos especificos de la subclase (OCP)."""
        extras = {
            k: v for k, v in datos.items()
            if k not in _CAMPOS_OMITIDOS_EN_DETALLES
        }
        if not extras:
            return ""
        return ", ".join(f"{k}={v}" for k, v in extras.items())

    def _formatear_fecha(self, fecha) -> str:
        if isinstance(fecha, datetime):
            return fecha.isoformat()
        return str(fecha) if fecha is not None else ""

    # ── entrada: prompts coherentes con la firma del controller ──────
    def pedir_texto(self, etiqueta: str, opcional: bool = False) -> Optional[str]:
        valor = input(f"{etiqueta}: ").strip()
        if not valor:
            return None if opcional else ""
        return valor

    def pedir_numero(self, etiqueta: str, opcional: bool = False) -> Optional[float]:
        crudo = input(f"{etiqueta}: ").strip()
        if not crudo:
            return None if opcional else 0.0
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

    # ── E/S de bajo nivel (punto unico para testear/mockear) ─────────
    def _print(self, linea: str) -> None:
        print(linea)
