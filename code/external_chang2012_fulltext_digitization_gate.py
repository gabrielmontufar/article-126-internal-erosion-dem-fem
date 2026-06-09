from __future__ import annotations

import csv
import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"


SOURCE = {
    "source": "Chang 2012 doctoral thesis, HKUST Institutional Repository",
    "record_url": "https://repository.hkust.edu.hk/ir/Record/1783.1-7478",
    "pdf_url": "https://repository.hkust.edu.hk/ir/bitstream/1783.1-7478/1/b1165745.pdf",
    "doi_or_identifier": "10.14711/thesis-b1165745",
    "pdf_size_bytes_reported_by_repository": 8337015,
    "rights_note": "Copyrighted to the author. Reproduction is prohibited without the author's prior written consent.",
}


ROWS = [
    {
        "target_id": "CHANG_F4_6",
        "figure_or_table": "Figure 4-6",
        "response_family": "triaxial compression, confining stress 50 kPa",
        "x_variable": "hydraulic gradient",
        "y_variable": "cumulative eroded soil weight and coefficient of permeability",
        "extraction_status": "DIGITIZATION_REQUIRED",
        "minimum_digitization_record": "axis calibration, curve id, point coordinates, pixel residual, uncertainty band, no raw-data label",
        "claim_allowed_now": "full-text route for future residual extraction",
        "claim_blocked_now": "numeric residual validation",
    },
    {
        "target_id": "CHANG_F4_11",
        "figure_or_table": "Figure 4-11",
        "response_family": "triaxial extension, confining stress 50 kPa",
        "x_variable": "hydraulic gradient",
        "y_variable": "cumulative eroded soil weight and coefficient of permeability",
        "extraction_status": "DIGITIZATION_REQUIRED",
        "minimum_digitization_record": "axis calibration, curve id, point coordinates, pixel residual, uncertainty band, no raw-data label",
        "claim_allowed_now": "full-text route for future residual extraction",
        "claim_blocked_now": "numeric residual validation",
    },
    {
        "target_id": "CHANG_F5_1_TO_F5_14",
        "figure_or_table": "Figures 5-1 to 5-14",
        "response_family": "critical hydraulic gradients under complex stress states",
        "x_variable": "stress state, porosity, hydraulic gradient or p-q stress path",
        "y_variable": "initiation, skeleton-deformation, and failure hydraulic-gradient boundaries",
        "extraction_status": "DIGITIZATION_REQUIRED",
        "minimum_digitization_record": "axis calibration, curve id, point coordinates, pixel residual, uncertainty band, no raw-data label",
        "claim_allowed_now": "full-text route for future boundary-residual extraction",
        "claim_blocked_now": "critical-gradient residual validation",
    },
    {
        "target_id": "CHANG_APPENDIX_A",
        "figure_or_table": "Appendix A figures",
        "response_family": "additional internal-erosion response curves",
        "x_variable": "hydraulic gradient or strain",
        "y_variable": "strain, eroded mass, permeability, and stress-strain response",
        "extraction_status": "DIGITIZATION_REQUIRED",
        "minimum_digitization_record": "axis calibration, curve id, point coordinates, pixel residual, uncertainty band, no raw-data label",
        "claim_allowed_now": "expanded full-text route for future residual extraction",
        "claim_blocked_now": "raw cyclic or residual validation",
    },
]


def main() -> None:
    DATA.mkdir(exist_ok=True)
    csv_path = DATA / "external_chang2012_fulltext_digitization_gate.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(ROWS[0].keys()))
        writer.writeheader()
        writer.writerows(ROWS)

    summary = {
        "status": "PASS_FULLTEXT_ROUTE_DIGITIZATION_REQUIRED_NOT_RESIDUAL_VALIDATION",
        **SOURCE,
        "digitization_target_count": len(ROWS),
        "claim_enabled_now": "verified public full-text route and target map for audited Chang 2012 residual digitization",
        "claim_blocked_now": (
            "second independent quantitative residual validation until curves are digitized with uncertainty records "
            "or author/repository numeric data are obtained"
        ),
        "rights_boundary": (
            "do not package or reproduce the PDF or full thesis tables; use source locator, derived residual metrics, "
            "and permission/data-request records for submission"
        ),
    }
    (DATA / "external_chang2012_fulltext_digitization_gate_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
