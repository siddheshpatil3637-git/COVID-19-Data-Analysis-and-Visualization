"""
Orchestrates the full pipeline: fetch -> clean -> analyze -> plot -> assemble
into a single self-contained HTML dashboard file.

Run: python3 build_dashboard.py
Output: ../output/covid_dashboard.html
"""

import os
import plotly.io as pio

from data_pipeline import fetch_data, load_raw, clean_data
from analysis import (
    excess_mortality_summary, stringency_vs_outcome_summary,
    correlation_check, headline_stats,
)
from charts import (
    plot_case_trends, plot_vaccination_rollout, plot_mortality_and_cfr,
    plot_excess_vs_official_bar, plot_excess_gap_ratio, plot_stringency_vs_outcome,
)
from narrative import build_summary_html
from config import (
    COMPARISON_COUNTRIES, VACCINE_COMPARISON_COUNTRIES, EXCESS_MORTALITY_COUNTRIES,
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "covid_dashboard.html")

DATA_NOTES_HTML = """
<div class="data-notes">
  <h3>A note on the data</h3>
  <ul>
    <li><strong>Source:</strong> Our World in Data's COVID-19 dataset, compiled from
      Johns Hopkins CSSE, national health ministries, and (for excess
      mortality) the Human Mortality Database / World Mortality Dataset and
      The Economist's excess mortality model.</li>
    <li><strong>Reporting gaps:</strong> Many countries stopped or reduced official
      case/death reporting well before OWID's dataset ends; recent-period
      comparisons should be read with that in mind, not as evidence the
      pandemic simply stopped.</li>
    <li><strong>Testing-rate bias:</strong> Case counts are a function of testing
      volume as much as true infection spread. Two countries with identical
      outbreaks but very different testing capacity will show very
      different official case curves - this is a major reason the analysis
      below leans on deaths and excess mortality rather than case counts
      wherever possible.</li>
    <li><strong>Inconsistent death definitions:</strong> Countries differ in whether a
      death is coded as "COVID" based on a positive test, a clinical
      judgment, or "died within N days of a positive test" - definitions
      that produce meaningfully different counts even for identical
      underlying mortality.</li>
    <li><strong>Excess mortality</strong> is itself an estimate (modeled against a
      historical baseline), not a perfect count, and is unavailable for some
      countries with poor vital-registration systems - which, somewhat
      ironically, are often the same countries where the official/true gap
      is likely largest and least visible.</li>
    <li><strong>Event annotations</strong> (lockdowns, variant surges, vaccine
      milestones) use approximate global/consensus timing for
      storytelling purposes. Actual timing varied by country, sometimes by
      months.</li>
  </ul>
</div>
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>COVID-19 Data Story: The Hidden Toll</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    max-width: 980px; margin: 0 auto; padding: 24px 20px 80px;
    color: #1a1a1a; line-height: 1.6; background: #fdfdfd;
  }}
  h1 {{ font-size: 2rem; margin-bottom: 0.3em; }}
  h2 {{ margin-top: 2.5em; border-top: 1px solid #eee; padding-top: 1em; }}
  h3 {{ margin-top: 1.5em; }}
  .lede {{ font-size: 1.15rem; color: #333; }}
  .narrative p {{ font-size: 1.02rem; }}
  .chart-block {{ margin: 2em 0; }}
  .data-notes {{ background: #f6f6f4; border-radius: 8px; padding: 1.2em 1.6em; margin-top: 2em; font-size: 0.92rem; color: #444; }}
  .data-notes li {{ margin-bottom: 0.5em; }}
  .footer {{ margin-top: 3em; font-size: 0.85rem; color: #888; text-align: center; }}
  .section-intro {{ color: #444; font-size: 0.98rem; margin-bottom: 0.5em; }}
</style>
</head>
<body>
{narrative}

<h2>1. The hidden toll: official deaths vs. true excess mortality</h2>
<p class="section-intro">Selected countries with reliable excess-mortality data,
spanning high, upper-middle, and lower-income economies. The gap between the
two bars is, in effect, the size of the undercount.</p>
<div class="chart-block">{chart1}</div>
<div class="chart-block">{chart2}</div>

<h2>2. Did stricter lockdowns actually mean fewer deaths?</h2>
<p class="section-intro">Each bubble is one country: average lockdown
stringency (2020-2022) on the x-axis, eventual deaths per million on the
y-axis, sized by population.</p>
<div class="chart-block">{chart3}</div>

<h2>3. Case trends by country</h2>
<p class="section-intro">Daily new cases per million, with major variant
surges and the first lockdown wave marked. Note how comparable countries'
case curves diverge sharply after Omicron, largely reflecting differences in
testing policy, not necessarily true spread.</p>
<div class="chart-block">{chart4}</div>

<h2>4. Vaccination rollout</h2>
<p class="section-intro">Share of each country's population fully
vaccinated over time.</p>
<div class="chart-block">{chart5}</div>

<h2>5. Mortality: absolute deaths vs. case-fatality rate</h2>
<p class="section-intro">These two views tell different stories on purpose:
deaths per million shows overall burden, while case-fatality rate shows how
dangerous a diagnosed infection was at any given point - watch how sharply
CFR drops after vaccine rollout even in countries where raw case counts stay
high.</p>
<div class="chart-block">{chart6}</div>

{data_notes}

<div class="footer">
  Data: Our World in Data (OWID) COVID-19 dataset. Built with pandas + Plotly.
</div>
</body>
</html>
"""


def fig_to_div(fig, include_js=False):
    return pio.to_html(fig, include_plotlyjs="cdn" if include_js else False, full_html=False)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Fetching data...")
    path = fetch_data()
    raw = load_raw(path)
    df = clean_data(raw)
    print(f"Loaded {len(df):,} rows across {df['location'].nunique()} locations.")

    print("Running analysis...")
    exc_summary = excess_mortality_summary(df)
    exc_selected = exc_summary[exc_summary["location"].isin(EXCESS_MORTALITY_COUNTRIES)]
    stats = headline_stats(exc_summary)

    strin_summary = stringency_vs_outcome_summary(df)
    corr = correlation_check(strin_summary)

    print("Building charts...")
    chart1 = plot_excess_vs_official_bar(exc_selected)
    chart2 = plot_excess_gap_ratio(exc_selected)
    chart3 = plot_stringency_vs_outcome(strin_summary)
    chart4 = plot_case_trends(df, COMPARISON_COUNTRIES)
    chart5 = plot_vaccination_rollout(df, VACCINE_COMPARISON_COUNTRIES)
    chart6 = plot_mortality_and_cfr(df, COMPARISON_COUNTRIES[:5])

    print("Assembling dashboard HTML...")
    narrative_html = build_summary_html(stats, corr)

    html = PAGE_TEMPLATE.format(
        narrative=narrative_html,
        chart1=fig_to_div(chart1, include_js=True),
        chart2=fig_to_div(chart2),
        chart3=fig_to_div(chart3),
        chart4=fig_to_div(chart4),
        chart5=fig_to_div(chart5),
        chart6=fig_to_div(chart6),
        data_notes=DATA_NOTES_HTML,
    )

    with open(OUTPUT_FILE, "w") as f:
        f.write(html)

    print(f"Done. Dashboard written to {OUTPUT_FILE}")
    print("\n--- Headline stats ---")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"  stringency-vs-mortality correlation: {corr:.3f}")


if __name__ == "__main__":
    main()
