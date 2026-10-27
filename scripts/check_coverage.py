"""Exige por separado el 85% de líneas y de ramas; TOTAL no basta."""
import json
from pathlib import Path

def main():
    total=json.loads(Path("evidencias/coverage.json").read_text())["totals"]
    lines=100*total["covered_lines"]/total["num_statements"]
    branches=100*total["covered_branches"]/total["num_branches"]
    print(f"Líneas: {lines:.2f}% | Ramas: {branches:.2f}% | Mínimo: 85% cada una")
    if min(lines,branches)<85:
        raise SystemExit("NO CUMPLE: ampliar pruebas.")
    print("CUMPLE ambos umbrales.")

if __name__=="__main__":
    main()
