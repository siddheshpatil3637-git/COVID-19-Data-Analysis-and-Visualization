# COVID-19 Data Story: The Hidden Toll

An interactive dashboard built from Our World in Data's COVID-19 dataset,
built to surface a specific, non-obvious finding rather than just chart
case counts.

## The insight

Across 123 countries with reliable excess-mortality data, the
median country's *true* pandemic death toll (measured by excess mortality)
was **1.3x** its officially reported COVID death count.
More than half of these countries (53%)
show a gap too large to be statistical noise. Separately, across countries,
average lockdown stringency barely correlates with eventual death rate
(r = 0.05) — the simple "stricter lockdown -> fewer deaths" story does
not hold up cleanly in the cross-country data.

Full write-up is in the dashboard itself (see below).

## Project structure

```
covid-dashboard/
  data/                     cached OWID CSV (auto-downloaded on first run)
  output/
    covid_dashboard.html    <- the deliverable: open this in a browser
  src/
    config.py               country lists + event annotation config
    data_pipeline.py         fetch / cache / clean / validate
    analysis.py              computes the stats behind the insight
    charts.py                plotly chart-building functions
    annotations.py           event-annotation overlay helper
    narrative.py             generates the write-up HTML from live stats
    build_dashboard.py       orchestrates everything -> output/covid_dashboard.html
```

## Running it

```
cd src
python3 build_dashboard.py
```

Requires `pandas` and `plotly`. On first run this downloads OWID's ~100MB
CSV (from https://covid.ourworldindata.org, falling back to OWID's public
GitHub mirror if that host isn't reachable) and caches it in `data/` so
subsequent runs are fast. Delete `data/owid-covid-data.csv` or call
`fetch_data(force_refresh=True)` to pull a fresh copy.

## Data notes

See the "A note on the data" section at the bottom of the dashboard for
caveats on reporting gaps, testing-rate bias, inconsistent death
definitions across countries, and the limitations of excess mortality
itself as an estimate.

Source: Our World in Data COVID-19 dataset (Johns Hopkins CSSE, national
health ministries, and — for excess mortality — the Human Mortality
Database / World Mortality Dataset and The Economist's excess mortality
model).
