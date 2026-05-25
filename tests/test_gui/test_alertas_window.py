"""Pruebas basicas de la vista GUI de alertas."""

import tkinter as tk

import pytest

from src.views_gui.alertas_window import AlertasWindow


class ControllerDoble:
    def __init__(self):
        self.llamadas = []

    def crear_alerta(self, **kwargs):
        self.llamadas.append(kwargs)
        return kwargs


@pytest.fixture(scope="module")
def root_tk():
    try:
        root = tk.Tk()
    except tk.TclError as error:
        pytest.skip(f"Tkinter no disponible en este entorno: {error}")
    root.withdraw()
    yield root
    root.destroy()


def _crear_ventana(root_tk):
    contenedor = tk.Toplevel(root_tk)
    controller = ControllerDoble()
    ventana = AlertasWindow(contenedor, controller=controller)
    return contenedor, controller, ventana


def test_alertas_window_bloquea_guardado_si_faltan_obligatorios(root_tk):
    contenedor, controller, ventana = _crear_ventana(root_tk)

    ventana.id_alerta_var.set("")
    ventana.id_medicion_var.set("MED001")
    ventana.descripcion_var.set("Descripcion prueba")
    ventana.fecha_var.set("2026-05-24")

    guardado = ventana.guardar_alerta()

    assert guardado is False
    assert controller.llamadas == []
    assert "obligatorio" in ventana.estado.valor().lower()
    contenedor.destroy()


def test_alertas_window_muestra_exito_al_guardar_alerta_valida(root_tk):
    contenedor, controller, ventana = _crear_ventana(root_tk)

    ventana.id_alerta_var.set("ALT700")
    ventana.id_medicion_var.set("MED700")
    ventana.descripcion_var.set("Evento preventivo")
    ventana.fecha_var.set("2026-05-24")
    ventana.nivel_var.set("Medio")
    ventana.estado_var.set("Activa")

    guardado = ventana.guardar_alerta()

    assert guardado is True
    assert len(controller.llamadas) == 1
    assert controller.llamadas[0]["id_alerta"] == "ALT700"
    assert "guardada correctamente" in ventana.estado.valor().lower()
    contenedor.destroy()
