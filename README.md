# Observatorio Calidad Aire

Sistema de gestion y consulta de calidad del aire a nivel municipal.

## Descripcion del sistema

El observatorio administra un catalogo de **municipios** y **estaciones
de monitoreo**, donde cada estacion esta asociada a un municipio. Sobre
ese catalogo se registran **mediciones** de contaminantes criterio
(PM2.5, PM10, etc.) y se administran **alertas ambientales**.

## Arquitectura y enfoque

El proyecto se desarrolla con:

- Patron **MVC** (Model - View - Controller).
- Patron **Repository/DAO** para persistencia.
- Archivos **JSON** como almacenamiento local.
- Validaciones de dominio y excepciones personalizadas.

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

El menu principal actual permite acceder a:

1. Modulo Estaciones
2. Modulo Municipios
3. Modulo Mediciones
4. Modulo Alertas
5. Salir

## Estructura del proyecto

- `src/models`: entidades del dominio.
- `src/repositories`: acceso a datos en archivos JSON.
- `src/controllers`: logica de coordinacion entre vistas y repositorios.
- `src/views`: menus de consola por modulo.
- `src/exceptions`: excepciones personalizadas.
- `data/`: archivos JSON de persistencia.
- `tests/`: pruebas unitarias con `pytest`.
- `entregables/actividad7/`: evidencias individuales por integrante.

## Modulos implementados (Actividad 7)

Cada modulo incluye modelo, repository, controller, view, validaciones,
reglas de negocio y pruebas unitarias.

### EstacionAmbiental

- CRUD completo sobre `data/estaciones.json`.
- Validaciones de campos obligatorios y estado `Activa/Inactiva`.
- Regla de negocio: no permitir estaciones duplicadas por `id_estacion`.

### Municipio

- CRUD completo sobre `data/municipios.json`.
- Validaciones de campos obligatorios y estado `Activo/Inactivo`.
- Regla de negocio: no permitir municipios duplicados por `id_municipio`.

### MedicionCalidadAire

- CRUD completo sobre `data/mediciones.json`.
- Validaciones de campos obligatorios y valor no negativo.
- Regla de negocio: clasificacion automatica por nivel:
  - menor a 50: `Bajo`
  - entre 50 y 100: `Medio`
  - mayor a 100: `Alto`

### AlertaAmbiental

- CRUD completo sobre `data/alertas.json`.
- Validaciones de campos obligatorios, nivel y estado permitidos.
- Regla de negocio: si el `nivel` es `Alto`, el `estado` final es `Activa`.

## Excepciones personalizadas

- `DatoInvalidoError`
- `RegistroDuplicadoError`
- `RegistroNoEncontradoError`
- `ArchivoInvalidoError`

## Pruebas unitarias

Ejecutar desde la raiz del proyecto:

```bash
pytest -v
```

Estado actual de la Actividad 7:

- 10 pruebas de AlertaAmbiental
- 10 pruebas de EstacionAmbiental
- 10 pruebas de Municipio
- 10 pruebas de MedicionCalidadAire

Total: **40 pruebas unitarias**.

## Integrantes y entidad asignada

| Integrante | Entidad | Estado |
|---|---|---|
| Liz Giselle Tuiran Alvarez | AlertaAmbiental | Implementado |
| Integrante 2 | EstacionAmbiental | Implementado |
| Integrante 3 | Municipio | Implementado |
| Integrante 4 | MedicionCalidadAire | Implementado |

## Nota de continuidad

La prioridad actual corresponde a **Actividad 7**. La base quedo lista
para iniciar **Actividad 8 (GoF)** en la siguiente fase sin afectar la
estabilidad del sistema actual.
