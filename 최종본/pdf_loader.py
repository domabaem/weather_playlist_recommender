from __future__ import annotations

import re
from dataclasses import dataclass
from typing import BinaryIO

import fitz


# 텍스트가 이 글자 수보다 적게 추출되면 이미지 기반 PDF일 가능성이 높다고 판단한다.
TEXT_FALLBACK_THRESHOLD = 80


@dataclass(frozen=True)
class PageText:
    # PDF 한 페이지에서 추출·전처리한 텍스트를 보관한다.
    page_number: int
    cleaned_text: str

    @property
    def char_count(self) -> int:
        return len(self.cleaned_text)


@dataclass(frozen=True)
class AiModeRecommendation:
    # PDF 추출 결과를 보고 어떤 분석 방식이 적합한지 설명한다.
    mode: str
    average_chars_per_page: float
    reason: str


@dataclass(frozen=True)
class PdfExtractResult:
    # LLM API에는 full_text를, 미리보기/이미지 분석에는 page_images를 넘길 수 있다.
    file_name: str
    page_count: int
    pages: list[PageText]
    full_text: str
    page_images: list[bytes]
    ai_mode: AiModeRecommendation


def read_uploaded_file(uploaded_file: BinaryIO | bytes) -> bytes:
    """Streamlit 업로드 파일을 PyMuPDF가 읽을 수 있는 bytes 형태로 변환한다."""
    if isinstance(uploaded_file, bytes):
        return uploaded_file

    # Streamlit UploadedFile은 파일처럼 동작하므로 처음 위치로 돌린 뒤 전체를 읽는다.
    uploaded_file.seek(0)
    return uploaded_file.read()


def clean_extracted_text(text: str) -> str:
    # PDF에서 섞여 나올 수 있는 NULL 문자와 불필요한 공백을 정리한다.
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.strip() for line in text.splitlines()]

    cleaned_lines: list[str] = []
    for index, line in enumerate(lines):
        # 빈 줄은 여러 개가 연속으로 나오지 않게 하나만 유지한다.
        if not line:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue

        # 강의자료 PDF 마지막 줄에 찍히는 페이지 번호는 요약에 방해되므로 제거한다.
        is_last_line = index == len(lines) - 1
        if is_last_line and line.isdigit():
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def extract_text_from_pdf(pdf_bytes: bytes, file_name: str = "uploaded.pdf") -> tuple[list[PageText], str]:
    # LLM API에 넘길 텍스트를 추출하는 함수이다.
    with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
        pages: list[PageText] = []
        for page_index, page in enumerate(document, start=1):
            # PyMuPDF의 get_text("text")로 페이지별 텍스트를 가져온 뒤 전처리한다.
            cleaned_text = clean_extracted_text(page.get_text("text"))
            pages.append(
                PageText(
                    page_number=page_index,
                    cleaned_text=cleaned_text,
                )
            )

    # 전체 요약용으로 페이지 텍스트를 하나의 문자열로 합친다.
    full_text = "\n\n".join(page.cleaned_text for page in pages if page.cleaned_text)
    return pages, full_text


def render_pdf_pages_to_images(
    pdf_bytes: bytes,
    dpi: int = 144,
    max_pages: int | None = None,
) -> list[bytes]:
    # 페이지 미리보기/이미지 분석에 넘길 페이지 이미지를 PNG bytes 형태로 변환하는 함수이다.
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)

    with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
        # 긴 PDF는 비용과 속도를 고려해 필요한 페이지만 이미지로 변환할 수 있다.
        page_limit = document.page_count if max_pages is None else min(max_pages, document.page_count)
        images: list[bytes] = []

        for page_index in range(page_limit):
            # PDF 페이지를 래스터 이미지로 렌더링한 뒤 PNG bytes로 저장한다.
            pixmap = document[page_index].get_pixmap(matrix=matrix, alpha=False)
            images.append(pixmap.tobytes("png"))

    return images


def recommend_ai_mode(pages: list[PageText], threshold: int = TEXT_FALLBACK_THRESHOLD) -> AiModeRecommendation:
    # 텍스트 추출량을 보고 텍스트 기반 요약에 적합한지(스캔본 가능성이 높은지) 판단한다.
    if not pages:
        return AiModeRecommendation(
            mode="VLM 우선",
            average_chars_per_page=0,
            reason="PDF 페이지 텍스트가 추출되지 않아 이미지 기반 분석이 필요합니다.",
        )

    average_chars = sum(page.char_count for page in pages) / len(pages)
    sparse_pages = [page.page_number for page in pages if page.char_count < threshold]

    if average_chars < threshold:
        return AiModeRecommendation(
            mode="VLM 우선",
            average_chars_per_page=average_chars,
            reason=(
                f"페이지당 평균 텍스트가 {average_chars:.0f}자로 적어 "
                "스캔본 또는 이미지 중심 PDF일 가능성이 높습니다."
            ),
        )

    if sparse_pages:
        sparse_page_text = ", ".join(str(page_number) for page_number in sparse_pages)
        return AiModeRecommendation(
            mode="LLM+VLM 혼합",
            average_chars_per_page=average_chars,
            reason=(
                f"전체 텍스트는 충분하지만 {sparse_page_text}페이지는 텍스트가 적어 "
                "이미지 분석을 함께 쓰는 것이 좋습니다."
            ),
        )

    return AiModeRecommendation(
        mode="LLM 우선",
        average_chars_per_page=average_chars,
        reason=(
            f"페이지당 평균 텍스트가 {average_chars:.0f}자로 충분히 추출되어 "
            "텍스트 기반 요약에 적합합니다."
        ),
    )


def process_pdf(
    pdf_bytes: bytes,
    file_name: str = "uploaded.pdf",
    dpi: int = 144,
    max_image_pages: int | None = None,
) -> PdfExtractResult:
    # PDF 처리의 메인 함수이다. 텍스트 추출과 이미지 변환을 모두 수행한다.
    with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
        page_count = document.page_count

    # LLM용 텍스트 데이터 생성
    pages, full_text = extract_text_from_pdf(pdf_bytes, file_name=file_name)

    # 미리보기/이미지 분석용 이미지 데이터 생성
    page_images = render_pdf_pages_to_images(pdf_bytes, dpi=dpi, max_pages=max_image_pages)

    ai_mode = recommend_ai_mode(pages)

    return PdfExtractResult(
        file_name=file_name,
        page_count=page_count,
        pages=pages,
        full_text=full_text,
        page_images=page_images,
        ai_mode=ai_mode,
    )
