"""Vista de consola para modulo MedicionCalidadAire."""

from src.controllers.medicion_calidad_aire_controller import MedicionCalidadAireController
from src.exceptions.custom_exceptions import DatoInvalidoError, RegistroDuplicadoError, RegistroNoEncontradoError


class MedicionCalidadAireView:
    """Interfaz de consola para CRUD de mediciones."""

    def __init__(self, controller=None):
        self.controller = controller or MedicionCalidadAireController()

    def mostrar_menu(self):
        while True:
            print("\n--- Menu Mediciones ---")
            print("1. Crear medicion")
            print("2. Listar mediciones")
            print("3. Buscar medicion")
            print("4. Actualizar medicion")
            print("5. Eliminar medicion")
            print("6. Volver")
            opcion = input("Seleccione una opcion: ").strip()

            try:
                if opcion == "1":
                    medicion = self.controller.crear_medicion(*self._pedir_datos())
                    print(f"Medicion creada: {medicion.id_medicion} - Nivel: {medicion.nivel}")
                elif opcion == "2":
                    mediciones = self.controller.listar_mediciones()
                    if not mediciones:
                        print("No hay mediciones registradas.")
                    for medicion in mediciones:
                        print(medicion.to_dict())
                elif opcion == "3":
                    id_medicion = input("ID medicion a buscar: ").strip()
                    medicion = self.controller.buscar_medicion(id_medicion)
                    if medicion is None:
                        print("Medicion no encontrada.")
                    else:
                        print(medicion.to_dict())
                elif opcion == "4":
                    id_medicion = input("ID medicion a actualizar: ").strip()
                    medicion = self.controller.actualizar_medicion(*self._pedir_datos(id_medicion))
                    print(f"Medicion actualizada: {medicion.id_medicion} - Nivel: {medicion.nivel}")
                elif opcion == "5":
                    id_medicion = input("ID medicion a eliminar: ").strip()
                    self.controller.eliminar_medicion(id_medicion)
                    print("Medicion eliminada correctamente.")
                elif opcion == "6":
                    return
                else:
                    print("Opcion invalida.")
            except (DatoInvalidoError, RegistroDuplicadoError, RegistroNoEncontradoError) as error:
                print(f"Error: {error}")

    def _pedir_datos(self, id_medicion_predefinido=None):
        id_medicion = id_medicion_predefinido if id_medicion_predefinido else input("ID medicion: ").strip()
        id_estacion = input("ID estacion: ").strip()
        contaminante = input("Contaminante: ").strip()
        valor = float(input("Valor: ").strip())
        unidad = input("Unidad: ").strip()
        fecha = input("Fecha (YYYY-MM-DD): ").strip()
        return id_medicion, id_estacion, contaminante, valor, unidad, fecha
