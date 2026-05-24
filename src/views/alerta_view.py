"""Vista de consola para modulo AlertaAmbiental."""

from src.controllers.alerta_controller import AlertaController
from src.exceptions.custom_exceptions import DatoInvalidoError, RegistroDuplicadoError, RegistroNoEncontradoError


class AlertaView:
    """Interfaz de consola para CRUD de alertas."""

    def __init__(self, controller=None):
        self.controller = controller or AlertaController()

    def mostrar_menu(self):
        while True:
            print("\n--- Menu Alertas ---")
            print("1. Crear alerta")
            print("2. Listar alertas")
            print("3. Buscar alerta")
            print("4. Actualizar alerta")
            print("5. Eliminar alerta")
            print("6. Volver")
            opcion = input("Seleccione una opcion: ").strip()

            try:
                if opcion == "1":
                    alerta = self.controller.crear_alerta(*self._pedir_datos())
                    print(f"Alerta creada: {alerta.id_alerta}")
                elif opcion == "2":
                    alertas = self.controller.listar_alertas()
                    if not alertas:
                        print("No hay alertas registradas.")
                    for alerta in alertas:
                        print(alerta.to_dict())
                elif opcion == "3":
                    id_alerta = input("ID alerta a buscar: ").strip()
                    alerta = self.controller.buscar_alerta(id_alerta)
                    print(alerta.to_dict() if alerta else "Alerta no encontrada.")
                elif opcion == "4":
                    id_alerta = input("ID alerta a actualizar: ").strip()
                    alerta = self.controller.actualizar_alerta(*self._pedir_datos(id_alerta))
                    print(f"Alerta actualizada: {alerta.id_alerta}")
                elif opcion == "5":
                    id_alerta = input("ID alerta a eliminar: ").strip()
                    self.controller.eliminar_alerta(id_alerta)
                    print("Alerta eliminada correctamente.")
                elif opcion == "6":
                    return
                else:
                    print("Opcion invalida.")
            except (DatoInvalidoError, RegistroDuplicadoError, RegistroNoEncontradoError) as error:
                print(f"Error: {error}")

    def _pedir_datos(self, id_alerta_predefinido=None):
        id_alerta = id_alerta_predefinido if id_alerta_predefinido else input("ID alerta: ").strip()
        id_medicion = input("ID medicion: ").strip()
        nivel = input("Nivel (Bajo/Medio/Alto): ").strip()
        descripcion = input("Descripcion: ").strip()
        fecha = input("Fecha (YYYY-MM-DD): ").strip()
        estado = input("Estado (Activa/Cerrada): ").strip()
        return id_alerta, id_medicion, nivel, descripcion, fecha, estado
