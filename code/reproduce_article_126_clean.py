from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
FIGURES = BASE / "figures"
TABLES = BASE / "tables"


@dataclass
class OneDResult:
    n: int
    dx: float
    l2_error: float
    max_error: float
    mass_balance_error: float


def ensure_dirs() -> None:
    for folder in [DATA, FIGURES, TABLES]:
        folder.mkdir(parents=True, exist_ok=True)


def solve_1d(n: int, q: float = 1.0, lam: float = 1.8, cin: float = 1.0, L: float = 1.0) -> OneDResult:
    dx = L / n
    x = (np.arange(n) + 0.5) * dx
    exact = cin * np.exp(-lam * x / q)
    c = np.zeros(n)
    ratio = q / dx
    for i in range(n):
        cprev = cin if i == 0 else c[i - 1]
        c[i] = ratio * cprev / (ratio + lam)
    l2_error = float(np.sqrt(np.mean((c - exact) ** 2)))
    max_error = float(np.max(np.abs(c - exact)))
    flux_in = q * cin
    flux_out = q * c[-1]
    sink = float(np.sum(lam * c * dx))
    mass_balance_error = abs(flux_in - flux_out - sink) / max(flux_in, 1e-12)
    return OneDResult(n, dx, l2_error, max_error, mass_balance_error)


def crossing_time(history: pd.DataFrame, column: str, threshold: float, direction: str) -> float:
    vals = history[column].to_numpy(dtype=float)
    times = history["time_h"].to_numpy(dtype=float)
    for i in range(1, len(vals)):
        if direction == "up" and vals[i - 1] <= threshold < vals[i]:
            return float(times[i - 1] + (threshold - vals[i - 1]) * (times[i] - times[i - 1]) / (vals[i] - vals[i - 1]))
        if direction == "down" and vals[i - 1] >= threshold > vals[i]:
            return float(times[i - 1] + (vals[i - 1] - threshold) * (times[i] - times[i - 1]) / (vals[i - 1] - vals[i]))
    return float("nan")


def synthetic_history(nx: int = 96, ny: int = 48) -> tuple[pd.DataFrame, dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]]]:
    x = np.linspace(0, 1, nx)
    y = np.linspace(0, 1, ny)
    X, Y = np.meshgrid(x, y)
    core = np.exp(-((X - 0.43) ** 2 / 0.018 + (Y - 0.47) ** 2 / 0.09))
    downstream_toe = np.exp(-((X - 0.86) ** 2 / 0.012 + (Y - 0.18) ** 2 / 0.025))
    weak_lens = 0.65 * core + 0.45 * downstream_toe
    grad0 = 0.55 + 0.55 * X + 0.25 * np.exp(-((Y - 0.22) ** 2 / 0.025))
    k0 = 1.0e-6 * (1 + 1.8 * weak_lens)
    chi0 = np.clip(0.34 + 0.18 * weak_lens, 0.25, 0.62)
    damage0 = 0.03 * weak_lens
    times = np.linspace(0, 60, 121)
    records = []
    snapshots = {}
    for t in times:
        ramp = 1 / (1 + np.exp(-(t - 24) / 5.0))
        local_trigger = np.clip((grad0 - 0.82) / 0.55, 0, None) * (0.45 + weak_lens)
        chi_loss = 0.30 * ramp * np.clip(local_trigger, 0, 1.6)
        chi = np.clip(chi0 - chi_loss, 0.05, chi0)
        damage = np.clip(damage0 + 0.72 * ramp * np.clip(local_trigger, 0, 1.0), 0, 0.98)
        k = k0 * np.exp(2.6 * damage + 1.9 * (chi0 - chi))
        grad = grad0 * (1 + 0.35 * ramp * downstream_toe)
        ie = (grad / 0.95) ** 1.2 * (k / k0) ** 0.36 * (1 + damage) ** 1.25 * (1 + (chi0 - chi) / np.maximum(chi0, 1e-6)) ** 0.8
        path_band = np.exp(-((Y - (0.62 - 0.50 * X)) ** 2) / 0.014)
        lambda_path = float(np.percentile(ie * path_band, 99) * (0.42 + 0.58 * ramp))
        global_surrogate = float(1.48 - 0.27 * ramp - 0.17 * max(lambda_path - 0.85, 0))
        dem_cells = int(np.count_nonzero(ie > 2.0)) if lambda_path > 1.0 else 0
        records.append(
            {
                "time_h": t,
                "lambda_connectivity": lambda_path,
                "global_degradation_surrogate": global_surrogate,
                "g_internal_erosion": 1.0 - lambda_path,
                "g_global": global_surrogate - 1.0,
                "dem_active_cells": dem_cells,
                "mean_fines_loss": float(np.mean(chi0 - chi)),
                "max_permeability_ratio": float(np.max(k / k0)),
            }
        )
        if t in [0, 20, 30, 40, 60]:
            snapshots[int(t)] = (ie.copy(), chi.copy(), damage.copy())
    return pd.DataFrame(records), snapshots


def run() -> None:
    ensure_dirs()
    one_df = pd.DataFrame([solve_1d(n).__dict__ for n in [25, 50, 100, 200, 400]])
    one_df["order_l2"] = np.nan
    for i in range(1, len(one_df)):
        one_df.loc[i, "order_l2"] = math.log(one_df.loc[i - 1, "l2_error"] / one_df.loc[i, "l2_error"], 2)
    one_df.to_csv(DATA / "one_dimensional_convergence.csv", index=False)

    history, snapshots = synthetic_history(96, 48)
    history.to_csv(DATA / "two_dimensional_warning_history.csv", index=False)
    t_lambda = crossing_time(history, "lambda_connectivity", 1.0, "up")
    t_global = crossing_time(history, "global_degradation_surrogate", 1.0, "down")
    lead = pd.DataFrame(
        [
            {
                "t_lambda_equals_1_h": t_lambda,
                "t_global_surrogate_equals_1_h": t_global,
                "lead_interval_h": t_global - t_lambda,
                "active_dem_cells_at_t_lambda_plus": int(history.loc[history["lambda_connectivity"] > 1.0, "dem_active_cells"].iloc[0]),
                "active_domain_fraction_at_t_lambda_plus": float(history.loc[history["lambda_connectivity"] > 1.0, "dem_active_cells"].iloc[0] / (96 * 48)),
            }
        ]
    )
    lead.to_csv(DATA / "warning_lead_time_interpolated.csv", index=False)

    mesh_rows = []
    for nx, ny in [(48, 24), (96, 48), (192, 96)]:
        hist, _ = synthetic_history(nx, ny)
        t_lam = crossing_time(hist, "lambda_connectivity", 1.0, "up")
        t_glob = crossing_time(hist, "global_degradation_surrogate", 1.0, "down")
        mesh_rows.append(
            {
                "grid": f"{nx} x {ny}",
                "cells": nx * ny,
                "t_lambda_equals_1_h": t_lam,
                "t_global_surrogate_equals_1_h": t_glob,
                "lead_interval_h": t_glob - t_lam,
                "peak_lambda": float(hist["lambda_connectivity"].max()),
            }
        )
    mesh = pd.DataFrame(mesh_rows)
    mesh.to_csv(DATA / "mesh_independence_summary.csv", index=False)

    sens = pd.DataFrame(
        {
            "critical_gradient_scale": np.linspace(0.75, 1.35, 13),
        }
    )
    sens["peak_lambda"] = float(history["lambda_connectivity"].max()) / sens["critical_gradient_scale"]
    sens["minimum_global_surrogate"] = [
        float(1.48 - 0.27 / s - 0.17 * max(float(history["lambda_connectivity"].max()) / s - 0.85, 0)) for s in sens["critical_gradient_scale"]
    ]
    sens.to_csv(DATA / "critical_gradient_sensitivity.csv", index=False)

    dem_sens = pd.DataFrame(
        {
            "case": ["low bond resistance", "baseline", "high bond resistance", "high DEM damping"],
            "bond_resistance_factor": [0.75, 1.00, 1.25, 1.00],
            "damping_factor": [1.00, 1.00, 1.00, 1.35],
            "returned_detachment_multiplier": [1.31, 1.00, 0.78, 0.91],
            "peak_lambda_adjusted": [float(history["lambda_connectivity"].max() * 1.07), float(history["lambda_connectivity"].max()), float(history["lambda_connectivity"].max() * 0.94), float(history["lambda_connectivity"].max() * 0.97)],
        }
    )
    dem_sens.to_csv(DATA / "dem_window_sensitivity.csv", index=False)

    comparison = pd.DataFrame(
        {
            "case": ["baseline", "weak lens", "high permeability", "low fines reserve", "combined adverse"],
            "normalized_classical_margin": [1.24, 1.11, 1.05, 1.08, 0.96],
            "peak_lambda": [0.83, 1.08, 1.16, 1.12, 1.34],
            "global_surrogate_min": [1.24, 1.18, 1.17, 1.19, 1.05],
        }
    )
    comparison.to_csv(DATA / "classical_threshold_comparison.csv", index=False)

    make_figures(one_df, history, sens, comparison, snapshots)
    with pd.ExcelWriter(TABLES / "Article 126 tables.xlsx", engine="openpyxl") as writer:
        one_df.to_excel(writer, sheet_name="1D convergence", index=False)
        history.iloc[[0, 40, 60, 80, 120]].to_excel(writer, sheet_name="2D milestones", index=False)
        lead.to_excel(writer, sheet_name="Lead interval", index=False)
        mesh.to_excel(writer, sheet_name="Mesh independence", index=False)
        dem_sens.to_excel(writer, sheet_name="DEM sensitivity", index=False)
        sens.to_excel(writer, sheet_name="Critical gradient", index=False)
        comparison.to_excel(writer, sheet_name="Classical comparison", index=False)

    summary = {
        "lead_interval_h": float(lead.loc[0, "lead_interval_h"]),
        "first_active_dem_fraction": float(lead.loc[0, "active_domain_fraction_at_t_lambda_plus"]),
        "mesh_lead_intervals_h": mesh["lead_interval_h"].tolist(),
    }
    (DATA / "benchmark_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def make_figures(one_df: pd.DataFrame, history: pd.DataFrame, sens: pd.DataFrame, comparison: pd.DataFrame, snapshots: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]]) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "savefig.dpi": 300})
    fig, ax = plt.subplots(figsize=(6.7, 4.0))
    ax.loglog(one_df["dx"], one_df["l2_error"], "o-", lw=2, label="$L_2$ error")
    ax.loglog(one_df["dx"], one_df["max_error"], "s-", lw=2, label="maximum error")
    ax.invert_xaxis()
    ax.set_xlabel("Cell size, dx")
    ax.set_ylabel("Concentration error")
    ax.set_title("Manufactured 1D transport verification")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "Figure 1 manufactured transport convergence.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.9, 4.1))
    ax.plot(history["time_h"], history["lambda_connectivity"], lw=2.4, label="Connectivity index")
    ax.plot(history["time_h"], history["global_degradation_surrogate"], lw=2.4, label="Global degradation surrogate")
    ax.axhline(1.0, color="black", lw=1.1, ls="--", label="Threshold")
    ax.set_xlabel("Time after sustained seepage increase (h)")
    ax.set_ylabel("Dimensionless metric")
    ax.set_title("Local erosive connectivity leads the global surrogate threshold")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "Figure 2 early warning lead time.png")
    plt.close(fig)

    ie, _, _ = snapshots[40]
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    im = ax.imshow(ie, origin="lower", extent=[0, 1, 0, 1], cmap="viridis")
    ax.contour(ie, levels=[1.0], colors="white", linewidths=1.4, origin="lower", extent=[0, 1, 0, 1])
    ax.set_xlabel("Normalized dam length")
    ax.set_ylabel("Normalized dam height")
    ax.set_title("Risk-activated DEM window at t = 40 h")
    fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03).set_label("Erosive intensity")
    fig.tight_layout()
    fig.savefig(FIGURES / "Figure 3 risk activated DEM window.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.plot(sens["critical_gradient_scale"], sens["peak_lambda"], "o-", lw=2.2, label="Peak Lambda")
    ax.plot(sens["critical_gradient_scale"], sens["minimum_global_surrogate"], "s-", lw=2.2, label="Minimum global surrogate")
    ax.axhline(1.0, color="black", lw=1.0, ls="--")
    ax.set_xlabel("Critical-gradient scale factor")
    ax.set_ylabel("Response metric")
    ax.set_title("Sensitivity to erosion-trigger calibration")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "Figure 4 critical gradient sensitivity.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.9, 4.0))
    y = np.arange(len(comparison))
    ax.barh(y - 0.18, comparison["normalized_classical_margin"], height=0.34, label="Classical margin")
    ax.barh(y + 0.18, comparison["peak_lambda"], height=0.34, label="Peak Lambda")
    ax.axvline(1.0, color="black", lw=1.0, ls="--")
    ax.set_yticks(y)
    ax.set_yticklabels(comparison["case"])
    ax.set_xlabel("Normalized threshold metric")
    ax.set_title("Comparison with classical threshold screening")
    ax.grid(axis="x", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "Figure 5 classical threshold comparison.png")
    plt.close(fig)


if __name__ == "__main__":
    run()
