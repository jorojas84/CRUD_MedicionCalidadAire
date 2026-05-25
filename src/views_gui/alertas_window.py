"""Ventana Tkinter para registro de alertas ambientales."""

import tkinter as tk
from tkinter import ttk

from src.controllers.alerta_controller import AlertaController
from src.exceptions.custom_exceptions import DatoInvalidoError, RegistroDuplicadoError
from src.views_gui.widgets_estado import EstadoWidget


def validar_campos_obligatorios(campos: dict[str, str]) -> tuple[bool, str]:
    """Valida que los campos requeridos no vengan vacios."""
    for nombre, valor in campos.items():
        if not str(valor).strip():
            return False, f"El campo '{nombre}' es obligatorio"
    return True, ""


class AlertasWindow:
    """Formulario GUI para crear alertas."""

    NIVELES = ("Bajo", "Medio", "Alto")
    ESTADOS = ("Activa", "Cerrada")

    def __init__(self, root: tk.Tk | tk.Toplevel, controller: AlertaController | None = None) -> None:
        self.root = root
        self.controller = controller or AlertaController()
        self.root.title("Registro de Alertas")
        self._crear_variables()
        self._crear_layout()

    def _crear_variables(self) -> None:
        self.id_alerta_var = tk.StringVar()
        self.id_medicion_var = tk.StringVar()
        self.nivel_var = tk.StringVar(value=self.NIVELES[1])
        self.descripcion_var = tk.StringVar()
        self.fecha_var = tk.StringVar()
        self.estado_var = tk.StringVar(value=self.ESTADOS[0])

    def _crear_layout(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)

        etiquetas = [
            ("ID alerta", self.id_alerta_var),
            ("ID medicion", self.id_medicion_var),
            ("Descripcion", self.descripcion_var),
            ("Fecha (YYYY-MM-DD)", self.fecha_var),
        ]

        for i, (texto, variable) in enumerate(etiquetas):
            ttk.Label(frame, text=texto).grid(row=i, column=0, sticky="w", padx=(0, 8), pady=4)
            ttk.Entry(frame, textvariable=variable, width=36).grid(row=i, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Nivel").grid(row=4, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Combobox(frame, textvariable=self.nivel_var, values=self.NIVELES, state="readonly").grid(
            row=4, column=1, sticky="ew", pady=4
        )

        ttk.Label(frame, text="Estado").grid(row=5, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Combobox(frame, textvariable=self.estado_var, values=self.ESTADOS, state="readonly").grid(
            row=5, column=1, sticky="ew", pady=4
        )

        botonera = ttk.Frame(frame)
        botonera.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(10, 4))
        ttk.Button(botonera, text="Guardar alerta", command=self.guardar_alerta).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(botonera, text="Limpiar", command=self.limpiar_formulario).grid(row=0, column=1)

        self.estado = EstadoWidget(frame)
        self.estado.label.grid(row=7, column=0, columnspan=2, sticky="w", pady=(8, 0))

        frame.columnconfigure(1, weight=1)

    def _datos_formulario(self) -> dict[str, str]:
        return {
            "id_alerta": self.id_alerta_var.get(),
            "id_medicion": self.id_medicion_var.get(),
            "descripcion": self.descripcion_var.get(),
            "fecha": self.fecha_var.get(),
            "nivel": self.nivel_var.get(),
            "estado": self.estado_var.get(),
        }

    def guardar_alerta(self) -> bool:
        self.estado.mostrar("Guardando alerta...", "info")
        datos = self._datos_formulario()

        valido, mensaje = validar_campos_obligatorios(
            {
                "id_alerta": datos["id_alerta"],
                "id_medicion": datos["id_medicion"],
                "descripcion": datos["descripcion"],
                "fecha": datos["fecha"],
            }
        )
        if not valido:
            self.estado.mostrar(mensaje, "error")
            return False

        try:
            self.controller.crear_alerta(
                id_alerta=datos["id_alerta"],
                id_medicion=datos["id_medicion"],
                nivel=datos["nivel"],
                descripcion=datos["descripcion"],
                fecha=datos["fecha"],
                estado=datos["estado"],
            )
        except (DatoInvalidoError, RegistroDuplicadoError, ValueError) as error:
            self.estado.mostrar(f"Error: {error}", "error")
            return False

        self.estado.mostrar("Alerta guardada correctamente", "success")
        return True

    def limpiar_formulario(self) -> None:
        self.id_alerta_var.set("")
        self.id_medicion_var.set("")
        self.descripcion_var.set("")
        self.fecha_var.set("")
        self.nivel_var.set(self.NIVELES[1])
        self.estado_var.set(self.ESTADOS[0])
        self.estado.mostrar("Formulario limpio", "info")


def ejecutar() -> None:
    root = tk.Tk()
    AlertasWindow(root)
    root.mainloop()


if __name__ == "__main__":
    ejecutar()
