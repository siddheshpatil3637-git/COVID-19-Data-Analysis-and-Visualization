"""
Chart-building functions. Each returns a plotly Figure; nothing here writes
files or fetches data - that's build_dashboard.py's job. Keeping plotting
pure and side-effect-free makes these easy to reuse or test individually.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from annotations import add_event_annotations
from config import GLOBAL_EVENTS

TEMPLATE = "plotly_white"


def plot_case_trends(df, countries):
    sub = df[df["location"].isin(countries)]
    fig = px.line(
        sub, x="date", y="new_cases_smoothed_per_million", color="location",
        template=TEMPLATE,
        title="Daily New Cases (7-day smoothed, per million people)",
        labels={"new_cases_smoothed_per_million": "New cases per million", "date": "", "location": "Country"},
    )
    add_event_annotations(fig, [e for e in GLOBAL_EVENTS if e["kind"] in ("variant", "lockdown", "milestone")])
    fig.update_layout(legend_title_text="", hovermode="x unified", height=520)
    return fig


def plot_vaccination_rollout(df, countries):
    sub = df[df["location"].isin(countries)]
    fig = px.line(
        sub, x="date", y="people_fully_vaccinated_per_hundred", color="location",
        template=TEMPLATE,
        title="Vaccination Rollout: Share of Population Fully Vaccinated",
        labels={"people_fully_vaccinated_per_hundred": "% fully vaccinated", "date": "", "location": "Country"},
    )
    add_event_annotations(fig, [e for e in GLOBAL_EVENTS if e["kind"] in ("vaccine", "milestone")])
    fig.update_layout(legend_title_text="", hovermode="x unified", height=520, yaxis_range=[0, 100])
    return fig


def plot_mortality_and_cfr(df, countries):
    """Two stacked subplots: deaths per million over time, and case-fatality
    rate over time. Kept separate on purpose - a falling CFR with rising
    deaths (or vice versa) tells a completely different story than a single
    blended metric would."""
    sub = df[df["location"].isin(countries)].copy()
    # CFR computed from smoothed series to reduce divide-by-zero noise on
    # single-day case counts; still nulled out below when cases are near zero.
    sub["cfr_pct"] = (sub["new_deaths_smoothed"] / sub["new_cases_smoothed"]) * 100
    sub.loc[sub["new_cases_smoothed"] < 1, "cfr_pct"] = None

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
        subplot_titles=("Deaths per million (7-day smoothed)", "Case-fatality rate: deaths ÷ cases (%)"),
    )
    colors = px.colors.qualitative.Plotly
    for i, country in enumerate(countries):
        c = sub[sub["location"] == country]
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatter(x=c["date"], y=c["new_deaths_smoothed_per_million"], name=country,
                                  legendgroup=country, line=dict(color=color)), row=1, col=1)
        fig.add_trace(go.Scatter(x=c["date"], y=c["cfr_pct"], name=country, legendgroup=country,
                                  showlegend=False, line=dict(color=color)), row=2, col=1)

    fig.update_layout(template=TEMPLATE, height=650, hovermode="x unified",
                       title="Mortality Over Time: Absolute Deaths vs. Case-Fatality Rate")
    fig.update_yaxes(title_text="Deaths / million", row=1, col=1)
    fig.update_yaxes(title_text="CFR (%)", row=2, col=1)
    return fig


def plot_excess_vs_official_bar(latest_df):
    """Core insight chart #1: official COVID deaths vs. true excess mortality
    per million, side by side, sorted by the size of the gap. This is the
    chart that carries the article's main claim."""
    d = latest_df.sort_values("gap_per_million", ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=d["location"], x=d["total_deaths_per_million"], name="Officially reported COVID deaths",
        orientation="h", marker_color="#4C72B0",
    ))
    fig.add_trace(go.Bar(
        y=d["location"], x=d["excess_mortality_cumulative_per_million"], name="Estimated true excess mortality",
        orientation="h", marker_color="#C44E52", opacity=0.55,
    ))
    fig.update_layout(
        template=TEMPLATE, barmode="overlay", height=480,
        title="The Hidden Toll: Official COVID Deaths vs. True Excess Mortality (per million, cumulative)",
        xaxis_title="Deaths per million people", legend=dict(orientation="h", y=-0.15),
    )
    return fig


def plot_excess_gap_ratio(latest_df):
    """Core insight chart #2: the *ratio* of true to official deaths - makes
    the scale of undercounting immediately legible as a single number per
    country, rather than requiring the reader to eyeball two bars."""
    d = latest_df.copy()
    d = d[d["total_deaths_per_million"] > 0]
    d["ratio"] = d["excess_mortality_cumulative_per_million"] / d["total_deaths_per_million"]
    d = d.sort_values("ratio", ascending=True)
    colors = ["#C44E52" if r > 1.5 else ("#DD8452" if r > 1 else "#55A868") for r in d["ratio"]]
    fig = go.Figure(go.Bar(
        y=d["location"], x=d["ratio"], orientation="h", marker_color=colors,
        text=[f"{r:.1f}×" for r in d["ratio"]], textposition="outside",
    ))
    fig.add_vline(x=1, line_dash="dash", line_color="gray",
                  annotation_text="Official count = true toll", annotation_position="top")
    fig.update_layout(
        template=TEMPLATE, height=420,
        title="True Pandemic Death Toll as a Multiple of the Officially Reported Count",
        xaxis_title="True excess mortality ÷ officially reported deaths",
    )
    return fig


def plot_stringency_vs_outcome(summary_df):
    """Scatter: average lockdown stringency vs. eventual deaths per million,
    sized by population, colored by continent. Tests the intuitive
    assumption that stricter lockdowns straightforwardly bought lower
    mortality."""
    fig = px.scatter(
        summary_df, x="avg_stringency", y="total_deaths_per_million",
        size="population", color="continent", hover_name="location",
        template=TEMPLATE, size_max=45,
        title="Lockdown Strictness vs. Eventual COVID Mortality (bubble = population)",
        labels={"avg_stringency": "Average stringency index (2020-2022)",
                "total_deaths_per_million": "Total deaths per million"},
    )
    fig.update_layout(height=550)
    return fig
