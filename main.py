"""Punto de entrada principal de la Actividad 7."""

from src.views.medicion_calidad_aire_view import MedicionCalidadAireView


class _DummyView:
    def __init__(self, nombre: str) -> None:
        self._nombre = nombre

    def mostrar_menu(self) -> None:
        print(f"\n[Dummy] Para esta prueba el modulo {self._nombre} no esta disponible")


def _mostrar_menu_principal() -> None:
    print("\n--- Observatorio de Calidad del Aire ---")
    print("1. Modulo Estaciones")
    print("2. Modulo Municipios")
    print("3. Modulo Mediciones")
    print("4. Modulo Alertas")
    print("5. Salir")


def main() -> None:
    estacion_view = _DummyView("Estaciones")
    municipio_view = _DummyView("Municipios")
    medicion_view = MedicionCalidadAireView()
    alerta_view = _DummyView("Alertas")

    while True:
        _mostrar_menu_principal()
        opcion = input("Seleccione una opcion: ").strip()
        if opcion == "1":
            estacion_view.mostrar_menu()
        elif opcion == "2":
            municipio_view.mostrar_menu()
        elif opcion == "3":
            medicion_view.mostrar_menu()
        elif opcion == "4":
            alerta_view.mostrar_menu()
        elif opcion == "5":
            print("Saliendo del sistema...")
            break
        else:
            print("Opcion invalida. Intente de nuevo.")


if __name__ == "__main__":
    main()
