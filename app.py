import streamlit as st
import json
import os
import plotly.graph_objects as go
from parser import extract_text_from_file, extract_skills
from matching import compute_match, get_model

# ═══════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="JobLens — Smart Job Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════
# GLOBAL STYLES
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Outfit:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ──────────────────────────────
   BASE
────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    color: #dde3ed;
}
.stApp {
    background: #0a0e17;
    background-image:
        radial-gradient(ellipse 70% 45% at 15% 0%,   rgba(56,189,248,0.06) 0%, transparent 65%),
        radial-gradient(ellipse 55% 40% at 85% 100%, rgba(251,191,36,0.05) 0%, transparent 65%),
        radial-gradient(ellipse 40% 30% at 50% 50%,  rgba(99,102,241,0.03) 0%, transparent 60%);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1220px;
}

/* ──────────────────────────────
   TYPOGRAPHY SCALE
────────────────────────────── */
.t-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: #38bdf8;
}
.t-hero {
    font-family: 'Syne', sans-serif;
    font-size: clamp(3rem, 6vw, 5rem);
    font-weight: 800;
    line-height: 1.05;
    background: linear-gradient(120deg, #f0f9ff 0%, #38bdf8 45%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.t-section {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.67rem;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #38bdf8;
    margin-bottom: 1rem;
}

/* ──────────────────────────────
   DIVIDER
────────────────────────────── */
.divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(56,189,248,0.3) 30%, rgba(129,140,248,0.3) 70%, transparent 100%);
    margin: 2rem 0;
}

/* ──────────────────────────────
   WIDGET CONTRAST FIXES
   Targets every Streamlit internal
   so nothing is invisible on dark bg
────────────────────────────── */

/* Widget labels */
label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
.stTextArea label,
.stFileUploader label {
    color: #94a3b8 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
}

/* Textarea — typed text visible, gold cursor, dim placeholder */
textarea,
.stTextArea textarea {
    background: #0f1623 !important;
    border: 1.5px solid rgba(56,189,248,0.18) !important;
    border-radius: 12px !important;
    color: #dde3ed !important;
    caret-color: #38bdf8 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.92rem !important;
    line-height: 1.6 !important;
    resize: vertical !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
textarea::placeholder,
.stTextArea textarea::placeholder {
    color: #475569 !important;
    opacity: 1 !important;
}
textarea:focus,
.stTextArea textarea:focus {
    border-color: rgba(56,189,248,0.55) !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.08) !important;
    outline: none !important;
}

/* File uploader container */
[data-testid="stFileUploader"] {
    background: rgba(56,189,248,0.03) !important;
    border: 1.5px dashed rgba(56,189,248,0.25) !important;
    border-radius: 12px !important;
    padding: 0.5rem !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(56,189,248,0.55) !important;
}
/* "Browse files" button */
[data-testid="stFileUploader"] button,
[data-testid="stFileUploaderDropzone"] button {
    background: rgba(56,189,248,0.18) !important;
    color: #ffffff !important;
    border: 1px solid rgba(56,189,248,0.5) !important;
    border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    transition: all 0.18s !important;
}
[data-testid="stFileUploader"] button:hover,
[data-testid="stFileUploaderDropzone"] button:hover {
    background: rgba(56,189,248,0.32) !important;
    border-color: rgba(56,189,248,0.8) !important;
    color: #ffffff !important;
}
/* Helper text & icon inside dropzone */
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span {
    color: #475569 !important;
    font-size: 0.82rem !important;
}
[data-testid="stFileUploaderDropzone"] svg {
    fill: #38bdf8 !important;
    opacity: 0.5 !important;
}

/* Generic text */
.stMarkdown p, p { color: #94a3b8; }
p strong { color: #dde3ed; }

/* Alerts / info / warning / success boxes */
[data-testid="stAlert"] {
    background: rgba(15,22,35,0.8) !important;
    border-radius: 10px !important;
    border-left-width: 3px !important;
}
[data-testid="stAlert"] p { color: #cbd5e0 !important; font-size: 0.88rem !important; }

/* Expander */
[data-testid="stExpander"] {
    background: rgba(15,22,35,0.6) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
    color: #94a3b8 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
}
[data-testid="stExpander"] summary:hover { color: #dde3ed !important; }
[data-testid="stExpander"] p,
[data-testid="stExpander"] li { color: #94a3b8 !important; font-size: 0.88rem !important; }
[data-testid="stExpander"] strong { color: #bae6fd !important; }

/* Progress bar */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #38bdf8, #818cf8) !important;
    border-radius: 999px !important;
}
.stProgress > div > div {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 999px !important;
}
.stProgress { margin-bottom: 0.15rem !important; }

/* st.write text used near progress bars */
.stMarkdown { color: #94a3b8 !important; }

/* Spinner */
.stSpinner > div { border-top-color: #38bdf8 !important; }

/* ──────────────────────────────
   MISSING SKILL BUTTONS
────────────────────────────── */
div.stButton > button {
    background: rgba(248,113,113,0.07) !important;
    color: #fca5a5 !important;
    border: 1px solid rgba(248,113,113,0.25) !important;
    border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    padding: 5px 8px !important;
    transition: all 0.16s ease !important;
    width: 100% !important;
    letter-spacing: 0.01em !important;
}
div.stButton > button:hover {
    background: rgba(248,113,113,0.16) !important;
    border-color: rgba(248,113,113,0.5) !important;
    color: #fecaca !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(248,113,113,0.15) !important;
}

/* ──────────────────────────────
   SKILL BADGES
────────────────────────────── */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.77rem;
    font-weight: 500;
    margin: 3px 3px;
    letter-spacing: 0.01em;
}
.badge-resume {
    background: rgba(52,211,153,0.1);
    color: #6ee7b7;
    border: 1px solid rgba(52,211,153,0.22);
}
.badge-jd {
    background: rgba(56,189,248,0.1);
    color: #7dd3fc;
    border: 1px solid rgba(56,189,248,0.22);
}

/* ──────────────────────────────
   SCORE DISPLAY
────────────────────────────── */
.score-wrap { text-align: center; padding: 1.2rem 0; }
.score-num {
    font-family: 'Syne', sans-serif;
    font-size: 5rem;
    font-weight: 800;
    line-height: 1;
}
.score-green { color: #6ee7b7; }
.score-amber { color: #fbbf24; }
.score-red   { color: #f87171; }

.ptrack {
    background: rgba(255,255,255,0.05);
    border-radius: 999px;
    height: 6px;
    overflow: hidden;
    margin: 0.9rem auto;
    max-width: 240px;
}
.pfill { height: 100%; border-radius: 999px; }

.pill {
    display: inline-block;
    padding: 5px 18px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 0.6rem;
    letter-spacing: 0.02em;
}
.pill-green { background: rgba(52,211,153,0.1);  color: #6ee7b7; border: 1px solid rgba(52,211,153,0.3); }
.pill-amber { background: rgba(251,191,36,0.1);  color: #fbbf24; border: 1px solid rgba(251,191,36,0.28); }
.pill-red   { background: rgba(248,113,113,0.1); color: #fca5a5; border: 1px solid rgba(248,113,113,0.28); }

/* ──────────────────────────────
   STAT COUNTERS
────────────────────────────── */
.stat-box { text-align: center; padding: 1.6rem 0; }
.stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    line-height: 1;
}
.stat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.63rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #94a3b8;
    margin-top: 0.35rem;
}

/* ──────────────────────────────
   ROADMAP
────────────────────────────── */
.roadmap-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #f0f9ff;
    margin-bottom: 1.4rem;
}
.rm-col-head {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: #38bdf8;
    margin-bottom: 0.8rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(56,189,248,0.15);
}
.rm-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 9px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 0.87rem;
    color: #94a3b8;
    line-height: 1.55;
}
.rm-item:last-child { border-bottom: none; }
.rm-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    margin-top: 7px;
    flex-shrink: 0;
}
.dot-sky   { background: #38bdf8; box-shadow: 0 0 7px rgba(56,189,248,0.6); }
.dot-green { background: #6ee7b7; box-shadow: 0 0 7px rgba(110,231,183,0.6); }

/* ──────────────────────────────
   FOOTER
────────────────────────────── */
.footer {
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #1e293b;
    padding: 2.5rem 0 1rem;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════
if 'selected_skill' not in st.session_state:
    st.session_state.selected_skill = None

# ═══════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center;padding:2.5rem 0 1.8rem;">
    <div class="t-hero">JobLens</div>
    <div style="font-size:1.05rem;color:#e2e8f0;margin-top:0.8rem;font-weight:300;">
        Drop your resume. Paste a JD. Know exactly where you stand.
    </div>
</div>
<hr class="divider">
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# LOAD MODEL & DATA
# ═══════════════════════════════════════════════════════════
with st.spinner("Warming up the AI engine…"):
    model = get_model()
    rec_data = {}
    if os.path.exists("recommendations.json"):
        with open("recommendations.json", "r") as f:
            rec_data = json.load(f)

# ═══════════════════════════════════════════════════════════
# CATEGORY DEFINITIONS  (shared between progress bars & radar)
# ═══════════════════════════════════════════════════════════
CATEGORIES = {
    "💻 Coding": [
        'Python','Java','C++','C','R','SQL','JavaScript','TypeScript','Go','Rust',
        'OOP','Data Structures','Algorithms','DSA','Problem Solving',
        'Competitive Programming','Git','GitHub','Version Control'
    ],
    "🤖 AI / DS": [
        'Machine Learning','Deep Learning','NLP','Computer Vision','Data Analysis',
        'Data Science','Statistics','Probability','Linear Algebra','EDA',
        'Feature Engineering','Model Evaluation','Scikit-learn','TensorFlow',
        'PyTorch','XGBoost','Pandas','NumPy','Matplotlib','Seaborn',
        'Time Series Analysis','Recommendation Systems'
    ],
    "🌐 Web Dev": [
        'HTML','CSS','JavaScript','React','Next.js','Angular','Vue.js',
        'Node.js','Express.js','REST APIs','GraphQL','Bootstrap','Tailwind CSS',
        'Frontend Development','Backend Development','Full Stack Development'
    ],
    "☁️ Tools / Cloud": [
        'Docker','Kubernetes','AWS','Azure','GCP','CI/CD','Jenkins',
        'GitHub Actions','Linux','Shell Scripting','Spark','Hadoop',
        'Tableau','PowerBI','Excel','PostgreSQL','MySQL','MongoDB',
        'Airflow','Kafka','Cloud Computing','Cloud Services','Containerization','Cloud'
    ],
    "📊 Data & Analytics": [
        'Data Visualization','Dashboarding','Business Intelligence','ETL',
        'Data Warehousing','Big Data','A/B Testing','Hypothesis Testing',
        'Reporting','KPI Analysis'
    ],
    "🤝 Professional": [
        'Communication','Leadership','Teamwork','Problem-solving','Critical Thinking',
        'Time Management','Adaptability','Collaboration','Presentation Skills',
        'Decision Making','Creativity','Work Ethic'
    ],
}

# ═══════════════════════════════════════════════════════════
# INPUTS
# ═══════════════════════════════════════════════════════════
c1, c2 = st.columns(2, gap="large")

with c1:
    st.markdown('<div class="t-section">① Resume</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "PDF resume",
        type="pdf",
        label_visibility="collapsed",
    )
    if uploaded_file:
        st.markdown(
            f'<div style="font-size:0.82rem;color:#e2e8f0;margin-top:6px;font-family:\'JetBrains Mono\',monospace;">✓ &nbsp;{uploaded_file.name}</div>',
            unsafe_allow_html=True,
        )

with c2:
    st.markdown('<div class="t-section">② Job Description</div>', unsafe_allow_html=True)
    jd_text = st.text_area(
        "Job description",
        placeholder="Paste the full job description here…",
        height=185,
        label_visibility="collapsed",
    )
    st.markdown(
        '<div style="font-size:0.72rem;color:#64748b;font-family:\'JetBrains Mono\',monospace;margin-top:4px;letter-spacing:0.05em;">⌨ &nbsp;Paste text, then click outside or press Ctrl + Enter to apply</div>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════
# MAIN ANALYSIS
# ═══════════════════════════════════════════════════════════
if uploaded_file and jd_text:

    with open("temp_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Analysing your profile…"):
        resume_text   = extract_text_from_file("temp_resume.pdf")
        resume_skills = extract_skills(resume_text)
        jd_skills     = extract_skills(jd_text)
        match_score, missing_skills = compute_match(resume_skills, jd_skills)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── PARSED SKILLS ───────────────────────────────────────
    st.markdown('<div class="t-section">Parsed Skills</div>', unsafe_allow_html=True)
    s1, s2 = st.columns(2, gap="large")

    with s1:
        st.markdown('<div style="font-size:0.7rem;color:#94a3b8;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:10px;font-family:\'JetBrains Mono\',monospace;">From Resume</div>', unsafe_allow_html=True)
        html = "".join(f'<span class="badge badge-resume">{s}</span>' for s in resume_skills) \
               or '<span style="color:#64748b;font-size:0.85rem;">No skills detected</span>'
        st.markdown(f'<div style="line-height:2.3;">{html}</div>', unsafe_allow_html=True)

    with s2:
        st.markdown('<div style="font-size:0.7rem;color:#94a3b8;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:10px;font-family:\'JetBrains Mono\',monospace;">From Job Description</div>', unsafe_allow_html=True)
        html = "".join(f'<span class="badge badge-jd">{s}</span>' for s in jd_skills) \
               or '<span style="color:#64748b;font-size:0.85rem;">No skills detected</span>'
        st.markdown(f'<div style="line-height:2.3;">{html}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── MATCH ANALYSIS ──────────────────────────────────────
    st.markdown('<div class="t-section">Match Analysis</div>', unsafe_allow_html=True)

    score_cls  = "score-green" if match_score >= 70 else ("score-amber" if match_score >= 40 else "score-red")
    bar_color  = "#6ee7b7"     if match_score >= 70 else ("#fbbf24"     if match_score >= 40 else "#f87171")
    status     = "🔥 Strong Match" if match_score >= 70 else ("⚡ Moderate Fit" if match_score >= 40 else "🔧 Needs Work")
    pill_cls   = "pill-green"  if match_score >= 70 else ("pill-amber"  if match_score >= 40 else "pill-red")

    ma1, ma2, ma3, ma4 = st.columns([1, 1.6, 1.6, 1], gap="large")

    with ma1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-num" style="color:#7dd3fc;">{len(resume_skills)}</div>
            <div class="stat-label">Resume Skills</div>
        </div>""", unsafe_allow_html=True)

    with ma2:
        # Gauge chart
        gauge_color = "#6ee7b7" if match_score >= 70 else ("#fbbf24" if match_score >= 40 else "#f87171")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=match_score,
            number={'suffix': '%', 'font': {'family': 'Syne', 'size': 36, 'color': gauge_color}},
            gauge={
                'axis': {'range': [0, 100], 'tickfont': {'color': '#64748b', 'size': 10}, 'tickcolor': '#64748b'},
                'bar': {'color': gauge_color, 'thickness': 0.28},
                'bgcolor': 'rgba(0,0,0,0)',
                'borderwidth': 0,
                'steps': [
                    {'range': [0,  40],  'color': 'rgba(248,113,113,0.08)'},
                    {'range': [40, 70],  'color': 'rgba(251,191,36,0.08)'},
                    {'range': [70, 100], 'color': 'rgba(110,231,183,0.08)'},
                ],
                'threshold': {
                    'line': {'color': gauge_color, 'width': 2},
                    'thickness': 0.82,
                    'value': match_score,
                },
            },
        ))
        fig_gauge.update_layout(
            height=230,
            margin=dict(t=20, b=0, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Outfit, sans-serif', color='#94a3b8'),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown(f'<div style="text-align:center;margin-top:-10px;"><span class="pill {pill_cls}">{status}</span></div>', unsafe_allow_html=True)

    with ma3:
        # Category progress bars
        st.markdown('<div style="padding-top:0.3rem;"></div>', unsafe_allow_html=True)
        resume_lower = [s.lower() for s in resume_skills]
        jd_lower     = [s.lower() for s in jd_skills]
        any_rendered = False

        for cat_name, cat_skills in CATEGORIES.items():
            cat_lower  = [s.lower() for s in cat_skills]
            jd_in_cat  = [s for s in jd_skills if s.lower() in cat_lower]
            if not jd_in_cat:
                continue
            matched    = [s for s in jd_in_cat if s.lower() in resume_lower]
            score_frac = len(matched) / len(jd_in_cat)
            pct        = int(score_frac * 100)
            color      = "#6ee7b7" if pct >= 70 else ("#fbbf24" if pct >= 40 else "#f87171")
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2px;">'
                f'<span style="font-size:0.8rem;color:#94a3b8;">{cat_name}</span>'
                f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;color:{color};">{pct}%</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.progress(score_frac)
            st.markdown('<div style="margin-bottom:6px;"></div>', unsafe_allow_html=True)
            any_rendered = True

        if not any_rendered:
            st.markdown('<div style="color:#64748b;font-size:0.85rem;padding-top:1rem;">No category overlap detected.</div>', unsafe_allow_html=True)

    with ma4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-num" style="color:#fca5a5;">{len(missing_skills)}</div>
            <div class="stat-label">Gaps Found</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── MISSING SKILLS ──────────────────────────────────────
    st.markdown('<div class="t-section">Skills to Bridge</div>', unsafe_allow_html=True)

    if missing_skills:
        st.markdown(
            '<div style="font-size:0.84rem;color:#cbd5e0;margin-bottom:1rem;">Click any skill below to view its personalised learning roadmap.</div>',
            unsafe_allow_html=True,
        )
        btn_cols = st.columns(6)
        for i, skill in enumerate(missing_skills):
            with btn_cols[i % 6]:
                if st.button(skill, key=f"btn_{skill}", use_container_width=True):
                    st.session_state.selected_skill = skill

        # ── ROADMAP ─────────────────────────────────────────
        if st.session_state.selected_skill:
            sel  = st.session_state.selected_skill
            info = next((v for k, v in rec_data.items() if k.lower() == sel.lower()), None)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="roadmap-title">Roadmap for <span style="color:#38bdf8;">{sel}</span></div>',
                unsafe_allow_html=True,
            )

            if info:
                rd1, rd2 = st.columns(2, gap="large")
                with rd1:
                    st.markdown('<div class="rm-col-head">📖 Learning Resources</div>', unsafe_allow_html=True)
                    items = "".join(
                        f'<div class="rm-item"><div class="rm-dot dot-sky"></div><span>{r}</span></div>'
                        for r in info.get("learning_resources", [])
                    ) or '<div style="color:#64748b;font-size:0.85rem;">None listed.</div>'
                    st.markdown(items, unsafe_allow_html=True)

                with rd2:
                    st.markdown('<div class="rm-col-head">🛠 Project Suggestions</div>', unsafe_allow_html=True)
                    items = "".join(
                        f'<div class="rm-item"><div class="rm-dot dot-green"></div><span>{p}</span></div>'
                        for p in info.get("project_suggestions", [])
                    ) or '<div style="color:#64748b;font-size:0.85rem;">None listed.</div>'
                    st.markdown(items, unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div style="color:#94a3b8;font-size:0.9rem;padding:0.8rem 0;">Roadmap for <strong style="color:#38bdf8;">{sel}</strong> is coming soon. Keep building!</div>',
                    unsafe_allow_html=True,
                )

        # ── INTERVIEW PREP ───────────────────────────────────
        st.markdown('<div style="margin-top:1.5rem;"></div>', unsafe_allow_html=True)
        with st.expander("🎓 Interview Preparation — How to discuss these gaps?"):
            st.markdown("""
**When an interviewer points out a missing skill:**

- **Acknowledge & Contextualise** — "While I haven't implemented [Skill] in a large-scale project yet, I have a strong foundation in related areas like [Matched Skill]."

- **Show Proactive Learning** — "I've already started a structured roadmap for [Skill] and am currently working on a mini-project to master it."

- **Translate Value** — Focus on how your existing skills make you a fast learner for the new tool. Employers value growth mindset over checkbox completion.
""")

    else:
        st.balloons()
        st.markdown("""
        <div style="text-align:center;padding:2rem 0;">
            <div style="font-size:2.5rem;margin-bottom:0.6rem;">🎉</div>
            <div style="font-family:'Syne',serif;font-size:1.6rem;color:#6ee7b7;font-weight:700;">Perfect Coverage</div>
            <div style="font-size:0.9rem;color:#94a3b8;margin-top:0.5rem;">
                Your resume matches every required skill. You're ready to apply!
            </div>
        </div>""", unsafe_allow_html=True)
