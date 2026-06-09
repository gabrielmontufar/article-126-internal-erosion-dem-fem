from __future__ import annotations

import csv
import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = [
        {
            "source_family": "Zhu et al. 2025 Computers and Geotechnics 188:107620",
            "doi": "10.1016/j.compgeo.2025.107620",
            "verified_url": "https://www.sciencedirect.com/science/article/abs/pii/S0266352X25005695",
            "metadata_url": "https://www.researchgate.net/publication/395303288_A_probabilistic_model_for_predicting_suffusion-induced_fines_loss",
            "title": "A probabilistic model for predicting suffusion-induced fines loss",
            "reported_external_evidence": "validated against four experiments under constant and multi-stage hydraulic gradients",
            "candidate_residual_variables": "cumulative eroded fines mass; fines-loss probability; spatiotemporal fines distribution; hydraulic-gradient stage",
            "current_local_data_status": "metadata_only_no_numeric_tables_or_digitized_curves",
            "q1_high_use": "second independent fines-loss family residual validation if numeric data are acquired",
            "claim_enabled_now": "external acquisition target and novelty boundary",
            "claim_blocked_now": "second-family residual validation or calibration claim",
            "next_required_action": "obtain full text, supplementary tables or digitize published curves with uncertainty notes",
            "status": "DATA_EXTRACTION_REQUIRED",
        },
        {
            "source_family": "Boschi et al. 2025 Computers and Geotechnics 188:107525",
            "doi": "unknown_in_local_matrix",
            "title": "DEM-PFV suffusion heterogeneity candidate",
            "reported_external_evidence": "permeability tests and suffusion heterogeneity according to local novelty matrix",
            "candidate_residual_variables": "permeability change; heterogeneity index; erodimetric response",
            "current_local_data_status": "metadata_only_no_numeric_tables_or_digitized_curves",
            "q1_high_use": "possible pore-scale heterogeneity boundary check after Zhu family",
            "claim_enabled_now": "secondary acquisition target",
            "claim_blocked_now": "quantitative residual ranking or validation claim",
            "next_required_action": "obtain full text or extract numerical permeability/heterogeneity values",
            "status": "DATA_EXTRACTION_REQUIRED",
        },
    ]
    write_csv(DATA / "external_zhu2025_second_family_acquisition_gate.csv", rows)
    summary = {
        "status": "DATA_EXTRACTION_REQUIRED",
        "primary_candidate": "Zhu et al. 2025, Computers and Geotechnics 188:107620",
        "doi": "10.1016/j.compgeo.2025.107620",
        "why_it_matters": (
            "Zhu et al. 2025 is a second independent fines-loss family because it reports a "
            "probabilistic model validated against four suffusion experiments."
        ),
        "verified_sources": [
            {
                "source": "ScienceDirect article page",
                "url": "https://www.sciencedirect.com/science/article/abs/pii/S0266352X25005695",
                "evidence_used": "article identity, DOI, abstract-level validation statement, authorship, and data-curation metadata",
            },
            {
                "source": "ResearchGate metadata page",
                "url": "https://www.researchgate.net/publication/395303288_A_probabilistic_model_for_predicting_suffusion-induced_fines_loss",
                "evidence_used": "metadata confirmation only; no numeric residual data used",
            },
        ],
        "claim_boundary": (
            "The current local package has metadata and abstract-level evidence only. "
            "It cannot claim second-family residual validation until numeric tables, "
            "supplemental data or digitized curves are acquired and audited."
        ),
        "proposed_next_script_after_data": "code/external_validation_zhu2025_second_family_residuals.py",
        "proposed_next_output_after_data": "data/external_zhu2025_second_family_residuals.csv",
    }
    (DATA / "external_zhu2025_second_family_acquisition_gate_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    request_text = """Subject: Data request for suffusion fines-loss validation study

Dear Dr. Zhu and co-authors,

I am preparing a reproducible geotechnical benchmark on suffusion-induced fines-loss prediction and would like to compare against the validation experiments reported in:

Zhu, Y.; Xu, S.; Yu, T.; Sun, H.; Jin, B.; Fan, D. (2025). A probabilistic model for predicting suffusion-induced fines loss. Computers and Geotechnics, 188, 107620. https://doi.org/10.1016/j.compgeo.2025.107620

Would you be willing to share the tabulated validation data, or the numerical curves underlying the four validation experiments under constant and multi-stage hydraulic gradients? The most useful fields would be:

- hydraulic-gradient stage and time/step;
- cumulative eroded fines mass or fines-loss ratio;
- initial fines content/distribution and relative density;
- permeability or flow-related parameters used in the validation;
- any published model outputs corresponding to the experimental curves.

The data would be used only for a cited, reproducible residual comparison. If redistribution is not allowed, I can document the acquisition route and report only derived residual metrics with proper attribution.

Sincerely,
"""
    (DATA / "zhu2025_data_request_template.txt").write_text(request_text, encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
