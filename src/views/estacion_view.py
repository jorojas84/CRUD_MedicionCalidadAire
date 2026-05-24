"""Vista de consola para modulo EstacionAmbiental."""

from src.controllers.estacion_controller import EstacionController
from src.exceptions.custom_exceptions import RegistroNoEncontradoError
from src.models.estacion_ambiental import DuplicateEstacionError, EstacionValidationError


class EstacionView:
    """Interfaz de consola para CRUD de estaciones."""

    def __init__(self, controller=None):
        self.controller = controller or EstacionController()

    def mostrar_menu(self):
        while True:
            print("\n--- Menu Estaciones ---")
            print("1. Crear estacion")
            print("2. Listar estaciones")
            print("3. Buscar estacion")
            print("4. Actualizar estacion")
            print("5. Eliminar estacion")
            print("6. Volver")
            opcion = input("Seleccione una opcion: ").strip()
            try:
                if opcion == "1":
                    estacion = self.controller.crear_estacion(*self._pedir_datos())
                    print(f"Estacion creada: {estacion.id_estacion}")
                elif opcion == "2":
                    estaciones = self.controller.listar_estaciones()
                    if not estaciones:
                        print("No hay estaciones registradas.")
                    for estacion in estaciones:
                        print(estacion.to_dict())
                elif opcion == "3":
                    id_estacion = input("ID estacion a buscar: ").strip()
                    estacion = self.controller.buscar_estacion(id_estacion)
                    if estacion is None:
                        print("Estacion no encontrada.")
                    else:
                        print(estacion.to_dict())
                elif opcion == "4":
                    id_estacion = input("ID estacion a actualizar: ").strip()
                    estacion = self.controller.actualizar_estacion(*self._pedir_datos(id_estacion))
                    print(f"Estacion actualizada: {estacion.id_estacion}")
                elif opcion == "5":
                    id_estacion = input("ID estacion a eliminar: ").strip()
                    self.controller.eliminar_estacion(id_estacion)
                    print("Estacion eliminada correctamente.")
                elif opcion == "6":
                    return
                else:
                    print("Opcion invalida.")
            except (EstacionValidationError, DuplicateEstacionError, RegistroNoEncontradoError) as error:
                print(f"Error: {error}")

    def _pedir_datos(self, id_estacion_predefinido=None):
        id_estacion = id_estacion_predefinido if id_estacion_predefinido else input("ID estacion: ").strip()
        nombre = input("Nombre: ").strip()
        municipio = input("Municipio: ").strip()
        tipo_estacion = input("Tipo estacion: ").strip()
        estado = input("Estado (Activa/Inactiva): ").strip()
        return id_estacion, nombre, municipio, tipo_estacion, estado
