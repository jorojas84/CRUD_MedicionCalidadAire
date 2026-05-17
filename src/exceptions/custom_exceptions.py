"""Definicion de excepciones personalizadas."""


class DatoInvalidoError(Exception):
    """Se lanza cuando un dato no cumple validaciones."""


class RegistroDuplicadoError(Exception):
    """Se lanza cuando se intenta crear un registro repetido."""


class RegistroNoEncontradoError(Exception):
    """Se lanza cuando no se encuentra un registro solicitado."""
