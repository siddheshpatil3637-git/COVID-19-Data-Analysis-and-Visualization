"""
Computes the statistics that back the article's central claim: official
COVID death counts substantially understate the pandemic's true toll, and
the size of that gap is not random - it correlates with reporting capacity,
not with how badly a country was actually hit.
"""

import pandas as pd
from data_pipeline import latest_snapshot, AGGREGATE_LOCATIONS


def excess_mortality_summary(df: pd.DataFrame) -> pd.DataFrame:
    """One row per country: latest cumulative official deaths/million vs.
    latest cumulative excess mortality/million, plus the gap and ratio."""
    snap = latest_snapshot(df, "excess_mortality_cumulative_per_million")
    snap = snap[~snap["location"].isin(AGGREGATE_LOCATIONS)]
    snap = snap.dropna(subset=["total_deaths_per_million"])
    snap = snap.copy()
    snap["gap_per_million"] = snap["excess_mortality_cumulative_per_million"] - snap["total_deaths_per_million"]
    snap["ratio"] = snap["excess_mortality_cumulative_per_million"] / snap["total_deaths_per_million"].replace(0, pd.NA)
    return snap[["location", "date", "total_deaths_per_million", "excess_mortality_cumulative_per_million",
                 "gap_per_million", "ratio"]].reset_index(drop=True)


def stringency_vs_outcome_summary(df: pd.DataFrame) -> pd.DataFrame:
    """One row per country: average stringency index over the pandemic vs.
    eventual cumulative deaths per million. Used to test whether stricter
    lockdowns clearly bought lower mortality."""
    real = df[~df["location"].isin(AGGREGATE_LOCATIONS)]
    avg_stringency = real.groupby(["location", "continent"], as_index=False)["stringency_index"].mean()
    avg_stringency = avg_stringency.rename(columns={"stringency_index": "avg_stringency"})

    final_deaths = latest_snapshot(real, "total_deaths_per_million")[["location", "total_deaths_per_million", "population"]]

    out = avg_stringency.merge(final_deaths, on="location", how="inner")
    return out.dropna(subset=["avg_stringency", "total_deaths_per_million", "population"])


def correlation_check(summary_df: pd.DataFrame) -> float:
    """Pearson correlation between average stringency and eventual deaths
    per million. Near zero / positive would be the counterintuitive finding
    worth flagging (i.e. stricter lockdowns did NOT clearly track with lower
    mortality across countries, at least not in a simple bivariate sense)."""
    return summary_df["avg_stringency"].corr(summary_df["total_deaths_per_million"])


def headline_stats(excess_df: pd.DataFrame) -> dict:
    """Summary stats for the write-up.

    The "top ratio" example is chosen among countries with
    total_deaths_per_million > 200 (not just any nonzero value): with a
    near-zero official-death denominator, the ratio metric explodes for
    reasons that are more about that denominator than about a meaningful,
    discussable undercount (e.g. 12 official deaths/million and 1,500
    excess/million yields a 124x ratio that is technically true but a poor
    headline number). The median ratio plus a robustly-documented example
    are more honest to lead with.
    """
    valid = excess_df.dropna(subset=["ratio"])
    valid = valid[valid["total_deaths_per_million"] > 10]
    median_ratio = valid["ratio"].median()
    undercounted_pct = (valid["ratio"] > 1.3).mean() * 100

    robust = valid[valid["total_deaths_per_million"] > 200]
    top = robust.sort_values("ratio", ascending=False).iloc[0]

    return {
        "n_countries": len(valid),
        "median_ratio": median_ratio,
        "top_country": top["location"],
        "top_ratio": top["ratio"],
        "pct_countries_undercounted": undercounted_pct,
    }
