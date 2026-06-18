# -*- coding: utf-8 -*-
from __future__ import annotations
import os, sys
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

import streamlit as st
from pdf_loader import process_pdf, read_uploaded_file
from pptx_loader import process_pptx
from style import inject_css, hero, steps_indicator

st.set_page_config(page_title="AI Lecture Notes", layout="wide", page_icon=None)
inject_css()

hero(
    "Lecture Note Generator",
    "Upload your lecture material and get AI-powered study notes instantly.",
    eyebrow="Step 1 — Upload"
)
steps_indicator(1)

st.markdown('<p class="section-title">강의자료 업로드</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "PDF, PPTX, PNG, JPG 파일을 드래그하거나 클릭해서 업로드하세요",
    type=["pdf", "pptx", "png", "jpg", "jpeg"],
    label_visibility="collapsed",
)

if uploaded_file is None:
    st.markdown(
        '''<div style="
            background:#0F0F0F;
            border: 1px dashed #2A2A2A;
            border-radius: 8px;
            padding: 56px 32px;
            text-align: center;
            margin-top: 8px;">
            <div style="font-size:0.72rem;letter-spacing:0.16em;text-transform:uppercase;
                        color:#333;margin-bottom:14px;">Drag & Drop or Click Above</div>
            <div style="font-size:1.05rem;font-weight:600;color:#555;">
                강의자료 파일을 업로드하세요
            </div>
            <div style="font-size:0.82rem;color:#333;margin-top:8px;">
                PDF · PPTX · PNG · JPG &nbsp;/&nbsp; 최대 200MB
            </div>
        </div>''',
        unsafe_allow_html=True,
    )
    st.stop()

_name      = uploaded_file.name.lower()
_is_image  = _name.endswith((".png", ".jpg", ".jpeg"))
_is_pptx   = _name.endswith(".pptx")

if _is_image:
    st.markdown('<p class="section-title">이미지 미리보기</p>', unsafe_allow_html=True)
    st.image(uploaded_file, use_container_width=True)
    st.markdown(
        '<div class="card"><p style="margin:0;color:#555;font-size:0.88rem;">'
        '이미지 파일은 다음 단계에서 분석됩니다.</p></div>',
        unsafe_allow_html=True,
    )
    st.stop()

with st.spinner("분석 중..."):
    if _is_pptx:
        result = process_pptx(uploaded_file.getvalue(), uploaded_file.name)
    else:
        pdf_bytes = read_uploaded_file(uploaded_file)
        result    = process_pdf(pdf_bytes, file_name=uploaded_file.name, max_image_pages=None)

st.session_state["pdf_result"] = result
st.session_state["file_name"]  = uploaded_file.name
if "lecture_note" not in st.session_state:
    st.session_state["lecture_note"] = None

st.markdown("<br>", unsafe_allow_html=True)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("파일명",      result.file_name[:14] + ("…" if len(result.file_name) > 14 else ""))
m2.metric("총 페이지",   result.page_count)
m3.metric("추출 글자",   f"{len(result.full_text):,}")
m4.metric("페이지 평균", f"{result.ai_mode.average_chars_per_page:.0f}자")
m5.metric("추천 방식",   result.ai_mode.mode)

st.markdown(
    f'''<div class="card" style="margin-top:12px;">
        <p style="margin:0;font-size:0.85rem;color:#555;line-height:1.8;">
            {result.ai_mode.reason}
        </p>
    </div>''',
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

preview_col, text_col = st.columns(2, gap="large")
with preview_col:
    st.markdown('<p class="section-title">페이지 이미지</p>', unsafe_allow_html=True)
    if result.page_images:
        page_nums = [p.page_number for p in result.pages[:len(result.page_images)]]
        sel       = st.selectbox("페이지", page_nums, label_visibility="collapsed")
        st.image(result.page_images[sel - 1], use_container_width=True)
    else:
        st.markdown('<div class="card"><p style="color:#444;margin:0;font-size:0.85rem;">변환된 이미지가 없습니다.</p></div>', unsafe_allow_html=True)

with text_col:
    st.markdown('<p class="section-title">추출된 텍스트</p>', unsafe_allow_html=True)
    sel_t = st.selectbox("텍스트 페이지", [p.page_number for p in result.pages],
                         key="text_page", label_visibility="collapsed")
    st.text_area("", value=result.pages[sel_t - 1].cleaned_text,
                 height=400, label_visibility="collapsed")

with st.expander("전체 텍스트 보기"):
    st.text_area("", value=result.full_text, height=280, label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<p class="section-title">다음 단계</p>', unsafe_allow_html=True)
if st.button("AI 요약 생성하기", type="primary", use_container_width=True):
    st.switch_page("pages/summarize_page.py")
