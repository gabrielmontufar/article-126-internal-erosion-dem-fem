from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
DATA.mkdir(parents=True, exist_ok=True)


def run() -> None:
    # Published observations transcribed from Lee, Kim and Chung (2021),
    # International Journal of Geo-Engineering, open-access article
    # "Evaluation of the internal stability of well-graded silty sand through
    # the long-term seepage test", DOI 10.1186/s40703-021-00151-6.
    observations = pd.DataFrame(
        [
            {
                "case": "gap_graded_short_term",
                "soil": "gap-graded silty sand",
                "test_type": "stepwise short-term seepage",
                "reported_trigger_i": 10.0,
                "reported_applied_i": 12.0,
                "i_over_short_term_trigger": 1.20,
                "reported_fines_or_soil_loss_percent": 4.1,
                "reported_k_over_k0": 3.0,
                "reported_behavior": "critical-gradient state reached; fines discharge and permeability increase",
            },
            {
                "case": "gap_graded_long_term_subcritical",
                "soil": "gap-graded silty sand",
                "test_type": "long-term constant-gradient seepage",
                "reported_trigger_i": 10.0,
                "reported_applied_i": 5.0,
                "i_over_short_term_trigger": 0.50,
                "reported_fines_or_soil_loss_percent": 14.0,
                "reported_k_over_k0": 2.0,
                "reported_behavior": "suffusion occurred below the short-term critical gradient",
            },
            {
                "case": "gwanak_short_term",
                "soil": "well-graded Gwanak silty sand",
                "test_type": "stepwise short-term seepage",
                "reported_trigger_i": 35.0,
                "reported_applied_i": 40.0,
                "i_over_short_term_trigger": 1.14,
                "reported_fines_or_soil_loss_percent": 5.1,
                "reported_k_over_k0": 1.2,
                "reported_behavior": "critical-gradient state reached after permeability increase",
            },
            {
                "case": "gwanak_long_term_subcritical",
                "soil": "well-graded Gwanak silty sand",
                "test_type": "long-term constant-gradient seepage",
                "reported_trigger_i": 35.0,
                "reported_applied_i": 17.0,
                "i_over_short_term_trigger": 17.0 / 35.0,
                "reported_fines_or_soil_loss_percent": 11.3,
                "reported_k_over_k0": 3.0,
                "reported_behavior": "delayed suffusion and permeability surge below the short-term critical gradient",
            },
        ]
    )

    challenge = pd.DataFrame(
        [
            {
                "reviewer_challenge": "A model based only on a local critical hydraulic-gradient cutoff would incorrectly classify the long-term subcritical tests as safe.",
                "external_evidence": "Lee et al. (2021) report suffusion at i/i_crit = 0.50 for gap-graded silty sand and about 0.49 for Gwanak silty sand.",
                "manuscript_response": "The proposed trigger is not a pure i/i_c cutoff; Lambda combines gradient, permeability increase, damage and fine loss along an exit-to-source path.",
                "status": "passed_for_scope",
                "scope_limit": "Phenomenological external validation of the need for path/history-sensitive screening; not quantitative calibration to a laboratory column.",
            },
            {
                "reviewer_challenge": "A dam-scale screening method must not present a synthetic lead interval as physical operational timing.",
                "external_evidence": "The long-term tests show delayed changes over hours to days depending on fabric and clogging, so physical timing is material- and history-dependent.",
                "manuscript_response": "The revised manuscript labels the reported interval as synthetic/numerically defined and explicitly rejects operational alert claims.",
                "status": "passed_for_scope",
                "scope_limit": "Timing remains synthetic until calibrated with laboratory, centrifuge, field or instrumented-dam data.",
            },
            {
                "reviewer_challenge": "The paper must fit Computers and Geotechnics by contributing geotechnical computation, not a generic dam-safety narrative.",
                "external_evidence": "Recent C&G papers emphasize advanced computational methods, constitutive links, DEM/CFD/DFM/PFV modelling, field-scale FEM and reproducible validation logic.",
                "manuscript_response": "The revised contribution is framed as a reproducible hybrid DEM-FEM activation rule and graph-connectivity indicator for dam-scale numerical screening.",
                "status": "passed_for_scope",
                "scope_limit": "The paper is a numerical-method paper; it is not a regulatory dam-safety procedure.",
            },
        ]
    )

    observations.to_csv(DATA / "external_lee2021_observations.csv", index=False)
    challenge.to_csv(DATA / "external_validation_challenge_results.csv", index=False)

    summary = {
        "source": "Lee, Kim and Chung (2021), International Journal of Geo-Engineering, DOI 10.1186/s40703-021-00151-6",
        "external_observation_count": int(len(observations)),
        "challenge_count": int(len(challenge)),
        "passed_for_bounded_scope": int((challenge["status"] == "passed_for_scope").sum()),
        "not_claimed": "No quantitative field calibration, field validation, or operational alert-system validation is claimed.",
    }
    (DATA / "external_validation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    run()
