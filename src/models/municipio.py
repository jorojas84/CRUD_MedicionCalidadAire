from dataclasses import dataclass

@dataclass
class Municipio:
    codigo_dane: str
    nombre: str
    departamento: str
    poblacion: int
    area_km2: float

    def to_dict(self) -> dict:
        return {
            "codigo_dane": self.codigo_dane,
            "nombre": self.nombre,
            "departamento": self.departamento,
            "poblacion": self.poblacion,
            "area_km2": self.area_km2
        }

    @staticmethod
    def from_dict(data: dict) -> 'Municipio':
        return Municipio(
            codigo_dane=data["codigo_dane"],
            nombre=data["nombre"],
            departamento=data["departamento"],
            poblacion=data["poblacion"],
            area_km2=data["area_km2"]
        )