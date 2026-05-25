"""Excepciones personalizadas para el modulo Municipio."""


class MunicipioError(Exception):
    """Error base para operaciones de municipios."""


class MunicipioNoEncontradoError(MunicipioError):
    """Se lanza cuando no se encuentra un municipio."""


class DatosMunicipioInvalidosError(MunicipioError):
    """Se lanza cuando los datos de municipio son invalidos."""


class ReglaNegocioMunicipioError(MunicipioError):
    """Se lanza cuando se incumple una regla de negocio del modulo."""
