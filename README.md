# Observatorio Calidad Aire

Proyecto base en Python con arquitectura MVC simple y persistencia JSON.

## Instalacion

1. Crear y activar entorno virtual (opcional):

```bash
python -m venv .venv
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecucion

Desde la carpeta `observatorio_calidad_aire`, ejecutar:

```bash
python -m src.main
```

## Estructura

- `src/models`: entidades del dominio.
- `src/repositories`: acceso a datos en archivos JSON.
- `src/controllers`: logica de coordinacion entre vista consola y repositorio.
- `src/exceptions`: excepciones personalizadas.
- `src/views`, `src/services`, `src/decorators`: reservados para futuras actividades.
- `data/alertas.json`: persistencia de alertas.
- `tests`: pruebas unitarias con `pytest`.

## Modulo implementado

Se implementa completamente el modulo `AlertaAmbiental`:

- Modelo con validaciones y regla de negocio (`nivel = Alto` fuerza `estado = Activa`).
- Repository con CRUD completo y persistencia JSON.
- Controller para conectar `main.py` con repository.
- Menu de consola para pruebas manuales.
- Pruebas unitarias del modulo.

Las entidades `estacion_ambiental`, `municipio` y `medicion_calidad_aire` quedan como placeholders para otros integrantes.

## Pruebas unitarias

Ejecutar desde la raiz del proyecto:

```bash
pytest
```
# EstacionAmbiental module - Auto-test with pre-commit hook
