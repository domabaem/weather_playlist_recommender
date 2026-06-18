# -*- coding: utf-8 -*-
"""Step 2 — Summarize : 강의 텍스트를 '블록 노트' JSON으로 요약한다.

기존에는 {섹션: ["한 줄", ...]} 형태의 고정 스키마만 만들어서
출력이 전부 '헤더 + 불릿' 으로만 나왔다. 이제는 내용 성격에 맞는
여러 블록 타입(chips/flow/compare/tree/definitions/qa/callout/text)을
AI가 직접 골라서 생성한다.

최종 노트 형태:
    {
      "title": "...", "subtitle": "...",
      "blocks": [ {"type": "...", ...}, ... ]
    }
output_page.py 가 이 blocks 를 타입별로 렌더링한다.
"""
from __future__ import annotations
import json, os, re, sys

# Windows UTF-8 강제
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
for _s in (sys.stdout, sys.stderr):
    if _s and hasattr(_s, "reconfigure"):
        try: _s.reconfigure(encoding="utf-8")
        except Exception: pass

from typing import List, Dict, Any
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import inject_css, hero, steps_indicator, info_bar

st.set_page_config(page_title="AI Summarize", layout="wide", page_icon=None)
inject_css()

pdf_result = st.session_state.get("pdf_result", None)
file_name  = st.session_state.get("file_name", "")

hero(
    "Summarize Lecture",
    "Claude가 강의 내용을 분석해 시각 블록 노트로 정리합니다.",
    eyebrow="Step 2 — Summarize",
)
steps_indicator(2)

if pdf_result is None:
    st.markdown('<div class="card"><p style="color:#555;margin:0;">강의자료를 먼저 업로드해주세요.</p></div>', unsafe_allow_html=True)
    if st.button("Upload으로 돌아가기", type="primary"):
        st.switch_page("app.py")
    st.stop()

info_bar(file_name, pdf_result.page_count, pdf_result.ai_mode.mode)

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL   = "claude-sonnet-4-6"

# ─────────────────────────────────────────────────────────────────────────────
# 블록 타입 정의 (UI 선택 + 프롬프트 설명용)
#   key, 라벨, 기본 ON, 프롬프트 설명
# ─────────────────────────────────────────────────────────────────────────────
BLOCK_TYPES = [
    ("chips",       "핵심 개념(태그)", True,
     '핵심 용어/키워드를 정의 없이 단어만 나열. {"type":"chips","title":"핵심 개념","items":["뉴런","시냅스"]}'),
    ("text",        "일반 필기",       True,
     '불릿 필기. 중요한 항목은 emphasis로 강조(star/wavy/highlight/underline, 블록당 1~2개만). '
     '{"type":"text","title":"개요","items":[{"text":"내용","emphasis":"none"},{"text":"중요","emphasis":"star"}]}'),
    ("definitions", "용어 정의",       True,
     '용어와 한 줄 정의를 쌍으로. {"type":"definitions","title":"용어 정리","items":[{"term":"활동전위","desc":"막전위가 역치를 넘어 역전"}]}'),
    ("flow",        "과정/흐름",       True,
     '순서·절차를 단계로(화살표로 이어짐). {"type":"flow","title":"반사 경로","steps":["자극","수용기","중추","반응기"]}'),
    ("compare",     "비교표",          True,
     '2~3개 대상을 컬럼으로 대조. {"type":"compare","title":"비교","columns":[{"head":"중추","items":["뇌·척수"]},{"head":"말초","items":["체성·자율"]}]}'),
    ("tree",        "분류 트리",       True,
     '계층/분류 구조. {"type":"tree","title":"분류","root":"신경계","nodes":[{"label":"중추","children":["뇌","척수"]}]}'),
    ("callout",     "시험 포인트/팁",  True,
     '짧은 강조 노트. variant=exam(시험)/tip(팁)/warn(주의)/note. {"type":"callout","title":"시험","variant":"exam","items":["출제 단골 포인트"]}'),
    ("qa",          "예상 질문(Q&A)", True,
     '예상 문제와 답. {"type":"qa","title":"핵심 질문","items":[{"q":"분극과 탈분극의 차이?","a":"분극 -70mV 안정, 탈분극 Na+ 유입"}]}'),
    ("table",       "표",             True,
     '행/열 데이터 표. {"type":"table","title":"연산 정리","headers":["연산","조건","결과"],"rows":[["덧셈","같은 크기","원소별 합"]]}'),
    ("steps",       "번호 단계",       True,
     '순서가 있는 절차(번호). {"type":"steps","title":"풀이 절차","items":["증대행렬 구성","피벗 아래 0","후진대입"]}'),
    ("timeline",    "타임라인",        True,
     '시간/순서 축. {"type":"timeline","title":"학습 순서","items":[{"time":"1주차","desc":"기초"},{"time":"2주차","desc":"심화"}]}'),
    ("pros_cons",   "장점/단점",       True,
     '장단점 대조. {"type":"pros_cons","title":"방법 비교","pros":["안정적","빠름"],"cons":["번거로움"]}'),
    ("bar_chart",   "막대그래프",      True,
     '수치 비교 막대. value는 숫자. {"type":"bar_chart","title":"연산량","items":[{"label":"A","value":33},{"label":"B","value":100}]}'),
    ("quadrant",    "2×2 매트릭스",    True,
     '4분면 분류(SWOT 등). {"type":"quadrant","title":"분류","cells":[{"label":"강점","items":["..."]},{"label":"약점","items":["..."]},{"label":"기회","items":["..."]},{"label":"위협","items":["..."]}]}'),
    ("cycle",       "순환도",          True,
     '순환·반복 과정. {"type":"cycle","title":"피드백 사이클","steps":["입력","처리","평가","갱신"]}'),
    ("formula",     "수식",            True,
     '수식과 의미. {"type":"formula","title":"핵심 수식","items":[{"expr":"x = A⁻¹b","desc":"선형계의 유일해"}]}'),
]
TYPE_LABEL = {k: lab for k, lab, *_ in BLOCK_TYPES}
VALID_EMPH = {"none", "star", "wavy", "highlight", "underline"}
VALID_VARIANT = {"exam", "tip", "warn", "note", "info"}

# ─────────────────────────────────────────────────────────────────────────────
# 관용 정규화 : 모델이 blocks/sections, type/kind, title/heading 등 어떤 키로
# 응답하든 표준 블록 스키마로 흡수한다. (스키마 드리프트 방어의 핵심)
# ─────────────────────────────────────────────────────────────────────────────
KIND_MAP = {
    "exam_points": ("callout", "exam"), "exam": ("callout", "exam"),
    "test_points": ("callout", "exam"), "출제포인트": ("callout", "exam"),
    "시험": ("callout", "exam"), "시험포인트": ("callout", "exam"),
    "tip": ("callout", "tip"), "tips": ("callout", "tip"), "팁": ("callout", "tip"),
    "warn": ("callout", "warn"), "warning": ("callout", "warn"),
    "caution": ("callout", "warn"), "주의": ("callout", "warn"),
    "callout": ("callout", None), "info": ("callout", "info"),
    "key_concepts": ("chips", None), "concepts": ("chips", None),
    "keywords": ("chips", None), "key_terms": ("chips", None),
    "tags": ("chips", None), "chips": ("chips", None), "핵심개념": ("chips", None),
    "definitions": ("definitions", None), "terms": ("definitions", None),
    "glossary": ("definitions", None), "용어": ("definitions", None), "용어정의": ("definitions", None),
    "flow": ("flow", None), "process": ("flow", None), "steps": ("flow", None),
    "sequence": ("flow", None), "procedure": ("flow", None),
    "흐름": ("flow", None), "과정": ("flow", None), "절차": ("flow", None),
    "compare": ("compare", None), "comparison": ("compare", None),
    "vs": ("compare", None), "비교": ("compare", None),
    "tree": ("tree", None), "classification": ("tree", None),
    "hierarchy": ("tree", None), "taxonomy": ("tree", None),
    "분류": ("tree", None), "계층": ("tree", None),
    "qa": ("qa", None), "q&a": ("qa", None), "questions": ("qa", None),
    "review_questions": ("qa", None), "faq": ("qa", None),
    "질문": ("qa", None), "예상문제": ("qa", None), "복습질문": ("qa", None),
    "summary": ("text", None), "overview": ("text", None),
    "key_points": ("text", None), "points": ("text", None),
    "notes": ("text", None), "text": ("text", None), "mnemonics": ("text", None),
    "examples": ("text", None), "formulas": ("text", None), "visual_notes": ("text", None),
    "필기": ("text", None), "요약": ("text", None),
}
KIND_MAP.update({
    "table": ("table", None), "grid": ("table", None), "표": ("table", None),
    "steps": ("steps", None), "step": ("steps", None), "절차": ("steps", None),
    "순서": ("steps", None), "단계": ("steps", None),
    "timeline": ("timeline", None), "타임라인": ("timeline", None),
    "연표": ("timeline", None), "history": ("timeline", None),
    "pros_cons": ("pros_cons", None), "proscons": ("pros_cons", None), "장단점": ("pros_cons", None),
    "bar_chart": ("bar_chart", None), "bar": ("bar_chart", None), "barchart": ("bar_chart", None),
    "chart": ("bar_chart", None), "graph": ("bar_chart", None), "막대": ("bar_chart", None),
    "quadrant": ("quadrant", None), "matrix": ("quadrant", None), "swot": ("quadrant", None),
    "매트릭스": ("quadrant", None),
    "cycle": ("cycle", None), "loop": ("cycle", None), "circular": ("cycle", None), "순환": ("cycle", None),
    "formula": ("formula", None), "formulas": ("formula", None), "equation": ("formula", None),
    "수식": ("formula", None), "공식": ("formula", None),
})


def _first_list(d: dict, keys: List[str]) -> list:
    for k in keys:
        v = d.get(k)
        if isinstance(v, list) and v:
            return v
    return []


def _strings(lst: list) -> List[str]:
    out = []
    for x in lst:
        if isinstance(x, dict):
            x = x.get("text") or x.get("name") or x.get("term") or x.get("label") or ""
        s = str(x).strip()
        if s:
            out.append(s)
    return out


def _canon_type(block: dict):
    raw = str(block.get("type") or block.get("kind") or block.get("category") or "").lower().strip()
    if raw in KIND_MAP:
        return KIND_MAP[raw]
    for key, val in KIND_MAP.items():
        if key in raw:
            return val
    return ("text", None)


def coerce_blocks(data: Any) -> Dict[str, Any]:
    """어떤 변형 스키마든 {title, subtitle, blocks:[표준블록]} 으로 변환."""
    if not isinstance(data, dict):
        return {"title": "강의 노트", "subtitle": "", "blocks": []}
    title = str(data.get("title") or data.get("name") or "강의 노트").strip()
    subtitle = str(data.get("subtitle") or data.get("description") or "").strip()
    raw_blocks = _first_list(data, ["blocks", "sections", "items", "content", "groups"])
    blocks: List[Dict[str, Any]] = []

    for b in raw_blocks:
        if not isinstance(b, dict):
            s = str(b).strip()
            if s:
                blocks.append({"type": "text", "title": "",
                               "items": [{"text": s, "emphasis": "none"}]})
            continue
        typ, forced_variant = _canon_type(b)
        title_b = str(b.get("title") or b.get("heading") or b.get("label") or b.get("name") or "").strip()
        blk: Dict[str, Any] = {"type": typ, "title": title_b}

        if typ == "chips":
            items = _strings(_first_list(b, ["items", "keywords", "terms", "list", "concepts", "tags"]))
            if not items:
                continue
            blk["items"] = items[:14]
        elif typ == "flow":
            steps = _strings(_first_list(b, ["steps", "items", "sequence", "list", "stages"]))
            if len(steps) < 2:
                continue
            blk["steps"] = steps[:10]
        elif typ == "definitions":
            items = []
            for i in _first_list(b, ["items", "terms", "list", "definitions"]):
                if isinstance(i, dict):
                    term = str(i.get("term") or i.get("name") or i.get("word") or i.get("title") or "").strip()
                    desc = str(i.get("desc") or i.get("definition") or i.get("meaning")
                               or i.get("explanation") or i.get("description") or "").strip()
                else:
                    s = str(i)
                    sep = "—" if "—" in s else (":" if ":" in s else "-")
                    term, _, desc = s.partition(sep)
                    term, desc = term.strip(), desc.strip()
                if term:
                    items.append({"term": term[:24], "desc": desc})
            if not items:
                continue
            blk["items"] = items[:10]
        elif typ == "compare":
            raw_cols = _first_list(b, ["columns", "cols", "sides", "groups"])
            if not raw_cols:
                for a, bkey in (("left", "right"), ("a", "b"), ("first", "second")):
                    if isinstance(b.get(a), dict) and isinstance(b.get(bkey), dict):
                        raw_cols = [b[a], b[bkey]]; break
            cols = []
            for c in raw_cols:
                if not isinstance(c, dict):
                    continue
                head = str(c.get("head") or c.get("title") or c.get("name") or c.get("label") or "").strip()
                citems = _strings(_first_list(c, ["items", "points", "list", "content"]))
                if head:
                    cols.append({"head": head[:18], "items": citems[:6]})
            if len(cols) < 2:
                continue
            blk["columns"] = cols[:3]
        elif typ == "tree":
            nodes = []
            for n in _first_list(b, ["nodes", "children", "items", "branches"]):
                if isinstance(n, dict):
                    lab = str(n.get("label") or n.get("name") or n.get("title") or "").strip()
                    ch = _strings(_first_list(n, ["children", "items", "sub", "nodes"]))
                    if lab:
                        nodes.append({"label": lab, "children": ch[:6]})
                elif str(n).strip():
                    nodes.append({"label": str(n).strip(), "children": []})
            if not nodes:
                continue
            blk["root"] = str(b.get("root") or b.get("name") or title_b or "").strip()
            blk["nodes"] = nodes[:8]
        elif typ == "qa":
            items = []
            for i in _first_list(b, ["items", "questions", "list", "qas"]):
                if isinstance(i, dict):
                    q = str(i.get("q") or i.get("question") or i.get("Q") or "").strip()
                    a = str(i.get("a") or i.get("answer") or i.get("A") or "").strip()
                    if q:
                        items.append({"q": q, "a": a})
                elif str(i).strip():
                    items.append({"q": str(i).strip(), "a": ""})
            if not items:
                continue
            blk["items"] = items[:6]
        elif typ == "callout":
            items = _strings(_first_list(b, ["items", "points", "list", "content", "lines"]))
            if not items:
                continue
            var = forced_variant or str(b.get("variant") or "note").lower().strip()
            blk["variant"] = var if var in VALID_VARIANT else "note"
            blk["items"] = items[:5]
        elif typ == "table":
            headers = _strings(_first_list(b, ["headers", "header", "columns", "cols"]))
            rows = []
            for r in _first_list(b, ["rows", "data", "items"]):
                if isinstance(r, (list, tuple)):
                    rows.append([str(x).strip() for x in r])
                elif isinstance(r, dict):
                    rows.append([str(v).strip() for v in r.values()])
            if not rows and not headers:
                continue
            blk["headers"] = headers[:5]
            blk["rows"] = [row[:5] for row in rows[:10]]
        elif typ == "steps":
            steps = _strings(_first_list(b, ["items", "steps", "list"]))
            if len(steps) < 2:
                continue
            blk["items"] = steps[:8]
        elif typ == "timeline":
            items = []
            for i in _first_list(b, ["items", "events", "list"]):
                if isinstance(i, dict):
                    tm = str(i.get("time") or i.get("date") or i.get("label") or "").strip()
                    ds = str(i.get("desc") or i.get("text") or i.get("event") or "").strip()
                else:
                    s = str(i); sep = ":" if ":" in s else "—"
                    tm, _, ds = s.partition(sep); tm, ds = tm.strip(), ds.strip()
                    if not ds:
                        tm, ds = "", s.strip()
                if tm or ds:
                    items.append({"time": tm, "desc": ds})
            if not items:
                continue
            blk["items"] = items[:8]
        elif typ == "pros_cons":
            pros = _strings(_first_list(b, ["pros", "advantages", "good", "장점", "merits"]))
            cons = _strings(_first_list(b, ["cons", "disadvantages", "bad", "단점", "demerits"]))
            if not pros and not cons:
                continue
            blk["pros"] = pros[:6]; blk["cons"] = cons[:6]
        elif typ == "bar_chart":
            items = []
            for i in _first_list(b, ["items", "data", "bars", "values"]):
                if isinstance(i, dict):
                    lab = str(i.get("label") or i.get("name") or "").strip()
                    raw = str(i.get("value", i.get("val", ""))).replace(",", "").strip()
                    try:
                        val = float(raw)
                    except Exception:
                        val = None
                    if lab and val is not None:
                        items.append({"label": lab, "value": val})
            if len(items) < 2:
                continue
            blk["items"] = items[:8]
        elif typ == "quadrant":
            cells = []
            for cspec in _first_list(b, ["cells", "quadrants", "items", "groups"]):
                if isinstance(cspec, dict):
                    lab = str(cspec.get("label") or cspec.get("title") or cspec.get("name") or "").strip()
                    citems = _strings(_first_list(cspec, ["items", "points", "list"]))
                    cells.append({"label": lab, "items": citems[:4]})
            if len(cells) < 2:
                continue
            blk["cells"] = cells[:4]
        elif typ == "cycle":
            steps = _strings(_first_list(b, ["steps", "items", "stages", "list"]))
            if len(steps) < 2:
                continue
            blk["steps"] = steps[:6]
        elif typ == "formula":
            items = []
            for i in _first_list(b, ["items", "formulas", "list"]):
                if isinstance(i, dict):
                    expr = str(i.get("expr") or i.get("formula") or i.get("text") or "").strip()
                    desc = str(i.get("desc") or i.get("meaning") or i.get("description") or "").strip()
                else:
                    s = str(i); sep = ":" if ":" in s else "—"
                    expr, _, desc = s.partition(sep); expr, desc = expr.strip(), desc.strip()
                if expr:
                    items.append({"expr": expr, "desc": desc})
            if not items:
                continue
            blk["items"] = items[:6]
        else:  # text
            items = []
            for i in _first_list(b, ["items", "points", "content", "lines", "bullets", "list"]):
                if isinstance(i, dict):
                    txt = str(i.get("text") or i.get("content") or i.get("point") or "").strip()
                    emph = str(i.get("emphasis") or i.get("highlight") or "none").lower().strip()
                    emph = emph if emph in VALID_EMPH else "none"
                else:
                    txt, emph = str(i).strip(), "none"
                if txt:
                    items.append({"text": txt, "emphasis": emph})
            if not items:
                continue
            blk["type"] = "text"
            blk["items"] = items[:8]
        blocks.append(blk)

    return {"title": title or "강의 노트", "subtitle": subtitle, "blocks": blocks}


def split_text(text: str, chunk_size: int) -> List[str]:
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def _schema_doc(allowed: List[str]) -> str:
    lines = []
    for k, lab, _on, desc in BLOCK_TYPES:
        if k in allowed:
            lines.append(f'  - {k} ({lab}): {desc}')
    return "\n".join(lines)


COMMON_RULES = """규칙:
- 최상위 배열 키는 반드시 "blocks", 각 블록의 종류 키는 반드시 "type" 를 사용하라.
  ("sections", "kind", "heading" 같은 다른 키 이름은 절대 쓰지 마라.)
- 내용 성격에 가장 맞는 블록 타입을 선택하라.
  순서/과정→flow, 절차(번호)→steps, 핵심 용어 목록→chips, 용어+정의→definitions,
  두 대상 대조→compare, 장단점→pros_cons, 계층/분류→tree, 4분면 분류→quadrant,
  시간·순서 변화→timeline, 순환/반복→cycle, 수치 비교→bar_chart, 수식→formula,
  행/열 데이터→table, 출제 포인트→callout(exam), 예상문제→qa.
- 다양한 블록 타입을 고루 섞어라. 한 종류의 블록을 남발하지 말고
  같은 type 은 최대 2개까지만 사용하라(text 는 예외적으로 더 가능).
- 같은 내용을 여러 블록에 중복하지 마라.
- 모든 텍스트는 한 줄(약 40자 이내)로 간결하게.
- title 은 짧은 한국어 섹션명. subtitle 은 강의명/범위 한 줄(없으면 "").
- 허용된 블록 타입만 사용하라.
- 반드시 아래 JSON 객체 하나만 출력하라. 설명·마크다운·코드펜스(```), 다른 말 금지."""


def create_extract_prompt(text: str, allowed: List[str], requirements: str,
                          tone: str, language: str) -> str:
    extra = f"\n추가 요구사항: {requirements.strip()}" if requirements.strip() else ""
    tone_s = f"\n작성 톤: {tone}" if tone else ""
    lang_s = f"\n출력 언어: {language}" if language else ""
    return f"""너는 강의자료를 '시각 블록 노트'로 정리하는 AI다.
아래 강의 일부에서 핵심을 뽑아 블록 목록으로 만들어라.

사용 가능한 블록 타입:
{_schema_doc(allowed)}

{COMMON_RULES}{tone_s}{lang_s}{extra}

출력 형식:
{{"title": "강의 제목", "subtitle": "부제", "blocks": [ <블록>, ... ]}}

강의자료:
{text}"""


def create_consolidate_prompt(blocks_json: str, title: str, allowed: List[str],
                              requirements: str, tone: str, language: str,
                              density: str) -> str:
    extra = f"\n추가 요구사항: {requirements.strip()}" if requirements.strip() else ""
    tone_s = f"\n작성 톤: {tone}" if tone else ""
    lang_s = f"\n출력 언어: {language}" if language else ""
    dens = {
        "압축 (한 장)": "A4 한 장 분량으로 가장 중요한 것만. 블록 6~9개, 각 블록 항목 2~5개.",
        "표준":        "핵심 위주로 적당히. 블록 8~12개.",
        "풍부":        "빈틈없이 풍부하게. 블록 10~16개.",
    }.get(density, "A4 한 장 분량.")
    return f"""너는 여러 조각으로 추출된 강의 블록들을 최종 시험 대비 노트로 통합하는 AI다.
아래 블록들을 중복 제거·병합하고, 더 적절한 블록 타입으로 재구성하라.
(예: 흩어진 용어 단어들은 chips 로, 용어+설명은 definitions 로,
 순서가 있으면 flow 로, 두 대상 대조는 compare 로, 계층은 tree 로 묶어라.)
분량 가이드: {dens}

{COMMON_RULES}{tone_s}{lang_s}{extra}

출력 형식:
{{"title": "{title}", "subtitle": "부제", "blocks": [ <블록>, ... ]}}

통합할 블록들(JSON):
{blocks_json}"""


def _extract_objects(s: str, i: int) -> List[Dict[str, Any]]:
    """배열 시작 직후 위치 i 부터 완성된 {...} 객체들만 brace 매칭으로 추출.

    출력이 중간에 잘려 배열이 닫히지 않아도, 그 전까지 '완성된' 객체는 모두 건진다.
    """
    objs, n = [], len(s)
    while i < n:
        while i < n and s[i] != "{":
            if s[i] == "]":
                return objs
            i += 1
        if i >= n:
            break
        depth = 0; in_str = False; esc = False; start = i; complete = False
        while i < n:
            ch = s[i]
            if in_str:
                if esc: esc = False
                elif ch == "\\": esc = True
                elif ch == '"': in_str = False
            else:
                if ch == '"': in_str = True
                elif ch == "{": depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            objs.append(json.loads(s[start:i + 1]))
                        except Exception:
                            pass
                        i += 1; complete = True
                        break
            i += 1
        if not complete:        # 객체 도중에 끊김 → 더 건질 게 없음
            break
    return objs


def _salvage(s: str) -> Dict[str, Any]:
    """완전 파싱 실패(주로 max_tokens로 잘림) 시, 부분 복구."""
    out: Dict[str, Any] = {}
    mt = re.search(r'"title"\s*:\s*"([^"]*)"', s)
    ms = re.search(r'"subtitle"\s*:\s*"([^"]*)"', s)
    if mt: out["title"] = mt.group(1)
    if ms: out["subtitle"] = ms.group(1)
    ma = re.search(r'"(blocks|sections|items|groups|content)"\s*:\s*\[', s)
    out["blocks"] = _extract_objects(s, ma.end()) if ma else []
    return out


def _extract_json(text: str) -> Dict[str, Any]:
    """모델 출력에서 JSON 객체를 최대한 안전하게 추출(잘린 출력 복구 포함)."""
    s = (text or "").strip()
    if s.startswith("```"):
        s = s.split("```")[1]
        if s.lstrip().lower().startswith("json"):
            s = s.lstrip()[4:]
    s = s.strip()
    try:
        return json.loads(s)
    except Exception:
        pass
    # 본문 중 첫 { ... 마지막 } 추출 시도
    m = re.search(r"\{.*\}", s, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    # 잘린 출력: 완성된 블록만이라도 복구
    return _salvage(s)


def _flatten_to_text(b):
    """비허용 블록을 text 항목으로 평탄화(내용 보존)."""
    out = []
    for key in ("items", "steps", "pros", "cons"):
        for x in (b.get(key) or []):
            if isinstance(x, dict):
                v = (x.get("text") or x.get("term") or x.get("q") or x.get("expr")
                     or x.get("desc") or x.get("label"))
                if v:
                    out.append({"text": str(v), "emphasis": "none"})
            elif str(x).strip():
                out.append({"text": str(x).strip(), "emphasis": "none"})
    for r in (b.get("rows") or []):
        if isinstance(r, (list, tuple)):
            out.append({"text": " / ".join(str(c) for c in r), "emphasis": "none"})
    for col in (b.get("columns") or []) + (b.get("cells") or []):
        if isinstance(col, dict):
            head = col.get("head") or col.get("label") or ""
            for x in (col.get("items") or []):
                out.append({"text": (head + ": " + str(x)).strip(": "), "emphasis": "none"})
    return out[:8]


def validate_blocks(raw_blocks, allowed):
    """coerce_blocks 가 표준 형태로 만든 블록을 받아 허용 타입만 통과
    (비허용은 가능하면 text 로 강등해 내용 보존)."""
    out = []
    if not isinstance(raw_blocks, list):
        return out
    allow = set(allowed)
    for b in raw_blocks:
        if not isinstance(b, dict):
            continue
        typ = str(b.get("type", "text")).lower().strip()
        if typ in allow:
            out.append(b)
        elif "text" in allow:
            items = _flatten_to_text(b)
            if items:
                out.append({"type": "text",
                            "title": str(b.get("title", "")).strip(), "items": items})
    return out


# 한 종류의 블록 남발 방지: 타입별 최대 개수
DIVERSITY_CAP = {"text": 5, "callout": 3, "chips": 2}
DEFAULT_CAP = 2


def cap_diversity(blocks):
    seen = {}
    out = []
    for b in blocks:
        t = b.get("type", "text")
        lim = DIVERSITY_CAP.get(t, DEFAULT_CAP)
        if seen.get(t, 0) < lim:
            out.append(b)
            seen[t] = seen.get(t, 0) + 1
    return out


def run_summary(text, chunk_size, allowed, requirements, tone, language,
                density, progress_bar, status_text) -> Dict[str, Any]:
    from anthropic import Anthropic
    if not API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY 환경 변수가 설정되지 않았습니다.")
    client = Anthropic(api_key=API_KEY)
    chunks = split_text(text, chunk_size)

    title = (os.path.splitext(file_name)[0] or file_name) or "강의 노트"
    subtitle = ""
    collected: List[Dict[str, Any]] = []

    total_steps = len(chunks) + 1
    for idx, chunk in enumerate(chunks):
        status_text.markdown(
            f'<p style="color:#555;font-size:0.82rem;margin:0;">Reading {idx+1} / {len(chunks)}...</p>',
            unsafe_allow_html=True)
        progress_bar.progress((idx + 1) / total_steps)
        prompt = create_extract_prompt(chunk, allowed, requirements, tone, language)
        resp = client.messages.create(
            model=MODEL, max_tokens=8000,
            messages=[{"role": "user", "content": prompt}])
        coerced = coerce_blocks(_extract_json(resp.content[0].text))
        if idx == 0:
            title = (coerced["title"] or title).strip()
            subtitle = (coerced["subtitle"] or "").strip()
        collected.extend(validate_blocks(coerced["blocks"], allowed))

    # 통합·재구성
    status_text.markdown(
        '<p style="color:#555;font-size:0.82rem;margin:0;">한 장으로 정리하는 중...</p>',
        unsafe_allow_html=True)
    blocks_json = json.dumps(collected, ensure_ascii=False)
    if len(blocks_json) > 12000:        # 토큰 보호: 너무 길면 앞부분만
        blocks_json = blocks_json[:12000]
    cons_prompt = create_consolidate_prompt(
        blocks_json, title, allowed, requirements, tone, language, density)
    resp = client.messages.create(
        model=MODEL, max_tokens=8000,
        messages=[{"role": "user", "content": cons_prompt}])
    final = coerce_blocks(_extract_json(resp.content[0].text))
    progress_bar.progress(1.0)

    final_blocks = validate_blocks(final.get("blocks"), allowed)
    if not final_blocks:                # 통합 실패 시 1차 결과로 폴백
        final_blocks = collected
    final_blocks = cap_diversity(final_blocks)   # 한 종류 남발 방지
    if not final_blocks:                # 그것도 비면 원문 일부라도 표시(빈 노트 방지)
        snippet = (text or "").strip().replace("\n", " ")
        if snippet:
            chunks_txt = [snippet[i:i + 38] for i in range(0, min(len(snippet), 38 * 8), 38)]
            final_blocks = [{
                "type": "text", "title": "원문 발췌 (자동 요약 실패)",
                "items": [{"text": c, "emphasis": "none"} for c in chunks_txt],
            }]

    note = {
        "title": (final.get("title") or title).strip() or "강의 노트",
        "subtitle": (final.get("subtitle") or subtitle).strip(),
        "blocks": final_blocks,
        "_allowed": allowed,
    }
    return note


# ── UI ───────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">요구사항</p>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<p style="margin:0 0 10px;font-size:0.82rem;color:#444;">AI가 요약할 때 반영할 내용을 입력하세요. 비워두면 기본 방식으로 요약합니다.</p>', unsafe_allow_html=True)
requirements = st.text_area(
    "",
    placeholder="",
    height=100, label_visibility="collapsed",
)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<p class="section-title">출력 옵션</p>', unsafe_allow_html=True)
c_tone, c_lang, c_dens = st.columns(3)
with c_tone:
    tone = st.selectbox("작성 톤",
        ["기본 (간결·핵심)", "친근한 설명체", "교과서 문체", "시험 직전 압축형"], index=0)
with c_lang:
    language = st.selectbox("출력 언어",
        ["한국어", "English"], index=0)
with c_dens:
    density = st.selectbox("분량",
        ["압축 (한 장)", "표준", "풍부"], index=0,
        help="블록 개수/항목 수에 대한 힌트를 AI에 줍니다.")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<p class="section-title">사용할 블록 타입</p>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<p style="margin:0 0 10px;font-size:0.82rem;color:#444;">AI가 내용에 맞춰 아래 타입 중에서 골라 노트를 구성합니다.</p>', unsafe_allow_html=True)

allowed: List[str] = []
for row_start in range(0, len(BLOCK_TYPES), 4):
    cols = st.columns(4)
    for col, (k, lab, default_on, _desc) in zip(cols, BLOCK_TYPES[row_start:row_start + 4]):
        with col:
            if st.checkbox(lab, value=default_on, key=f"blk_{k}"):
                allowed.append(k)
st.markdown('</div>', unsafe_allow_html=True)

if not allowed:
    st.markdown('<div class="card"><p style="margin:0;color:#888;font-size:0.85rem;">적어도 하나 이상의 블록 타입을 선택해주세요.</p></div>', unsafe_allow_html=True)

chunk_size = 3000
st.markdown("<br>", unsafe_allow_html=True)

if st.button("요약 시작", type="primary", use_container_width=True, disabled=not allowed):
    try:
        progress_bar = st.progress(0)
        status_text  = st.empty()
        note = run_summary(
            pdf_result.full_text, chunk_size, allowed, requirements,
            tone, language, density, progress_bar, status_text)
        status_text.markdown('<p style="color:#888;font-size:0.82rem;margin:0;">완료</p>', unsafe_allow_html=True)
        st.session_state["lecture_note"] = note
        st.markdown(f'<div class="card"><p style="margin:0;color:#888;font-size:0.88rem;">요약 완료 — 블록 {len(note["blocks"])}개 생성됨.</p></div>', unsafe_allow_html=True)
        with st.expander("결과 미리보기 (JSON)"):
            st.json({k: v for k, v in note.items() if not k.startswith("_")})
    except Exception as e:
        st.markdown(f'<div class="card"><p style="margin:0;color:#888;font-size:0.85rem;">오류: {e}</p></div>', unsafe_allow_html=True)
        st.stop()

if st.session_state.get("lecture_note"):
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-title">다음 단계</p>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("노트 출력하기", type="primary", use_container_width=True):
            st.switch_page("pages/output_page.py")
    with col_b:
        if st.button("← 처음으로 돌아가기", use_container_width=True):
            st.switch_page("app.py")
