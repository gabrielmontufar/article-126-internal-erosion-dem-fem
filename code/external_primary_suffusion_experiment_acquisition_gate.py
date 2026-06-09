from __future__ import annotations

import csv
import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = [
        {
            "source_family": "Sterpi 2003 primary suffusion experiment",
            "citation_key": "Sterpi_2003",
            "doi_or_source": "10.1061/(ASCE)1532-3641(2003)3:1(111)",
            "verified_public_locator": "https://doi.org/10.1061/(ASCE)1532-3641(2003)3:1(111)",
            "why_priority": "Zhu 2025 identifies Sterpi as a baseline validation case and reports hydraulic gradient 0.18 at abstract/snippet level.",
            "minimum_residual_variables": "time_or_stage; hydraulic_gradient; cumulative_fines_loss_or_eroded_mass; specimen_initial_state",
            "preferred_residual_variables": "permeability_or_flow; porosity_or_void_ratio; fines_fraction_distribution; uncertainty or replicate information",
            "current_local_data_status": "metadata_and_literature_locator_only",
            "permitted_current_use": "priority primary-experiment acquisition target and claim-boundary support",
            "blocked_claim": "primary-experiment residual validation of fines-loss trajectory",
            "next_required_action": "obtain legal full text/tables or digitize curves with uncertainty audit",
            "status": "PRIMARY_DATA_EXTRACTION_REQUIRED",
        },
        {
            "source_family": "Chang 2012 internal erosion/overtopping thesis",
            "citation_key": "Chang_2012",
            "doi_or_source": "10.14711/thesis-b1165745",
            "verified_public_locator": "https://researchportal.hkust.edu.hk/en/studentTheses/internal-erosion-and-overtopping-erosion-of-earth-dams-and-landsl/",
            "why_priority": "independent thesis-scale internal-erosion source with suffusion and erodibility variables for possible raw/table extraction",
            "minimum_residual_variables": "hydraulic_gradient_or_flow; fines_loss_or_eroded_mass; grain_size_distribution; void_ratio_or_density; time_or_stage",
            "preferred_residual_variables": "permeability evolution; specimen geometry; stress state; replicate information",
            "current_local_data_status": "metadata_and_public_thesis_locator_only",
            "permitted_current_use": "secondary raw/table acquisition target",
            "blocked_claim": "quantitative residual validation until tables/curves are extracted and audited",
            "next_required_action": "inspect thesis for machine-readable tables or digitizable curves; record permissions",
            "status": "PRIMARY_DATA_EXTRACTION_REQUIRED",
        },
        {
            "source_family": "Zhu 2025 validation-experiment table",
            "citation_key": "Zhu_2025_validation_sources",
            "doi_or_source": "10.1016/j.compgeo.2025.107620",
            "verified_public_locator": "https://www.sciencedirect.com/science/article/abs/pii/S0266352X25005695",
            "why_priority": "would identify all four validation experiments used by the probabilistic fines-loss model",
            "minimum_residual_variables": "experiment_identity; hydraulic_gradient_history; fines_loss_curve_or_table; model/experimental comparison",
            "preferred_residual_variables": "all validation curves; experimental initial states; uncertainty bands; supplementary data",
            "current_local_data_status": "closed_article_metadata_only",
            "permitted_current_use": "source-discovery target only",
            "blocked_claim": "Zhu-family residual validation or calibration",
            "next_required_action": "obtain legal PDF/full text, author data, or supplementary tables",
            "status": "PRIMARY_DATA_EXTRACTION_REQUIRED",
        },
    ]
    write_csv(DATA / "external_primary_suffusion_experiment_acquisition_gate.csv", rows)

    request_text = """Subject: Request for primary suffusion experiment data for reproducible residual validation

Dear [Author/Repository Contact],

I am preparing a reproducible computational geotechnics validation package for a suffusion screening method. I am looking for machine-readable or rights-safe tabulated data from primary suffusion experiments, especially hydraulic-gradient stages and cumulative fines-loss/eroded-mass histories.

Minimum useful fields:
- time, loading step, or hydraulic-gradient stage;
- imposed hydraulic gradient or flow condition;
- cumulative eroded fines mass, fines-loss ratio, or equivalent response;
- initial fines content/distribution, density/void ratio, and specimen notes;
- permeability/flow evolution if available.

The intended use is a cited residual comparison with RMSE/MAE and clear limits. If redistribution is not permitted, I can document the acquisition route and publish only derived summary metrics with proper attribution.
"""
    (DATA / "primary_suffusion_experiment_data_request_template.txt").write_text(
        request_text, encoding="utf-8"
    )

    summary = {
        "status": "PRIMARY_DATA_EXTRACTION_REQUIRED",
        "primary_targets": ["Sterpi_2003", "Chang_2012", "Zhu_2025_validation_sources"],
        "claim_enabled_now": "auditable acquisition route for primary suffusion experiment residual validation",
        "claim_blocked_now": "second independent residual validation against primary fines-loss experiments",
        "minimum_acceptance_rule": (
            "A source must provide at least time/stage, hydraulic gradient or flow condition, "
            "cumulative fines-loss or eroded-mass response, and initial specimen state. "
            "Digitized curves require an uncertainty record and must not be labeled raw data."
        ),
        "why_this_matters_for_q1_high": (
            "Lee A/B validation is already useful but small. A second residual-style primary-experiment "
            "family would materially reduce Q1 reviewer risk without depending on the closed Zhu 2025 article."
        ),
    }
    (DATA / "external_primary_suffusion_experiment_acquisition_gate_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
