from __future__ import annotations

import csv
import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"


ROWS = [
    {
        "gate_id": "CHANG_M1",
        "source": "Chang 2012 doctoral thesis",
        "public_locator": "https://researchportal.hkust.edu.hk/en/studentTheses/internal-erosion-and-overtopping-erosion-of-earth-dams-and-landsl/",
        "doi_or_identifier": "10.14711/thesis-b1165745",
        "source_basis": "HKUST public thesis abstract",
        "mechanism_observation": "stress-controlled erosion apparatus allowed independent control of hydraulic gradient and stress state",
        "required_article126_behavior": "activation operator must be coupled to hydraulic path and mechanical state, not a single global hydraulic-gradient cutoff",
        "status": "PASS_MECHANISM_SUPPORT",
        "claim_allowed": "external mechanism support for stress-state-conditioned suffusion activation",
        "claim_blocked": "quantitative residual validation without extracted tables or curves",
    },
    {
        "gate_id": "CHANG_M2",
        "source": "Chang 2012 doctoral thesis",
        "public_locator": "https://researchportal.hkust.edu.hk/en/studentTheses/internal-erosion-and-overtopping-erosion-of-earth-dams-and-landsl/",
        "doi_or_identifier": "10.14711/thesis-b1165745",
        "source_basis": "HKUST public thesis abstract",
        "mechanism_observation": "internal erosion tests covered isotropic, drained triaxial compression and triaxial extension stress paths",
        "required_article126_behavior": "model boundary must state that validation spans mechanism classes but not all stress paths until source tables are extracted",
        "status": "PASS_MECHANISM_SUPPORT",
        "claim_allowed": "stress-path-aware acquisition target and mechanism boundary",
        "claim_blocked": "universal stress-path validation",
    },
    {
        "gate_id": "CHANG_M3",
        "source": "Chang 2012 doctoral thesis",
        "public_locator": "https://researchportal.hkust.edu.hk/en/studentTheses/internal-erosion-and-overtopping-erosion-of-earth-dams-and-landsl/",
        "doi_or_identifier": "10.14711/thesis-b1165745",
        "source_basis": "HKUST public thesis abstract",
        "mechanism_observation": "erosion process is separated into stable, initiation, development and failure phases with initiation, skeleton-deformation and failure hydraulic gradients",
        "required_article126_behavior": "article must keep the FEM-Dijkstra-DEM operator phase-aware and avoid one-threshold suffusion claims",
        "status": "PASS_MECHANISM_SUPPORT",
        "claim_allowed": "external support for phase-separated activation and failure boundary",
        "claim_blocked": "calibrated phase-transition prediction",
    },
    {
        "gate_id": "CHANG_M4",
        "source": "Chang 2012 doctoral thesis",
        "public_locator": "https://researchportal.hkust.edu.hk/en/studentTheses/internal-erosion-and-overtopping-erosion-of-earth-dams-and-landsl/",
        "doi_or_identifier": "10.14711/thesis-b1165745",
        "source_basis": "HKUST public thesis abstract",
        "mechanism_observation": "initiation gradient under compression first increases with shear stress ratio and then decreases near shear failure",
        "required_article126_behavior": "model claim must allow nonmonotonic stress-ratio effects and cannot assert monotonic safety with increasing shear stress ratio",
        "status": "PASS_MECHANISM_SUPPORT",
        "claim_allowed": "external nonmonotonic stress-ratio boundary for claim narrowing",
        "claim_blocked": "stress-ratio residual curve prediction",
    },
    {
        "gate_id": "CHANG_M5",
        "source": "Chang 2012 doctoral thesis",
        "public_locator": "https://researchportal.hkust.edu.hk/en/studentTheses/internal-erosion-and-overtopping-erosion-of-earth-dams-and-landsl/",
        "doi_or_identifier": "10.14711/thesis-b1165745",
        "source_basis": "HKUST public thesis abstract",
        "mechanism_observation": "soil erodibility is controlled by grain-size distribution, void ratio, fines content and plasticity index",
        "required_article126_behavior": "data-acquisition and validation targets must include initial specimen state and gradation variables before any primary residual claim",
        "status": "PASS_MECHANISM_SUPPORT",
        "claim_allowed": "external support for required acquisition variables",
        "claim_blocked": "erodibility-coefficient validation without extracted source data",
    },
]


def main() -> None:
    DATA.mkdir(exist_ok=True)
    csv_path = DATA / "external_chang2012_mechanism_gate.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(ROWS[0].keys()))
        writer.writeheader()
        writer.writerows(ROWS)

    summary = {
        "status": "PASS_EXTERNAL_MECHANISM_GATE_NOT_RESIDUAL_VALIDATION",
        "source": "Chang 2012 doctoral thesis, HKUST Research Portal",
        "doi_or_identifier": "10.14711/thesis-b1165745",
        "public_locator": "https://researchportal.hkust.edu.hk/en/studentTheses/internal-erosion-and-overtopping-erosion-of-earth-dams-and-landsl/",
        "mechanism_gate_count": len(ROWS),
        "passed_mechanism_gate_count": sum(row["status"].startswith("PASS") for row in ROWS),
        "claim_enabled_now": (
            "external mechanism support for stress-state-conditioned, phase-aware suffusion activation and "
            "primary-data acquisition variables"
        ),
        "claim_blocked_now": (
            "quantitative residual validation against Chang 2012 until legal full-text tables, curves, or "
            "author data are extracted and uncertainty-audited"
        ),
        "ethical_constraint": (
            "use this gate as mechanism and acquisition support only; do not cite it as calibrated residual validation"
        ),
    }
    (DATA / "external_chang2012_mechanism_gate_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
