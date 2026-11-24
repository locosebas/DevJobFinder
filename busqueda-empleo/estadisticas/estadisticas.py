"""Estadística colectiva y anónima de búsqueda de empleo.

Cada persona aporta UN archivo agregado (aportes/<alias>.json) calculado a partir de su tablero de
vacantes. El aporte no guarda empresas, enlaces, notas, respuestas, CV, salario propio ni fechas
exactas: solo conteos por categoría, y las categorías con menos de MINIMO casos se suman en "Otro"
para que no se pueda reconocer una vacante puntual.

Uso:
    # 1) Generar tu aporte desde un export del tablero (carpeta con un .json por vacante,
    #    o un único .json con una lista de vacantes). Muestra el resultado antes de escribirlo.
    python3 estadisticas.py aporte RUTA_EXPORT [--alias ALIAS] [--escribir]

    # 2) Recalcular el resumen colectivo (README.md) con todos los aportes
    python3 estadisticas.py resumen

Campos que se leen de cada vacante (los demás se ignoran):
    estado, fuente, modalidad, ubicacion, salario, titulo, coincidencias, encaje, tipo,
    enviadaEl / publicada / actualizado (solo el mes).
"""
import glob, json, os, re, secrets, sys
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
APORTES = os.path.join(AQUI, "aportes")
MINIMO = 3
VERSION = 1

# --- Normalización -----------------------------------------------------------------------------

POSTULADA = {"enviada", "entrevista", "en_proceso", "contacto", "aceptada", "cambios",
             "rechazada", "rechazada_por_mi", "oferta"}
RESPUESTA = {"entrevista", "en_proceso", "contacto", "aceptada", "oferta", "cambios"}
ENTREVISTA = {"entrevista", "en_proceso", "aceptada", "oferta"}


def etapa(estado):
    e = (estado or "").lower()
    if e in POSTULADA:
        return "postulada"
    if e in ("descartada",):
        return "descartada_antes_de_postular"
    return "pendiente"  # aprobada, requiere_accion, por_revisar...


def portal(fuente):
    f = (fuente or "").lower()
    for clave, nombre in [("linkedin", "LinkedIn"), ("computrabajo", "Computrabajo"),
                          ("getonboard", "GetOnBoard"), ("get on board", "GetOnBoard"),
                          ("himalayas", "Himalayas"), ("elempleo", "elempleo"),
                          ("workable", "Workable"), ("ashby", "Ashby"), ("greenhouse", "Greenhouse"),
                          ("lever", "Lever"), ("freelancer", "Freelancer.com"), ("torre", "Torre"),
                          ("mercor", "Mercor"), ("bamboo", "BambooHR"), ("remoteok", "RemoteOK"),
                          ("we work remotely", "We Work Remotely"), ("correo", "Correo / referido"),
                          ("feria", "Feria presencial")]:
        if clave in f:
            return nombre
    return "Otro"


def modalidad(m, tipo=None):
    m = (m or "").lower()
    if (tipo or "").lower() == "freelance" or "freelance" in m:
        return "Freelance"
    if "híbrid" in m or "hibrid" in m:
        return "Híbrido"
    if "remot" in m or "home based" in m:
        return "Remoto"
    if "presencial" in m:
        return "Presencial"
    return "No publicada"


LATAM = r"latam|latin|am[eé]rica latina|sudam|south america"
MUNDO = r"mundial|worldwide|cualquier pa[ií]s|anywhere|global"


def region(u, pais_propio="colombia"):
    u = (u or "").lower()
    if re.search(MUNDO, u):
        return "Mundial"
    if re.search(LATAM, u):
        return "LATAM"
    if pais_propio in u or re.search(r"bogot|medell|cali\b|barranquilla|antioquia|cundinamarca", u):
        return "País propio"
    if not u or "verificar" in u or u.strip() == "remoto":
        return "Sin especificar"
    return "Otro país"


FAMILIAS = [
    ("SRE / Confiabilidad", r"\bsre\b|site reliability|reliability|incident|on-?call|observab"),
    ("Seguridad / DevSecOps", r"devsecops|security|seguridad|ciberseg"),
    ("IA / ML / LLM", r"\bai\b|\bia\b|\bml\b|machine learning|llm|genai|mlops|agent|inteligencia artificial|data scien|evals?\b"),
    ("Plataforma", r"platform|plataforma"),
    ("DevOps", r"devops|ci/cd|release"),
    ("Cloud / Infraestructura", r"cloud|aws|azure|gcp|infra|kubernetes|linux|sysadmin|network|redes|datacenter"),
    ("Software / Backend", r"software|backend|back-end|developer|desarrollador|engineer|python|golang|\bgo\b|fullstack|full stack"),
]


def familia(titulo):
    t = (titulo or "").lower()
    for nombre, rx in FAMILIAS:
        if re.search(rx, t):
            return nombre
    return "Otro"


def seniority(titulo):
    t = (titulo or "").lower()
    if re.search(r"principal|staff|architect|arquitect", t):
        return "Staff / Principal / Arquitecto"
    if re.search(r"\blead\b|l[ií]der|head|manager|gerente", t):
        return "Líder"
    if re.search(r"senior|\bsr\b|\bsr\.|ssr|semi ?senior", t):
        return "Senior / Semi senior"
    if re.search(r"junior|\bjr\b|trainee|practicante", t):
        return "Junior"
    return "Sin especificar"


TECNOLOGIAS = {
    "Python": r"python", "AWS": r"\baws\b", "Azure": r"azure", "GCP": r"\bgcp\b|google cloud",
    "Kubernetes": r"kubernetes|\bk8s\b|\beks\b|\baks\b|\bgke\b", "Terraform": r"terraform",
    "Docker": r"docker|contenedor", "CI/CD": r"ci/cd|ci-cd|pipeline", "GitHub Actions": r"github actions",
    "GitLab CI": r"gitlab", "Jenkins": r"jenkins", "ArgoCD / GitOps": r"argo|gitops",
    "Helm": r"\bhelm\b", "Ansible": r"ansible", "IaC": r"\biac\b|infraestructura como c[oó]digo",
    "Linux": r"linux", "Bash": r"\bbash\b|shell", "Go": r"\bgo\b|golang", "Observabilidad": r"observab",
    "Monitoreo y alertas": r"monitoreo|alert", "Prometheus / Grafana": r"prometheus|grafana",
    "Datadog": r"datadog", "SRE / On-call": r"\bsre\b|on-?call|site reliability",
    "Incidentes / postmortems": r"incident|postmortem", "IAM": r"\biam\b|identidad",
    "LLM / IA": r"\bllm|\bia\b|\bai\b|inteligencia artificial|genai", "Agentes de IA": r"agente|agent",
    "MCP": r"\bmcp\b", "RAG": r"\brag\b", "Integraciones / APIs": r"integraci|\bapi",
    "Automatización": r"automatizaci", "Kafka / mensajería": r"kafka|rabbit|sqs|pub/?sub|mensajer",
    "Bases de datos": r"sql|postgres|mysql|mongo|dynamo|cosmos|redis", "Redes": r"\bred(es)?\b|network|vpc|vnet",
    "Seguridad": r"segur|security|devsecops", "Edge / IoT": r"\bedge\b|iot", "Java": r"\bjava\b",
    "Node / TypeScript": r"node|typescript|javascript",
}


def tecnologias(coincidencias):
    """Las 'coincidencias' de cada vacante pueden traer texto propio entre paréntesis (p. ej. dónde
    usaste la herramienta): se descarta todo y solo se cuenta el nombre canónico de la tecnología."""
    encontradas = set()
    for c in coincidencias or []:
        c = re.sub(r"\(.*?\)", "", str(c)).lower()
        for nombre, rx in TECNOLOGIAS.items():
            if re.search(rx, c):
                encontradas.add(nombre)
    return encontradas


def salario(s):
    """Devuelve un rango en USD/mes o una categoría. No se guarda el valor, solo el rango."""
    s0 = (s or "").lower()
    if not s0 or re.search(r"no publicad|confidencial|a convenir|por confirmar|seg[uú]n", s0) and not re.search(r"\d", s0):
        return "No publicado"
    if re.search(r"precio fijo|fixed price", s0):
        return "Proyecto a precio fijo"
    if re.search(r"\b(inr|gbp|mxn|brl|ars|clp|pen)\b", s0):
        return "Otra moneda"
    nums = []
    for n in re.findall(r"\d[\d.,]*", s0):
        n = re.sub(r"[.,]\d{2}$", "", n.rstrip(".,")) if re.search(r"\d{3}[.,]\d{2}$", n) else n.rstrip(".,")
        if not re.fullmatch(r"\d+([.,]\d+)*", n) or (n.count(".") + n.count(",") > 1
                                                     and not re.fullmatch(r"\d{1,3}([.,]\d{3})+", n)):
            continue
        if re.fullmatch(r"\d{1,3}([.,]\d{3})+", n):   # separador de miles: 8.500.000 / 152,000
            nums.append(float(re.sub(r"[.,]", "", n)))
        else:                                          # decimal: 12,5 / 5.5
            nums.append(float(n.replace(",", ".")))
    nums = [n for n in nums if n >= 5]
    if not nums:
        return "No publicado"
    v = nums[0]
    if "millon" in s0 and v < 1000:
        v *= 1_000_000
    if "cop" in s0 or v >= 500000:
        usd = v / 4000
    elif re.search(r"hora|hour|/h\b|hr\b", s0):
        usd = v * 160
    elif re.search(r"a[nñ]o|annual|year|yr", s0) or v >= 30000:
        usd = v / 12
    else:
        usd = v
    for tope, nombre in [(1000, "< USD 1.000"), (2000, "USD 1.000–2.000"), (3000, "USD 2.000–3.000"),
                         (5000, "USD 3.000–5.000"), (8000, "USD 5.000–8.000")]:
        if usd < tope:
            return nombre
    return "≥ USD 8.000"


def encaje(e):
    try:
        e = float(e)
    except (TypeError, ValueError):
        return "Sin calcular"
    return "≥ 65 (alto)" if e >= 65 else "40–64 (medio)" if e >= 40 else "< 40 (bajo)"


MESES = {"ene": 1, "jan": 1, "feb": 2, "mar": 3, "abr": 4, "apr": 4, "may": 5, "jun": 6, "jul": 7,
         "ago": 8, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12, "dec": 12}


def mes(v):
    for campo in ("enviadaEl", "publicada", "actualizado"):
        t = str(v.get(campo) or "").lower()
        m = re.search(r"(20\d\d)-(\d\d)", t)
        if m:
            return f"{m.group(1)}-{m.group(2)}"
        m = re.search(r"\b(ene|jan|feb|mar|abr|apr|may|jun|jul|ago|aug|sep|oct|nov|dic|dec)\w*\.? (20\d\d)", t)
        if m:
            return f"{m.group(2)}-{MESES[m.group(1)]:02d}"
    return "Sin fecha"


# --- Aporte ------------------------------------------------------------------------------------

def cargar_export(ruta):
    if os.path.isdir(ruta):
        docs = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(os.path.join(ruta, "*.json")))]
    else:
        docs = json.load(open(ruta, encoding="utf-8"))
        docs = docs if isinstance(docs, list) else list(docs.values())
    return [d.get("data", d) for d in docs if isinstance(d, dict)]


def suprimir(c):
    """Junta en 'Otro' las categorías con menos de MINIMO casos (anonimato)."""
    out = Counter()
    for k, n in c.items():
        out[k if n >= MINIMO else "Otro"] += n
    return dict(out.most_common())


def cruzado(vs, clave):
    """Por categoría: postuladas, con respuesta y con entrevista."""
    tabla = {}
    for v in vs:
        if etapa(v.get("estado")) != "postulada":
            continue
        k = clave(v)
        t = tabla.setdefault(k, {"postuladas": 0, "con_respuesta": 0, "con_entrevista": 0})
        t["postuladas"] += 1
        e = (v.get("estado") or "").lower()
        t["con_respuesta"] += e in RESPUESTA
        t["con_entrevista"] += e in ENTREVISTA
    grandes = {k: t for k, t in tabla.items() if t["postuladas"] >= MINIMO}
    resto = [t for k, t in tabla.items() if t["postuladas"] < MINIMO]
    if resto:
        grandes["Otro"] = {c: sum(t[c] for t in resto) for c in ("postuladas", "con_respuesta", "con_entrevista")}
    return dict(sorted(grandes.items(), key=lambda kv: -kv[1]["postuladas"]))


def aporte(vs, alias, perfil):
    post = [v for v in vs if etapa(v.get("estado")) == "postulada"]
    techs = Counter(t for v in vs for t in tecnologias(v.get("coincidencias")))
    meses = Counter(mes(v) for v in vs)
    validos = [m for m, n in meses.items() if m != "Sin fecha" and n >= MINIMO]
    return {
        "version": VERSION,
        "alias": alias,
        "perfil": perfil,
        "periodo": {"desde": min(validos, default=None), "hasta": max(validos, default=None)},
        "totales": {
            "vacantes_revisadas": len(vs),
            "postuladas": len(post),
            "descartadas_antes_de_postular": sum(etapa(v.get("estado")) == "descartada_antes_de_postular" for v in vs),
            "pendientes": sum(etapa(v.get("estado")) == "pendiente" for v in vs),
            "con_respuesta": sum((v.get("estado") or "").lower() in RESPUESTA for v in post),
            "con_entrevista": sum((v.get("estado") or "").lower() in ENTREVISTA for v in post),
            "ofertas_aceptadas": sum((v.get("estado") or "").lower() == "aceptada" for v in post),
        },
        "por_portal": cruzado(vs, lambda v: portal(v.get("fuente"))),
        "por_familia_de_rol": cruzado(vs, lambda v: familia(v.get("titulo"))),
        "por_seniority": suprimir(Counter(seniority(v.get("titulo")) for v in vs)),
        "por_modalidad": suprimir(Counter(modalidad(v.get("modalidad"), v.get("tipo")) for v in vs)),
        "por_region": suprimir(Counter(region(v.get("ubicacion")) for v in vs)),
        "salario_publicado_usd_mes": suprimir(Counter(salario(v.get("salario")) for v in vs)),
        "por_encaje": suprimir(Counter(encaje(v.get("encaje")) for v in vs)),
        "por_mes": dict(sorted(suprimir(meses).items())),
        "tecnologias_detectadas": {k: n for k, n in techs.most_common() if n >= MINIMO},
    }


# --- Resumen colectivo ---------------------------------------------------------------------------

def pct(a, b):
    return f"{100 * a / b:.0f}%" if b else "—"


def sumar(dicts):
    total = Counter()
    for d in dicts:
        total.update(d)
    return total


def sumar_cruzado(dicts):
    out = {}
    for d in dicts:
        for k, t in d.items():
            o = out.setdefault(k, Counter())
            o.update(t)
    return dict(sorted(out.items(), key=lambda kv: -kv[1]["postuladas"]))


def resumen():
    aps = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(os.path.join(APORTES, "*.json")))]
    if not aps:
        sys.exit("No hay aportes en aportes/.")
    T = sumar(a["totales"] for a in aps)
    L = ["# Estadística colectiva de búsqueda de empleo", "",
         "> Generado por `estadisticas.py resumen` — no editar a mano. Datos agregados y anónimos:",
         "> sin empresas, enlaces ni fechas exactas; categorías con menos de "
         f"{MINIMO} casos sumadas en \"Otro\".", "",
         f"**Personas que aportan:** {len(aps)} · **Vacantes revisadas:** {T['vacantes_revisadas']} · "
         f"**Periodo:** {min(a['periodo']['desde'] or '9999' for a in aps)} a {max(a['periodo']['hasta'] or '' for a in aps)}", "",
         "## Embudo", "",
         "| Etapa | Vacantes | % de postuladas |", "|---|---|---|",
         f"| Revisadas | {T['vacantes_revisadas']} | |",
         f"| Descartadas antes de postular (compuertas) | {T['descartadas_antes_de_postular']} | |",
         f"| Pendientes (aprobadas o requieren acción) | {T['pendientes']} | |",
         f"| **Postuladas** | **{T['postuladas']}** | 100% |",
         f"| Con alguna respuesta (contacto, proceso, entrevista) | {T['con_respuesta']} | {pct(T['con_respuesta'], T['postuladas'])} |",
         f"| Con entrevista | {T['con_entrevista']} | {pct(T['con_entrevista'], T['postuladas'])} |",
         f"| Oferta aceptada | {T['ofertas_aceptadas']} | {pct(T['ofertas_aceptadas'], T['postuladas'])} |", ""]
    for titulo, clave in [("Tasa de respuesta por portal", "por_portal"),
                          ("Tasa de respuesta por familia de rol", "por_familia_de_rol")]:
        L += [f"## {titulo}", "", "| Categoría | Postuladas | Con respuesta | Con entrevista |", "|---|---|---|---|"]
        for k, t in sumar_cruzado(a[clave] for a in aps).items():
            L.append(f"| {k} | {t['postuladas']} | {t['con_respuesta']} ({pct(t['con_respuesta'], t['postuladas'])}) | "
                     f"{t['con_entrevista']} ({pct(t['con_entrevista'], t['postuladas'])}) |")
        L.append("")
    for titulo, clave in [("Tecnologías pedidas que coinciden con el perfil de quien aporta", "tecnologias_detectadas"),
                          ("Modalidad", "por_modalidad"), ("Región", "por_region"), ("Seniority", "por_seniority"),
                          ("Salario publicado (USD/mes aproximado)", "salario_publicado_usd_mes"),
                          ("Encaje con el perfil", "por_encaje"), ("Vacantes por mes", "por_mes")]:
        c = sumar(a.get(clave, {}) for a in aps)
        n = sum(c.values())
        items = sorted(c.items()) if clave == "por_mes" else c.most_common()
        L += [f"## {titulo}", "", "| Categoría | Vacantes | % |", "|---|---|---|"]
        base = T["vacantes_revisadas"]
        L += [f"| {k} | {v} | {pct(v, base)} |" for k, v in items]
        L.append("")
    L += ["## Perfiles que aportan", "", "| Alias | Rol objetivo | Años de experiencia | País | Vacantes |", "|---|---|---|---|---|"]
    for a in aps:
        p = a.get("perfil", {})
        L.append(f"| {a['alias']} | {p.get('rol_objetivo', '—')} | {p.get('anios_experiencia', '—')} | "
                 f"{p.get('pais', '—')} | {a['totales']['vacantes_revisadas']} |")
    open(os.path.join(AQUI, "README.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"README.md actualizado con {len(aps)} aporte(s).")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("aporte", "resumen"):
        sys.exit(__doc__)
    if sys.argv[1] == "resumen":
        return resumen()
    args = sys.argv[2:]
    if not args:
        sys.exit("Falta RUTA_EXPORT.")
    alias = args[args.index("--alias") + 1] if "--alias" in args else "aporte-" + secrets.token_hex(4)
    perfil = {"rol_objetivo": os.environ.get("ROL_OBJETIVO", "—"),
              "anios_experiencia": os.environ.get("ANIOS_EXPERIENCIA", "—"),
              "pais": os.environ.get("PAIS", "—")}
    a = aporte(cargar_export(args[0]), alias, perfil)
    print(json.dumps(a, ensure_ascii=False, indent=2))
    if "--escribir" in args:
        os.makedirs(APORTES, exist_ok=True)
        ruta = os.path.join(APORTES, alias + ".json")
        json.dump(a, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("Escrito:", os.path.relpath(ruta, AQUI))
    else:
        print("\n(Simulación. Revisa que no haya nada que te identifique y repite con --escribir.)")


if __name__ == "__main__":
    main()
