"""Valida los aportes a la estadística colectiva (lo corre GitHub Actions en cada pull request).

Uso: python3 validar_aporte.py ARCHIVO_CAMBIADO [ARCHIVO_CAMBIADO ...]

Falla si el PR toca algo fuera de aportes/*.json y README.md, si un aporte no tiene la forma
esperada, si trae texto que parezca dato personal (enlaces, correos, teléfonos) o si el README.md
no coincide con lo que genera `estadisticas.py resumen`.
"""
import json, os, re, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = "busqueda-empleo/estadisticas/"
PERMITIDOS = re.compile(rf"^{re.escape(BASE)}(aportes/[a-z0-9][a-z0-9-]{{1,39}}\.json|README\.md)$")
CLAVES = {"version", "alias", "perfil", "periodo", "totales", "por_portal", "por_familia_de_rol",
          "por_seniority", "por_modalidad", "por_region", "salario_publicado_usd_mes", "por_encaje",
          "por_mes", "tecnologias_detectadas"}
SOSPECHOSO = re.compile(r"https?://|www\.|@[a-z0-9-]+\.[a-z]|\+?\d[\d -]{8,}\d", re.I)
errores = []


def textos(x):
    if isinstance(x, dict):
        for k, v in x.items():
            yield str(k)
            yield from textos(v)
    elif isinstance(x, list):
        for v in x:
            yield from textos(v)
    elif isinstance(x, str):
        yield x


def numeros(x, ruta):
    for k, v in x.items():
        if isinstance(v, dict):
            numeros(v, f"{ruta}.{k}")
        elif not (isinstance(v, int) and v >= 0):
            errores.append(f"{ruta}.{k} debe ser un entero >= 0")


def validar(ruta):
    nombre = os.path.basename(ruta)[:-5]
    try:
        a = json.load(open(ruta, encoding="utf-8"))
    except (OSError, ValueError) as e:
        return errores.append(f"{ruta}: no es JSON válido ({e})")
    if set(a) - CLAVES:
        errores.append(f"{ruta}: claves no permitidas {sorted(set(a) - CLAVES)}")
    if a.get("alias") != nombre:
        errores.append(f"{ruta}: 'alias' debe ser igual al nombre del archivo ({nombre})")
    if set(a.get("perfil", {})) - {"rol_objetivo", "anios_experiencia", "pais"}:
        errores.append(f"{ruta}: 'perfil' solo admite rol_objetivo, anios_experiencia y pais")
    for clave in CLAVES - {"version", "alias", "perfil", "periodo"}:
        if not isinstance(a.get(clave), dict):
            errores.append(f"{ruta}: falta '{clave}' o no es un objeto")
        else:
            numeros(a[clave], clave)
    for t in textos(a):
        if len(t) > 60 or SOSPECHOSO.search(t):
            errores.append(f"{ruta}: texto no permitido (¿dato personal?): {t[:60]!r}")


def main():
    cambiados = [c for c in sys.argv[1:] if c.strip()]
    for c in cambiados:
        if not PERMITIDOS.match(c):
            errores.append(f"Archivo fuera de lo permitido en un aporte: {c}")
    raiz = os.path.dirname(os.path.dirname(AQUI))
    for c in cambiados:
        if c.endswith(".json") and PERMITIDOS.match(c) and os.path.exists(os.path.join(raiz, c)):
            validar(os.path.join(raiz, c))
    antes = open(os.path.join(AQUI, "README.md"), encoding="utf-8").read()
    subprocess.run([sys.executable, os.path.join(AQUI, "estadisticas.py"), "resumen"], check=True,
                   capture_output=True)
    if open(os.path.join(AQUI, "README.md"), encoding="utf-8").read() != antes:
        errores.append("README.md no está actualizado: ejecuta `python3 estadisticas.py resumen` y súbelo.")
    if errores:
        print("\n".join("✗ " + e for e in errores))
        sys.exit(1)
    print(f"✓ Aporte válido ({len(cambiados)} archivo(s)).")


if __name__ == "__main__":
    main()
