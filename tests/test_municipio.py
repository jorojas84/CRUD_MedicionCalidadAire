import unittest
import os
from src.repositories.municipio_repository import MunicipioRepository
from src.controllers.municipio_controller import MunicipioController
from src.decorators.email_decorator import EmailNotificationDecorator
from src.exceptions.municipio_exceptions import (
    MunicipioNoEncontradoError,
    DatosMunicipioInvalidosError,
    ReglaNegocioMunicipioError
)

class TestMunicipioCRUD(unittest.TestCase):
    def setUp(self):
        self.test_file = 'data/test_municipios.json'
        self.repo = MunicipioRepository(self.test_file)
        self.repo.guardar_todos([])
        
        controlador_base = MunicipioController(self.repo)
        self.controller = EmailNotificationDecorator(controlador_base)
        self.controller_directo = controlador_base 

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    # 1. Prueba Inserción Exitosa
    def test_crear_municipio_exitoso(self):
        mun = self.controller.crear_municipio("11001", "Bogotá", "Cundinamarca", 7000000, 1775.0)
        self.assertEqual(mun.nombre, "Bogotá")

    # 2. Prueba de Validación: Población Negativa
    def test_crear_poblacion_invalida(self):
        with self.assertRaises(DatosMunicipioInvalidosError):
            self.controller.crear_municipio("05001", "Medellín", "Antioquia", -100, 382.0)

    # 3. Prueba de Validación: Área cero o negativa
    def test_crear_area_invalida(self):
        with self.assertRaises(DatosMunicipioInvalidosError):
            self.controller.crear_municipio("76001", "Cali", "Valle", 2000000, 0)

    # 4. Prueba de Validación: Campos vacíos
    def test_crear_campos_vacios(self):
        with self.assertRaises(DatosMunicipioInvalidosError):
            self.controller.crear_municipio("13001", "", "Bolívar", 1000000, 100.0)

    # 5. Prueba Consultar Exitosa
    def test_obtener_municipio_existente(self):
        self.controller.crear_municipio("47001", "Santa Marta", "Magdalena", 500000, 2393.0)
        mun = self.controller_directo.obtener_municipio("47001")
        self.assertIsNotNone(mun)
        self.assertEqual(mun.codigo_dane, "47001")

    # 6. Prueba Consultar Inexistente
    def test_obtener_municipio_no_existente(self):
        with self.assertRaises(MunicipioNoEncontradoError):
            self.controller_directo.obtener_municipio("99999")

    # 7. Prueba Actualizar Exitosa
    def test_actualizar_municipio_exitoso(self):
        self.controller.crear_municipio("15001", "Tunja", "Boyacá", 170000, 118.0)
        mun_actualizado = self.controller.actualizar_municipio("15001", "Tunja", "Boyacá", 180000, 120.0)
        self.assertEqual(mun_actualizado.poblacion, 180000)

    # 8. Prueba Actualizar Inexistente
    def test_actualizar_municipio_no_existente(self):
        with self.assertRaises(MunicipioNoEncontradoError):
            self.controller.actualizar_municipio("88888", "Falso", "Falso", 100, 10.0)

    # 9. Prueba Eliminar Exitosa (Población < 500,000)
    def test_eliminar_municipio_exitoso(self):
        self.controller.crear_municipio("25175", "Chía", "Cundinamarca", 130000, 79.0)
        self.controller_directo.eliminar_municipio("25175")
        with self.assertRaises(MunicipioNoEncontradoError):
            self.controller_directo.obtener_municipio("25175")

    # 10. Prueba REGLA DE NEGOCIO: Prohibir eliminar municipio Categoría Especial (> 500,000)
    def test_eliminar_municipio_regla_negocio(self):
        self.controller.crear_municipio("08001", "Barranquilla", "Atlántico", 1200000, 154.0)
        with self.assertRaises(ReglaNegocioMunicipioError):
            self.controller_directo.eliminar_municipio("08001")

if __name__ == '__main__':
    unittest.main()