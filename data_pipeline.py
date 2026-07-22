"""
Data pipeline: fetch -> cache -> clean -> validate.

Why per-capita over raw counts:
Raw case/death counts are dominated by population size, not by how badly a
country was actually hit. Comparing the US and New Zealand on raw death
counts tells you almost nothing except that the US has 65x the population.
Per-million / per-hundred figures are what make cross-country comparison
meaningful, so wherever OWID provides a per-capita version of a metric we
prefer it for anything involving country comparison.
"""

import os
import urllib.request
import pandas as pd

# OWID's canonical hosted URL. If unreachable in this environment, we fall
# back to the identical file mirrored in OWID's own public GitHub repo.
PRIMARY_URL = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
FALLBACK_URL = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"

LOCAL_CACHE = os.path.join(os.path.dirname(__file__), "..", "data", "owid-covid-data.csv")

USE_COLS = [
    "iso_code", "continent", "location", "date",
    "total_cases", "new_cases", "new_cases_smoothed",
    "total_deaths", "new_deaths", "new_deaths_smoothed",
    "total_cases_per_million", "new_cases_per_million", "new_cases_smoothed_per_million",
    "total_deaths_per_million", "new_deaths_per_million", "new_deaths_smoothed_per_million",
    "people_vaccinated_per_hundred", "people_fully_vaccinated_per_hundred",
    "total_boosters_per_hundred", "new_vaccinations_smoothed_per_million",
    "stringency_index",
    "excess_mortality_cumulative_per_million", "excess_mortality",
    "population",
]

# Aggregate "locations" OWID includes alongside real countries (continents,
# income groups, "World"). Useful for some views, but must be excluded from
# country-level rankings or they'll distort them.
AGGREGATE_LOCATIONS = {
    "Africa", "Asia", "Europe", "European Union (27)", "North America",
    "Oceania", "South America", "World",
    "High-income countries", "Low-income countries",
    "Lower-middle-income countries", "Upper-middle-income countries",
}


def fetch_data(force_refresh: bool = False) -> str:
    """Download the OWID CSV if not already cached locally. Returns the path
    to the local file. Tries the primary OWID URL, falls back to the GitHub
    mirror (same data, published by OWID) if that host isn't reachable."""
    os.makedirs(os.path.dirname(LOCAL_CACHE), exist_ok=True)

    if os.path.exists(LOCAL_CACHE) and not force_refresh:
        return LOCAL_CACHE

    for url in (PRIMARY_URL, FALLBACK_URL):
        try:
            urllib.request.urlretrieve(url, LOCAL_CACHE)
            return LOCAL_CACHE
        except Exception as e:
            print(f"Could not fetch from {url}: {e}")
            continue

    raise RuntimeError("Failed to download OWID data from any known source.")


def load_raw(path: str = None) -> pd.DataFrame:
    path = path or fetch_data()
    df = pd.read_csv(path, usecols=USE_COLS, parse_dates=["date"])
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate the raw dataframe.

    - Drops rows with no location/date (shouldn't happen, but validate anyway)
    - Flags aggregate rows (continents, income groups, "World") separately
      from real countries rather than silently dropping them, since some
      views (e.g. income-group comparison) actually want them.
    - Forward-fills cumulative fields within each country's time series where
      there are short reporting gaps (a day of missing data doesn't mean
      cumulative cases reset to zero) but does NOT forward-fill the daily
      "new_*" fields, since a gap in daily reporting is not evidence that
      zero cases occurred.
    """
    df = df.dropna(subset=["location", "date"]).copy()
    df = df.sort_values(["location", "date"])

    df["is_aggregate"] = df["location"].isin(AGGREGATE_LOCATIONS)

    cumulative_cols = [c for c in df.columns if c.startswith("total_") or "per_hundred" in c or "cumulative" in c]
    df[cumulative_cols] = df.groupby("location")[cumulative_cols].ffill()

    return df


def get_country_slice(df: pd.DataFrame, countries: list) -> pd.DataFrame:
    return df[df["location"].isin(countries)].copy()


def latest_snapshot(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """For each location, return the most recent non-null row for `metric`."""
    sub = df.dropna(subset=[metric])
    return sub.sort_values("date").groupby("location", as_index=False).tail(1)


if __name__ == "__main__":
    path = fetch_data()
    print(f"Data cached at: {path}")
    raw = load_raw(path)
    print(f"Rows: {len(raw):,}  |  Locations: {raw['location'].nunique()}  |  Date range: {raw['date'].min().date()} to {raw['date'].max().date()}")
    clean = clean_data(raw)
    print("Cleaned.")
