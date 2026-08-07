import streamlit as st
import urllib.parse
from styles import load_css

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Thank You & Contact",
    page_icon="🎓",
    layout="wide"
)

# Apply global styles
load_css("light")

# HIDE 'app' NAVIGATION ITEM & INJECT FLOATING ANIMATIONS + ROUNDED PILL STYLING
st.markdown("""
<style>
/* Hide the top 'app' link in Streamlit sidebar */
[data-testid="stSidebarNav"] ul li:first-child {
    display: none !important;
}

/* Base Light Theme Background */
.main {
    background-color: #f8fafc !important;
}

/* Smooth Floating Keyframes */
@keyframes smoothFloat {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-7px); }
    100% { transform: translateY(0px); }
}

/* Rounded Pill Action Buttons with Floating Effect */
.pill-btn {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 10px !important;
    padding: 16px 24px !important;
    border-radius: 50px !important; /* Fully Rounded Pill Style */
    font-weight: 800 !important;
    font-size: 16px !important;
    text-decoration: none !important;
    box-shadow: 0 6px 18px rgba(0,0,0,0.1) !important;
    animation: smoothFloat 4s ease-in-out infinite !important;
    transition: all 0.3s ease !important;
}

.pill-btn:hover {
    transform: translateY(-10px) scale(1.03) !important;
    box-shadow: 0 12px 25px rgba(0,0,0,0.18) !important;
}

/* Individual Button Themes */
.pill-linkedin {
    background-color: #0077b5 !important;
    color: #ffffff !important;
    border: none !important;
}

.pill-github {
    background-color: #0f172a !important;
    color: #ffffff !important;
    border: none !important;
}

.pill-email {
    background-color: #ffffff !important;
    color: #ea4335 !important;
    border: 2px solid #ea4335 !important;
}

.pill-whatsapp {
    background-color: #25d366 !important;
    color: #ffffff !important;
    border: none !important;
}

/* Floating Stagger Delays */
.delay-1 { animation-delay: 0s !important; }
.delay-2 { animation-delay: 0.8s !important; }
.delay-3 { animation-delay: 1.6s !important; }
.delay-4 { animation-delay: 2.4s !important; }

/* Rounded Floating Tech Stack Pills */
.tech-pill-card {
    background: #ffffff !important;
    padding: 16px 20px !important;
    border-radius: 50px !important;
    text-align: center !important;
    font-weight: 800 !important;
    font-size: 15px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04) !important;
    animation: smoothFloat 4.5s ease-in-out infinite !important;
    transition: transform 0.3s ease !important;
}

.tech-pill-card:hover {
    transform: translateY(-8px) !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# PROFILE & CONTACT CONFIGURATION
# ==========================================================

LINKEDIN_URL = "https://www.linkedin.com/in/gulafsha-72793a252?utm_source=share_via&utm_content=profile&utm_medium=member_android"
GITHUB_URL = "https://cullenfeels-cmyk.github.io/Portfolio/"
EMAIL_ADDRESS = "cullenfeels@gmail.com"
WHATSAPP_NUMBER = "917455081845"

DEFAULT_MESSAGE = "Hi Gulafsha! I explored your RetailPulse AI Analytics Dashboard and would like to connect with you."

encoded_msg = urllib.parse.quote(DEFAULT_MESSAGE)
WHATSAPP_LINK = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_msg}"

email_subject = urllib.parse.quote("Inquiry: RetailPulse AI Analytics Dashboard")
email_body = urllib.parse.quote("Hi Gulafsha,\n\nI reviewed your Data Analyst Portfolio Project and would like to get in touch.")
MAILTO_LINK = f"mailto:{EMAIL_ADDRESS}?subject={email_subject}&body={email_body}"

# ==========================================================
# HERO BANNER
# ==========================================================

st.markdown("""
<div style="
    background: #ffffff;
    padding: 40px 20px;
    border-radius: 24px;
    text-align: center;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    margin-bottom: 30px;
">
    <div style="font-size: 48px; margin-bottom: 8px;">🎓</div>
    <h1 style="font-size: 46px; font-weight: 900; color: #0f172a !important; margin: 0 0 10px 0;">
        Thank You for Exploring!
    </h1>
    <p style="font-size: 18px; color: #475569 !important; font-weight: 700; margin: 0;">
        RetailPulse AI • Interactive Retail Sales & Demand Analytics Platform
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# CENTERED CREATOR CARD
# ==========================================================

col_l, col_c, col_r = st.columns([1, 2.2, 1])

with col_c:
    st.markdown("""
    <div style="
        background: #ffffff;
        border: 2px solid #e2e8f0;
        padding: 32px 25px;
        border-radius: 24px;
        text-align: center;
        box-shadow: 0 6px 18px rgba(0,0,0,0.04);
        margin-bottom: 35px;
    ">
        <div style="
            color: #64748b !important;
            font-weight: 800;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 8px;
            text-align: center;
        ">
            PROJECT CREATOR
        </div>
        <h2 style="
            color: #0f172a !important;
            font-size: 44px;
            font-weight: 900;
            margin: 0 0 18px 0;
            letter-spacing: 2px;
            text-transform: uppercase;
            text-align: center;
        ">
            GULAFSHA
        </h2>
        <div style="
            background: linear-gradient(135deg, #0f172a, #1e3a8a);
            padding: 16px 20px;
            border-radius: 50px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(15, 23, 42, 0.25);
        ">
            <span style="
                color: #FFFFFF !important;
                font-weight: 800 !important;
                font-size: 24px !important;
                letter-spacing: 0.5px;
            ">
                🎓 Data Analyst Portfolio Project
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================================
# FLOATING ROUNDED TECH STACK PILLS
# ==========================================================

st.markdown("<h3 style='text-align:center; color:#0f172a; font-weight: 800; margin-bottom: 25px;'>🛠️ Core Tech Stack & Analytical Framework</h3>", unsafe_allow_html=True)

t1, t2, t3, t4 = st.columns(4)

with t1:
    st.markdown('<div class="tech-pill-card delay-1" style="border: 2px solid #ef4444; color: #991b1b !important;">🚀 Streamlit</div>', unsafe_allow_html=True)

with t2:
    st.markdown('<div class="tech-pill-card delay-2" style="border: 2px solid #0284c7; color: #0369a1 !important;">🐼 Pandas</div>', unsafe_allow_html=True)

with t3:
    st.markdown('<div class="tech-pill-card delay-3" style="border: 2px solid #2563eb; color: #1d4ed8 !important;">🔢 NumPy</div>', unsafe_allow_html=True)

with t4:
    st.markdown('<div class="tech-pill-card delay-4" style="border: 2px solid #7c3aed; color: #6d28d9 !important;">📊 Plotly Express</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

b1, b2, b3, b4 = st.columns(4)

with b1:
    st.markdown('<div class="tech-pill-card delay-1" style="border: 2px solid #eab308; color: #a16207 !important;">⚡ Power BI</div>', unsafe_allow_html=True)

with b2:
    st.markdown('<div class="tech-pill-card delay-2" style="border: 2px solid #dc2626; color: #b91c1c !important;">🗄️ SQL</div>', unsafe_allow_html=True)

with b3:
    st.markdown('<div class="tech-pill-card delay-3" style="border: 2px solid #16a34a; color: #15803d !important;">📈 Excel</div>', unsafe_allow_html=True)

with b4:
    st.markdown('<div class="tech-pill-card delay-4" style="border: 2px solid #334155; color: #0f172a !important;">🐙 Git & GitHub</div>', unsafe_allow_html=True)

st.markdown("<br><hr style='border: 0; height: 1px; background: #cbd5e1; margin: 30px 0;'><br>", unsafe_allow_html=True)

# ==========================================================
# FLOATING ROUNDED ACTION BUTTONS WITH SVG ICONS
# ==========================================================

st.markdown("<h3 style='text-align:center; color:#0f172a; font-weight: 800; margin-bottom: 8px;'>🌐 Connect & Collaborate</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#64748b; font-size: 15px; margin-bottom: 25px;'>Reach out via LinkedIn, view my GitHub portfolio, or initiate a direct inquiry.</p>", unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)

# SVG Icons
linkedin_svg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/></svg>'

github_svg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.1-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/></svg>'

email_svg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ea4335"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>'

whatsapp_svg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.816 9.816 0 0 0 12.04 2m.01 1.67c4.54 0 8.24 3.7 8.24 8.24 0 2.2-.86 4.27-2.42 5.82a8.18 8.18 0 0 1-5.83 2.42c-1.48 0-2.93-.39-4.2-1.14l-.3-.18-3.12.82.83-3.04-.2-.32a8.19 8.19 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.26-8.24m4.53 11.53c-.25-.13-1.47-.72-1.7-.81-.23-.08-.39-.13-.56.13-.17.25-.64.81-.79.97-.15.16-.29.18-.54.06s-1.05-.39-2-1.23c-.74-.66-1.24-1.47-1.39-1.72-.15-.25-.02-.38.11-.51.11-.11.25-.29.37-.43.13-.15.17-.25.25-.42.08-.17.04-.31-.02-.44s-.56-1.35-.77-1.85c-.2-.48-.41-.42-.56-.43h-.48c-.17 0-.44.06-.67.31-.23.25-.88.86-.88 2.1 0 1.24.9 2.44 1.03 2.61.13.17 1.77 2.7 4.29 3.79.6.26 1.07.41 1.44.53.6.19 1.15.16 1.58.1.48-.07 1.47-.6 1.68-1.18.21-.58.21-1.07.15-1.18-.06-.11-.22-.18-.47-.31z"/></svg>'

with s1:
    st.markdown(f'<a href="{LINKEDIN_URL}" target="_blank" class="pill-btn pill-linkedin delay-1">{linkedin_svg} <span style="color:#ffffff !important;">LinkedIn Profile</span></a>', unsafe_allow_html=True)

with s2:
    st.markdown(f'<a href="{GITHUB_URL}" target="_blank" class="pill-btn pill-github delay-2">{github_svg} <span style="color:#ffffff !important;">GitHub Portfolio</span></a>', unsafe_allow_html=True)

with s3:
    st.markdown(f'<a href="{MAILTO_LINK}" target="_blank" class="pill-btn pill-email delay-3">{email_svg} <span style="color:#ea4335 !important;">Direct Email</span></a>', unsafe_allow_html=True)

with s4:
    st.markdown(f'<a href="{WHATSAPP_LINK}" target="_blank" class="pill-btn pill-whatsapp delay-4">{whatsapp_svg} <span style="color:#ffffff !important;">WhatsApp Chat</span></a>', unsafe_allow_html=True)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("<br><br><hr style='border: 0; height: 1px; background: #cbd5e1;'>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 14px; font-weight: 600; padding: 15px 0;">
    RetailPulse AI • Executive Analytics Portfolio<br>
    Designed & Developed by Gulafsha • © 2026
</div>
""", unsafe_allow_html=True)