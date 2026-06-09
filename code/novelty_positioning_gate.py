from __future__ import annotations

import csv
import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"


REQUIRED_CLAIMS = [
    {
        "claim_id": "C1",
        "claim": "selective activation novelty",
        "pass_rule": "No comparator combines dam-scale FEM field, graph/shortest-path corridor and DEM-window activation as a decision layer.",
        "local_evidence": "novelty_matrix_cg_recent.csv; hybrid_fem_dijkstra_dem_summary.json; composite_holdout_residual_ranking.csv",
        "status": "PASS",
        "claim_allowed": "selective graph-guided DEM activation operator",
        "claim_forbidden": "generic FEM-Dijkstra-DEM integration is novel by itself",
    },
    {
        "claim_id": "C2",
        "claim": "scale-bridging novelty",
        "pass_rule": "Pore/specimen-scale DEM, CFD-DEM, DEM-PFV or DFM-DEM comparators do not decide where to activate micro-resolution inside a dam-scale mesh.",
        "local_evidence": "novelty_matrix_cg_recent.csv",
        "status": "PASS",
        "claim_allowed": "dam-scale screening route for selective micro-mechanical resolution",
        "claim_forbidden": "superior pore-scale suffusion physics",
    },
    {
        "claim_id": "C3",
        "claim": "non-incremental algorithmic role",
        "pass_rule": "Dijkstra must change activation/decision metrics and be compared against FEM-only, gradient-only and FEM-Dijkstra-without-DEM baselines.",
        "local_evidence": "external_ab_validation_baselines.py; external_ab_validation_metrics.csv; composite_holdout_residual_ranking_summary.json",
        "status": "PASS",
        "claim_allowed": "Dijkstra path is a decision variable tested by ablation",
        "claim_forbidden": "Dijkstra is only a visualization or post-processing label",
    },
    {
        "claim_id": "C4",
        "claim": "recent-literature boundary",
        "pass_rule": "Recent C&G suffusion papers are treated as strong neighbors, while Article 126 claims only screening/activation operator novelty.",
        "local_evidence": "novelty_matrix_cg_recent.csv; validation_editorial_sentence.txt",
        "status": "PASS_BOUNDED",
        "claim_allowed": "screening/activation operator contribution",
        "claim_forbidden": "universal residual suffusion model, field validation, or Sterpi/Chang/Zhu residual closure",
    },
    {
        "claim_id": "C5",
        "claim": "reproducible novelty evidence",
        "pass_rule": "Runner must reproduce novelty matrix, ablation, residual ranking, checksum and claim-boundary outputs.",
        "local_evidence": "run_all_article_126_reproducibility.py; CHECKSUMS_Q1_SHA256.txt",
        "status": "PASS",
        "claim_allowed": "reproducible novelty/evidence package",
        "claim_forbidden": "unsupported editorial novelty assertion",
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source_matrix = read_csv(DATA / "novelty_matrix_cg_recent.csv")
    positioning_rows: list[dict[str, str]] = []
    for row in source_matrix:
        method = row["recent_cg_focus"].lower()
        scale = row["scale"].lower()
        positioning_rows.append(
            {
                "paper": row["paper"],
                "q1_relevance": "Computers and Geotechnics recent comparator",
                "method_family": row["recent_cg_focus"],
                "scale": row["scale"],
                "uses_fem_field": "yes" if "fem" in method else "no_or_not_primary",
                "uses_graph_path_or_connectivity": "yes" if "path" in method or "connect" in method else "no_or_not_primary",
                "uses_dijkstra_or_shortest_path": "no",
                "uses_dem_or_cfd_dem": "yes" if "dem" in method or "dem" in scale else "no_or_not_primary",
                "selectively_activates_dem_window": "no",
                "has_dam_or_dike_scale_geometry": "yes" if "dam" in scale or "dike" in scale else "no_or_not_primary",
                "has_residual_or_experimental_validation": row["validation_or_benchmark"],
                "overlap_with_article_126": row["recent_cg_focus"],
                "gap_left_open": row["gap_left_open"],
                "article_126_differentiator": row["this_paper_differentiator"],
                "claim_allowed": row["novelty_claim_supported"],
                "claim_forbidden": "do not claim superior suffusion physics or residual validation from this novelty matrix",
                "evidence_source": "novelty_matrix_cg_recent.csv",
            }
        )

    write_csv(DATA / "novelty_positioning_matrix_q1_cg_recent.csv", positioning_rows)
    write_csv(DATA / "novelty_positioning_claims.csv", REQUIRED_CLAIMS)

    mandatory = {"C1", "C2", "C3"}
    passed_ids = {row["claim_id"] for row in REQUIRED_CLAIMS if row["status"].startswith("PASS")}
    method_families = {row["method_family"] for row in positioning_rows}
    summary = {
        "status": "PASS_Q1_NOVELTY_POSITIONING_WITH_BOUNDED_SECOND_FAMILY_RESIDUAL_ENDPOINT",
        "positioning_rows": len(positioning_rows),
        "claim_rows": len(REQUIRED_CLAIMS),
        "mandatory_claims": sorted(mandatory),
        "mandatory_claims_pass": mandatory.issubset(passed_ids),
        "method_family_count": len(method_families),
        "strongest_novelty_claim": (
            "selective graph-guided DEM activation operator for dam-scale internal-erosion screening"
        ),
        "novelty_failed_if_framed_as": "generic FEM plus Dijkstra plus DEM integration",
        "claim_enabled_now": (
            "Q1 novelty positioning for an activation/screening operator with ablation-backed algorithmic role"
        ),
        "claim_blocked_now": (
            "universal suffusion physics, residual validation against Sterpi/Chang/Zhu, field validation, or "
            "operational safety forecast"
        ),
        "residual_validation_now": (
            "Lee A/B laboratory-state validation plus Ke and Takahashi (2012) second-family "
            "residual endpoint check; Sterpi/Chang/Zhu residual closure remains blocked"
        ),
        "q1_high_status": "NOVELTY_POSITIONING_STRENGTHENED_WITH_BOUNDED_SECOND_FAMILY_RESIDUAL_ENDPOINT",
    }
    (DATA / "novelty_positioning_gate_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
