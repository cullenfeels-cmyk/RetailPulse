def load_css(theme="dark"):
    import streamlit as st

    if theme == "dark":
        bg = "#020617"
        card = "#111827"
        text = "white"
        subtext = "#cbd5e1"
    else:
        bg = "#f8fafc"
        card = "#ffffff"
        text = "#111827"
        subtext = "#475569"

    st.markdown(f"""
    <style>

    /* ==========================================================
       HIDE 'app' NAVIGATION ITEM FROM SIDEBAR GLOBALLY
       ========================================================== */
    /* Target first item in sidebar navigation list */
    [data-testid="stSidebarNav"] ul li:first-child {{
        display: none !important;
    }}

    /* Backup selector targeting links with 'app' specifically */
    [data-testid="stSidebarNav"] li:has(a[href*="app"]) {{
        display: none !important;
    }}

    /* GLOBAL */
    html, body, [class*="css"] {{
        color: {text} !important;
    }}

    .stApp {{
        background: {bg};
    }}

    /* SIDEBAR */
    section[data-testid="stSidebar"] {{
        background-color: {card} !important;
        color: {text} !important;
    }}

    /* KPI CARDS */
    div[data-testid="metric-container"] {{
        background-color: {card};
        border-radius: 12px;
        padding: 15px;
        color: {text} !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }}

    /* HEADINGS */
    h1, h2, h3, h4, h5, h6 {{
        color: {text} !important;
    }}

    /* CUSTOM TITLE */
    .dashboard-title {{
        font-size: 34px;
        font-weight: bold;
        color: {text};
    }}

    .dashboard-subtitle {{
        font-size: 16px;
        color: {subtext};
    }}

    </style>
    """, unsafe_allow_html=True)