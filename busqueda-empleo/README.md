# Búsqueda de empleo: herramientas

Scripts para postular por lotes con salida mínima (pocos tokens), más un
registro de postulaciones. **No pongas aquí datos de contacto, salario ni
respuestas personales**: viven solo en tu carpeta local de ejecución
(`datos_privados.json` y `reglas.json`, ambos en `.gitignore`). Hay
ejemplos en `scripts/*.example.json`.

## Piezas

| Pieza | Dónde | Para qué |
|---|---|---|
| Tablero de vacantes (opcional) | Un artefacto de claude.ai con base de datos (colecciones `vacantes`, `respuestas`, `meta/busqueda`) | Estado de cada vacante y banco de respuestas. Pídele a Claude que te lo cree. |
| Scripts (fuente) | `busqueda-empleo/scripts/` (este repo) | Se copian a tu carpeta local para ejecutarlos. |
| Scripts (ejecución) | Tu carpeta local, p. ej. `C:/Users/<usuario>/Documents/Postulaciones/lote/` | Junto con `datos_privados.json` y `reglas.json`. |
| Chrome de postulaciones | Chrome con depuración remota en el puerto 9222 y un perfil propio | Sesiones abiertas en los portales (Computrabajo, LinkedIn, etc.). Los scripts se conectan por CDP (Chrome DevTools Protocol). |
| Registro | `aplicaciones-log.md` | Una fila por postulación. |
| Estadística colectiva | [`estadisticas/`](estadisticas/README.md) | Resultados agregados y anónimos de todas las personas que aportan. Para sumar los tuyos: [`COMO-APORTAR.md`](estadisticas/COMO-APORTAR.md). |

## Reglas que no cambian

- Aprobar una vacante en el tablero autoriza enviar la postulación completa.
- Honestidad: solo se afirma lo que está en el banco de respuestas; si no está, se te pregunta a ti.
- Nunca se comparte cédula, fecha de nacimiento ni dirección exacta; nunca se aceptan términos de
  privacidad, tratamiento de datos ni consentimientos legales por ti (esas vacantes quedan "Requiere tu acción").
- CAPTCHA, cuentas nuevas, contraseñas y pagos los haces tú.
- Formato del CV: cada trabajo en 4 líneas (cargo / empresa / ciudad / fechas) para que los ATS
  (Applicant Tracking System) lo lean bien.
- Tu salario esperado y tus pisos van en `datos_privados.json`, no aquí.

## Política y compuertas

**Cantidad primero, calidad después.** Antes de postular solo se aplican filtros baratos; el trabajo de
calidad (agente revisor, verificación ATS, investigación de la empresa) se hace cuando hay entrevista.
Rúbrica adaptada de [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search).

Compuertas (`comun.compuerta()`), la primera que falla decide:

1. **Ubicación:** tu país (o una región que lo incluya: LATAM, mundial) debe estar entre las
   ubicaciones. Ajusta `PAISES` en `comun.py` a tu caso.
2. **Modalidad × salario:** presencial solo por encima de un piso alto; híbrida se descarta por debajo
   de un piso medio; remota siempre pasa. Salario no publicado → pasa. Pisos en `datos_privados.json`.
3. **Idioma:** si la vacante pide inglés C2 o nativo → `MARCADA` (decides tú); si exige otro idioma → `DESCARTADA`.

`revisar_compuertas.py CARPETA_EXPORT [PREFIJO]` revisa un export del tablero sin abrir el navegador
y deja `resultados_compuertas.json`.

## Flujo barato por lotes

1. Exportar del tablero solo lo necesario (por id o con una consulta a una carpeta local).
2. Ejecutar el script del portal; imprime **una línea por vacante**: `ENVIADA`, `YA`, `DESCARTADA`/`MARCADA`,
   `PREGUNTAS`, `BLOQUEADA`, `LISTA`.
3. `PREGUNTAS` = hay preguntas sin regla: se anotan en la vacante para que las respondas una vez;
   luego se agrega la regla a `reglas.json` y se reintenta. Nunca improvisar respuestas.
4. Actualizar el tablero en un solo lote.

Scripts listos: `postular_ct.py` (Computrabajo). Pendientes con el mismo patrón: GetOnBoard, LinkedIn
Easy Apply (pausas largas, máximo 10 por día), Greenhouse y BambooHR.

## Ahorro de tokens

- Sesión nueva con este README en vez de seguir un chat largo.
- Scripts con salida mínima; nada de capturas de pantalla salvo que algo falle sin explicación.
- Si Chrome no responde: `comun.destrabar()` activa (no cierra) las pestañas colgadas.
