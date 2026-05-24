# Evidencia Individual - Actividad 7

## Datos generales

- Estudiante: **Liz Giselle Tuiran Alvarez**
- Rama de trabajo: `dev_ltuiran07`
- Entidad asignada: `AlertaAmbiental`
- Proyecto: `observatorio_calidad_aire`

## Alcance desarrollado

Para la Actividad 7 se implemento el modulo `AlertaAmbiental` con enfoque MVC + Repository/DAO y persistencia en JSON, incluyendo:

- CRUD completo: crear, listar, buscar, actualizar y eliminar.
- Validaciones de datos de entrada.
- Excepciones personalizadas.
- Regla de negocio: si `nivel` es `Alto`, la alerta queda en estado `Activa`.
- Pruebas unitarias del modulo y pruebas de integracion del proyecto.

## Evidencias capturadas

Las capturas se encuentran en la carpeta `Evidencias/` y corresponden a:

1. `Evidencias/01 rama activa.jpg` - Rama activa (`dev_ltuiran07`).
2. `Evidencias/02 Ejecucion de pruebas.jpg` - Ejecucion de `pytest -v`.
3. `Evidencias/03 menu principal.jpg` - Menu principal del sistema.
4. `Evidencias/04 menu alertas.jpg` - Menu del modulo Alertas.
5. `Evidencias/05 CRUD CREAR.jpg` - Operacion crear alerta.
6. `Evidencias/06 CRUD LISTAR.jpg` - Operacion listar alertas.
7. `Evidencias/07 CRUD ACTUALIZAR.jpg` - Operacion actualizar alerta.
8. `Evidencias/08 CRUD ELIMINAR.jpg` - Operacion eliminar alerta.
9. `Evidencias/08 REGLA DE NEGOCIO DE ALERTA.jpg` - Validacion de regla de negocio (nivel alto => activa).
10. `Evidencias/09 JSON REGISTROS GUARDADOS.jpg` - Persistencia en `data/alertas.json`.

### Visualizacion de evidencias

![01 rama activa](../../Evidencias/01%20rama%20activa.jpg)

![02 ejecucion de pruebas](../../Evidencias/02%20Ejecucion%20de%20pruebas.jpg)

![03 menu principal](../../Evidencias/03%20menu%20principal.jpg)

![04 menu alertas](../../Evidencias/04%20menu%20alertas.jpg)

![05 CRUD crear](../../Evidencias/05%20CRUD%20CREAR.jpg)

![06 CRUD listar](../../Evidencias/06%20CRUD%20LISTAR.jpg)

![07 CRUD actualizar](../../Evidencias/07%20CRUD%20ACTUALIZAR.jpg)

![08 CRUD eliminar](../../Evidencias/08%20CRUD%20ELIMINAR.jpg)

![08 regla de negocio alerta](../../Evidencias/08%20REGLA%20DE%20NEGOCIO%20DE%20ALERTA.jpg)

![09 json registros guardados](../../Evidencias/09%20JSON%20REGISTROS%20GUARDADOS.jpg)

## Resultado de pruebas

- Ejecucion de pruebas unitarias: `pytest -v`
- Resultado general del proyecto: **40 passed**.

## Conclusiones

Se cumple con los criterios tecnicos de la Actividad 7 para la entidad `AlertaAmbiental`: patron MVC, DAO/Repository, persistencia JSON, validaciones, excepciones y evidencia de pruebas unitarias.
