# Evidencia Individual - Jose

- **Entidad:** `MedicionCalidadAire` (clase base abstracta) +
  `MedicionCalidadAirePM` (subclase concreta para PM10 / PM2.5).

## Archivos principales

- `src/models/medicion_calidad_aire.py` — modelo polimorfico de mediciones.
- `src/repositories/medicion_calidad_aire_repository.py` — persistencia JSON.
- `src/controllers/medicion_calidad_aire_controller.py` — casos de uso.
- `src/views/medicion_calidad_aire_view.py` — menu de consola y prompts.
- `src/factories/medicion_factory.py` — registro `tipo -> clase` para crear
  y deserializar mediciones (patron Factory).
- `data/mediciones.json` — datos de ejemplo (4 AUTOMATICAS + 3 MANUALES).
- `tests/test_medicion_repository.py` — pruebas del repositorio (10).
- `tests/test_medicion_modelo.py` — pruebas del modelo: clasificacion ICA y
  validaciones (10).
- `tests/test_medicion_controller.py` — pruebas del controller con vista
  stub (10).

## Reglas de negocio

- **Clasificacion ICA** segun Res. 2254/2017 (Tabla 6). Cada subclase
  declara sus propios puntos de corte; la base resuelve el nivel con la
  misma logica. Categorias: `Buena`, `Aceptable`,
  `Daniña a la salud de grupos sensibles`, `Daniña a la salud`,
  `Muy daniña a la salud`, `Peligrosa`.
- **Origen del dato:** una medicion es `MANUAL` (creada por el usuario)
  o `AUTOMATICO` (proveniente del sensor). Las automaticas son
  inmutables y no pueden actualizarse ni eliminarse.
- **Integridad referencial:** al crear una medicion manual la vista
  valida en linea que el `codigo_dane_municipio` y el `id_estacion`
  existan en sus respectivos repositorios.
- **Validaciones del modelo:** id, codigo DANE e id estacion no vacios;
  fecha tipo `datetime`; valor numerico positivo; origen valido.

## Patrones aplicados

- **MVC:** modelo, vista y controlador separados.
- **Repository:** `IMedicionRepository` define el contrato CRUD;
  `MedicionRepository` lo implementa sobre JSON.
- **Factory:** `MedicionFactory` centraliza el mapa `tipo -> clase`
  concreta. Agregar un contaminante nuevo (SO2, NO2, CO, O3...) requiere
  unicamente registrar su subclase en la factory (OCP).

## Datos de ejemplo

`data/mediciones.json` ya trae 7 registros listos para probar el menu:
4 automaticas y 3 manuales sobre municipios `05001` (Medellin), `11001`
(Bogota) y `76001` (Cali), con sus estaciones correspondientes en
`data/estaciones.json` y `data/municipios.json`.

## Como ejecutar

```bash
python -m src.main
```

Luego seleccionar la opcion **3. Modulo Mediciones**. El menu permite:

1. Crear medicion (manual) — valida tipo, municipio, estacion, fecha y valor.
2. Listar mediciones.
3. Actualizar medicion — solo MANUALES.
4. Eliminar medicion — solo MANUALES.
5. Recalcular niveles.
6. Volver.

## Evidencias a adjuntar

1. Pantallazo del CRUD en consola (crear/listar/actualizar/eliminar).
2. Pantallazo de `pytest -v` mostrando las **30 pruebas** del modulo
   de mediciones pasando.

```bash
pytest tests/test_medicion_repository.py tests/test_medicion_modelo.py tests/test_medicion_controller.py -v
```
