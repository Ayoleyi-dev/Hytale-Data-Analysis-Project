
import streamlit as st

st.set_page_config(
    page_title="Hytale Analytics Lab",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1280px;
        padding-top: 2.0rem;
        padding-bottom: 4rem;
    }

    .ha-hero {
        margin: 0 0 1.45rem 0;
        padding: 1.35rem 1.45rem;
        border-radius: 10px;
        border: 1px solid rgba(114, 215, 216, 0.22);
        border-left: 4px solid #E6B85C;
        background:
            linear-gradient(135deg, rgba(22, 47, 59, 0.92), rgba(11, 29, 39, 0.92));
        box-shadow: 0 12px 28px rgba(0,0,0,0.15);
    }

    .ha-eyebrow {
        color: #E6B85C;
        font-size: 0.73rem;
        font-weight: 800;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    .ha-title {
        color: #F4E9D2;
        font-family: "Trebuchet MS", "Segoe UI", sans-serif;
        font-weight: 900;
        line-height: 1.07;
        font-size: clamp(2rem, 4vw, 3.25rem);
        margin-bottom: 0.65rem;
    }

    .ha-body {
        color: #B9CBD1;
        line-height: 1.6;
        max-width: 980px;
    }

    .ha-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 0.42rem;
        margin-top: 0.9rem;
    }

    .ha-chip {
        border-radius: 5px;
        border: 1px solid rgba(114, 215, 216, 0.22);
        background: rgba(114, 215, 216, 0.07);
        color: #DDF5F2;
        padding: 0.26rem 0.52rem;
        font-size: 0.76rem;
        font-weight: 700;
    }

    .ha-section-row {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.62rem;
        margin: 1.9rem 0 0.75rem 0;
    }

    .ha-diamond {
        width: 9px;
        height: 9px;
        transform: rotate(45deg);
        background: #E6B85C;
        box-shadow: 0 0 0 4px rgba(230,184,92,0.08);
    }

    .ha-section-title {
        color: #F4E9D2;
        font-family: "Trebuchet MS", "Segoe UI", sans-serif;
        font-size: 1.35rem;
        font-weight: 800;
    }

    .ha-section-note {
        color: #91A7B2;
        font-size: 0.83rem;
    }

    .ha-note {
        margin: 0.8rem 0 1.2rem 0;
        padding: 0.72rem 0.85rem;
        border-radius: 6px;
        border-left: 3px solid #72D7D8;
        background: rgba(114, 215, 216, 0.06);
        color: #BFD1D6;
        line-height: 1.55;
        font-size: 0.88rem;
    }

    .ha-note-gold {
        border-left-color: #E6B85C;
        background: rgba(230,184,92,0.06);
        color: #D8CFB8;
    }

    .ha-footer {
        margin-top: 2.1rem;
        padding-top: 0.9rem;
        border-top: 1px solid rgba(114,215,216,0.12);
        color: #71868F;
        font-size: 0.77rem;
        line-height: 1.5;
    }

    [data-testid="stMetric"] {
        border-radius: 8px;
        border: 1px solid rgba(114,215,216,0.14);
        border-top: 2px solid rgba(230,184,92,0.68);
        background: rgba(15,34,45,0.55);
        padding: 0.75rem 0.85rem;
    }

    [data-testid="stExpander"] {
        border: 1px solid rgba(114,215,216,0.12);
        border-radius: 8px;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(114,215,216,0.12);
    }

    @media (max-width: 800px) {
        .block-container {
            padding-top: 1.35rem;
        }
        .ha-hero {
            padding: 1.05rem 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

pages = {
    "Project": [
        st.Page("story_page.py", title="Project Story", icon="🧭"),
    ],
    "Analytics": [
        st.Page("app.py", title="Synthetic Analytics Demo", icon="🧪"),
        st.Page("pages/2_Observed_Server_Data.py", title="Observed Server Data", icon="📡"),
    ],
    "Trust & Methods": [
        st.Page("pages/3_Data_Provenance.py", title="Data Provenance", icon="🔎"),
    ],
}

st.sidebar.caption("Independent Hytale analytics portfolio")
st.navigation(pages).run()
