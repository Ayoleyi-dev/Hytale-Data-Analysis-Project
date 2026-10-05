import streamlit as st

st.set_page_config(page_title="Hytale Analytics Portfolio", page_icon="📊", layout="wide")

pages = {
    "Project": [st.Page("story_page.py", title="Project Story", icon="🧭")],
    "Analytics": [
        st.Page("app.py", title="Synthetic Analytics Demo", icon="🧪"),
        st.Page(r"pages/2_Observed_Server_Data.py", title="Observed Server Data", icon="📡"),
    ],
    "Trust & Methods": [
        st.Page(r"pages/3_Data_Provenance.py", title="Data Provenance", icon="🔎"),
    ],
}
st.navigation(pages).run()
