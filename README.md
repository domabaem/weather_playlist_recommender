# AI Lecture Notes

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Claude API](https://img.shields.io/badge/Claude_API-Anthropic-111111?style=flat-square)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-PDF_Processing-0C7BDC?style=flat-square)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF_Output-6A5ACD?style=flat-square)
![Status](https://img.shields.io/badge/Status-MVP-blue?style=flat-square)

강의자료를 업로드하면 AI가 내용을 분석해 카드형 강의 노트로 정리하고, 최종 결과를 PDF로 저장할 수 있는 Streamlit 기반 프로젝트입니다.

최종 실행 코드는 `최종본/` 폴더에 있습니다.

---

## 프로젝트 소개

이 프로젝트는 PDF 또는 PPTX 형태의 강의자료를 입력받아 핵심 내용을 정리하는 AI 강의 필기 생성기입니다.

사용자는 강의자료를 업로드한 뒤, AI 요약 옵션을 선택하고, 결과를 보기 좋은 노트 형태로 확인할 수 있습니다. 마지막 단계에서는 정리된 내용을 PDF 파일로 다운로드할 수 있습니다.

---

## 주요 기능

```text
1. 강의자료 업로드
   - PDF, PPTX 파일 업로드
   - 이미지 파일 미리보기

2. 입력 자료 분석
   - PDF 텍스트 추출
   - PDF 페이지 이미지 변환
   - PPTX 슬라이드 텍스트 추출
   - LLM/VLM 처리 방식 추천

3. AI 요약 생성
   - Claude API 기반 요약
   - 요약 톤, 출력 언어, 분량 선택
   - 핵심 요약, 개념 정리, 복습 질문 등 블록 생성

4. 결과 출력
   - 카드형 강의 노트 미리보기
   - 테마 및 레이아웃 선택
   - PDF 파일 다운로드
```

---

## 시스템 아키텍처

```text
[사용자]
   |
   | 강의자료 업로드
   v
[Streamlit app.py]
   |
   +-------------------------+
   |                         |
   v                         v
[PDF 처리]               [PPTX 처리]
pdf_loader.py            pptx_loader.py
   |                         |
   v                         v
텍스트 추출              슬라이드 텍스트 추출
페이지 이미지 변환
   |
   v
[AI 요약 페이지]
pages/summarize_page.py
   |
   | Claude API 요청
   v
[요약 JSON 생성]
   |
   v
[출력 페이지]
pages/output_page.py
   |
   v
HTML 스타일 미리보기 + PDF 다운로드
```

---

## 폴더 구조

```text
최종본/
├─ app.py
├─ pdf_loader.py
├─ pptx_loader.py
├─ style.py
├─ requirements.txt
├─ run.bat
└─ pages/
   ├─ summarize_page.py
   └─ output_page.py
```

파일별 역할은 다음과 같습니다.

```text
app.py
    파일 업로드와 첫 화면을 담당합니다.

pdf_loader.py
    PDF 텍스트 추출, 페이지 이미지 변환, AI 처리 방식 추천을 담당합니다.

pptx_loader.py
    PPTX 슬라이드 텍스트 추출을 담당합니다.

pages/summarize_page.py
    Claude API를 사용해 강의자료를 요약합니다.

pages/output_page.py
    요약 결과를 카드형 노트로 보여주고 PDF 다운로드를 제공합니다.

style.py
    Streamlit 화면 스타일을 담당합니다.

run.bat
    Windows에서 앱을 쉽게 실행하기 위한 실행 파일입니다.
```

---

## 실행 방법

### 1. 최종본 폴더로 이동

```bash
cd 최종본
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. API 키 설정

Claude API를 사용하기 위해 Anthropic API 키가 필요합니다.

방법 1: 환경변수 설정

```bash
set ANTHROPIC_API_KEY=your_api_key
```

방법 2: `최종본/` 폴더에 `apikey.txt` 파일을 만들고 API 키를 한 줄로 저장

```text
sk-ant-...
```

주의: `apikey.txt`는 GitHub에 올리지 않는 것이 좋습니다.

### 4. 앱 실행

```bash
streamlit run app.py
```

Windows에서는 `최종본/run.bat`을 실행해도 됩니다.

---

## 사용 흐름

```text
1. 앱 실행
2. PDF 또는 PPTX 강의자료 업로드
3. 추출된 텍스트와 페이지 미리보기 확인
4. AI 요약 생성하기 클릭
5. 요약 옵션 선택
6. Claude API로 강의 노트 생성
7. 결과 미리보기
8. PDF 다운로드
```

---

## 발표 및 시연 영상

- [발표 영상](https://youtu.be/UxyeQ9u-Tt8)
- [시연 영상](./demo.mp4)

---

## 사용 기술

```text
Python
Streamlit
Anthropic Claude API
PyMuPDF
python-pptx
ReportLab
```

---

## 팀원별 역할 및 기여도

| 이름 | 역할 | 기여도 |
|---|---|---|
| 이윤수 | UI·A4디자인·다운로드, PPT 제작, 시연 영상 | 작성 예정 |
| 왕혜영 | 입력·PDF 처리, README 작성, PPT 제작, 발표 영상 | 작성 예정 |
| 장지연 | Claude 요약 로직 | 작성 예정 |
