from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def main() -> None:
    predictions = pd.read_csv(DATA / "external_ab_validation_predictions.csv")
    holdout = predictions[predictions["split"].eq("B_holdout_validation")].copy()
    if holdout.empty:
        raise SystemExit("No B_holdout_validation rows found")

    obs_loss_range = float(holdout["observed_fines_or_soil_loss_percent"].max() - holdout["observed_fines_or_soil_loss_percent"].min())
    if obs_loss_range <= 0:
        raise SystemExit("Observed fines-loss range is not positive")
    k_obs = holdout["observed_k_over_k0"].dropna()
    obs_k_range = float(k_obs.max() - k_obs.min()) if len(k_obs) >= 2 else 0.0
    if obs_k_range <= 0:
        raise SystemExit("Observed k/k0 range is not positive")

    rows: list[dict[str, object]] = []
    for model, group in holdout.groupby("model"):
        class_error = float((group["predicted_unstable"] != group["observed_unstable"]).mean())
        loss_mae = float((group["predicted_fines_or_soil_loss_percent"] - group["observed_fines_or_soil_loss_percent"]).abs().mean())
        k_group = group.dropna(subset=["observed_k_over_k0", "predicted_k_over_k0"])
        k_mae = float((k_group["predicted_k_over_k0"] - k_group["observed_k_over_k0"]).abs().mean())
        score = class_error + loss_mae / obs_loss_range + k_mae / obs_k_range
        rows.append(
            {
                "model": model,
                "holdout_cases": int(len(group)),
                "k_metric_cases": int(len(k_group)),
                "classification_error_rate": class_error,
                "fines_loss_mae_percent": loss_mae,
                "observed_fines_loss_range_percent": obs_loss_range,
                "normalized_fines_loss_mae": loss_mae / obs_loss_range,
                "k_over_k0_mae": k_mae,
                "observed_k_over_k0_range": obs_k_range,
                "normalized_k_over_k0_mae": k_mae / obs_k_range,
                "composite_holdout_residual_ranking_score": score,
            }
        )

    ranking = pd.DataFrame(rows).sort_values("composite_holdout_residual_ranking_score", ascending=True)
    ranking.insert(0, "rank", range(1, len(ranking) + 1))
    ranking.to_csv(DATA / "composite_holdout_residual_ranking.csv", index=False)

    full = ranking.iloc[0].to_dict()
    summary = {
        "validation_type": "Lee A/B composite holdout residual ranking",
        "source_prediction_file": "external_ab_validation_predictions.csv",
        "holdout_split": "B_holdout_validation",
        "observed_fines_loss_range_percent": obs_loss_range,
        "observed_k_over_k0_range": obs_k_range,
        "best_model": full["model"],
        "best_score": float(full["composite_holdout_residual_ranking_score"]),
        "ranking": [
            {
                "rank": int(row["rank"]),
                "model": row["model"],
                "score": float(row["composite_holdout_residual_ranking_score"]),
            }
            for _, row in ranking.iterrows()
        ],
        "claim_boundary": (
            "Residual ranking is computed only on the Lee et al. B holdout screening cases. "
            "It is not a Deng validation, field validation, or operational dam-safety validation."
        ),
    }
    (DATA / "composite_holdout_residual_ranking_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
