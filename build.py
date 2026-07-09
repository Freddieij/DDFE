#!/usr/bin/env python3
"""
build.py - Reconstrói o bundle completo (estilo Codigo.txt) a partir dos
arquivos individuais em PowerQuery/ e Deneb/.

Uso:
    python build.py                 # imprime o bundle no stdout
    python build.py -o saida.txt    # grava em arquivo
    python build.py --check         # só valida (arquivos existem + JSON ok)

Rede de segurança de sincronização:
Se algum dia suspeitar que o mini-repo divergiu do Power BI, reexporte o M/Deneb
do pbix, rode `python build.py -o _rebuilt.txt` e compare com o export.
"""
import io, os, sys, json, argparse

ROOT = os.path.dirname(os.path.abspath(__file__))

# Ordem lógica/de dependência das queries M (fonte da verdade da ordem).
QUERIES = [
    "CaminhoArquivo",
    "Input_Tech",
    "tech_map",
    "TechLayout",
    "Input_Fuel",
    "fuel_map",
    "FuelLayout",
    "energy_view",
    "TraceabilityEngine",
]
DENEB = "Deneb/RES_FlowDiagram.json"


def read(path):
    with io.open(path, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n").rstrip("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", help="arquivo de saída (default: stdout)")
    ap.add_argument("--check", action="store_true", help="apenas valida, não gera bundle")
    args = ap.parse_args()

    errors = []
    parts = []

    for name in QUERIES:
        p = os.path.join(ROOT, "PowerQuery", name + ".pq")
        if not os.path.exists(p):
            errors.append("FALTANDO: " + p)
            continue
        parts.append("// %s\n\n%s\n" % (name, read(p)))

    dp = os.path.join(ROOT, DENEB)
    if not os.path.exists(dp):
        errors.append("FALTANDO: " + dp)
    else:
        try:
            json.loads(read(dp))
        except json.JSONDecodeError as e:
            errors.append("JSON INVÁLIDO em %s: %s" % (DENEB, e))
        parts.append("// DENEB:\n\n%s\n" % read(dp))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)

    print("OK: %d queries + Deneb (JSON válido)" % len(QUERIES), file=sys.stderr)
    if args.check:
        return

    bundle = "\n\n".join(parts) + "\n"
    if args.out:
        with io.open(os.path.join(ROOT, args.out), "w", encoding="utf-8", newline="\n") as f:
            f.write(bundle)
        print("Bundle gravado em %s" % args.out, file=sys.stderr)
    else:
        sys.stdout.write(bundle)


if __name__ == "__main__":
    main()
