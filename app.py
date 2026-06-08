from __future__ import annotations

import streamlit as st

from pdf_loader import process_pdf, read_uploaded_file


# Streamlit 기본 페이지 설정
st.set_page_config(
    page_title="AI Lecture Note Generator",
    layout="wide",
)

st.title("AI Lecture Note Generator")
st.caption("입력/PDF 처리 담당 화면")

# 사용자가 PDF, PNG, JPG 강의자료를 업로드하는 부분
uploaded_file = st.file_uploader(
    "강의자료 업로드",
    type=["pdf", "png", "jpg", "jpeg"],
)

if uploaded_file is None:
    st.info("PDF, PNG, JPG 강의자료를 업로드하세요.")
    st.stop()

# 이미지 파일은 여기서 미리보기만 제공한다.
# 실제 이미지 분석은 2번 담당의 VLM/Claude API 모듈과 연결하면 된다.
if uploaded_file is not None and uploaded_file.type != "application/pdf":
    st.subheader("이미지 입력 미리보기")
    st.image(uploaded_file, use_container_width=True)
    st.warning("이미지 OCR/요약은 Claude 처리 담당 모듈에서 연결합니다.")
    st.stop()

# PDF 파일은 텍스트 추출과 페이지 이미지 변환을 동시에 수행한다.
with st.spinner("강의자료를 분석하는 중입니다."):
    # Streamlit 업로드 파일을 bytes로 바꿔 PyMuPDF에 전달한다.
    pdf_bytes = read_uploaded_file(uploaded_file)
    result = process_pdf(
        pdf_bytes,
        file_name=uploaded_file.name,
        max_image_pages=None,
    )

# 처리 결과 요약 정보 표시
metric_cols = st.columns(5)
metric_cols[0].metric("파일명", result.file_name)
metric_cols[1].metric("PDF 페이지", result.page_count)
metric_cols[2].metric("추출 글자 수", len(result.full_text))
metric_cols[3].metric("평균 글자 수", f"{result.ai_mode.average_chars_per_page:.0f}자/쪽")
metric_cols[4].metric("추천 방식", result.ai_mode.mode)

st.info(
    f"판단 근거: {result.ai_mode.reason}\n\n"
    f"LLM 사용: {'예' if result.ai_mode.use_llm else '아니오'} / "
    f"VLM 사용: {'예' if result.ai_mode.use_vlm else '선택'}\n\n"
    f"{result.ai_mode.integration_note}"
)

st.divider()

preview_col, text_col = st.columns([1, 1])

with preview_col:
    st.subheader("페이지 이미지 변환")
    if result.page_images:
        # 이 PNG bytes 목록은 VLM API에 이미지 입력으로 넘길 수 있다.
        page_numbers = [page.page_number for page in result.pages[: len(result.page_images)]]
        selected_page = st.selectbox("미리보기 페이지", page_numbers)
        image_index = selected_page - 1
        st.image(result.page_images[image_index], use_container_width=True)
    else:
        st.info("변환된 페이지 이미지가 없습니다.")

with text_col:
    st.subheader("전처리된 추출 텍스트")
    # 이 텍스트는 LLM API에 요약 입력으로 넘길 수 있다.
    selected_text_page = st.selectbox(
        "텍스트 페이지",
        [page.page_number for page in result.pages],
        key="text_page",
    )
    page_text = result.pages[selected_text_page - 1].cleaned_text
    st.text_area(
        "페이지 텍스트",
        value=page_text,
        height=480,
    )

with st.expander("전체 추출 텍스트"):
    # 전체 PDF 텍스트를 확인할 수 있게 제공한다.
    st.text_area(
        "전체 텍스트",
        value=result.full_text,
        height=360,
    )
