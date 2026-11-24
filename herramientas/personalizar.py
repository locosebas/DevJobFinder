"""Reemplaza los marcadores de identidad del repo con los valores de perfil/marcadores.json.

Uso:
    python3 herramientas/personalizar.py            # simulación: lista los archivos que cambiarían
    python3 herramientas/personalizar.py --aplicar  # escribe los cambios

Solo toca marcadores de identidad. Los de experiencia ([EMPRESA_n], [PROYECTO_n], ...) se dejan
a propósito: ver perfil/onboarding.md, etapa 5.
"""
import json, os, sys

PERMITIDOS = {"[TU_NOMBRE]", "[TU_USUARIO_GITHUB]", "[TU_CORREO]", "[NOMBRE_REPO]"}
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUIR = {".git", "node_modules", "perfil", "herramientas"}


def main():
    aplicar = "--aplicar" in sys.argv
    ruta = os.path.join(RAIZ, "perfil", "marcadores.json")
    if not os.path.exists(ruta):
        sys.exit("Falta perfil/marcadores.json (copia perfil/marcadores.example.json y llénalo).")
    valores = json.load(open(ruta, encoding="utf-8"))
    extra = set(valores) - PERMITIDOS
    if extra:
        sys.exit(f"Marcadores no permitidos: {sorted(extra)}. Ver perfil/onboarding.md, etapa 5.")
    valores = {k: v for k, v in valores.items() if v.strip()}
    total = 0
    for dp, dns, fns in os.walk(RAIZ):
        dns[:] = [d for d in dns if d not in EXCLUIR]
        for n in fns:
            p = os.path.join(dp, n)
            try:
                t = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            nuevo = t
            for k, v in valores.items():
                nuevo = nuevo.replace(k, v)
            if nuevo != t:
                total += 1
                print(("ACTUALIZADO " if aplicar else "CAMBIARÍA   ") + os.path.relpath(p, RAIZ))
                if aplicar:
                    open(p, "w", encoding="utf-8").write(nuevo)
    print(f"{total} archivo(s). " + ("Listo." if aplicar else "Ejecuta con --aplicar para escribir."))


if __name__ == "__main__":
    main()
