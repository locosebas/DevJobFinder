# Cómo aportar a la estadística colectiva

La idea: cada persona que use este plan para buscar empleo suma **sus números**
(nunca sus datos) a una estadística común. Así todos ven qué portales y qué
tipos de rol responden de verdad, qué modalidad y salarios se publican y qué
tecnologías aparecen más.

## Qué se comparte y qué no

| Se comparte (agregado) | Nunca se comparte |
|---|---|
| Conteos por estado: revisadas, descartadas, postuladas, con respuesta, con entrevista | Nombre de empresas, títulos exactos de vacantes, enlaces |
| Tasa de respuesta por portal y por familia de rol | Notas, respuestas a formularios, cartas, CV |
| Modalidad, región, seniority, rango de salario publicado | Tu salario esperado, tus pisos de compuertas |
| Tecnologías detectadas (solo el nombre canónico) | Dónde usaste cada tecnología, tus empleadores |
| Mes (no día) | Nombres de reclutadores, correos, teléfonos |
| Alias, rol objetivo, rango de años, país (opcionales) | Tu nombre |

Toda categoría con menos de 3 vacantes se suma en "Otro", para que no se
pueda reconocer una vacante puntual.

## Pasos

1. **Exporta tu tablero de vacantes** a una carpeta local (un `.json` por
   vacante). Con Claude Code: *"exporta la colección `vacantes` de mi tablero
   a una carpeta local"* (usa ArtifactData con `out_dir`). También sirve un
   único `.json` con una lista de vacantes que tenga los campos de abajo.
2. **Genera tu aporte en modo simulación** y revísalo:

   ```bash
   cd busqueda-empleo/estadisticas
   ROL_OBJETIVO="SRE" ANIOS_EXPERIENCIA="5-8" PAIS="México" \
     python3 estadisticas.py aporte RUTA_A_TU_EXPORT
   ```

   Las tres variables son opcionales. Si no pones `--alias`, se genera uno
   aleatorio.
3. **Escríbelo y actualiza el resumen:**

   ```bash
   python3 estadisticas.py aporte RUTA_A_TU_EXPORT --alias mi-alias --escribir
   python3 estadisticas.py resumen
   ```

4. **Envíalo a [locosebas/DevJobFinder](https://github.com/locosebas/DevJobFinder)**
   con un pull request desde tu fork que solo toque
   `busqueda-empleo/estadisticas/aportes/<tu-alias>.json` y
   `busqueda-empleo/estadisticas/README.md`. Hazlo desde una rama aparte
   (p. ej. `aporte/<tu-alias>`) que solo tenga esos dos archivos, no desde
   la rama donde guardas tu perfil y tu avance. Un chequeo automático
   valida el aporte y el mantenedor lo aprueba. Para actualizarlo más adelante,
   repite el paso 3 con el **mismo alias**: tu archivo se reemplaza, no se
   duplica.

## Formato mínimo de cada vacante

```json
{
  "titulo": "Senior DevOps Engineer",
  "fuente": "LinkedIn",
  "estado": "enviada",
  "modalidad": "Remoto",
  "ubicacion": "LATAM",
  "salario": "USD 4.000–5.000 al mes",
  "coincidencias": ["Kubernetes", "AWS", "Terraform"],
  "encaje": 72,
  "enviadaEl": "2026-10-15"
}
```

Valores de `estado`: `aprobada` / `requiere_accion` (pendientes),
`descartada` (no pasó las compuertas), `enviada`, `contacto`, `en_proceso`,
`entrevista`, `aceptada`, `rechazada`. El script ignora cualquier otro campo
(empresa, url, notas…), así que no hace falta limpiarlos a mano.
