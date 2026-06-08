# AI 강의 필기 생성기: 입력/PDF 처리 파트 설명

이 문서는 코드를 잘 모르는 사람도 프로젝트 흐름을 이해할 수 있도록 정리한 설명서이다.

현재 1번 담당 파트는 **사용자가 올린 강의자료를 읽고, AI가 처리할 수 있는 입력 데이터로 바꾸는 역할**을 한다.

---

## 1. 현재 구현된 파일

```text
app.py
    사용자가 파일을 업로드하는 Streamlit 화면

pdf_loader.py
    PDF에서 텍스트를 뽑고, PDF 페이지를 이미지로 바꾸는 처리 모듈

requirements.txt
    실행에 필요한 라이브러리 목록
```

현재 앱은 기본 PDF를 자동으로 불러오지 않는다.  
사용자가 직접 파일을 업로드해야 분석이 시작된다.

---

## 2. 시스템 아키텍처

```text
[사용자]
   |
   | PDF / 이미지 업로드
   v
[app.py: Streamlit 화면]
   |
   | 업로드 파일을 bytes로 변환
   v
[pdf_loader.py: PDF 처리]
   |
   +-----------------------------+
   |                             |
   v                             v
[텍스트 추출]                 [페이지 이미지 변환]
LLM 입력용                    VLM 입력용
   |                             |
   v                             v
result.full_text              result.page_images
   |                             |
   +-------------+---------------+
                 |
                 v
       [LLM/VLM 사용 방식 추천]
                 |
                 v
          result.ai_mode
                 |
                 v
       [2번 담당: AI 요약 처리]
                 |
                 v
       [3번 담당: HTML/PDF 출력]
```

---

## 3. 전체 파이프라인

```text
1. 사용자가 PDF를 업로드한다.

2. app.py가 업로드 파일을 받는다.

3. pdf_loader.py가 PDF를 분석한다.

4. PDF에서 텍스트를 추출한다.
   -> LLM API 입력으로 사용

5. PDF 전체 페이지를 이미지로 변환한다.
   -> VLM API 입력으로 사용

6. 텍스트 추출량을 보고 LLM/VLM 중 어떤 방식을 우선 쓸지 추천한다.

7. Streamlit 화면에 분석 결과를 보여준다.

8. 2번 담당이 이 결과를 받아 AI 요약을 만든다.

9. 3번 담당이 요약 결과를 HTML 카드와 PDF로 출력한다.
```

---

## 4. 1번 담당 파트가 만드는 결과

PDF 하나를 업로드하면 크게 세 가지 결과가 만들어진다.

```text
result.full_text
    PDF에서 추출한 전체 텍스트
    LLM API에 넘길 입력값

result.page_images
    PDF 전체 페이지를 PNG 이미지로 변환한 값
    VLM API에 넘길 입력값

result.ai_mode
    이 파일을 LLM 중심으로 처리할지,
    VLM 중심으로 처리할지,
    둘 다 사용할지 추천한 결과
```

즉, 1번 담당은 AI가 바로 사용할 수 있는 재료를 준비하는 역할이다.

---

## 5. Streamlit 화면에서 보이는 것

앱을 실행하면 사용자는 파일을 직접 업로드한다.

PDF가 업로드되면 화면에서 다음 내용을 확인할 수 있다.

```text
파일명
PDF 페이지 수
추출된 전체 글자 수
페이지당 평균 글자 수
추천 처리 방식
판단 근거
PDF 페이지 이미지 미리보기
페이지별 텍스트 미리보기
전체 추출 텍스트
```

추천 처리 방식은 예를 들어 다음처럼 나온다.

```text
추천 방식: LLM 우선
판단 근거: 텍스트가 충분히 추출되어 텍스트 기반 요약에 적합합니다.
```

---

## 6. LLM과 VLM을 같이 쓰는 경우

LLM과 VLM을 같이 써도 최종 결과물은 하나로 합쳐야 한다.

추천 흐름은 다음과 같다.

```text
PDF 텍스트
   -> LLM 요약

PDF 페이지 이미지
   -> VLM 이미지 분석

LLM 요약 + VLM 분석
   -> 최종 통합
   -> 하나의 JSON 결과
   -> HTML 카드
   -> PDF 다운로드
```

최종 JSON은 이런 형태가 적당하다.

```json
{
  "title": "강의 제목",
  "summary": ["핵심 요약"],
  "key_concepts": ["핵심 개념"],
  "visual_notes": ["이미지와 도표 설명"],
  "exam_points": ["시험 포인트"],
  "review_questions": ["복습 질문"]
}
```

---

## 7. 2번 담당이 하면 좋은 일

2번 담당은 Claude API 또는 다른 LLM/VLM API를 연결하는 역할이다.

추천 구현 방향은 다음과 같다.

```text
1. 1번 담당 결과를 입력으로 받는다.

2. result.full_text를 LLM에 보내 텍스트 요약을 만든다.

3. 필요하면 result.page_images를 VLM에 보내 이미지/도표 설명을 만든다.

4. LLM 결과와 VLM 결과를 하나로 합친다.

5. 최종 결과는 JSON 형식으로 고정한다.
```

2번 담당에게 넘기면 좋은 값은 다음이다.

```text
result.full_text
result.page_images
result.ai_mode
```

특히 `result.ai_mode`를 보고 처리 방식을 정하면 된다.

```text
LLM 우선
    텍스트 요약을 중심으로 처리

VLM 우선
    이미지 분석을 중심으로 처리

LLM+VLM 혼합
    텍스트 요약과 이미지 분석을 둘 다 사용
```

---

## 8. 3번 담당이 하면 좋은 일

3번 담당은 최종 결과를 보기 좋게 보여주고 PDF로 저장하는 역할이다.

추천 구현 방향은 다음과 같다.

```text
1. 2번 담당이 만든 JSON 결과를 받는다.

2. JSON 내용을 HTML 카드 형태로 배치한다.

3. Streamlit 화면에서 요약 결과를 미리보기로 보여준다.

4. HTML을 Playwright로 PDF 파일로 변환한다.

5. Streamlit 다운로드 버튼으로 PDF를 내려받게 한다.
```

화면 구성은 다음 정도면 충분하다.

```text
강의 제목
핵심 요약
핵심 개념
이미지/도표 설명
시험 포인트
복습 질문
PDF 다운로드 버튼
```

---

## 9. 실행 방법

프로젝트 폴더에서 실행한다.

```powershell
cd C:\Users\ladde\Desktop\3_1_Semester\ai_base\기말프로젝트
.\.conda\python.exe -m streamlit run app.py
```

다른 PC에서 처음 실행하는 경우 패키지를 설치한다.

```powershell
.\.conda\python.exe -m pip install -r requirements.txt
```

---

## 10. 최종 정리

```text
1번 담당
    파일 업로드, PDF 텍스트 추출, PDF 이미지 변환, LLM/VLM 추천 판단

2번 담당
    LLM/VLM API 연결, 요약 생성, JSON 결과 생성

3번 담당
    JSON 결과를 HTML 카드로 표시, PDF 다운로드 구현
```

현재 1번 담당 파트는 다음 단계로 넘길 준비가 되어 있다.

```text
텍스트 입력: result.full_text
이미지 입력: result.page_images
추천 방식: result.ai_mode
```
