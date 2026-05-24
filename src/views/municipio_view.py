"""Vista de consola para el modulo Municipio."""

from src.controllers.municipio_controller import MunicipioController
from src.exceptions.municipio_exceptions import (
    DatosMunicipioInvalidosError,
    MunicipioNoEncontradoError,
    ReglaNegocioMunicipioError,
)


class MunicipioView:
    """Interfaz de consola para CRUD de municipios."""

    def __init__(self, controller=None):
        self.controller = controller or MunicipioController()

    def mostrar_menu(self):
        while True:
            print("\n--- Menu Municipios ---")
            print("1. Crear municipio")
            print("2. Listar municipios")
            print("3. Buscar municipio")
            print("4. Actualizar municipio")
            print("5. Eliminar municipio")
            print("6. Volver")

            opcion = input("Seleccione una opcion: ").strip()

            try:
                if opcion == "1":
                    datos = self._pedir_datos()
                    municipio = self.controller.crear_municipio(*datos)
                    print(f"Municipio creado: {municipio.id_municipio}")
                elif opcion == "2":
                    municipios = self.controller.listar_municipios()
                    if not municipios:
                        print("No hay municipios registrados.")
                    for municipio in municipios:
                        print(municipio.to_dict())
                elif opcion == "3":
                    id_municipio = input("ID municipio a buscar: ").strip()
                    municipio = self.controller.buscar_municipio(id_municipio)
                    print(municipio.to_dict())
                elif opcion == "4":
                    id_municipio = input("ID municipio a actualizar: ").strip()
                    datos = self._pedir_datos(id_municipio)
                    municipio = self.controller.actualizar_municipio(*datos)
                    print(f"Municipio actualizado: {municipio.id_municipio}")
                elif opcion == "5":
                    id_municipio = input("ID municipio a eliminar: ").strip()
                    self.controller.eliminar_municipio(id_municipio)
                    print("Municipio eliminado correctamente.")
                elif opcion == "6":
                    return
                else:
                    print("Opcion invalida. Intente de nuevo.")
            except (
                DatosMunicipioInvalidosError,
                MunicipioNoEncontradoError,
                ReglaNegocioMunicipioError,
            ) as error:
                print(f"Error: {error}")

    def _pedir_datos(self, id_municipio_predefinido=None):
        id_municipio = (
            id_municipio_predefinido
            if id_municipio_predefinido
            else input("ID municipio: ").strip()
        )
        nombre = input("Nombre: ").strip()
        departamento = input("Departamento: ").strip()
        region = input("Region: ").strip()
        estado = input("Estado (Activo/Inactivo): ").strip()
        return id_municipio, nombre, departamento, region, estado
