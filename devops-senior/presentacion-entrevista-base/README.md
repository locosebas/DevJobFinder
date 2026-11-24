# Presentación base para entrevistas (DevOps / Plataforma)

Presentación en inglés que se usa como **base para la mayoría de las
entrevistas**: experiencia ([EMPRESA_1], [EMPRESA_2]) con íconos de las
herramientas, preguntas técnicas con respuestas modelo y preguntas para el
entrevistador. Las notas del presentador tienen el guion en inglés y tips en
español ("ES:").

- **Presentación publicada (Slides):** (enlace a tu artefacto publicado)
- Creada para la entrevista del 2026-11-04 (ver `../temas/31-entrevista-2026-11-04/`).

## Estructura (24 diapositivas)

| Bloque | Diapositivas (`project/slides/<id>.html`) |
|---|---|
| Intro | `cover`, `journey`, `toolbox` |
| [EMPRESA_1] | `empresa1` (CI/CD), `empresa1obs` (observabilidad: Grafana + alertas/on-call), `empresa1int` (SSO/OIDC con Entra ID, proveedores externos, CI) |
| [EMPRESA_2] | `empresa2` (PaaS de cómputo), `empresa2terraform` (módulos, state/backends, migraciones), `empresa2triage` + `empresa2triage2` (diagnóstico de tickets de Zendesk con Claude: RAG + MCP, certezas/hipótesis, **no auto-resuelve**), `ops` |
| Preguntas | `qdivider`, `egress`, `egresscloud`, `egressdebug` (salida a internet desde un Pod), `incident`, `incidentroles`, `incidentexample` (incidente en producción), `rapidk8s`, `rapidlinux`, `rapidaws`, `morequestions` |
| Cierre | `askthem`, `close` |

## Cómo reutilizarla para otra entrevista

1. Las diapositivas de **experiencia** (intro, [EMPRESA_1], [EMPRESA_2]) son fijas.
2. Las de **preguntas** se cambian según lo que mande cada reclutador:
   agregar/quitar archivos en `project/slides/` y ajustar `order` en
   `project/deck.json`.
3. Publicar como una presentación nueva del tipo Slides (o actualizar la
   existente). Los íconos están en `iconos/` como PNG; en la presentación
   publicada ya están subidos como assets (`/_blob/<id>` en los `src`). En
   una presentación nueva hay que volver a subirlos y reemplazar esos `src`.

## Pendientes de completar (marcados en las notas)

- Fuente de datos de Grafana en [EMPRESA_1] (Azure Monitor / Log Analytics / Prometheus / Loki).
- Nombre del proveedor de correos integrado en [EMPRESA_1].
- Backend real del state de Terraform en [EMPRESA_2].
- Cifra real de ahorro de tiempo del diagnóstico con Claude (si existe).
- Un incidente real propio contado en 4 frases (síntoma, diagnóstico, arreglo, prevención).

Íconos: logos de [devicon](https://devicon.dev) y [Simple Icons](https://simpleicons.org).
