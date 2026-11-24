# Onboarding: adaptar el plan de estudio a un usuario nuevo

Este repo es un plan de estudio para roles Senior (DevOps / Plataforma + IA, y
Senior Software Engineer) que se trabaja **con Claude Code** como tutor. Se
publicó sin los datos de su autor original: los nombres de personas y
empresas se reemplazaron por marcadores y todos los niveles de dominio están
en ⬜ (sin evaluar).

Claude: si `perfil/perfil.md` dice **PENDIENTE**, guía al usuario por estas
etapas **en orden**, haciendo **una pregunta por vez** y esperando cada
respuesta. No avances de etapa sin cerrar la anterior.

## Etapa 1 — Identidad y preferencias (5 min)

1. Pregunta el nombre con el que quiere aparecer en las presentaciones.
2. Pregunta el idioma y la variante (país, tú/usted/vos) para todas las
   respuestas; actualiza la sección "Idioma y tono" de `CLAUDE.md`.
3. Muestra la lista de preferencias de aprendizaje de `perfil/perfil.md` y
   pregunta cuáles quiere activar. Refléjalas en `CLAUDE.md`.

## Etapa 2 — Objetivo (5 min)

4. Rol objetivo, horizonte y horas por semana.
5. Ruta principal: `devops-senior/`, `swe-senior/` o ambas.
6. Pide una vacante real de referencia (enlace o texto pegado).

## Etapa 3 — Experiencia (10 min)

7. Pide la hoja de vida (pegada o como archivo) y resume la experiencia en
   la tabla de `perfil/perfil.md`. Datos sensibles → `perfil/perfil.privado.md`.
8. Con la vacante y la hoja de vida, llena
   `devops-senior/00-diagnostico/gap-analysis.md` (o el de `swe-senior/`).

## Etapa 4 — Examen diagnóstico (30-45 min)

9. Haz el diagnóstico general de la Fase 0 del roadmap
   (`devops-senior/00-diagnostico/roadmap.md`): 1-2 preguntas abiertas por
   tema, **de a una**, sin dar la respuesta antes de que el usuario conteste.
10. Califica cada tema con la escala ⬜/🔴/🟡/🟢/🔵 y llena
    `examenes/registro/progreso.md`, `examenes/registro/resultados.md`, el
    "Tablero de avance" del roadmap, la columna **Tú** de
    `glosario-ia-ofertas.md` y los niveles de `recursos/stack-herramientas.md`
    / `.html`.
11. Presenta el resultado como **lista numerada** con el nivel al lado de
    cada tema, y propone por dónde empezar.

## Etapa 5 — Personalizar el repo

12. Crea `perfil/marcadores.json` con los valores del usuario y ejecuta:

    ```bash
    python3 herramientas/personalizar.py            # muestra qué cambiaría
    python3 herramientas/personalizar.py --aplicar  # aplica los cambios
    ```

    El script solo reemplaza marcadores de **identidad** (`[TU_NOMBRE]`,
    `[TU_USUARIO_GITHUB]`, `[TU_CORREO]`, `[NOMBRE_REPO]`).
13. Los marcadores de **experiencia** (`[EMPRESA_0]`, `[EMPRESA_1]`,
    `[EMPRESA_2]`, `[PROYECTO_1]`, `[TU_CARRERA]`, `[TU_UNIVERSIDAD]`,
    `[UNIVERSIDAD_INTERCAMBIO]`) **no se reemplazan automáticamente**: el
    material de `presentaciones/`, `devops-senior/presentacion-*` y
    `pruebas-tecnicas/` cuenta la historia laboral del autor original, y
    cambiar solo el nombre de la empresa pondría en boca del usuario logros
    que no son suyos. Úsalo como **ejemplo de formato**: cuando el usuario
    prepare una entrevista o prueba, reescribe esas piezas con sus propias
    historias (formato STAR: Situación, Tarea, Acción, Resultado).
14. Muestra la estadística colectiva (`busqueda-empleo/estadisticas/README.md`):
    qué portales y familias de rol responden más. Úsala para priorizar dónde
    postular. Pregunta si quiere aportar sus números cuando tenga
    postulaciones (`busqueda-empleo/estadisticas/COMO-APORTAR.md`); si dice
    que sí, anótalo en `perfil/perfil.md` y recuérdaselo cada ~50 postulaciones.
15. Cambia el estado de `perfil/perfil.md` a **COMPLETO**, haz commit y push.

## Qué es de ejemplo y qué es reutilizable tal cual

| Reutilizable tal cual | Ejemplo a reescribir con tu historia |
|---|---|
| `devops-senior/temas/`, `swe-senior/temas/` | `devops-senior/presentacion-experiencia/` |
| `devops-senior/formulas-de-cero/`, `recursos/`, `certificaciones/` | `devops-senior/presentacion-entrevista-base/` |
| `devops-senior/examenes/README.md` (cómo pedir exámenes) | `pruebas-tecnicas/*/libreto-diapositivas.md` y las partes de "mi experiencia" |
| `busqueda-empleo/scripts/` (con tus `datos_privados.json` y `reglas.json` locales) | `devops-senior/temas/29-*`, `31-*` (preparación de entrevistas puntuales) |

> **Ojo con `pruebas-tecnicas/`:** son soluciones a pruebas reales de
> procesos de selección. Úsalas para estudiar; no las reenvíes como propias.
