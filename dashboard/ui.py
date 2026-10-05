
from __future__ import annotations

from html import escape
import streamlit as st

CYAN = "#72D7D8"
CYAN_SOFT = "#A4E7E2"
GOLD = "#E6B85C"
CREAM = "#F4E9D2"
MUTED = "#9FB0B8"
BLUE = "#66B8FF"


def hero(eyebrow: str, title: str, body: str, chips: list[str] | None = None) -> None:
    chips = chips or []
    chip_html = "".join(
        f'<span class="ha-chip">{escape(str(chip))}</span>' for chip in chips
    )
    st.markdown(
        f"""
        <div class="ha-hero">
          <div class="ha-eyebrow">{escape(eyebrow)}</div>
          <div class="ha-title">{escape(title)}</div>
          <div class="ha-body">{escape(body)}</div>
          <div class="ha-chips">{chip_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str, note: str = "") -> None:
    note_html = f'<span class="ha-section-note">{escape(note)}</span>' if note else ""
    st.markdown(
        f"""
        <div class="ha-section-row">
          <span class="ha-diamond"></span>
          <span class="ha-section-title">{escape(title)}</span>
          {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def note(text: str, kind: str = "info") -> None:
    cls = "ha-note ha-note-gold" if kind == "gold" else "ha-note"
    st.markdown(
        f'<div class="{cls}">{escape(text)}</div>',
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        """
        <div class="ha-footer">
          Independent analytics portfolio • Hytale and related marks belong to their respective owners •
          not affiliated with or endorsed by Hypixel Studios
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_plot(fig, legend_title: str = ""):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5,16,24,0.18)",
        font=dict(
            family="Trebuchet MS, Segoe UI, sans-serif",
            color="#D9E4E7",
            size=12,
        ),
        title_font=dict(
            family="Trebuchet MS, Segoe UI, sans-serif",
            color=CREAM,
            size=17,
        ),
        legend_title_text=legend_title,
        margin=dict(l=35, r=20, t=55, b=45),
        hoverlabel=dict(
            bgcolor="#10232F",
            bordercolor="#31505D",
            font_color="#F7FBFC",
        ),
    )
    fig.update_xaxes(
        gridcolor="rgba(114,215,216,0.08)",
        linecolor="rgba(114,215,216,0.12)",
        zeroline=False,
    )
    fig.update_yaxes(
        gridcolor="rgba(114,215,216,0.08)",
        linecolor="rgba(114,215,216,0.12)",
        zeroline=False,
    )
    return fig
