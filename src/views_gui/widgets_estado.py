"""Widgets reutilizables para mensajes de estado en GUI."""

import tkinter as tk
from tkinter import ttk


class EstadoWidget:
    """Maneja mensajes de estado visibles para el usuario."""

    COLORES = {
        "info": "#1f2937",
        "success": "#065f46",
        "error": "#991b1b",
    }

    def __init__(self, parent) -> None:
        self._texto = tk.StringVar(value="Listo para registrar alertas")
        self.label = ttk.Label(parent, textvariable=self._texto)
        self._set_color("info")

    def mostrar(self, mensaje: str, tipo: str = "info") -> None:
        self._texto.set(mensaje)
        self._set_color(tipo)

    def valor(self) -> str:
        return self._texto.get()

    def _set_color(self, tipo: str) -> None:
        color = self.COLORES.get(tipo, self.COLORES["info"])
        self.label.configure(foreground=color)
