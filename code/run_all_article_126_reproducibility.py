from __future__ import annotations

import subprocess
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
CODE = BASE / "code"


def run_script(name: str) -> None:
    script = CODE / name
    print(f"[run] {script.name}")
    subprocess.run([sys.executable, str(script)], cwd=str(BASE), check=True)


def main() -> None:
    # Rebuilds all evidence used by the revised Computers and Geotechnics package.
    # The legacy clean benchmark preserves Figures 1-5 and the 1D verification.
    # The hybrid script closes the claim-code gap by implementing a real 2D
    # triangular FEM solve, Dijkstra path search and bonded-particle DEM window.
    run_script("reproduce_article_126_clean.py")
    run_script("hybrid_dem_fem_graph_benchmark.py")
    run_script("external_validation_lee2021.py")
    run_script("novelty_validation_scorecard.py")
    print("[ok] all reproducibility scripts completed")


if __name__ == "__main__":
    main()
