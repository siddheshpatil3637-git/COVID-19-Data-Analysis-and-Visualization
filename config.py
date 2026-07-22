"""
Configuration: country selections and event annotations.
Kept separate from plotting/pipeline logic so it's easy to edit without
touching chart code.
"""

# Countries chosen for contrast: different lockdown postures, different
# vaccination trajectories, different income levels (which turns out to
# matter a lot for excess-mortality reporting quality).
COMPARISON_COUNTRIES = [
    "United States",
    "Sweden",          # famously light-touch lockdown policy
    "New Zealand",      # famously strict / elimination strategy
    "India",
    "Brazil",
    "United Kingdom",
    "Russia",           # large official-vs-excess mortality gap
    "South Africa",
]

VACCINE_COMPARISON_COUNTRIES = [
    "United States",
    "United Kingdom",
    "Israel",
    "India",
    "Brazil",
    "Nigeria",
]

# Countries with reliable excess-mortality data, used for the core "hidden
# toll" insight chart. High/upper-middle/lower income mix on purpose.
EXCESS_MORTALITY_COUNTRIES = [
    "United States",
    "United Kingdom",
    "Germany",
    "France",
    "Russia",
    "Mexico",
    "Egypt",
    "South Africa",
    "India",
    "Brazil",
]

# Global event markers. Dates are approximate global/consensus timings
# (variant surges especially vary by country by a few weeks/months) - this
# is a simplified overlay for storytelling, not epidemiological ground truth.
GLOBAL_EVENTS = [
    {"date": "2020-03-11", "label": "WHO declares pandemic", "kind": "milestone"},
    {"date": "2020-03-01", "end": "2020-06-01", "label": "First wave of lockdowns", "kind": "lockdown"},
    {"date": "2020-12-08", "label": "First COVID vaccine administered (UK)", "kind": "vaccine"},
    {"date": "2020-12-01", "end": "2021-03-01", "label": "Alpha variant surge", "kind": "variant"},
    {"date": "2021-04-01", "end": "2021-08-01", "label": "Delta variant surge", "kind": "variant"},
    {"date": "2021-11-01", "end": "2022-02-01", "label": "Omicron variant surge", "kind": "variant"},
    {"date": "2021-12-01", "label": "Boosters roll out widely", "kind": "vaccine"},
    {"date": "2023-05-05", "label": "WHO ends COVID Public Health Emergency", "kind": "milestone"},
]

EVENT_COLORS = {
    "lockdown": "#6c757d",
    "variant": "#d62728",
    "vaccine": "#2ca02c",
    "milestone": "#1f77b4",
}

DATA_URL = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
LOCAL_CACHE = "data/owid-covid-data.csv"
