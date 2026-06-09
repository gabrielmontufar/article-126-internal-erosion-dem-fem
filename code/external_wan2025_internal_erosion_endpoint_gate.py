from __future__ import annotations

import csv
import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"


SOURCE = {
    "source_id": "Wan_Pan_Luo_Peng_2025_SciRep",
    "source": "Wan, Pan, Luo and Peng (2025), Scientific Reports",
    "title": "Experimental study on the impact of water flow velocity on internal erosion of granite residual soil",
    "doi": "10.1038/s41598-025-06012-x",
    "public_locator": "https://www.nature.com/articles/s41598-025-06012-x",
    "rights_note": "Open-access article; this package stores only source-reported endpoint values and derived metrics.",
    "source_basis": (
        "Scientific Reports conclusion text reports wetting-front arrival times at 100 cm and cumulative fine-particle "
        "loss over 90 min for 25, 50 and 100 L/H flow conditions."
    ),
}

OBSERVATIONS = [
    {
        "case_id": "WAN2025_Q25",
        "flow_rate_l_per_h": 25.0,
        "wetting_front_arrival_100cm_min": 29.89,
        "cumulative_fine_particle_loss_90min_g": 202.61,
    },
    {
        "case_id": "WAN2025_Q50",
        "flow_rate_l_per_h": 50.0,
        "wetting_front_arrival_100cm_min": 24.93,
        "cumulative_fine_particle_loss_90min_g": 226.99,
    },
    {
        "case_id": "WAN2025_Q100",
        "flow_rate_l_per_h": 100.0,
        "wetting_front_arrival_100cm_min": 21.78,
        "cumulative_fine_particle_loss_90min_g": 252.33,
    },
]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def is_strictly_increasing(values: list[float]) -> bool:
    return all(b > a for a, b in zip(values, values[1:]))


def is_strictly_decreasing(values: list[float]) -> bool:
    return all(b < a for a, b in zip(values, values[1:]))


def ranks(values: list[float]) -> list[int]:
    order = {value: rank for rank, value in enumerate(sorted(values), start=1)}
    return [order[value] for value in values]


def spearman_no_ties(x: list[float], y: list[float]) -> float:
    rx = ranks(x)
    ry = ranks(y)
    n = len(x)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    return 1.0 - (6.0 * d2) / (n * (n * n - 1.0))


def linear_slope(x: list[float], y: list[float]) -> float:
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    denominator = sum((xi - x_mean) ** 2 for xi in x)
    return numerator / denominator


def main() -> None:
    DATA.mkdir(exist_ok=True)
    enriched_rows: list[dict[str, object]] = []
    for row in OBSERVATIONS:
        enriched_rows.append(
            {
                **SOURCE,
                **row,
                "claim_scope": "open primary endpoint directionality only; not Chang/Sterpi/Zhu suffusion residual validation",
            }
        )

    flow = [row["flow_rate_l_per_h"] for row in OBSERVATIONS]
    wetting = [row["wetting_front_arrival_100cm_min"] for row in OBSERVATIONS]
    loss = [row["cumulative_fine_particle_loss_90min_g"] for row in OBSERVATIONS]
    metrics = [
        {
            "metric": "flow_order",
            "value": "strictly_increasing" if is_strictly_increasing(flow) else "not_strictly_increasing",
            "pass": is_strictly_increasing(flow),
            "claim_scope": "input-condition ordering",
        },
        {
            "metric": "wetting_front_time_vs_flow",
            "value": "strictly_decreasing" if is_strictly_decreasing(wetting) else "not_strictly_decreasing",
            "pass": is_strictly_decreasing(wetting),
            "claim_scope": "higher flow should accelerate front arrival",
        },
        {
            "metric": "cumulative_loss_vs_flow",
            "value": "strictly_increasing" if is_strictly_increasing(loss) else "not_strictly_increasing",
            "pass": is_strictly_increasing(loss),
            "claim_scope": "higher flow should increase cumulative erosion endpoint",
        },
        {
            "metric": "spearman_flow_wetting_time",
            "value": spearman_no_ties(flow, wetting),
            "pass": spearman_no_ties(flow, wetting) == -1.0,
            "claim_scope": "rank-order endpoint check",
        },
        {
            "metric": "spearman_flow_cumulative_loss",
            "value": spearman_no_ties(flow, loss),
            "pass": spearman_no_ties(flow, loss) == 1.0,
            "claim_scope": "rank-order endpoint check",
        },
        {
            "metric": "wetting_time_slope_min_per_l_per_h",
            "value": linear_slope(flow, wetting),
            "pass": linear_slope(flow, wetting) < 0.0,
            "claim_scope": "descriptive endpoint slope",
        },
        {
            "metric": "cumulative_loss_slope_g_per_l_per_h",
            "value": linear_slope(flow, loss),
            "pass": linear_slope(flow, loss) > 0.0,
            "claim_scope": "descriptive endpoint slope",
        },
    ]

    write_csv(DATA / "external_wan2025_internal_erosion_endpoints.csv", enriched_rows)
    write_csv(DATA / "external_wan2025_internal_erosion_endpoint_gate_metrics.csv", metrics)

    summary = {
        "status": "PASS_OPEN_PRIMARY_ENDPOINT_DIRECTIONAL_GATE_NOT_SUFFUSION_RESIDUAL_VALIDATION",
        **SOURCE,
        "case_count": len(OBSERVATIONS),
        "flow_rates_l_per_h": flow,
        "wetting_front_arrival_100cm_min": wetting,
        "cumulative_fine_particle_loss_90min_g": loss,
        "all_directional_metrics_pass": all(bool(row["pass"]) for row in metrics),
        "spearman_flow_wetting_time": spearman_no_ties(flow, wetting),
        "spearman_flow_cumulative_loss": spearman_no_ties(flow, loss),
        "wetting_time_slope_min_per_l_per_h": linear_slope(flow, wetting),
        "cumulative_loss_slope_g_per_l_per_h": linear_slope(flow, loss),
        "claim_enabled_now": (
            "open primary endpoint support that the screening operator must preserve flow-rate-sensitive acceleration "
            "of wetting-front arrival and increased cumulative fine-particle loss"
        ),
        "claim_blocked_now": (
            "second-family suffusion residual validation against Sterpi/Chang/Zhu; calibrated erosion-path prediction; "
            "raw trajectory validation"
        ),
        "ethical_constraint": (
            "use as a limited endpoint directionality gate only; do not label as raw data, field validation, or "
            "Chang/Sterpi/Zhu residual validation"
        ),
    }
    (DATA / "external_wan2025_internal_erosion_endpoint_gate_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
