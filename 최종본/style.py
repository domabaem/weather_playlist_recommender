"""공통 CSS 스타일 — 모든 페이지에서 inject_css()를 호출한다."""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

/* ── Streamlit 기본 UI 완전 제거 ── */
[data-testid="stSidebarNav"]   { display: none !important; }
[data-testid="stToolbar"]      { display: none !important; }
[data-testid="stDecoration"]   { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
[data-testid="stSidebar"]      { display: none !important; }
#MainMenu                      { display: none !important; }
footer                         { display: none !important; }
header                         { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* ── 전체 배경 ── */
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: #0A0A0A;
}
[data-testid="stHeader"] { display: none !important; }

/* ── 본문 ── */
html, body {
    background: #0A0A0A;
    color: #E8E8E8;
}
[class*="css"] {
    font-family: 'Inter', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
}
.block-container {
    max-width: 1080px;
    padding: 3rem 2rem 4rem 2rem;
    background: #0A0A0A;
}

/* ── 헤더 ── */
.page-hero {
    padding: 56px 0 40px 0;
    border-bottom: 1px solid #222;
    margin-bottom: 40px;
}
.page-hero-eyebrow {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #555;
    margin: 0 0 16px 0;
}
.page-hero h1 {
    font-family: 'Playfair Display', 'Georgia', serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: #F0F0F0;
    margin: 0 0 12px 0;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.page-hero p {
    font-size: 0.95rem;
    color: #666;
    margin: 0;
    font-weight: 400;
    line-height: 1.6;
}

/* ── 스텝 인디케이터 ── */
.steps {
    display: flex;
    align-items: center;
    margin-bottom: 40px;
    gap: 0;
}
.step { display: flex; align-items: center; gap: 10px; }
.step-circle {
    width: 26px; height: 26px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700;
}
.step-active   .step-circle { background: #F0F0F0; color: #0A0A0A; }
.step-done     .step-circle { background: #333; color: #888; border: 1px solid #444; }
.step-inactive .step-circle { background: transparent; color: #444; border: 1px solid #2A2A2A; }
.step-active   .step-label  { color: #F0F0F0; font-size: 0.82rem; font-weight: 600; }
.step-done     .step-label  { color: #555; font-size: 0.82rem; }
.step-inactive .step-label  { color: #333; font-size: 0.82rem; }
.step-line { flex: 1; height: 1px; background: #1E1E1E; margin: 0 12px; min-width: 32px; }
.step-line-done { background: #333; }

/* ── 섹션 타이틀 ── */
.section-title {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #555;
    margin: 0 0 12px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid #1A1A1A;
}

/* ── 카드 ── */
.card {
    background: #111;
    border: 1px solid #1E1E1E;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 12px;
}
.card:hover { border-color: #2A2A2A; }

/* ── 정보 바 ── */
.info-bar {
    background: #111;
    border: 1px solid #1E1E1E;
    border-radius: 8px;
    padding: 12px 20px;
    margin-bottom: 28px;
    font-size: 0.85rem;
    color: #555;
    display: flex;
    align-items: center;
    gap: 16px;
}
.info-bar strong { color: #CCC; }
.info-bar .sep { color: #2A2A2A; }

/* ── 배지 ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    background: #1A1A1A;
    color: #888;
    border: 1px solid #2A2A2A;
}

/* ── 메트릭 ── */
[data-testid="metric-container"] {
    background: #111 !important;
    border: 1px solid #1E1E1E !important;
    border-radius: 8px !important;
    padding: 16px 20px !important;
}
div[data-testid="stMetricValue"] {
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: #E8E8E8 !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.7rem !important;
    color: #444 !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
[data-testid="stMetricDelta"] { display: none; }

/* ── 버튼 ── */
.stButton > button {
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.15s !important;
    padding: 0.5rem 1.2rem !important;
}
.stButton > button[kind="primary"] {
    background: #F0F0F0 !important;
    border: none !important;
    color: #0A0A0A !important;
}
.stButton > button[kind="primary"]:hover {
    background: #FFFFFF !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(255,255,255,0.08) !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid #2A2A2A !important;
    color: #888 !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #555 !important;
    color: #CCC !important;
}

/* ── 다운로드 버튼 ── */
.stDownloadButton > button {
    background: #F0F0F0 !important;
    color: #0A0A0A !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.6rem 1.5rem !important;
}
.stDownloadButton > button:hover {
    background: #FFFFFF !important;
    box-shadow: 0 4px 20px rgba(255,255,255,0.1) !important;
    transform: translateY(-1px) !important;
}

/* ── 입력창 ── */
.stTextInput input {
    background: #111 !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 6px !important;
    color: #E8E8E8 !important;
    font-size: 0.9rem !important;
}
.stTextInput input:focus {
    border-color: #555 !important;
    box-shadow: 0 0 0 2px rgba(255,255,255,0.05) !important;
}
.stTextInput input::placeholder { color: #333 !important; }

/* ── 셀렉트박스 ── */
.stSelectbox > div > div {
    background: #111 !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 6px !important;
    color: #E8E8E8 !important;
}

/* ── 슬라이더 ── */
.stSlider [data-baseweb="slider"] { padding-top: 6px; }
.stSlider [data-baseweb="thumb"] { background: #F0F0F0 !important; }
.stSlider [data-baseweb="track-fill"] { background: #F0F0F0 !important; }
.stSlider [data-baseweb="track"] { background: #222 !important; }

/* ── 프로그레스 바 ── */
.stProgress > div > div > div {
    background: #F0F0F0 !important;
    border-radius: 4px !important;
}
.stProgress > div > div {
    background: #1A1A1A !important;
    border-radius: 4px !important;
}

/* ── 텍스트 영역 ── */
.stTextArea textarea {
    background: #111 !important;
    border: 1px solid #1E1E1E !important;
    border-radius: 6px !important;
    color: #CCC !important;
    font-size: 0.85rem !important;
    line-height: 1.7 !important;
}

/* ── 이미지 ── */
[data-testid="stImage"] img {
    border-radius: 6px;
    border: 1px solid #1E1E1E;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #111 !important;
    border: 1px solid #1E1E1E !important;
    border-radius: 6px !important;
    color: #666 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
}
.streamlit-expanderContent {
    background: #0D0D0D !important;
    border: 1px solid #1E1E1E !important;
    border-top: none !important;
}

/* ── Alert ── */
[data-testid="stAlert"] {
    background: #111 !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 6px !important;
    color: #AAA !important;
    font-size: 0.88rem !important;
}

/* ── 구분선 ── */
hr { border-color: #1A1A1A !important; margin: 24px 0 !important; }

/* ── 파일 업로더 ── */
[data-testid="stFileUploader"] > div {
    background: #111 !important;
    border: 1px dashed #2A2A2A !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"] label { color: #555 !important; font-size: 0.85rem !important; }

/* ── 전체 텍스트 색상 ── */
p, span, div, li { color: inherit; }
label { color: #555 !important; font-size: 0.82rem !important; font-weight: 500 !important; }
h1, h2, h3 { color: #E8E8E8; }
</style>
"""

def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str, eyebrow: str = "AI Lecture Notes"):
    st.markdown(
        f'''<div class="page-hero">
            <p class="page-hero-eyebrow">{eyebrow}</p>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>''',
        unsafe_allow_html=True,
    )


def steps_indicator(current: int):
    labels = ["Upload", "Summarize", "Export"]
    parts  = []
    for i, label in enumerate(labels, 1):
        if i < current:
            cls, circle = "step-done", "&#10003;"
        elif i == current:
            cls, circle = "step-active", str(i)
        else:
            cls, circle = "step-inactive", str(i)
        parts.append(
            f'<div class="step {cls}">'
            f'<div class="step-circle">{circle}</div>'
            f'<span class="step-label">{label}</span>'
            f'</div>'
        )
        if i < len(labels):
            line_cls = "step-line-done" if i < current else ""
            parts.append(f'<div class="step-line {line_cls}"></div>')
    st.markdown(f'<div class="steps">{"".join(parts)}</div>', unsafe_allow_html=True)


def info_bar(file_name: str, page_count: int, mode: str):
    st.markdown(
        f'''<div class="info-bar">
            <strong>{file_name}</strong>
            <span class="sep">|</span>
            <span>{page_count} pages</span>
            <span class="sep">|</span>
            <span class="badge">{mode}</span>
        </div>''',
        unsafe_allow_html=True,
    )
