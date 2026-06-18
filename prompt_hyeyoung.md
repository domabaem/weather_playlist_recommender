# PDF 입력·처리 구현

> C:\Users\ladde\Desktop\3_1_Semester\ai_base\기말프로젝트\인공지능개론_기말.pdf
>
> 에 파일 읽고 역할 분담으로 내가 할 일이
>
> 1번 담당: 입력·PDF 처리
> • Streamlit 파일 업로드 연결
> • PyMuPDF 텍스트 추출
> • PDF 페이지 이미지 변환
> • 추출 결과 전처리
> • 샘플 강의자료 테스트 이건데

<details><summary>20 previous messages</summary>

> 먼저 프로젝트 구조랑 PDF 내용을 같이 확인해볼게요. 역할 범위가 입력/PDF 처리 쪽이라, 이미 Streamlit 코드가 있는지와 PyMuPDF를 어디에 붙이면 자연스러운지부터 볼게요.
>
> 파일 목록은 보이는데 PowerShell 프로필 로딩 경고랑 한글 파일명 인코딩이 살짝 섞였어요. 프로필을 끄고 UTF-8 출력으로 다시 확인하겠습니다.
>
> 방금 샌드박스 쪽에서 프로세스 시작 오류가 한 번 났습니다. 같은 확인을 단일 명령으로 다시 시도해볼게요.
>
> 일반 PowerShell 호출이 막혀서, 이미 승인된 형태의 PowerShell 실행 경로로 프로젝트 파일 목록을 확인해보겠습니다.
>
> 프로젝트 폴더에는 PDF 하나만 있는 상태입니다. 이제 PDF 자체를 PyMuPDF로 열어 페이지 수와 텍스트를 확인해서, 이 역할에 맞는 최소 구현 파일을 만들 수 있는지 보겠습니다.
>
> Python 실행도 샌드박스 시작 단계에서 막혔습니다. PDF 확인에는 꼭 필요해서 같은 명령을 승인 요청으로 다시 실행하겠습니다.
>
> 현재 환경에는 `fitz`(PyMuPDF)가 설치되어 있지 않습니다. 맡은 범위가 PyMuPDF 추출/페이지 이미지 변환이라서, 먼저 의존성을 명확히 잡고 작은 Streamlit 앱 + PDF 처리 모듈 형태로 만들어보겠습니다.
>
> `streamlit`은 이미 있고 PyMuPDF만 없습니다. 샘플 PDF 테스트까지 끝내려면 `pymupdf` 하나를 설치한 뒤 구현을 검증하는 흐름이 가장 깔끔합니다.
>
> 설치가 됐습니다. 이제 실제 `인공지능개론_기말.pdf`를 열어 텍스트 추출과 페이지 구조를 확인하겠습니다.
>
> PDF는 7쪽짜리 수행계획서이고, 3쪽에 말씀하신 1번 담당 범위가 그대로 적혀 있습니다. 이제 그 범위만 독립 함수 단위로 구현해서 나중에 `app.py` 통합이 쉽게 되도록 만들겠습니다.
>
> 구현은 PDF 처리 전담 모듈을 `pdf_loader.py`로 분리하고, 확인용 Streamlit 화면을 `app.py`에 얇게 붙이는 식으로 가겠습니다. 샘플 강의자료 테스트는 별도 `sample_test.py`로 두면 발표/통합 전에 “내 파트 동작함”을 바로 보여주기 좋습니다.
>
> <details><summary>Created 4 files</summary>
>
> - Wrote `./app.py` (+93 -0)
> - Wrote `./pdf_loader.py` (+144 -0)
> - Wrote `./requirements.txt` (+3 -0)
> - Wrote `./sample_test.py` (+31 -0)
>
> </details>
>
> 파일 4개를 만들었습니다: 처리 모듈, Streamlit 확인 화면, 샘플 테스트, 의존성 목록입니다. 이제 문법 검사와 샘플 PDF 테스트를 돌려서 실제 추출/이미지 변환까지 확인하겠습니다.
>
> 문법 검사는 통과했습니다. 샘플 테스트 실행만 샌드박스 시작 오류가 나서, 같은 테스트를 승인된 실행으로 다시 돌리겠습니다.
>
> 샘플 PDF 테스트까지 통과했습니다. Streamlit 앱도 바로 확인할 수 있게 로컬 서버를 띄워두겠습니다.
>
> 서버 시작도 샌드박스 프로세스 오류가 났습니다. 앱 확인을 위해 백그라운드 실행만 승인 요청으로 다시 시도하겠습니다.
>
> 서버 프로세스가 시작됐습니다. 포트가 실제로 응답하는지 한 번만 확인하고 마무리하겠습니다.
>
> 응답 확인 명령도 같은 샌드박스 오류라, 서버 상태 확인만 승인 실행으로 마저 확인하겠습니다.
>
> 서버 응답 확인 승인은 취소되었지만, Streamlit 프로세스 자체는 PID `13244`로 시작된 상태입니다. 마무리 전에 불필요한 비ASCII 아이콘 하나만 빼서 코드 스타일을 조금 더 단정하게 맞추겠습니다.
>
> <details><summary>Edited a file</summary>
>
> - Wrote `./app.py` (+0 -1)
>
> </details>
</details>

맞아요, 이건 가상환경 기준으로 맞추는 게 제출/시연 때 훨씬 안전합니다. 방금 전역 Python으로 띄운 Streamlit 프로세스는 정리하고, 프로젝트 안에 `.venv`를 만든 뒤 그 안에 의존성을 설치해서 다시 테스트하겠습니다.

> venv 말고 conda 가상환경 하나 만들어

<details><summary>6 previous messages</summary>

> 좋아요, `venv` 말고 Conda로 맞추겠습니다. 프로젝트 안에 로컬 Conda 환경을 `.conda` 폴더로 만들면 팀원이 폴더 기준으로 실행하기 쉬워서 그 방식으로 진행할게요.
>
> 일반 셸 실행이 샌드박스 시작 단계에서 막혔습니다. Conda가 설치되어 있는지 확인하고 환경 생성까지 이어가야 해서 승인 실행으로 진행하겠습니다.
>
> Conda는 설치되어 있습니다. 이제 프로젝트 폴더 안에 `.conda` 환경을 만들고, 그 환경의 Python으로 `requirements.txt`를 설치해서 지금 만든 PDF 처리 코드가 그 안에서 돌아가게 맞추겠습니다.
>
> `.conda` 환경 생성이 끝났습니다. 이제 이 환경 안에 `streamlit`, `pymupdf`, `pillow`를 설치하고 샘플 테스트를 다시 돌려보겠습니다.
>
> 설치 명령이 2분 제한에 걸렸습니다. 일부 패키지가 이미 들어갔을 수 있어서, 먼저 현재 설치 상태를 확인한 뒤 부족한 것만 이어서 설치하겠습니다.
>
> 패키지는 모두 들어가 있습니다. 이제 전역 Python이 아니라 `.conda` 환경의 Python으로 문법 검사와 샘플 PDF 테스트를 확인하겠습니다.
</details>

Conda 가상환경 만들었습니다. 프로젝트 폴더 안에 `.conda`로 생성했고, 그 환경에 `streamlit`, `pymupdf`, `pillow` 설치까지 확인했습니다.

검증도 `.conda` Python으로 완료했습니다.

```powershell
.\.conda\python.exe -m py_compile pdf_loader.py app.py sample_test.py
.\.conda\python.exe sample_test.py
```

샘플 테스트 결과:

```text
샘플 PDF 테스트 성공
- 파일명: 인공지능개론_기말.pdf
- 페이지 수: 7
- 추출 글자 수: 2230
- 변환 이미지 수: 2
```

실행할 때는 프로젝트 폴더에서 이렇게 하면 됩니다.

```powershell
conda activate .\.conda
streamlit run app.py
```

활성화가 꼬이면 이 방식이 더 확실합니다.

```powershell
.\.conda\python.exe -m streamlit run app.py
```

> 근데 vlm이랑 llm api 둘 다 이용할 수도 있는 데 이미지 추출이랑 text 추출 코드 둘 다 작성한거야? 작성한 코드에 한글 주석으로 코드 설명 써줘

<details><summary>4 previous messages</summary>

> 맞아요. 지금 구조는 LLM용 텍스트 추출(`page.get_text`)과 VLM용 페이지 이미지 변환(`get_pixmap -> PNG bytes`)을 둘 다 만들어둔 상태입니다. 요청대로 코드 안에 한글 주석을 넣어서 어느 부분이 텍스트용이고 어느 부분이 이미지/VLM용인지 바로 보이게 정리하겠습니다.
>
> 이제 파일을 직접 수정합니다. 핵심은 `full_text`는 LLM 요약 API에 넘길 데이터, `page_images`는 VLM 이미지 분석 API에 넘길 PNG 데이터라는 점을 주석으로 분명히 남기겠습니다.
>
> <details><summary>Edited 3 files</summary>
>
> - Wrote `./app.py` (+12 -0)
> - Wrote `./pdf_loader.py` (+20 -1)
> - Wrote `./sample_test.py` (+3 -0)
>
> </details>
>
> 주석을 넣었습니다. 이제 Conda 환경 기준으로 문법 검사와 샘플 테스트를 다시 돌려서, 한글 주석 추가 때문에 실행이 깨지지 않는지 확인하겠습니다.
</details>

응, 둘 다 작성해뒀어.

[ pdf_loader.py ](</c:/Users/ladde/Desktop/3_1_Semester/ai_base/기말프로젝트/pdf_loader.py>) 안에:

- **LLM용 텍스트 추출 코드**: `extract_text_from_pdf()`
  - PyMuPDF `page.get_text("text")`로 PDF 텍스트 추출
  - `clean_extracted_text()`로 공백, 페이지 번호 같은 불필요한 부분 전처리
  - 최종적으로 `result.full_text`를 LLM API 입력으로 넘기면 됨

- **VLM용 이미지 추출 코드**: `render_pdf_pages_to_images()`
  - PyMuPDF `get_pixmap()`으로 PDF 페이지를 이미지로 렌더링
  - PNG `bytes` 형태로 변환
  - 최종적으로 `result.page_images`를 VLM API 이미지 입력으로 넘기면 됨

그리고 요청한 대로 [app.py](</c:/Users/ladde/Desktop/3_1_Semester/ai_base/기말프로젝트/app.py>), [pdf_loader.py](</c:/Users/ladde/Desktop/3_1_Semester/ai_base/기말프로젝트/pdf_loader.py>), [sample_test.py](</c:/Users/ladde/Desktop/3_1_Semester/ai_base/기말프로젝트/sample_test.py>)에 한글 주석으로 코드 설명도 추가했어.

Conda 환경 기준으로 다시 확인했고 테스트 통과했어.

```powershell
.\.conda\python.exe -m py_compile pdf_loader.py app.py sample_test.py
.\.conda\python.exe sample_test.py
```

결과:

```text
샘플 PDF 테스트 성공
- 페이지 수: 7
- 추출 글자 수: 2230
- 변환 이미지 수: 2
```

> 음 각 코드에 대해 설명하는 코드 마크다운으로 써서 파일 하나만들어줘 절차도 써줬으면 지금 작성된 python파일에 대한 전체 파이프라인도 써줘

좋아, 발표/제출할 때 바로 보여줄 수 있는 설명용 Markdown 파일로 정리하겠습니다. 현재 작성된 `pdf_loader.py`, `app.py`, `sample_test.py` 기준으로 전체 파이프라인, 실행 절차, 함수별 역할을 한 파일에 담을게요.

> 이어서 작성해줘

> 음 각 코드에 대해 설명하는 코드 마크다운으로 써서 파일 하나만들어줘 절차도 써줬으면 지금 작성된 python파일에 대한 전체 파이프라인도 써줘

<details><summary>3 previous messages</summary>

> 좋아, 이어서 바로 문서 파일 하나로 정리할게요. `PDF_PROCESSING_PIPELINE.md`에 전체 흐름, 실행 절차, 파일별 코드 설명, LLM/VLM 연결 지점을 같이 넣겠습니다.
>
> <details><summary>Created a file</summary>
>
> - Wrote `./PDF_PROCESSING_PIPELINE.md` (+756 -0)
>
> </details>
>
> 문서 파일을 만들었습니다. 마지막으로 파일이 정상 생성됐는지만 확인해서 경로를 알려드릴게요.
</details>

문서 파일 하나로 만들어뒀어.

[PDF_PROCESSING_PIPELINE.md](</c:/Users/ladde/Desktop/3_1_Semester/ai_base/기말프로젝트/PDF_PROCESSING_PIPELINE.md>)

안에 포함한 내용은:

- 현재 작성된 Python 파일 3개 설명
- 전체 PDF 처리 파이프라인
- Conda 가상환경 실행 절차
- `pdf_loader.py` 함수별 코드 설명
- `app.py` Streamlit 흐름 설명
- `sample_test.py` 테스트 코드 설명
- LLM API에는 `result.full_text`
- VLM API에는 `result.page_images`
- 1번 담당 역할과 코드 매칭표

발표하거나 보고서에 붙이기 좋게 코드블록이랑 설명 형식으로 정리해뒀어.

> 그래서 난 어떤 파일을 실행하면 되는거야..?

너는 이 파일 실행하면 돼:

```powershell
.\.conda\python.exe -m streamlit run app.py
```

즉, **실행 파일은 `app.py`**야.

프로젝트 폴더에서 이렇게 하면 됨:

```powershell
cd C:\Users\ladde\Desktop\3_1_Semester\ai_base\기말프로젝트
.\.conda\python.exe -m streamlit run app.py
```

테스트만 해보고 싶으면 이거:

```powershell
.\.conda\python.exe sample_test.py
```

정리하면:

```text
app.py          -> 실제 Streamlit 앱 실행
sample_test.py  -> PDF 처리 코드 테스트용
pdf_loader.py   -> 직접 실행 X, app.py가 가져다 쓰는 모듈
```

> cd C:\Users\ladde\Desktop\3_1_Semester\ai_base\기말프로젝트
> .\.conda\python.exe -m streamlit run app.py
> 테스트만 해보고 싶으면 이거:
>
> .\.conda\python.exe sample_test.py 둘이 차이가 뭐임?

차이는 **화면으로 확인하느냐 / 자동으로 검사만 하느냐**야.

`app.py` 실행:

```powershell
.\.conda\python.exe -m streamlit run app.py
```

이건 **실제 웹 앱 실행**이야.

브라우저에서 Streamlit 화면이 열리고, 너가 PDF를 업로드하거나 샘플 PDF를 선택해서 확인할 수 있어.

여기서 볼 수 있는 것:

```text
파일 업로드 화면
PDF 페이지 수
추출된 글자 수
페이지 이미지 미리보기
전처리된 텍스트 미리보기
이미지 분석 필요 여부
```

즉, **시연용 / 실제 사용용**이야.

`sample_test.py` 실행:

```powershell
.\.conda\python.exe sample_test.py
```

이건 **자동 테스트용**이야.

브라우저 안 열리고 터미널에서만 결과가 나와.

예를 들면:

```text
샘플 PDF 테스트 성공
- 파일명: 인공지능개론_기말.pdf
- 페이지 수: 7
- 추출 글자 수: 2230
- 변환 이미지 수: 2
```

이건 코드가 제대로 작동하는지 빠르게 확인하는 용도야.

정리하면:

```text
app.py
-> 사람이 직접 보는 웹 화면
-> 발표/시연/실제 실행용

sample_test.py
-> 코드가 정상인지 확인하는 자동 검사
-> 개발 중 확인용
```

너가 교수님이나 팀원한테 보여줄 때는 **`app.py` 실행**하면 돼.

> 근데 streamlit에서는 이미지로 추출한건 못봐?

볼 수 있어. 지금 `Streamlit`에서는 **PDF를 이미지로 변환한 결과를 왼쪽 영역에서 보여주게 되어 있어.**

실행하면:

```powershell
.\.conda\python.exe -m streamlit run app.py
```

브라우저 화면에서 아래 부분을 보면:

```text
페이지 이미지 변환
미리보기 페이지 [1, 2, 3 선택]
```

이 영역이 바로 **PDF 페이지를 이미지로 추출한 결과**야.

다만 지금 코드는 이미지 변환을 처음 3페이지만 하도록 해뒀어.

```python
result = process_pdf_path(SAMPLE_PDF_PATH, max_image_pages=3)
```

그래서 Streamlit에서는 1~3페이지만 이미지로 볼 수 있어.

정리하면:

```text
텍스트 추출 결과
-> 오른쪽 "전처리된 추출 텍스트"

이미지 추출 결과
-> 왼쪽 "페이지 이미지 변환"

sample_test.py
-> 이미지를 화면에 보여주지는 않음
-> 변환이 됐는지만 터미널에서 검사
```

그리고 중요한 점은, 현재 이미지는 파일로 저장되는 게 아니라 **PNG bytes 상태로 메모리에 만들어서 Streamlit에 바로 보여주는 방식**이야.

전체 페이지 이미지를 보고 싶으면 `app.py`에서 `max_image_pages=3`을 `max_image_pages=None`으로 바꾸면 돼.

> 음 None으로 하고 음 그 llm 입력할때 해당 파일을 llm api를 사용할지 vlm api를 사용할지 판단한것도 출력하게 하는건 어때? 다시 네가 pdf 읽고 판단해서 어떻게 하면 좋을지 의견 내봐 일단 코드 수정하지 말고

좋은 방향이야. Streamlit에서 **“이 파일은 LLM으로 처리할지, VLM으로 처리할지” 판단 결과를 출력**해주면 네 담당 파트가 훨씬 완성도 있어 보여.

내가 이 PDF 기준으로 판단하면:

```text
추천 처리 방식: LLM 우선
이유: 텍스트가 정상적으로 많이 추출됨
```

샘플 PDF는 7페이지이고, 이전 테스트에서 텍스트가 총 `2230자` 추출됐어. 페이지당 평균 약 `318자`라서 이미지 PDF나 스캔본은 아니고, PyMuPDF 텍스트 추출이 잘 되는 파일이야.

그래서 이 파일은:

```text
LLM API 사용 적합
-> result.full_text를 요약 API에 넘기면 됨
```

다만 PDF가 슬라이드 형태라서 화면 배치, 도표, 카드형 구조까지 이해시키고 싶다면:

```text
LLM + VLM 혼합 사용도 가능
-> 텍스트 요약은 LLM
-> 페이지 이미지/레이아웃 설명은 VLM
```

내가 추천하는 판단 출력 방식은 이거야.

```text
분석 추천: LLM 우선
텍스트 추출량: 2230자
페이지 수: 7페이지
페이지당 평균 글자 수: 약 318자
이미지 분석 필요 여부: 아니오
보조 설명: 텍스트 추출이 충분하므로 LLM 요약에 적합합니다. 단, 슬라이드 레이아웃이나 시각 요소까지 반영하려면 VLM을 함께 사용할 수 있습니다.
```

판단 기준은 이렇게 잡으면 좋음:

```text
1. 페이지당 평균 텍스트가 80자 이상
   -> LLM 우선

2. 페이지당 평균 텍스트가 80자 미만
   -> VLM 우선

3. 일부 페이지만 텍스트가 거의 없음
   -> LLM + VLM 혼합

4. 이미지, 표, 그래프, 슬라이드 구조 분석이 중요함
   -> LLM + VLM 혼합 추천
```

그리고 `max_image_pages=None`으로 바꾸는 것도 괜찮아. 이 샘플 PDF는 7페이지라 전체 이미지 변환해도 부담이 작아.

다만 나중에 100페이지짜리 PDF가 들어오면 느려질 수 있어서, 발표용이면 `None` 괜찮고 실제 서비스 느낌이면 `전체 변환 / 앞 3페이지만 변환` 옵션을 Streamlit에 두는 게 더 좋아 보여.

결론적으로 내 의견은:

```text
1. PDF 텍스트와 이미지 추출은 둘 다 수행
2. 추출된 텍스트 양을 기준으로 LLM/VLM 추천 방식 출력
3. 샘플 PDF는 "LLM 우선, VLM 선택 사용"으로 판단
4. Streamlit 화면에 추천 방식과 판단 근거를 metric 또는 info 박스로 표시
```

이렇게 하면 “입력/PDF 처리 담당”에서 단순 추출만 한 게 아니라, 다음 단계인 AI 처리 방식 선택까지 넘겨주는 느낌이라 역할 완성도가 좋아져.

> 어차피 MVP 라서 None 으로 둬도 될것같은데 음 근데 llm이랑 vlm을 같이 사용했을때 어쨌든 최종 결과물이 하나로 나와야하는데 그러면 음 어떻게 해야하지

맞아. **LLM이랑 VLM을 같이 써도 최종 결과물은 하나로 합쳐야 해.**

제일 깔끔한 구조는 이거야:

```text
PDF 입력
  |
  +-> 텍스트 추출
  |     -> LLM 요약
  |
  +-> 이미지 추출
        -> VLM 이미지 분석
              |
              v
      LLM이 최종 통합 정리
              |
              v
      하나의 JSON 결과
              |
              v
      HTML 카드 / PDF 출력
```

즉, LLM 결과와 VLM 결과를 따로 보여주는 게 아니라, **마지막에 한 번 더 합치는 단계**를 두는 거야.

예를 들면:

```text
LLM 결과:
- 텍스트 기반 핵심 개념
- 정의
- 시험 포인트
- 복습 질문

VLM 결과:
- 슬라이드 구조
- 그림/표/도식 설명
- 텍스트 추출에서 빠진 시각 정보
```

이걸 최종 통합 LLM에게 이렇게 넘김:

```text
아래는 텍스트 기반 요약과 이미지 기반 분석 결과이다.
중복 내용은 합치고, 빠진 시각 정보는 보완해서
최종 강의 필기 JSON 하나로 만들어라.
```

최종 결과는 항상 이런 하나의 형태로 고정하면 됨:

```json
{
  "title": "강의 제목",
  "summary": ["핵심 요약 1", "핵심 요약 2"],
  "key_concepts": ["개념 1", "개념 2"],
  "visual_notes": ["이미지/도표 설명"],
  "exam_points": ["시험 포인트"],
  "review_questions": ["복습 질문"]
}
```

MVP 기준으로는 이렇게 가는 게 좋아 보여:

```text
1. PDF에서 텍스트와 이미지를 둘 다 추출
2. 텍스트가 충분하면 LLM 요약을 메인으로 사용
3. 이미지 분석은 보조 정보로 사용
4. 마지막에 LLM이 두 결과를 하나의 JSON으로 통합
```

샘플 PDF 같은 경우는 텍스트 추출이 잘 되니까:

```text
LLM 메인 + VLM 보조
```

가 적합해.

그리고 `max_image_pages=None`은 MVP에서는 괜찮아. 지금 PDF가 7페이지라 부담이 작고, “전체 페이지를 이미지로도 처리 가능하다”는 걸 보여주기 좋아.

결론은 이거야:

```text
LLM과 VLM을 같이 써도 최종 산출물은 하나.
VLM은 이미지에서 놓친 정보를 보완하고,
LLM이 마지막에 전체 결과를 통합해서 JSON 하나로 만든다.
```

네 1번 파트는 여기까지 넘겨주면 돼:

```text
result.full_text
result.page_images
추천 처리 방식: LLM / VLM / LLM+VLM
```

그 다음 2번 담당이 이걸 받아서 요약하고, 3번 담당이 최종 JSON을 HTML/PDF로 보여주면 흐름이 자연스러워.

> 어쨌든 우리 담당에서 지금 코드 수정해야되는 것들이 뭐가 있지? 일단 None으로 바꾸는거랑

지금 네 담당 파트에서 수정하면 좋은 건 딱 이 정도야.

1. `max_image_pages=3`을 `None`으로 변경
PDF 전체 페이지를 이미지로 변환해서 VLM 입력으로 쓸 수 있게 하기.

```python
result = process_pdf_path(SAMPLE_PDF_PATH, max_image_pages=None)
```

```python
result = process_pdf(
    pdf_bytes,
    file_name=uploaded_file.name,
    max_image_pages=None,
)
```

2. LLM/VLM 추천 처리 방식 출력 추가
Streamlit 화면에 이런 식으로 보여주기.

```text
추천 처리 방식: LLM 우선
판단 근거: 텍스트가 충분히 추출되어 LLM 요약에 적합합니다.
보조 권장: 슬라이드 이미지/도표 분석이 필요하면 VLM을 함께 사용하세요.
```

3. 판단 함수 추가
`pdf_loader.py`에 처리 방식을 판단하는 함수 하나 추가하면 좋아.

예상 형태:

```python
def recommend_ai_mode(result: PdfExtractResult) -> dict:
    ...
```

출력 예시:

```python
{
    "mode": "LLM 우선",
    "reason": "페이지당 평균 텍스트가 충분히 추출되었습니다.",
    "use_llm": True,
    "use_vlm": False,
    "average_chars_per_page": 318
}
```

4. `PdfExtractResult`에 평균 글자 수 또는 추천 정보 추가
지금은 `needs_image_analysis`만 있음. 여기에 조금 더 설명 가능한 값이 있으면 Streamlit에서 보기 좋아.

예:

```text
평균 페이지 글자 수
추천 API
판단 근거
```

5. Streamlit 화면에 추천 결과 표시
현재 metric은 이거잖아.

```text
파일명 / PDF 페이지 / 추출 글자 수 / 이미지 분석 필요
```

여기에 하나 더 추가하거나 `st.info()`로 아래처럼 출력.

```text
AI 처리 추천: LLM 우선
평균 페이지 글자 수: 318자
이 PDF는 텍스트 추출이 충분하므로 LLM 요약에 적합합니다.
```

6. 문서 업데이트
`PDF_PROCESSING_PIPELINE.md`에 다음 내용 추가.

```text
MVP에서는 전체 페이지 이미지를 변환한다.
LLM/VLM 추천 판단 기준을 Streamlit에서 출력한다.
최종 통합은 2번 담당 요약 모듈에서 하나의 JSON으로 합친다.
```

그래서 최소 수정 목록은:

```text
필수
1. max_image_pages=None 변경
2. LLM/VLM 추천 판단 출력 추가

하면 좋은 것
3. 추천 판단 함수 분리
4. 평균 페이지 글자 수 표시
5. 문서 업데이트
```

내 기준으로는 **1, 2, 3, 5번은 하는 게 좋아**.
그러면 네 파트가 단순 “PDF 읽기”가 아니라 “AI 처리 모듈에 넘길 입력을 판단해서 준비하는 파트”가 돼서 훨씬 탄탄해 보여.

> 반영해줘

<details><summary>7 previous messages</summary>

> 반영하겠습니다. 이번 수정은 `max_image_pages=None`으로 전체 페이지 이미지를 만들고, PDF 처리 결과에 “LLM/VLM 추천 방식 + 판단 근거”를 함께 담아서 Streamlit에 보여주는 쪽으로 잡을게요.
>
> 구조를 확인했고, 수정 지점은 `pdf_loader.py`의 결과 모델/판단 함수, `app.py`의 전체 이미지 변환과 추천 출력, `sample_test.py`의 기대값, 문서 업데이트입니다. 이제 코드에 반영하겠습니다.
>
> <details><summary>Edited 3 files</summary>
>
> - Wrote `./app.py` (+12 -4)
> - Wrote `./pdf_loader.py` (+77 -0)
> - Wrote `./sample_test.py` (+7 -2)
>
> </details>
>
> 코드 쪽은 반영됐습니다. 이제 설명 문서도 현재 동작과 맞게 `전체 페이지 이미지 변환`, `AI 추천 방식 출력`, `최종 통합 JSON` 내용으로 업데이트하겠습니다.
>
> <details><summary>Edited a file</summary>
>
> - Wrote `./PDF_PROCESSING_PIPELINE.md` (+173 -22)
>
> </details>
>
> 문서까지 업데이트했습니다. 이제 Conda 환경으로 문법 검사와 샘플 테스트를 돌려서, 전체 페이지 이미지 변환과 추천 방식 출력이 실제로 맞는지 확인하겠습니다.
>
> 테스트 결과도 의도대로 나왔습니다: 샘플 PDF는 7페이지 전체가 이미지로 변환됐고, 추천 방식은 `LLM 우선`으로 판단됐습니다. 마지막으로 문서/코드에 예전 `max_image_pages=3` 설명이 남아있는지 빠르게 확인하겠습니다.
</details>

반영 완료했어.

수정된 핵심은 이거야.

- [app.py](</c:/Users/ladde/Desktop/3_1_Semester/ai_base/기말프로젝트/app.py>)
  - `max_image_pages=3` → `max_image_pages=None`
  - 이제 PDF **전체 페이지를 이미지로 변환**
  - Streamlit 화면에 `추천 방식`, `평균 글자 수`, `LLM/VLM 사용 판단 근거` 출력

- [pdf_loader.py](</c:/Users/ladde/Desktop/3_1_Semester/ai_base/기말프로젝트/pdf_loader.py>)
  - `AiModeRecommendation` 추가
  - `recommend_ai_mode()` 추가
  - PDF 텍스트 추출량을 보고 `LLM 우선 / VLM 우선 / LLM+VLM 혼합` 판단

- [sample_test.py](</c:/Users/ladde/Desktop/3_1_Semester/ai_base/기말프로젝트/sample_test.py>)
  - 전체 페이지 이미지 변환 기준으로 테스트 수정
  - 추천 방식이 `LLM 우선`인지도 검사

- [PDF_PROCESSING_PIPELINE.md](</c:/Users/ladde/Desktop/3_1_Semester/ai_base/기말프로젝트/PDF_PROCESSING_PIPELINE.md>)
  - 전체 파이프라인 문서도 현재 코드 기준으로 업데이트

테스트 결과도 통과했어.

```text
샘플 PDF 테스트 성공
- 파일명: 인공지능개론_기말.pdf
- 페이지 수: 7
- 추출 글자 수: 2230
- 변환 이미지 수: 7
- 추천 방식: LLM 우선
- 판단 근거: 페이지당 평균 텍스트가 317자로 충분히 추출되어 텍스트 기반 요약에 적합합니다.
```

이제 실행은 그대로 이거 하면 돼.

```powershell
.\.conda\python.exe -m streamlit run app.py
```

> 음 코드 실행하면 무조건 저 pdf 파일이 업로드 되는것같은데 처음에 업로드 아무것도 안되어있는걸로 했으면 좋겠는데

<details><summary>3 previous messages</summary>

> 맞아, 지금은 샘플 PDF가 있으면 체크박스가 기본으로 켜져서 자동 업로드처럼 보입니다. 초기 화면은 비어 있고, 사용자가 직접 업로드하거나 샘플 테스트 체크를 눌렀을 때만 처리되도록 바꾸겠습니다.
>
> <details><summary>Edited a file</summary>
>
> - Wrote `./app.py` (+1 -1)
>
> </details>
>
> 초기 체크 상태를 꺼두도록 수정했습니다. 이제 문법만 빠르게 확인해서 앱 파일이 깨지지 않았는지 보겠습니다.
</details>

수정했어.

이제 `app.py` 실행하면 처음에는 아무 PDF도 처리하지 않고, 화면에 업로드 안내만 떠.

```text
PDF, PNG, JPG 강의자료를 업로드하세요.
```

샘플 PDF를 쓰고 싶을 때만 사용자가 직접 `샘플 강의자료로 테스트` 체크하면 처리돼.

바뀐 부분은 [app.py](</c:/Users/ladde/Desktop/3_1_Semester/ai_base/기말프로젝트/app.py>) 여기야:

```python
use_sample = st.checkbox(
    "샘플 강의자료로 테스트",
    value=False,
    disabled=uploaded_file is not None or not SAMPLE_PDF_PATH.exists(),
)
```

문법 검사도 통과했어.

> ㄴㄴ 샘플 강의자료 테스트 자체가 없었으면 좋겠음 그 버튼 없애고 기능도 없애 그냥 무조건 유저가 새로 파일 업로드하는걸로

<details><summary>10 previous messages</summary>

> 알겠어. 앱에서는 샘플 테스트 흐름을 완전히 빼고, 무조건 사용자가 파일을 업로드해야만 처리되게 바꾸겠습니다. `sample_test.py`는 개발 검증용 파일이라 앱 기능은 아니지만, 문서와 화면에서는 샘플 테스트 버튼/기능이 안 보이게 정리할게요.
>
> 먼저 Streamlit 앱에서 샘플 관련 import, 경로, 체크박스, 분기 처리를 제거하겠습니다. 처리 흐름은 `업로드 없음 -> 안내 후 stop`, `업로드 있음 -> 해당 파일만 처리`로 단순해집니다.
>
> <details><summary>Edited a file</summary>
>
> - Wrote `./app.py` (+9 -25)
>
> </details>
>
> 이제 문서도 앱 기준으로 정리하겠습니다. 샘플 선택 흐름이 남아 있으면 헷갈리니까, Streamlit 실행 절차와 파이프라인 설명에서는 “사용자 업로드만 처리”로 바꾸겠습니다.
>
> 샘플 테스트 기능 자체가 헷갈릴 수 있어서, 제가 만든 `sample_test.py`도 제거하고 문서도 “업로드 파일만 처리” 기준으로 다시 정리하겠습니다. `pdf_loader.py`의 경로 처리 helper는 앱에서 쓰지 않는 일반 유틸로만 남겨두고 주석도 샘플 표현 없이 바꿀게요.
>
> <details><summary>Created a file, edited a file, deleted a file</summary>
>
> - Wrote `./PDF_PROCESSING_PIPELINE.md` (+470 -0)
> - Wrote `./pdf_loader.py` (+1 -1)
> - Deleted `./sample_test.py` (+0 -39)
>
> </details>
>
> 정리까지 반영했습니다. 이제 샘플 관련 문구가 앱/문서에 남아 있는지 확인하고, Conda 환경으로 문법 검사를 돌리겠습니다.
>
> 문서에는 “샘플 없음”을 설명하는 문장에만 샘플이라는 단어가 남아 있네요. 아예 그 표현도 빼서 더 깔끔하게 “자동 파일 로드 없음”으로 바꾸겠습니다.
>
> <details><summary>Edited a file</summary>
>
> - Wrote `./PDF_PROCESSING_PIPELINE.md` (+2 -2)
>
> </details>
>
> 마지막으로 샘플 관련 흔적이 남아 있지 않은지 한 번 더 확인하겠습니다.
</details>

반영했어. 이제 Streamlit 앱에는 **샘플 강의자료 테스트 버튼도 없고, 자동으로 PDF 불러오는 기능도 없어.**

이제 흐름은 완전히 이거야:

```text
앱 실행
-> 처음 화면은 비어 있음
-> 사용자가 직접 PDF/이미지 업로드
-> 업로드한 파일만 분석
```

수정한 것:

- [app.py](</c:/Users/ladde/Desktop/3_1_Semester/ai_base/기말프로젝트/app.py>)
  - 샘플 PDF 경로 제거
  - 샘플 체크박스 제거
  - 샘플 처리 분기 제거
  - 무조건 `uploaded_file`만 처리

- `sample_test.py`
  - 삭제함

- [PDF_PROCESSING_PIPELINE.md](</c:/Users/ladde/Desktop/3_1_Semester/ai_base/기말프로젝트/PDF_PROCESSING_PIPELINE.md>)
  - 사용자 업로드만 처리하는 기준으로 문서 다시 정리

문법 검사도 통과했어.

이제 실행은 이것만 쓰면 됨:

```powershell
.\.conda\python.exe -m streamlit run app.py
```

> 그리고 마크다운 파일에는 2번 담당과 3번 담당이 어떻게 했으면 좋을지 간단하게 써주고 그리고 지금 마크다운으로 코드 설명 너무 세세하게 보다는 코드를 읽거나 쓸줄 모르는 사람도 이해할 수 있도록 쉽고 간결하게 정리해서 써줬으면해 그리고 시스템 아키텍처(파이프라인) 그려주고

<details><summary>3 previous messages</summary>

> 문서는 발표/팀 공유용 톤으로 다시 정리하겠습니다. 코드 줄 단위 설명은 줄이고, “이 시스템이 뭘 하고 다음 담당자가 뭘 받으면 되는지”가 바로 보이게 바꿀게요.
>
> <details><summary>Created a file</summary>
>
> - Wrote `./PDF_PROCESSING_PIPELINE.md` (+286 -0)
>
> </details>
>
> 문서를 쉬운 설명 중심으로 다시 썼습니다. 이제 파일 내용이 정상적으로 잡혔는지, 예전처럼 너무 세세한 함수 설명이 남아 있지 않은지 확인하겠습니다.
</details>

마크다운 문서 다시 정리했어.

[PDF_PROCESSING_PIPELINE.md](</c:/Users/ladde/Desktop/3_1_Semester/ai_base/기말프로젝트/PDF_PROCESSING_PIPELINE.md>)

바꾼 방향은 이거야:

- 코드 줄 단위 설명 줄임
- 코드를 모르는 사람도 이해할 수 있게 쉬운 말로 정리
- 시스템 아키텍처 파이프라인 그림 추가
- 1번 담당 결과물이 뭔지 정리
- 2번 담당이 LLM/VLM API를 어떻게 받으면 좋을지 추가
- 3번 담당이 HTML/PDF 출력을 어떻게 하면 좋을지 추가
- 실행 방법도 간단하게 유지

문서 길이도 기존보다 훨씬 줄여서 발표/팀 공유용으로 보기 편하게 만들었어.

> 음 md 랑 python 파일 그리고 txt 파일만 깃헙에 보내면 되겠지?

응, 지금 네 담당 파트만 올리는 거면 **`.md`, `.py`, `.txt`만 보내면 충분해.**

올리면 되는 파일은 이거야:

```text
app.py
pdf_loader.py
requirements.txt
PDF_PROCESSING_PIPELINE.md
```

그리고 **안 올리는 게 좋은 것**:

```text
.conda/
__pycache__/
*.pyc
```

`인공지능개론_기말.pdf`는 상황 따라 달라.

- 팀원이 같은 샘플 PDF로 테스트해야 하면 올려도 됨
- 그냥 코드만 제출/공유하는 거면 안 올려도 됨
- 용량 크거나 강의자료 저작권 걱정 있으면 안 올리는 게 좋음

GitHub에 올릴 거면 `.gitignore`도 하나 있으면 좋아:

```text
.conda/
__pycache__/
*.pyc
.env
```

정리하면, 네 파트 제출용 최소 구성은:

```text
app.py
pdf_loader.py
requirements.txt
PDF_PROCESSING_PIPELINE.md
.gitignore
```

`.gitignore`는 있으면 깔끔하고, 없어도 코드 실행 자체에는 문제 없어.

> 커밋 메세지 뭐라 하지

이 정도가 제일 깔끔해:

```text
feat: add PDF upload and extraction pipeline
```

한국어로 하고 싶으면:

```text
feat: PDF 업로드 및 추출 파이프라인 추가
```

네가 한 작업이 좀 더 잘 드러나게 쓰면:

```text
feat: add PDF text/image extraction for AI input
```

내 추천은 이거:

```text
feat: add PDF text/image extraction pipeline
```

> github에 최종본 폴더 내의 코드들에 대해서 프로젝트 readme 작성해야하는데 이미 있는 READEME.md에 작성해줘 그리고 시연 영상 1분짜리 넣을 예정이긴한데  아직 영상은 없어서 칸만 만들어주고 링크는 빼놓아 그리고 마지막엔 팀원별 역할이랑 기여도 적을 예정이야 팀원은 왕혜영, 이윤수, 장지연이고 일단 3열짜리 table에 헤더는 이름, 역할, 기여도 로 해줘

<details><summary>5 previous messages</summary>

> 좋아요. 먼저 현재 폴더에 README 파일이 정확히 어떤 이름으로 있는지 확인하고, 기존 내용이 있으면 그 위에 맞춰서 최종 프로젝트 README 형태로 정리하겠습니다.
>
> 확인해보니 루트의 `README.md`가 비어 있고, 실제 최종 코드는 `최종본/` 폴더에 모여 있네요. 그 폴더의 앱 구조를 읽고 README를 그 기준으로 작성하겠습니다.
>
> README는 GitHub 첫 화면용이라 너무 길지 않게, “무슨 프로젝트인지, 어떻게 실행하는지, 최종본 폴더 구조가 뭔지”가 바로 보이도록 작성하겠습니다. 시연 영상은 자리만 만들고 링크는 비워둘게요.
>
> <details><summary>Edited a file</summary>
>
> - Wrote `./README.md` (+208 -0)
>
> </details>
>
> README를 작성했습니다. 마지막으로 헤더와 팀원 표, 시연 영상 자리, 최종본 폴더 설명이 들어갔는지 확인하겠습니다.
</details>

README.md 작성해뒀어.

[README.md](</c:/Users/ladde/Desktop/3_1_Semester/ai_base/기말프로젝트/README.md>)

넣은 내용은:

- 프로젝트 소개
- 주요 기능
- 시스템 아키텍처 파이프라인
- `최종본/` 폴더 구조
- 파일별 역할
- 실행 방법
- API 키 설정 방법
- 사용 흐름
- 시연 영상 자리만 생성, 링크 없음
- 사용 기술
- 팀원별 역할/기여도 3열 테이블

팀원 표는 요청한 대로 이렇게 넣어뒀어:

```markdown
| 이름 | 역할 | 기여도 |
|---|---|---|
| 왕혜영 | 작성 예정 | 작성 예정 |
| 이윤수 | 작성 예정 | 작성 예정 |
| 장지연 | 작성 예정 | 작성 예정 |
```

> 근데 우리 README badge  쓸거 없나

있어. README 상단에 붙이면 좋은 건 이 정도가 딱 적당해.

```markdown
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Claude API](https://img.shields.io/badge/Claude_API-Anthropic-111111?style=flat-square)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-PDF_Processing-0C7BDC?style=flat-square)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF_Output-6A5ACD?style=flat-square)
![Status](https://img.shields.io/badge/Status-MVP-blue?style=flat-square)
```

README 제목 바로 아래에 넣으면 예뻐.

```markdown
# AI Lecture Notes

![Python](...)
![Streamlit](...)
...
```

지금 프로젝트에는 이 배지들이 잘 맞아:

```text
Python       -> 개발 언어
Streamlit    -> 웹 앱 프레임워크
Claude API   -> AI 요약
PyMuPDF      -> PDF 처리
ReportLab    -> PDF 출력
Status MVP   -> 최종 프로젝트 MVP
```

반대로 아직 안 쓰는 게 좋은 배지는:

```text
License      -> LICENSE 파일 없으면 애매함
Build Passing -> GitHub Actions 없으면 쓰면 안 됨
Version      -> 릴리즈 태그 없으면 굳이 필요 없음
Coverage     -> 테스트 커버리지 없으면 쓰면 안 됨
```

> 넣어줘볼래?

<details><summary>4 previous messages</summary>

> 좋아요. README 제목 바로 아래에 현재 프로젝트 기술 스택에 맞는 배지만 깔끔하게 넣겠습니다. 없는 라이선스나 CI 배지는 안 넣고, 실제로 쓰는 기술 중심으로만 붙일게요.
>
> <details><summary>Edited a file</summary>
>
> - Wrote `./README.md` (+7 -0)
>
> </details>
>
> 배지를 넣었습니다. README 상단이 원하는 형태인지 빠르게 확인하겠습니다.
>
> <details><summary>Ran a command</summary>
>
> - Ran `rg -n "^#|badge|Python|Streamlit|Claude|PyMuPDF|ReportLab|Status" README.md`
>
> </details>
</details>

넣었어. README 상단이 이제 이렇게 시작해:

```markdown
# AI Lecture Notes

![Python](...)
![Streamlit](...)
![Claude API](...)
![PyMuPDF](...)
![ReportLab](...)
![Status](...)
```

추가한 배지는:

```text
Python 3.10+
Streamlit App
Claude API
PyMuPDF
ReportLab
Status MVP
```

없는 기능인 `License`, `Build Passing`, `Coverage` 같은 배지는 일부러 안 넣었어. 지금 프로젝트 상태랑 맞는 것만 넣어둔 게 깔끔해.
