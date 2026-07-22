"""
Helpers for layering event annotations (lockdowns, variant surges, vaccine
milestones) onto plotly time-series charts as shaded regions / vertical
lines, driven by the GLOBAL_EVENTS config rather than hardcoded per chart.
"""

from config import GLOBAL_EVENTS, EVENT_COLORS


def add_event_annotations(fig, events=None, y_label_offset=1.0, show_labels=True):
    """Adds vertical lines (point events) or shaded rectangles (date ranges)
    for each event in `events` to a plotly figure, with a label."""
    events = events or GLOBAL_EVENTS
    label_row = 0

    for ev in events:
        color = EVENT_COLORS.get(ev["kind"], "#999999")
        if "end" in ev:
            fig.add_vrect(
                x0=ev["date"], x1=ev["end"],
                fillcolor=color, opacity=0.10, line_width=0,
                annotation_text=ev["label"] if show_labels else None,
                annotation_position="top left",
                annotation=dict(font_size=9, font_color=color),
            )
        else:
            fig.add_vline(
                x=ev["date"], line_width=1, line_dash="dash", line_color=color,
                annotation_text=ev["label"] if show_labels else None,
                annotation_position="top",
                annotation=dict(font_size=9, font_color=color, textangle=-90),
            )
        label_row += 1

    return fig
