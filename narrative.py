"""
Builds the written insight summary as HTML, using the actual computed
statistics rather than hardcoded numbers, so the narrative stays accurate if
the underlying data is refreshed.
"""


def build_summary_html(stats: dict, corr: float) -> str:
    return f"""
    <div class="narrative">
      <h1>The Pandemic's Real Death Toll Was Never Really Counted</h1>
      <p class="lede">
        Across {stats['n_countries']} countries with reliable data, the typical
        (median) country's true pandemic death toll — measured by excess
        mortality, i.e. how many more people died than would normally have
        been expected — was <strong>{stats['median_ratio']:.1f}&times;</strong>
        higher than its official COVID-19 death count. In the worst
        well-documented case among larger outbreaks, <strong>{stats['top_country']}</strong>'s
        true toll was roughly <strong>{stats['top_ratio']:.0f}&times;</strong>
        its official figure. Overall, more than half of the countries with
        excess-mortality data ({stats['pct_countries_undercounted']:.0f}%)
        show a gap large enough (over 30%) that it can't be explained by
        normal statistical noise.
      </p>

      <p>
        This isn't really a story about any single country lying about its
        numbers — though in some cases that's part of it. It's a story about
        the limits of official case-and-death reporting itself. A country
        can only report a COVID death if someone tests positive, that test
        result reaches a health authority, and a doctor codes the death
        correctly as COVID-related. Every one of those steps is a place
        where deaths can quietly disappear from the official count,
        especially in countries with weaker testing infrastructure, informal
        healthcare systems, or an incentive to downplay the outbreak. Excess
        mortality sidesteps all of that: it just asks how many people died,
        period, compared to a pre-pandemic baseline — no test, diagnosis, or
        paperwork required.
      </p>

      <p>
        That means most of the charts the public actually saw during the
        pandemic — the ones ranking countries by official COVID deaths per
        million — were, to varying degrees, ranking countries by
        <em>reporting capacity</em> as much as by actual severity. A country
        with excellent healthcare data infrastructure and a country with a
        genuinely smaller outbreak can look identical on an official-deaths
        chart even if their true experiences were very different. Russia is
        the most extensively documented case of this gap: independent
        demographic analyses converged on a true toll several times its
        official figure years before Russian authorities acknowledged
        anything close to it.
      </p>

      <p>
        A second, related pattern shows up in the lockdown data: across the
        countries in this analysis, the correlation between how strict a
        country's lockdown policy was on average (OWID's stringency index)
        and its eventual death rate is essentially flat
        (r&nbsp;=&nbsp;{corr:.2f}). That doesn't mean lockdowns didn't work locally
        or in the short term — plenty of country-specific studies suggest
        they did, at least temporarily. It means that, looked at as a single
        global cross-section, "stricter policy" was not a reliable predictor
        of "fewer deaths per capita." Stringency was driven as much by a
        government's political capacity and public trust as by outbreak
        severity, and countries that locked down hardest were not
        systematically the ones that came out with the best outcomes. The
        confident, simple version of that claim — the one that shaped a lot
        of pandemic-era political argument — doesn't hold up cleanly in the
        cross-country data.
      </p>

      <p>
        Put the two findings together and a slightly uncomfortable picture
        emerges: the numbers we relied on in real time to judge which
        countries and which policies were "working" were noisier and more
        biased than they appeared, in ways that tracked institutional
        capacity more than actual outcomes. The charts below let you look at
        both stories directly — the official narrative each country's case
        and death curves told at the time, and the quieter, more honest one
        excess mortality tells in hindsight.
      </p>
    </div>
    """
