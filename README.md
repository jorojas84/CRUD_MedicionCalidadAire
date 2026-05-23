# Observatorio Calidad Aire

Sistema de gestion y consulta de calidad del aire a nivel municipal.

## Descripcion del sistema

El observatorio administra un catalogo de **municipios** y **estaciones
de monitoreo**, donde cada estacion esta asociada a un municipio. Sobre
ese catalogo se registran **mediciones** de contaminantes criterio
(PM2.5, PM10, etc.) provenientes de los sensores en campo, y se
**generan alertas** de forma automatica cuando un valor supera los
umbrales establecidos por la normativa vigente (Res. 2254 de 2017).

### Origen de las mediciones

Las mediciones llegan al sistema por dos vias y reciben un tratamiento
distinto segun su procedencia:

- **Automaticas (sensor)**: se ingieren desde un archivo de datos.
  Son **inmutables**: no pueden modificarse ni eliminarse, garantizando
  trazabilidad de la fuente original.
- **Manuales (operador)**: las registra un empleado autorizado. Admiten
  edicion y borrado posterior.

### Roles

| Rol | Capacidades |
|---|---|
| **Empleado** | Administra el catalogo (municipios y estaciones), registra mediciones y alertas manuales, y gestiona el ciclo de vida (editar/eliminar) de los registros que el mismo crea. |
| **Usuario** | Solo consulta: estado actual del aire por municipio o estacion y alertas activas. No tiene capacidades de escritura. |

---


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

## Modulos implementados

El proyecto se desarrolla en equipo. Cada modulo sigue el patron
MVC + Repository y cuenta con pruebas unitarias propias.

### `AlertaAmbiental`
- Modelo con validaciones y regla de negocio (`nivel = Alto` fuerza
  `estado = Activa`).
- Repository con CRUD completo y persistencia JSON.
- Controller conectado al `main.py`.
- Menu de consola y pruebas unitarias.

### `Municipio`
- Modelo con `codigo_dane` como identificador unico.
- Repository con CRUD sobre `data/municipios.json`.
- Controller integrado con el patron Decorator (`EmailNotificationDecorator`)
  para notificaciones por correo.
- Vista de consola con menu propio.

### `EstacionAmbiental`
- Modelo con validaciones (estado `Activa/Inactiva`, normalizacion de
  campos, IDs unicos).
- Repository con CRUD sobre `data/estaciones.json` y escritura atomica
  (archivo temporal + `os.replace`).
- Cobertura de pruebas: modelo, repositorio y persistencia JSON.

### `MedicionCalidadAire`
- Modelo abstracto que clasifica el ICA segun los puntos de corte de la
  **Res. 2254 de 2017 (Tabla 6)**; cada contaminante criterio se
  implementa como subclase concreta (hoy `MedicionCalidadAirePM` para
  PM10 y PM2.5; CO/SO2/NO2/O3 se agregan sin modificar el resto).
- Reglas de origen del dato: las mediciones **AUTOMATICAS** del sensor
  son inmutables; las **MANUALES** del operador admiten edicion y
  borrado.
- Repository con CRUD sobre `data/mediciones.json` y polimorfismo en la
  deserializacion (recupera la subclase concreta segun `tipo`).
- Controller que orquesta CRUD + sincronizacion del sensor (no
  sobreescribe mediciones manuales) y **autorregistra estaciones
  desconocidas** consultando `EstacionRepository`.
- Vista de consola polimorfica que se adapta a cualquier subclase.

## Pruebas unitarias

Ejecutar desde la raiz del proyecto:

```bash
pytest
```