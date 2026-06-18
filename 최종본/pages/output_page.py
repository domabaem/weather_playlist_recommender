# -*- coding: utf-8 -*-
"""Step 3 — Export : 블록 기반 강의 노트를 테마별 PDF로 렌더링/다운로드.

요약 단계에서 만든 노트는 다음 형태다:
    {"title": ..., "subtitle": ..., "blocks": [ {"type": ...}, ... ]}
각 블록의 type 에 따라 칩/플로우/비교표/트리/용어카드/Q&A 등으로 그린다.
구버전(플랫 {섹션:[문자열]}) 노트도 normalize_note 가 자동 변환한다.
"""
from __future__ import annotations

import io
import os
import math
import urllib.request
from typing import List, Dict, Any

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Flowable, FrameBreak,
)
import streamlit as st

st.set_page_config(page_title="강의 노트 출력", layout="wide")

W, H = A4

# ── 폰트 (최초 1회 다운로드 후 등록) ──────────────────────────────────────────
FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")
os.makedirs(FONT_DIR, exist_ok=True)
FONT_URLS = {
    "NanumGothic.ttf":     "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf",
    "NanumGothicBold.ttf": "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf",
    "NanumPenScript.ttf":  "https://github.com/google/fonts/raw/main/ofl/nanumpenscript/NanumPenScript-Regular.ttf",
}

@st.cache_resource
def load_fonts():
    for fname, url in FONT_URLS.items():
        fpath = os.path.join(FONT_DIR, fname)
        if not os.path.exists(fpath):
            urllib.request.urlretrieve(url, fpath)
    pdfmetrics.registerFont(TTFont("NanumGothic",     os.path.join(FONT_DIR, "NanumGothic.ttf")))
    pdfmetrics.registerFont(TTFont("NanumGothicBold", os.path.join(FONT_DIR, "NanumGothicBold.ttf")))
    pdfmetrics.registerFont(TTFont("NanumPen",        os.path.join(FONT_DIR, "NanumPenScript.ttf")))
    return True

load_fonts()


# ── 테마 ──────────────────────────────────────────────────────────────────────
THEMES: Dict[str, Dict[str, Any]] = {
    "📓 노트": {
        "bg": colors.HexColor("#FDFAF3"), "line": colors.HexColor("#C8D8E8"),
        "margin": colors.HexColor("#F4A9A8"), "ink": colors.HexColor("#1C1C3A"),
        "ink2": colors.HexColor("#3D3D6B"), "panel": colors.HexColor("#FFFFFF"),
        "hl_yellow": colors.HexColor("#FFE066"), "hl_green": colors.HexColor("#B8F0B8"),
        "hl_pink": colors.HexColor("#FFB3C6"), "hl_blue": colors.HexColor("#B3D9FF"),
        "accent": [colors.HexColor("#C0392B"), colors.HexColor("#1A3A6B"),
                   colors.HexColor("#1A6B3A"), colors.HexColor("#5B2C8D")],
        "title_font": "NanumPen", "body_font": "NanumGothic",
        "bold_font": "NanumGothicBold", "style": "notebook", "bullet": "•",
    },
    "🌙 다크": {
        "bg": colors.HexColor("#1A1A2E"), "line": colors.HexColor("#2A2A4E"),
        "margin": colors.HexColor("#E94560"), "ink": colors.HexColor("#E0E0FF"),
        "ink2": colors.HexColor("#A0A0CC"), "panel": colors.HexColor("#23233E"),
        "hl_yellow": colors.HexColor("#FFD700"), "hl_green": colors.HexColor("#00FF88"),
        "hl_pink": colors.HexColor("#FF6B9D"), "hl_blue": colors.HexColor("#00BFFF"),
        "accent": [colors.HexColor("#E94560"), colors.HexColor("#4FC3F7"),
                   colors.HexColor("#69F0AE"), colors.HexColor("#CE93D8")],
        "title_font": "NanumPen", "body_font": "NanumGothic",
        "bold_font": "NanumGothicBold", "style": "dark", "bullet": "▸",
    },
    "🌸 파스텔": {
        "bg": colors.HexColor("#FFF0F5"), "line": colors.HexColor("#FFD6E7"),
        "margin": colors.HexColor("#C9B8FF"), "ink": colors.HexColor("#3D2B56"),
        "ink2": colors.HexColor("#7B5EA7"), "panel": colors.HexColor("#FFFFFF"),
        "hl_yellow": colors.HexColor("#FFF176"), "hl_green": colors.HexColor("#C8F7C5"),
        "hl_pink": colors.HexColor("#FFB3DE"), "hl_blue": colors.HexColor("#B3E5FC"),
        "accent": [colors.HexColor("#E91E8C"), colors.HexColor("#7B5EA7"),
                   colors.HexColor("#00838F"), colors.HexColor("#FF6F00")],
        "title_font": "NanumPen", "body_font": "NanumGothic",
        "bold_font": "NanumGothicBold", "style": "pastel", "bullet": "♥",
    },
    "📰 신문": {
        "bg": colors.HexColor("#F5F0E8"), "line": colors.HexColor("#C8B89A"),
        "margin": colors.HexColor("#8B0000"), "ink": colors.HexColor("#1A1008"),
        "ink2": colors.HexColor("#3D2B0A"), "panel": colors.HexColor("#FFFFFF"),
        "hl_yellow": colors.HexColor("#F5E642"), "hl_green": colors.HexColor("#8BC34A"),
        "hl_pink": colors.HexColor("#E91E63"), "hl_blue": colors.HexColor("#1565C0"),
        "accent": [colors.HexColor("#8B0000"), colors.HexColor("#1A1008"),
                   colors.HexColor("#5D4037"), colors.HexColor("#3E2723")],
        "title_font": "NanumGothicBold", "body_font": "NanumGothic",
        "bold_font": "NanumGothicBold", "style": "newspaper", "bullet": "■",
    },
}

WAVY_COLOR = colors.HexColor("#D7263D")


# ── 측정/줄바꿈 헬퍼 ──────────────────────────────────────────────────────────
def sw(text: str, font: str, size: float) -> float:
    try:
        return pdfmetrics.stringWidth(text, font, size)
    except Exception:
        return len(text) * size * 0.6


def wrap_to_width(text: str, font: str, size: float, max_w: float) -> List[str]:
    """한글/영문 혼용 텍스트를 폭 기준으로 줄바꿈. 공백 우선, 없으면 글자 단위."""
    text = str(text).strip()
    if not text:
        return [""]
    lines, cur = [], ""
    for ch in text:
        trial = cur + ch
        if sw(trial, font, size) <= max_w or not cur:
            cur = trial
        else:
            # 가능하면 마지막 공백에서 끊기
            sp = cur.rfind(" ")
            if sp > len(cur) * 0.5:
                lines.append(cur[:sp])
                cur = cur[sp + 1:] + ch
            else:
                lines.append(cur)
                cur = ch
    if cur:
        lines.append(cur)
    return lines or [""]


# ── 공통 베이스 블록 ──────────────────────────────────────────────────────────
class Block(Flowable):
    """모든 블록의 공통 베이스. 헤더(라벨 바) 그리기와 측정 유틸 제공.

    서브클래스는 다음을 구현/설정:
      - self._body_height() : 헤더를 제외한 본문 높이 계산
      - self._draw_body(c, top_y) : 본문 그리기 (top_y = 본문 영역 상단 y)
    """
    HEADER_H = 6.6 * mm
    HEADER_FONT = 12.5
    GAP_AFTER_HEADER = 2.1 * mm
    PAD_BOTTOM = 2.2 * mm
    OPAQUE_PANEL = False   # True면 블록 영역에 깨끗한 패널을 깔아 배경 줄/요소 관통 방지

    def __init__(self, label: str, accent, t: Dict[str, Any], TW: float,
                 acc_idx: int = 0, show_header: bool = True):
        super().__init__()
        self.label = label or ""
        self.accent = accent
        self.t = t
        self.TW = TW
        self.width = TW
        self.acc_idx = acc_idx
        self.show_header = show_header and bool(self.label)
        self.height = self._calc_height()

    # 서브클래스가 채움
    def _body_height(self) -> float:
        return 0.0

    def _draw_body(self, c, top_y: float):
        pass

    def _calc_height(self) -> float:
        head = (self.HEADER_H + self.GAP_AFTER_HEADER) if self.show_header else 0.0
        return head + self._body_height() + self.PAD_BOTTOM

    def _draw_header(self, c):
        t = self.t
        y_top = self.height
        if not self.show_header:
            return
        if t["style"] == "newspaper":
            c.setFillColor(self.accent)
            c.rect(0, y_top - self.HEADER_H, self.TW, self.HEADER_H, fill=1, stroke=0)
            c.setFont(t["bold_font"], self.HEADER_FONT - 2.5)
            c.setFillColor(colors.white)
            c.drawString(2.5 * mm, y_top - 4.6 * mm, self.label)
        else:
            c.saveState()
            c.setFillColor(self.accent); c.setFillAlpha(0.16)
            c.roundRect(0, y_top - self.HEADER_H, self.TW, self.HEADER_H, 2.2, fill=1, stroke=0)
            c.restoreState()
            c.setStrokeColor(self.accent); c.setLineWidth(2.4)
            c.line(0, y_top - self.HEADER_H, 0, y_top)
            c.setFont(t["title_font"], self.HEADER_FONT)
            c.setFillColor(self.accent)
            c.drawString(3.0 * mm, y_top - 4.7 * mm, self.label)

    def draw(self):
        c = self.canv
        if self.OPAQUE_PANEL:
            # 배경(노트 줄 등)이 차트를 관통하지 않도록 깨끗한 패널을 먼저 깐다
            c.saveState()
            c.setFillColor(self.t["bg"])
            c.rect(-0.6 * mm, -0.8 * mm, self.width + 1.2 * mm, self.height + 1.0 * mm,
                   fill=1, stroke=0)
            c.restoreState()
        self._draw_header(c)
        top = self.height - ((self.HEADER_H + self.GAP_AFTER_HEADER) if self.show_header else 0.0)
        self._draw_body(c, top)


# ── 1) TEXT : 불릿 + 강조 ─────────────────────────────────────────────────────
class TextBlock(Block):
    LS = 4.8 * mm
    FONT = 8.2

    def __init__(self, label, accent, t, TW, items, acc_idx=0, show_header=True):
        # items: list[str] 또는 list[{"text","emphasis"}]
        self.items = []
        for it in (items or []):
            if isinstance(it, dict):
                txt = str(it.get("text", "")).strip()
                emph = str(it.get("emphasis", "") or "").strip().lower()
            else:
                txt, emph = str(it).strip(), ""
            if txt:
                self.items.append((txt, emph))
        self._wrapped = None
        super().__init__(label, accent, t, TW, acc_idx, show_header)

    def _wrap_all(self):
        if self._wrapped is None:
            body_font = self.t["body_font"]
            max_w = self.TW - 6.5 * mm
            self._wrapped = [
                (txt, emph, wrap_to_width(txt, body_font, self.FONT, max_w))
                for txt, emph in self.items
            ]
        return self._wrapped

    def _body_height(self):
        lines = sum(len(w) for _, _, w in self._wrap_all())
        return max(lines, 1) * self.LS

    def _draw_body(self, c, top_y):
        t = self.t
        y = top_y - self.LS * 0.72
        for txt, emph, lines in self._wrap_all():
            line_h = len(lines) * self.LS
            # 형광펜
            if emph == "highlight":
                c.saveState()
                c.setFillColor(t["hl_yellow"]); c.setFillAlpha(0.42)
                c.roundRect(4.6 * mm, y - line_h + self.LS * 0.55, self.TW - 5 * mm,
                            line_h, 1.4, fill=1, stroke=0)
                c.restoreState()
            # 불릿 / 별표
            if emph == "star":
                c.setFont(t["body_font"], self.FONT + 1.2)
                c.setFillColor(self.accent)
                c.drawString(1.6 * mm, y, "★")
            else:
                c.setFont(t["body_font"], self.FONT - 1)
                c.setFillColor(self.accent)
                c.drawString(2.0 * mm, y, t["bullet"])
            # 본문
            c.setFillColor(t["ink"])
            c.setFont(t["body_font"], self.FONT)
            for j, ln in enumerate(lines):
                c.drawString(5.4 * mm, y - j * self.LS, ln)
            # 물결 밑줄
            if emph == "wavy":
                wy = y - (len(lines) - 1) * self.LS - 1.3
                tw = min(sw(lines[0], t["body_font"], self.FONT), self.TW - 7 * mm)
                _wavy(c, 5.4 * mm, wy, tw)
            # 일반 밑줄
            elif emph == "underline":
                uy = y - (len(lines) - 1) * self.LS - 1.0
                tw = min(sw(lines[-1], t["body_font"], self.FONT), self.TW - 7 * mm)
                c.setStrokeColor(self.accent); c.setLineWidth(0.6)
                c.line(5.4 * mm, uy, 5.4 * mm + tw, uy)
            y -= line_h


def _wavy(c, x0, y, width):
    if width <= 0:
        return
    c.saveState()
    c.setStrokeColor(WAVY_COLOR); c.setLineWidth(0.55)
    amp, period, spp = 0.55, 2.6, 6
    n = max(1, int(width / period))
    p = c.beginPath(); p.moveTo(x0, y)
    for s in range(1, n * spp + 1):
        frac = s / spp
        p.lineTo(x0 + frac * period, y + amp * math.sin(2 * math.pi * frac))
    c.drawPath(p, stroke=1, fill=0)
    c.restoreState()


# ── 2) CHIPS : 둥근 태그 그리드 ───────────────────────────────────────────────
class ChipsBlock(Block):
    OPAQUE_PANEL = True
    CHIP_H = 6.0 * mm
    CHIP_FONT = 7.6
    GAP_X = 1.8 * mm
    GAP_Y = 1.7 * mm
    PAD_X = 3.0 * mm

    def __init__(self, label, accent, t, TW, items, acc_idx=0, show_header=True):
        self.chips = [str(i).strip() for i in (items or []) if str(i).strip()]
        self._rows = None
        super().__init__(label, accent, t, TW, acc_idx, show_header)

    def _layout(self):
        if self._rows is not None:
            return self._rows
        font = self.t["body_font"]
        rows, cur, cur_w = [], [], 0.0
        for chip in self.chips:
            w = sw(chip, font, self.CHIP_FONT) + self.PAD_X * 2
            w = min(w, self.TW)
            if cur and cur_w + w + self.GAP_X > self.TW:
                rows.append(cur); cur, cur_w = [], 0.0
            cur.append((chip, w)); cur_w += w + self.GAP_X
        if cur:
            rows.append(cur)
        self._rows = rows
        return rows

    def _body_height(self):
        rows = self._layout()
        return max(len(rows), 1) * (self.CHIP_H + self.GAP_Y)

    def _draw_body(self, c, top_y):
        t = self.t
        y = top_y - self.CHIP_H
        for row in self._layout():
            x = 0.0
            for chip, w in row:
                c.saveState()
                c.setFillColor(self.accent); c.setFillAlpha(0.10)
                c.roundRect(x, y, w, self.CHIP_H, 2.6, fill=1, stroke=0)
                c.restoreState()
                c.setStrokeColor(self.accent); c.setLineWidth(0.8)
                c.roundRect(x, y, w, self.CHIP_H, 2.6, fill=0, stroke=1)
                c.setFillColor(t["ink"])
                c.setFont(font_or(t, "body_font"), self.CHIP_FONT)
                c.drawCentredString(x + w / 2, y + self.CHIP_H / 2 - self.CHIP_FONT * 0.34, chip)
                x += w + self.GAP_X
            y -= (self.CHIP_H + self.GAP_Y)


def font_or(t, key):
    return t.get(key, "Helvetica")


# ── 3) CALLOUT : 시험/TIP 등 작은 강조 ────────────────────────────────────────
class CalloutBlock(Block):
    LS = 4.6 * mm
    FONT = 8.0
    VARIANT_HL = {
        "exam": "hl_pink", "warn": "hl_pink",
        "tip": "hl_blue", "note": "hl_yellow", "info": "hl_blue",
    }

    def __init__(self, label, accent, t, TW, items, variant="note",
                 acc_idx=0, show_header=False):
        self.variant = (variant or "note").lower()
        self.lines_in = [str(i).strip() for i in (items or []) if str(i).strip()]
        self._wrapped = None
        # 콜아웃은 자체 헤더(라벨)를 본문 안에서 그리므로 베이스 헤더는 끔
        super().__init__(label, accent, t, TW, acc_idx, show_header=False)

    def _wrap_all(self):
        if self._wrapped is None:
            self._wrapped = [
                wrap_to_width(s, self.t["body_font"], self.FONT, self.TW - 9 * mm)
                for s in self.lines_in
            ]
        return self._wrapped

    def _body_height(self):
        nlines = sum(len(w) for w in self._wrap_all())
        return 5.4 * mm + max(nlines, 1) * self.LS + 1.5 * mm

    def _draw_body(self, c, top_y):
        t = self.t
        bar = self.accent
        total_h = self._body_height()
        # 왼쪽 강조 바
        c.setFillColor(bar)
        c.rect(0, top_y - total_h, 1.7 * mm, total_h, fill=1, stroke=0)
        # 라벨 태그
        lab = self.label or self.variant.upper()
        lab_w = sw(lab, t["bold_font"], self.FONT) + 4.6 * mm
        c.saveState()
        c.setFillColor(bar); c.setFillAlpha(0.16)
        c.roundRect(3.0 * mm, top_y - 5.2 * mm, lab_w, 4.8 * mm, 1.6, fill=1, stroke=0)
        c.restoreState()
        c.setFillColor(bar)
        c.setFont(t["bold_font"], self.FONT)
        c.drawString(5.0 * mm, top_y - 4.4 * mm, lab)
        # 본문
        y = top_y - 5.2 * mm - self.LS
        c.setFillColor(t["ink"])
        for lines in self._wrap_all():
            for ln in lines:
                c.setFont(t["body_font"], self.FONT)
                c.drawString(4.0 * mm, y, ln)
                y -= self.LS


# ── 4) FLOW : 가로 화살표 플로우차트 ──────────────────────────────────────────
class FlowBlock(Block):
    OPAQUE_PANEL = True
    BOX_H = 8.6 * mm
    FONT = 7.8
    ARROW_W = 6.0 * mm
    GAP_Y = 3.0 * mm
    PAD_X = 3.4 * mm
    MIN_BOX = 16 * mm

    def __init__(self, label, accent, t, TW, steps, acc_idx=0, show_header=True):
        self.steps = [str(s).strip() for s in (steps or []) if str(s).strip()]
        self._rows = None
        super().__init__(label, accent, t, TW, acc_idx, show_header)

    def _box_w(self, text):
        w = sw(text, self.t["body_font"], self.FONT) + self.PAD_X * 2
        return max(self.MIN_BOX, min(w, self.TW))

    def _layout(self):
        if self._rows is not None:
            return self._rows
        rows, cur, cur_w = [], [], 0.0
        for s in self.steps:
            bw = self._box_w(s)
            add = bw + (self.ARROW_W if cur else 0)
            if cur and cur_w + add > self.TW:
                rows.append(cur); cur, cur_w = [], 0.0
                add = bw
            cur.append((s, bw)); cur_w += add
        if cur:
            rows.append(cur)
        self._rows = rows
        return rows

    def _body_height(self):
        rows = self._layout()
        return max(len(rows), 1) * (self.BOX_H + self.GAP_Y)

    def _draw_body(self, c, top_y):
        t = self.t
        y = top_y - self.BOX_H
        rows = self._layout()
        for ri, row in enumerate(rows):
            x = 0.0
            for bi, (s, bw) in enumerate(row):
                if bi > 0:
                    _arrow(c, x, y + self.BOX_H / 2, x + self.ARROW_W, y + self.BOX_H / 2, self.accent)
                    x += self.ARROW_W
                c.saveState()
                c.setFillColor(self.accent); c.setFillAlpha(0.10)
                c.roundRect(x, y, bw, self.BOX_H, 2.2, fill=1, stroke=0)
                c.restoreState()
                c.setStrokeColor(self.accent); c.setLineWidth(0.9)
                c.roundRect(x, y, bw, self.BOX_H, 2.2, fill=0, stroke=1)
                c.setFillColor(t["ink"])
                c.setFont(t["body_font"], self.FONT)
                c.drawCentredString(x + bw / 2, y + self.BOX_H / 2 - self.FONT * 0.34, s)
                x += bw
            y -= (self.BOX_H + self.GAP_Y)


def _arrow(c, x0, y, x1, y1, color):
    c.saveState()
    c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(1.1)
    c.line(x0 + 0.8 * mm, y, x1 - 0.6 * mm, y1)
    ah = 1.4 * mm
    c.line(x1 - 0.6 * mm, y1, x1 - 0.6 * mm - ah, y1 + ah * 0.7)
    c.line(x1 - 0.6 * mm, y1, x1 - 0.6 * mm - ah, y1 - ah * 0.7)
    c.restoreState()


# ── 5) DEFINITIONS : [용어 박스] + 설명 ───────────────────────────────────────
class DefinitionsBlock(Block):
    ROW_GAP = 2.6 * mm
    FONT = 8.0
    TERM_FONT = 8.0
    LS = 4.5 * mm
    TERM_PAD = 3.0 * mm
    TERM_GAP = 2.6 * mm

    def __init__(self, label, accent, t, TW, items, acc_idx=0, show_header=True):
        self.items = []
        for it in (items or []):
            if isinstance(it, dict):
                term = str(it.get("term", "")).strip()
                desc = str(it.get("desc", it.get("definition", ""))).strip()
            else:
                s = str(it)
                for sep in ("—", ":", "-"):
                    if sep in s:
                        term, desc = s.split(sep, 1); break
                else:
                    term, desc = s, ""
                term, desc = term.strip(), desc.strip()
            if term:
                self.items.append((term, desc))
        self._rows = None
        super().__init__(label, accent, t, TW, acc_idx, show_header)

    def _term_w(self, term):
        return sw(term, self.t["bold_font"], self.TERM_FONT) + self.TERM_PAD * 2

    def _layout(self):
        if self._rows is not None:
            return self._rows
        rows = []
        for term, desc in self.items:
            tw = self._term_w(term)
            desc_x = tw + self.TERM_GAP
            desc_w = self.TW - desc_x
            lines = wrap_to_width(desc, self.t["body_font"], self.FONT, desc_w) if desc else [""]
            rows.append((term, tw, lines))
        self._rows = rows
        return rows

    def _body_height(self):
        h = 0.0
        for _, _, lines in self._layout():
            row_h = max(6.2 * mm, len(lines) * self.LS + 1.6 * mm)
            h += row_h + self.ROW_GAP
        return h

    def _draw_body(self, c, top_y):
        t = self.t
        y = top_y
        for term, tw, lines in self._layout():
            row_h = max(6.2 * mm, len(lines) * self.LS + 1.6 * mm)
            box_y = y - row_h
            # 용어 박스
            c.saveState()
            c.setFillColor(self.accent); c.setFillAlpha(0.12)
            c.roundRect(0, box_y + (row_h - 6.0 * mm) / 2, tw, 6.0 * mm, 1.8, fill=1, stroke=0)
            c.restoreState()
            c.setStrokeColor(self.accent); c.setLineWidth(0.7)
            c.roundRect(0, box_y + (row_h - 6.0 * mm) / 2, tw, 6.0 * mm, 1.8, fill=0, stroke=1)
            c.setFillColor(self.accent)
            c.setFont(t["bold_font"], self.TERM_FONT)
            c.drawCentredString(tw / 2, box_y + row_h / 2 - self.TERM_FONT * 0.34, term)
            # 설명
            c.setFillColor(t["ink"])
            c.setFont(t["body_font"], self.FONT)
            dx = tw + self.TERM_GAP
            ty = y - self.LS * 0.9
            for ln in lines:
                c.drawString(dx, ty, ln)
                ty -= self.LS
            y -= (row_h + self.ROW_GAP)


# ── 6) COMPARE : 컬럼 비교 박스 ───────────────────────────────────────────────
class CompareBlock(Block):
    OPAQUE_PANEL = True
    HEAD_H = 6.4 * mm
    FONT = 7.8
    HEAD_FONT = 8.2
    LS = 4.5 * mm
    GUTTER = 4.0 * mm
    PAD = 3.0 * mm

    def __init__(self, label, accent, t, TW, columns, acc_idx=0, show_header=True):
        self.cols = []
        for col in (columns or []):
            head = str(col.get("head", col.get("title", ""))).strip()
            items = [str(i).strip() for i in (col.get("items", []) or []) if str(i).strip()]
            self.cols.append((head, items))
        self.cols = self.cols[:3] or [("", [])]
        self._wrapped = None
        super().__init__(label, accent, t, TW, acc_idx, show_header)

    def _col_w(self):
        n = len(self.cols)
        return (self.TW - self.GUTTER * (n - 1)) / n

    def _wrap_cols(self):
        if self._wrapped is not None:
            return self._wrapped
        cw = self._col_w() - self.PAD * 2 - 2.4 * mm
        out = []
        for head, items in self.cols:
            wlist = []
            for it in items:
                wlist.append(wrap_to_width(it, self.t["body_font"], self.FONT, cw))
            out.append((head, wlist))
        self._wrapped = out
        return out

    def _body_height(self):
        wrapped = self._wrap_cols()
        max_lines = max((sum(len(w) for w in wl) for _, wl in wrapped), default=0)
        return self.HEAD_H + 1.5 * mm + max_lines * self.LS + self.PAD * 2

    def _draw_body(self, c, top_y):
        t = self.t
        cw = self._col_w()
        total_h = self._body_height()
        wrapped = self._wrap_cols()
        accents = t["accent"]
        x = 0.0
        for ci, (head, wlist) in enumerate(wrapped):
            acc = accents[(self.acc_idx + ci) % len(accents)]
            # 박스 테두리
            c.setStrokeColor(t["line"]); c.setLineWidth(0.7)
            c.roundRect(x, top_y - total_h, cw, total_h, 2.4, fill=0, stroke=1)
            # 헤더
            c.saveState()
            c.setFillColor(acc)
            p = c.beginPath()
            p.roundRect(x, top_y - self.HEAD_H, cw, self.HEAD_H, 2.4)
            c.drawPath(p, fill=1, stroke=0)
            c.restoreState()
            c.setFillColor(colors.white)
            c.setFont(t["bold_font"], self.HEAD_FONT)
            c.drawCentredString(x + cw / 2, top_y - self.HEAD_H / 2 - self.HEAD_FONT * 0.34, head)
            # 항목
            c.setFillColor(t["ink"])
            iy = top_y - self.HEAD_H - self.PAD - self.LS * 0.5
            for lines in wlist:
                c.setFillColor(acc); c.setFont(t["body_font"], self.FONT - 1)
                c.drawString(x + self.PAD, iy, "•")
                c.setFillColor(t["ink"]); c.setFont(t["body_font"], self.FONT)
                for j, ln in enumerate(lines):
                    c.drawString(x + self.PAD + 3.0 * mm, iy - j * self.LS, ln)
                iy -= self.LS * len(lines)
            x += cw + self.GUTTER

        # VS 배지 (2컬럼일 때 가운데)
        if len(self.cols) == 2:
            mid_x = cw + self.GUTTER / 2
            cy = top_y - self.HEAD_H / 2
            c.saveState()
            c.setFillColor(t["bg"]); c.circle(mid_x, cy, 3.4 * mm, fill=1, stroke=0)
            c.setStrokeColor(t["ink2"]); c.setLineWidth(0.7)
            c.circle(mid_x, cy, 3.4 * mm, fill=0, stroke=1)
            c.setFillColor(t["ink2"]); c.setFont(t["bold_font"], 6.5)
            c.drawCentredString(mid_x, cy - 2.0, "VS")
            c.restoreState()


# ── 7) TREE : 분류 트리 ───────────────────────────────────────────────────────
class TreeBlock(Block):
    OPAQUE_PANEL = True
    LS = 5.0 * mm
    FONT = 8.0
    INDENT = 6.0 * mm

    def __init__(self, label, accent, t, TW, root, nodes, acc_idx=0, show_header=True):
        self.root = str(root or "").strip()
        # nodes: [{"label","children":[...]}] 또는 [{"label","children":[{"label",...}]}]
        self.flat = self._flatten(nodes)
        super().__init__(label, accent, t, TW, acc_idx, show_header)

    def _flatten(self, nodes, depth=1):
        out = []
        for n in (nodes or []):
            if isinstance(n, dict):
                lab = str(n.get("label", n.get("name", ""))).strip()
                children = n.get("children", [])
            else:
                lab, children = str(n).strip(), []
            if not lab:
                continue
            out.append((depth, lab))
            if children:
                if children and isinstance(children[0], (str, int, float)):
                    for ch in children:
                        out.append((depth + 1, str(ch).strip()))
                else:
                    out.extend(self._flatten(children, depth + 1))
        return out

    def _body_height(self):
        rows = (1 if self.root else 0) + len(self.flat)
        return max(rows, 1) * self.LS + 1.5 * mm

    def _draw_body(self, c, top_y):
        t = self.t
        y = top_y - self.LS * 0.7
        if self.root:
            c.setFillColor(self.accent); c.setFont(t["body_font"], self.FONT)
            c.drawString(0.5 * mm, y, "●")
            c.setFillColor(t["ink"]); c.setFont(t["bold_font"], self.FONT + 0.5)
            c.drawString(4.5 * mm, y, self.root)
            y -= self.LS
        for depth, lab in self.flat:
            x = depth * self.INDENT
            # 연결선 (├ / └ 느낌)
            c.setStrokeColor(t["line"]); c.setLineWidth(0.7)
            c.line(x - self.INDENT + 1.4 * mm, y + 3.0, x - self.INDENT + 1.4 * mm, y + 1.4 * mm)
            c.line(x - self.INDENT + 1.4 * mm, y + 1.4, x - 0.6 * mm, y + 1.4)
            # 노드 마커
            c.setFillColor(self.accent); c.setFont(t["body_font"], self.FONT - 1.5)
            c.drawString(x, y, "▪")
            c.setFillColor(t["ink"]); c.setFont(t["body_font"], self.FONT)
            c.drawString(x + 3.2 * mm, y, lab)
            y -= self.LS


# ── 8) QA : Q/A 박스 ──────────────────────────────────────────────────────────
class QABlock(Block):
    FONT = 8.0
    LS = 4.6 * mm
    ROW_GAP = 2.6 * mm
    BADGE = 4.4 * mm

    def __init__(self, label, accent, t, TW, items, acc_idx=0, show_header=True):
        self.qas = []
        for it in (items or []):
            if isinstance(it, dict):
                q = str(it.get("q", it.get("question", ""))).strip()
                a = str(it.get("a", it.get("answer", ""))).strip()
            else:
                q, a = str(it).strip(), ""
            if q:
                self.qas.append((q, a))
        self._wrapped = None
        super().__init__(label, accent, t, TW, acc_idx, show_header)

    def _wrap(self):
        if self._wrapped is not None:
            return self._wrapped
        tw = self.TW - self.BADGE - 3.5 * mm
        out = []
        for q, a in self.qas:
            ql = wrap_to_width(q, self.t["bold_font"], self.FONT, tw)
            al = wrap_to_width(a, self.t["body_font"], self.FONT, tw) if a else []
            out.append((ql, al))
        self._wrapped = out
        return out

    def _body_height(self):
        h = 0.0
        for ql, al in self._wrap():
            h += len(ql) * self.LS + (len(al) * self.LS if al else 0) + 1.6 * mm + self.ROW_GAP
        return h

    def _draw_body(self, c, top_y):
        t = self.t
        y = top_y
        for ql, al in self._wrap():
            # Q 배지
            qy = y - self.LS * 0.9
            c.setFillColor(self.accent)
            c.circle(self.BADGE / 2, qy + 1.0 * mm, self.BADGE / 2, fill=1, stroke=0)
            c.setFillColor(colors.white); c.setFont(t["bold_font"], self.FONT - 1)
            c.drawCentredString(self.BADGE / 2, qy + 1.0 * mm - (self.FONT - 1) * 0.34, "Q")
            c.setFillColor(t["ink"]); c.setFont(t["bold_font"], self.FONT)
            tx = self.BADGE + 3.0 * mm
            for j, ln in enumerate(ql):
                c.drawString(tx, qy - j * self.LS, ln)
            y = qy - len(ql) * self.LS
            # A 배지
            if al:
                ay = y - self.LS * 0.4
                c.setFillColor(t["ink2"])
                c.circle(self.BADGE / 2, ay + 1.0 * mm, self.BADGE / 2, fill=1, stroke=0)
                c.setFillColor(colors.white); c.setFont(t["bold_font"], self.FONT - 1)
                c.drawCentredString(self.BADGE / 2, ay + 1.0 * mm - (self.FONT - 1) * 0.34, "A")
                c.setFillColor(t["ink2"]); c.setFont(t["body_font"], self.FONT)
                for j, ln in enumerate(al):
                    c.drawString(tx, ay - j * self.LS, ln)
                y = ay - len(al) * self.LS
            y -= self.ROW_GAP


# ── 블록 디스패치 ─────────────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════
# 추가 블록 8종
# ════════════════════════════════════════════════════════════════════════════

# ── 9) TABLE : 일반 표(헤더 + 행) ─────────────────────────────────────────────
class TableBlock(Block):
    OPAQUE_PANEL = True
    HROW = 6.4 * mm
    FONT = 7.6
    LS = 4.2 * mm
    PAD = 1.8 * mm

    def __init__(self, label, accent, t, TW, headers, rows, acc_idx=0, show_header=True):
        self.headers = [str(h).strip() for h in (headers or [])]
        self.rows = [[str(c).strip() for c in r] for r in (rows or []) if isinstance(r, (list, tuple))]
        ncol = max([len(self.headers)] + [len(r) for r in self.rows] + [1])
        self.ncol = ncol
        self.headers = (self.headers + [""] * ncol)[:ncol]
        self.rows = [(r + [""] * ncol)[:ncol] for r in self.rows]
        self._wrapped = None
        super().__init__(label, accent, t, TW, acc_idx, show_header)

    def _cw(self):
        return self.TW / self.ncol

    def _wrap_rows(self):
        if self._wrapped is None:
            cw = self._cw() - self.PAD * 2
            self._wrapped = [[wrap_to_width(c, self.t["body_font"], self.FONT, cw) for c in r]
                             for r in self.rows]
        return self._wrapped

    def _row_h(self, wrapped_row):
        return max(self.LS * max((len(c) for c in wrapped_row), default=1) + self.PAD, self.HROW)

    def _body_height(self):
        h = self.HROW if any(self.headers) else 0
        for wr in self._wrap_rows():
            h += self._row_h(wr)
        return h

    def _draw_body(self, c, top_y):
        t = self.t; cw = self._cw(); y = top_y
        total_h = self._body_height()
        # 헤더
        if any(self.headers):
            c.setFillColor(self.accent)
            c.rect(0, top_y - self.HROW, self.TW, self.HROW, fill=1, stroke=0)
            c.setFillColor(colors.white); c.setFont(t["bold_font"], self.FONT)
            for i, h in enumerate(self.headers):
                c.drawCentredString(i * cw + cw / 2, top_y - self.HROW / 2 - self.FONT * 0.34, h)
            y = top_y - self.HROW
        # 행
        wrapped = self._wrap_rows()
        for ri, wr in enumerate(wrapped):
            rh = self._row_h(wr)
            if ri % 2 == 1:
                c.saveState(); c.setFillColor(self.accent); c.setFillAlpha(0.06)
                c.rect(0, y - rh, self.TW, rh, fill=1, stroke=0); c.restoreState()
            c.setFillColor(t["ink"]); c.setFont(t["body_font"], self.FONT)
            for ci, cell in enumerate(wr):
                cx = ci * cw + self.PAD
                ty = y - self.LS * 0.9
                for ln in cell:
                    c.drawString(cx, ty, ln); ty -= self.LS
            y -= rh
        # 격자선
        c.setStrokeColor(t["line"]); c.setLineWidth(0.5)
        c.rect(0, top_y - total_h, self.TW, total_h, fill=0, stroke=1)
        for i in range(1, self.ncol):
            c.line(i * cw, top_y - total_h, i * cw, top_y)


# ── 10) STEPS : 번호가 매겨진 절차 ────────────────────────────────────────────
class StepsBlock(Block):
    OPAQUE_PANEL = True
    FONT = 8.0
    LS = 4.6 * mm
    GAP = 2.2 * mm
    NUM = 5.0 * mm

    def __init__(self, label, accent, t, TW, items, acc_idx=0, show_header=True):
        self.steps = [str(i).strip() for i in (items or []) if str(i).strip()]
        self._w = None
        super().__init__(label, accent, t, TW, acc_idx, show_header)

    def _wrap(self):
        if self._w is None:
            self._w = [wrap_to_width(s, self.t["body_font"], self.FONT, self.TW - self.NUM - 4 * mm)
                       for s in self.steps]
        return self._w

    def _body_height(self):
        return sum(max(len(w) * self.LS, self.NUM) + self.GAP for w in self._wrap())

    def _draw_body(self, c, top_y):
        t = self.t; y = top_y
        wrapped = self._wrap()
        for i, lines in enumerate(wrapped, 1):
            block_h = max(len(lines) * self.LS, self.NUM)
            cy = y - self.NUM / 2
            # 연결선
            if i < len(wrapped):
                c.setStrokeColor(self.accent); c.setLineWidth(0.7)
                c.line(self.NUM / 2, cy - self.NUM / 2, self.NUM / 2, y - block_h - self.GAP + self.NUM / 2)
            # 번호 원
            c.setFillColor(self.accent); c.circle(self.NUM / 2, cy, self.NUM / 2, fill=1, stroke=0)
            c.setFillColor(colors.white); c.setFont(t["bold_font"], self.FONT)
            c.drawCentredString(self.NUM / 2, cy - self.FONT * 0.34, str(i))
            # 텍스트
            c.setFillColor(t["ink"]); c.setFont(t["body_font"], self.FONT)
            ty = y - self.LS * 0.85
            for ln in lines:
                c.drawString(self.NUM + 3 * mm, ty, ln); ty -= self.LS
            y -= (block_h + self.GAP)


# ── 11) TIMELINE : 시간/순서 축 ───────────────────────────────────────────────
class TimelineBlock(Block):
    OPAQUE_PANEL = True
    FONT = 8.0
    LS = 4.4 * mm
    GAP = 2.4 * mm
    DOT = 2.0 * mm
    AXIS = 3.0 * mm

    def __init__(self, label, accent, t, TW, items, acc_idx=0, show_header=True):
        self.items = []
        for i in (items or []):
            if isinstance(i, dict):
                tm = str(i.get("time", i.get("date", i.get("label", "")))).strip()
                ds = str(i.get("desc", i.get("text", ""))).strip()
            else:
                s = str(i); sep = ":" if ":" in s else "—"
                tm, _, ds = s.partition(sep); tm, ds = tm.strip(), ds.strip()
                if not ds: tm, ds = "", s.strip()
            if tm or ds:
                self.items.append((tm, ds))
        self._w = None
        super().__init__(label, accent, t, TW, acc_idx, show_header)

    def _wrap(self):
        if self._w is None:
            x = self.AXIS + 4 * mm
            self._w = []
            for tm, ds in self.items:
                tw = sw(tm + "  ", self.t["bold_font"], self.FONT) if tm else 0
                self._w.append((tm, wrap_to_width(ds, self.t["body_font"], self.FONT, self.TW - x - tw)))
        return self._w

    def _body_height(self):
        return sum(max(len(w) * self.LS, self.LS) + self.GAP for _, w in self._wrap())

    def _draw_body(self, c, top_y):
        t = self.t; y = top_y; x = self.AXIS
        wrapped = self._wrap()
        # 세로 축
        c.setStrokeColor(self.accent); c.setLineWidth(0.8)
        c.line(x, top_y - self._body_height() + self.GAP, x, top_y - self.LS * 0.4)
        for (tm, lines) in wrapped:
            dy = y - self.LS * 0.85
            c.setFillColor(self.accent); c.circle(x, dy + 0.8 * mm, self.DOT, fill=1, stroke=0)
            tx = x + 4 * mm
            if tm:
                c.setFillColor(self.accent); c.setFont(t["bold_font"], self.FONT)
                c.drawString(tx, dy, tm + " ")
                tx += sw(tm + "  ", t["bold_font"], self.FONT)
            c.setFillColor(t["ink"]); c.setFont(t["body_font"], self.FONT)
            ty = dy
            for ln in lines:
                c.drawString(tx, ty, ln); ty -= self.LS; tx = x + 4 * mm
            y -= (max(len(lines) * self.LS, self.LS) + self.GAP)


# ── 12) PROS_CONS : 장점/단점 ─────────────────────────────────────────────────
class ProsConsBlock(Block):
    OPAQUE_PANEL = True
    HEAD = 6.0 * mm
    FONT = 7.8
    LS = 4.4 * mm
    GUT = 4.0 * mm
    PAD = 3.0 * mm
    GREEN = colors.HexColor("#2E9E5B")
    RED = colors.HexColor("#D7263D")

    def __init__(self, label, accent, t, TW, pros, cons, acc_idx=0, show_header=True):
        self.pros = [str(i).strip() for i in (pros or []) if str(i).strip()]
        self.cons = [str(i).strip() for i in (cons or []) if str(i).strip()]
        self._w = None
        super().__init__(label, accent, t, TW, acc_idx, show_header)

    def _cw(self): return (self.TW - self.GUT) / 2

    def _wrap(self):
        if self._w is None:
            w = self._cw() - self.PAD - 4 * mm
            self._w = ([wrap_to_width(i, self.t["body_font"], self.FONT, w) for i in self.pros],
                       [wrap_to_width(i, self.t["body_font"], self.FONT, w) for i in self.cons])
        return self._w

    def _body_height(self):
        p, n = self._wrap()
        rows = max(sum(len(x) for x in p), sum(len(x) for x in n))
        return self.HEAD + rows * self.LS + self.PAD * 2

    def _draw_col(self, c, x, head, color, wlist, top_y, total_h):
        t = self.t; cw = self._cw()
        c.setStrokeColor(t["line"]); c.setLineWidth(0.7)
        c.roundRect(x, top_y - total_h, cw, total_h, 2.2, fill=0, stroke=1)
        c.saveState(); c.setFillColor(color)
        p = c.beginPath(); p.roundRect(x, top_y - self.HEAD, cw, self.HEAD, 2.2)
        c.drawPath(p, fill=1, stroke=0); c.restoreState()
        c.setFillColor(colors.white); c.setFont(t["bold_font"], self.FONT + 0.4)
        c.drawCentredString(x + cw / 2, top_y - self.HEAD / 2 - self.FONT * 0.34, head)
        sym = "✓" if color == self.GREEN else "✗"
        iy = top_y - self.HEAD - self.PAD - self.LS * 0.5
        for lines in wlist:
            c.setFillColor(color); c.setFont(t["body_font"], self.FONT)
            c.drawString(x + self.PAD, iy, sym)
            c.setFillColor(t["ink"])
            for j, ln in enumerate(lines):
                c.drawString(x + self.PAD + 4 * mm, iy - j * self.LS, ln)
            iy -= self.LS * len(lines)

    def _draw_body(self, c, top_y):
        total_h = self._body_height(); cw = self._cw()
        p, n = self._wrap()
        self._draw_col(c, 0, "장점", self.GREEN, p, top_y, total_h)
        self._draw_col(c, cw + self.GUT, "단점", self.RED, n, top_y, total_h)


# ── 13) BAR_CHART : 가로 막대그래프 ───────────────────────────────────────────
class BarChartBlock(Block):
    OPAQUE_PANEL = True
    FONT = 7.8
    ROW = 7.2 * mm
    LABEL_W = 26 * mm
    BAR_H = 4.0 * mm

    def __init__(self, label, accent, t, TW, items, acc_idx=0, show_header=True):
        self.items = []
        for i in (items or []):
            if isinstance(i, dict):
                lab = str(i.get("label", i.get("name", ""))).strip()
                try: val = float(str(i.get("value", i.get("val", 0))).replace(",", "").strip())
                except Exception: val = 0.0
                if lab:
                    self.items.append((lab, val))
        self._max = max([v for _, v in self.items] + [1.0])
        super().__init__(label, accent, t, TW, acc_idx, show_header)

    def _body_height(self):
        return max(len(self.items), 1) * self.ROW

    def _draw_body(self, c, top_y):
        t = self.t; y = top_y - self.ROW
        accents = t["accent"]
        bar_area = self.TW - self.LABEL_W - 16 * mm
        for idx, (lab, val) in enumerate(self.items):
            acc = accents[(self.acc_idx + idx) % len(accents)]
            cy = y + self.ROW / 2
            # 라벨
            c.setFillColor(t["ink"]); c.setFont(t["body_font"], self.FONT)
            c.drawString(0, cy - self.FONT * 0.34, lab[:14])
            # 막대
            bw = max(1.0, bar_area * (val / self._max))
            bx = self.LABEL_W
            c.saveState(); c.setFillColor(acc); c.setFillAlpha(0.22)
            c.roundRect(bx, cy - self.BAR_H / 2, bar_area, self.BAR_H, 1.2, fill=1, stroke=0); c.restoreState()
            c.setFillColor(acc)
            c.roundRect(bx, cy - self.BAR_H / 2, bw, self.BAR_H, 1.2, fill=1, stroke=0)
            # 값
            c.setFillColor(t["ink2"]); c.setFont(t["bold_font"], self.FONT)
            v_txt = (f"{val:g}")
            c.drawString(bx + bw + 2 * mm, cy - self.FONT * 0.34, v_txt)
            y -= self.ROW


# ── 14) QUADRANT : 2×2 매트릭스 ──────────────────────────────────────────────
class QuadrantBlock(Block):
    OPAQUE_PANEL = True
    CELL_H = 22 * mm
    HEAD = 5.4 * mm
    FONT = 7.4
    LS = 4.0 * mm
    GUT = 3.0 * mm
    PAD = 2.6 * mm

    def __init__(self, label, accent, t, TW, cells, acc_idx=0, show_header=True):
        self.cells = []
        for cspec in (cells or [])[:4]:
            if isinstance(cspec, dict):
                lab = str(cspec.get("label", cspec.get("title", ""))).strip()
                items = [str(x).strip() for x in (cspec.get("items", []) or []) if str(x).strip()]
                self.cells.append((lab, items))
        while len(self.cells) < 4:
            self.cells.append(("", []))
        super().__init__(label, accent, t, TW, acc_idx, show_header)

    def _body_height(self):
        return self.CELL_H * 2 + self.GUT

    def _draw_cell(self, c, x, y, w, h, lab, items, acc):
        t = self.t
        c.saveState(); c.setFillColor(acc); c.setFillAlpha(0.07)
        c.roundRect(x, y, w, h, 2.4, fill=1, stroke=0); c.restoreState()
        c.setStrokeColor(acc); c.setLineWidth(0.8)
        c.roundRect(x, y, w, h, 2.4, fill=0, stroke=1)
        c.setFillColor(acc); c.setFont(t["bold_font"], self.FONT + 0.6)
        c.drawString(x + self.PAD, y + h - self.HEAD + 1.0, lab)
        c.setFillColor(t["ink"]); c.setFont(t["body_font"], self.FONT)
        iy = y + h - self.HEAD - self.LS * 0.6
        for it in items:
            for ln in wrap_to_width("· " + it, t["body_font"], self.FONT, w - self.PAD * 2):
                if iy < y + self.PAD: break
                c.drawString(x + self.PAD, iy, ln); iy -= self.LS
        return

    def _draw_body(self, c, top_y):
        t = self.t; accents = t["accent"]
        cw = (self.TW - self.GUT) / 2
        positions = [(0, top_y - self.CELL_H),
                     (cw + self.GUT, top_y - self.CELL_H),
                     (0, top_y - self.CELL_H * 2 - self.GUT),
                     (cw + self.GUT, top_y - self.CELL_H * 2 - self.GUT)]
        for i, (x, y) in enumerate(positions):
            lab, items = self.cells[i]
            self._draw_cell(c, x, y, cw, self.CELL_H, lab, items,
                            accents[(self.acc_idx + i) % len(accents)])


# ── 15) CYCLE : 순환 다이어그램 ──────────────────────────────────────────────
class CycleBlock(Block):
    OPAQUE_PANEL = True
    FONT = 7.4
    SIZE = 58 * mm   # 다이어그램 높이

    def __init__(self, label, accent, t, TW, steps, acc_idx=0, show_header=True):
        self.steps = [str(s).strip() for s in (steps or []) if str(s).strip()][:6]
        super().__init__(label, accent, t, TW, acc_idx, show_header)

    def _body_height(self):
        return self.SIZE

    def _draw_body(self, c, top_y):
        import math as _m
        t = self.t; n = len(self.steps)
        if n == 0:
            return
        cx = self.TW / 2
        cy = top_y - self.SIZE / 2
        R = self.SIZE / 2 - 9 * mm
        node_r = 9 * mm
        pts = []
        for i in range(n):
            ang = _m.pi / 2 - i * (2 * _m.pi / n)   # 12시부터 시계방향
            pts.append((cx + R * _m.cos(ang), cy + R * _m.sin(ang)))
        # 화살표(다음 노드로, 마지막→처음)
        c.setStrokeColor(self.accent); c.setFillColor(self.accent); c.setLineWidth(1.0)
        for i in range(n):
            x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % n]
            dx, dy = x1 - x0, y1 - y0
            d = _m.hypot(dx, dy) or 1
            ux, uy = dx / d, dy / d
            sx, sy = x0 + ux * node_r, y0 + uy * node_r
            ex, ey = x1 - ux * node_r, y1 - uy * node_r
            c.line(sx, sy, ex, ey)
            ah = 1.6 * mm
            c.line(ex, ey, ex - ux * ah - uy * ah * 0.6, ey - uy * ah + ux * ah * 0.6)
            c.line(ex, ey, ex - ux * ah + uy * ah * 0.6, ey - uy * ah - ux * ah * 0.6)
        # 노드
        for i, (x, y) in enumerate(pts):
            c.saveState(); c.setFillColor(self.accent); c.setFillAlpha(0.12)
            c.circle(x, y, node_r, fill=1, stroke=0); c.restoreState()
            c.setStrokeColor(self.accent); c.setLineWidth(0.9); c.circle(x, y, node_r, fill=0, stroke=1)
            c.setFillColor(t["ink"]); c.setFont(t["body_font"], self.FONT)
            lines = wrap_to_width(self.steps[i], t["body_font"], self.FONT, node_r * 1.7)
            ty = y + (len(lines) - 1) * 1.7 * mm
            for ln in lines[:3]:
                c.drawCentredString(x, ty - self.FONT * 0.34, ln); ty -= 3.4 * mm


# ── 16) FORMULA : 수식 박스 ──────────────────────────────────────────────────
class FormulaBlock(Block):
    OPAQUE_PANEL = True
    EXPR_FONT = 11.0
    DESC_FONT = 7.6
    LS = 4.3 * mm
    GAP = 2.6 * mm
    BOX_H = 9.5 * mm

    def __init__(self, label, accent, t, TW, items, acc_idx=0, show_header=True):
        self.items = []
        for i in (items or []):
            if isinstance(i, dict):
                expr = str(i.get("expr", i.get("formula", i.get("text", "")))).strip()
                desc = str(i.get("desc", i.get("meaning", i.get("description", "")))).strip()
            else:
                s = str(i); sep = ":" if ":" in s else "—"
                expr, _, desc = s.partition(sep); expr, desc = expr.strip(), desc.strip()
            if expr:
                self.items.append((expr, desc))
        self._w = None
        super().__init__(label, accent, t, TW, acc_idx, show_header)

    def _wrap(self):
        if self._w is None:
            self._w = [(e, wrap_to_width(d, self.t["body_font"], self.DESC_FONT, self.TW - 6 * mm) if d else [])
                       for e, d in self.items]
        return self._w

    def _body_height(self):
        h = 0
        for _, dl in self._wrap():
            h += self.BOX_H + (len(dl) * self.LS if dl else 0) + self.GAP
        return h

    def _draw_body(self, c, top_y):
        t = self.t; y = top_y
        for expr, dl in self._wrap():
            c.saveState(); c.setFillColor(self.accent); c.setFillAlpha(0.08)
            c.roundRect(0, y - self.BOX_H, self.TW, self.BOX_H, 2.4, fill=1, stroke=0); c.restoreState()
            c.setStrokeColor(self.accent); c.setLineWidth(0.7)
            c.roundRect(0, y - self.BOX_H, self.TW, self.BOX_H, 2.4, fill=0, stroke=1)
            c.setFillColor(t["ink"]); c.setFont(t["bold_font"], self.EXPR_FONT)
            c.drawCentredString(self.TW / 2, y - self.BOX_H / 2 - self.EXPR_FONT * 0.34, expr)
            y -= self.BOX_H
            if dl:
                c.setFillColor(t["ink2"]); c.setFont(t["body_font"], self.DESC_FONT)
                ty = y - self.LS * 0.9
                for ln in dl:
                    c.drawCentredString(self.TW / 2, ty, ln); ty -= self.LS
                y -= len(dl) * self.LS
            y -= self.GAP


def make_block(spec: Dict[str, Any], t, TW, acc_idx: int) -> Block | None:
    typ = str(spec.get("type", "text")).lower().strip()
    label = spec.get("title", spec.get("label", ""))
    accent = t["accent"][acc_idx % len(t["accent"])]
    try:
        if typ == "chips":
            return ChipsBlock(label, accent, t, TW, spec.get("items", []), acc_idx)
        if typ == "callout":
            return CalloutBlock(label, accent, t, TW, spec.get("items", []),
                                variant=spec.get("variant", "note"), acc_idx=acc_idx)
        if typ == "flow":
            return FlowBlock(label, accent, t, TW, spec.get("steps", spec.get("items", [])), acc_idx)
        if typ == "definitions":
            return DefinitionsBlock(label, accent, t, TW, spec.get("items", []), acc_idx)
        if typ == "compare":
            return CompareBlock(label, accent, t, TW, spec.get("columns", []), acc_idx)
        if typ == "tree":
            return TreeBlock(label, accent, t, TW, spec.get("root", ""), spec.get("nodes", []), acc_idx)
        if typ == "qa":
            return QABlock(label, accent, t, TW, spec.get("items", []), acc_idx)
        if typ == "table":
            return TableBlock(label, accent, t, TW, spec.get("headers", []), spec.get("rows", []), acc_idx)
        if typ == "steps":
            return StepsBlock(label, accent, t, TW, spec.get("items", spec.get("steps", [])), acc_idx)
        if typ == "timeline":
            return TimelineBlock(label, accent, t, TW, spec.get("items", []), acc_idx)
        if typ == "pros_cons":
            return ProsConsBlock(label, accent, t, TW, spec.get("pros", []), spec.get("cons", []), acc_idx)
        if typ == "bar_chart":
            return BarChartBlock(label, accent, t, TW, spec.get("items", []), acc_idx)
        if typ == "quadrant":
            return QuadrantBlock(label, accent, t, TW, spec.get("cells", []), acc_idx)
        if typ == "cycle":
            return CycleBlock(label, accent, t, TW, spec.get("steps", spec.get("items", [])), acc_idx)
        if typ == "formula":
            return FormulaBlock(label, accent, t, TW, spec.get("items", []), acc_idx)
        # 기본 text
        return TextBlock(label, accent, t, TW, spec.get("items", []), acc_idx)
    except Exception:
        return None


# ── 배경 ──────────────────────────────────────────────────────────────────────
def make_bg_fn(t):
    style = t["style"]
    def draw_bg(c, doc):
        c.saveState()
        c.setFillColor(t["bg"]); c.rect(0, 0, W, H, fill=1, stroke=0)
        if style in ("notebook", "pastel"):
            c.setStrokeColor(t["line"]); c.setLineWidth(0.35)
            if style == "pastel":
                c.setDash(2, 3)
            y = H - 26 * mm
            while y > 14 * mm:
                c.line(8 * mm, y, W - 8 * mm, y); y -= 6.8 * mm
            c.setDash()
            c.setStrokeColor(t["margin"]); c.setLineWidth(1.0)
            c.line(14 * mm, H - 14 * mm, 14 * mm, 14 * mm)
        elif style == "dark":
            c.setStrokeColor(t["line"]); c.setLineWidth(0.3)
            y = H - 24 * mm
            while y > 12 * mm:
                c.line(8 * mm, y, W - 8 * mm, y); y -= 6.8 * mm
        elif style == "newspaper":
            c.setStrokeColor(t["margin"]); c.setLineWidth(2.0)
            c.line(8 * mm, H - 24 * mm, W - 8 * mm, H - 24 * mm)
        c.setFont(t["title_font"], 9); c.setFillColor(t["ink2"])
        c.drawCentredString(W / 2, 9 * mm, f"- {c.getPageNumber()} -")
        c.restoreState()
    return draw_bg


# ── 노트 정규화 (구버전 호환) ─────────────────────────────────────────────────
LEGACY_LABELS = {
    "summary": ("text", "✏  핵심 요약"),
    "key_concepts": ("chips", "💡  핵심 개념"),
    "definitions": ("definitions", "📖  용어 정의"),
    "formulas": ("text", "∑  공식 · 식"),
    "examples": ("text", "🔎  예시 · 사례"),
    "visual_notes": ("text", "🖼  이미지 · 도표"),
    "exam_points": ("callout", "⚠  시험 포인트"),
    "mnemonics": ("text", "🧠  암기 팁"),
    "review_questions": ("qa", "❓  복습 질문"),
}


_VALID_EMPH = {"none", "star", "wavy", "highlight", "underline"}
_VALID_VARIANT = {"exam", "tip", "warn", "note", "info"}
_KIND_MAP = {
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
_KIND_MAP.update({
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


def _first_list(d, keys):
    for k in keys:
        v = d.get(k)
        if isinstance(v, list) and v:
            return v
    return []


def _strings(lst):
    out = []
    for x in lst:
        if isinstance(x, dict):
            x = x.get("text") or x.get("name") or x.get("term") or x.get("label") or ""
        s = str(x).strip()
        if s:
            out.append(s)
    return out


def _canon_type(block):
    raw = str(block.get("type") or block.get("kind") or block.get("category") or "").lower().strip()
    if raw in _KIND_MAP:
        return _KIND_MAP[raw]
    for key, val in _KIND_MAP.items():
        if key in raw:
            return val
    return ("text", None)


def coerce_blocks(data):
    """blocks/sections, type/kind, title/heading 등 어떤 변형이든 표준 블록으로 흡수."""
    if not isinstance(data, dict):
        return {"title": "강의 노트", "subtitle": "", "blocks": []}
    title = str(data.get("title") or data.get("name") or "강의 노트").strip()
    subtitle = str(data.get("subtitle") or data.get("description") or "").strip()
    raw_blocks = _first_list(data, ["blocks", "sections", "items", "content", "groups"])
    blocks = []
    for b in raw_blocks:
        if not isinstance(b, dict):
            s = str(b).strip()
            if s:
                blocks.append({"type": "text", "title": "",
                               "items": [{"text": s, "emphasis": "none"}]})
            continue
        typ, forced_variant = _canon_type(b)
        title_b = str(b.get("title") or b.get("heading") or b.get("label") or b.get("name") or "").strip()
        blk = {"type": typ, "title": title_b}
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
            blk["variant"] = var if var in _VALID_VARIANT else "note"
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
        else:
            items = []
            for i in _first_list(b, ["items", "points", "content", "lines", "bullets", "list"]):
                if isinstance(i, dict):
                    txt = str(i.get("text") or i.get("content") or i.get("point") or "").strip()
                    emph = str(i.get("emphasis") or i.get("highlight") or "none").lower().strip()
                    emph = emph if emph in _VALID_EMPH else "none"
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


def normalize_note(note: Dict[str, Any]) -> Dict[str, Any]:
    """노트를 표준 블록 스키마로 정규화.

    - blocks / sections / items / content / groups 중 하나라도 있으면 coerce 로 흡수
    - 그것도 없으면(구버전 플랫 {섹션:[문자열]}) LEGACY_LABELS 로 변환
    """
    note = note or {}
    has_block_array = any(
        isinstance(note.get(k), list) and note.get(k)
        for k in ("blocks", "sections", "items", "content", "groups")
    )
    if has_block_array:
        return coerce_blocks(note)

    blocks = []
    for key, (typ, label) in LEGACY_LABELS.items():
        items = note.get(key)
        if not items:
            continue
        if typ == "qa":
            blocks.append({"type": "qa", "title": label,
                           "items": [{"q": str(i), "a": ""} for i in items]})
        elif typ == "chips":
            blocks.append({"type": "chips", "title": label, "items": items})
        elif typ == "callout":
            blocks.append({"type": "callout", "title": label,
                           "variant": "exam", "items": items})
        elif typ == "definitions":
            blocks.append({"type": "definitions", "title": label, "items": items})
        else:
            blocks.append({"type": "text", "title": label, "items": items})
    return {"title": note.get("title", "강의 노트"),
            "subtitle": note.get("subtitle", ""), "blocks": blocks}


# ── PDF 빌드 ──────────────────────────────────────────────────────────────────
def build_pdf(note: Dict[str, Any], theme_name: str, layout: str = "2단") -> bytes:
    data = normalize_note(note)
    t = THEMES.get(theme_name, THEMES["📓 노트"])
    buf = io.BytesIO()

    LEFT, RIGHT, TOP, BOT = 14 * mm, 10 * mm, 16 * mm, 12 * mm
    inner_w = W - LEFT - RIGHT
    inner_h = H - TOP - BOT
    HEAD_H = 17 * mm   # 제목+부제 상단 영역

    title_txt = data.get("title", "강의 노트")
    sub_txt = data.get("subtitle", "")

    def bg_with_title(c, doc):
        make_bg_fn(t)(c, doc)
        if c.getPageNumber() == 1:
            c.saveState()
            c.setFillColor(t["ink"]); c.setFont(t["title_font"], 22)
            c.drawString(LEFT, H - TOP - 7 * mm, title_txt)
            if sub_txt:
                c.setFillColor(t["ink2"]); c.setFont(t["body_font"], 8.5)
                c.drawString(LEFT, H - TOP - 12 * mm, sub_txt)
            c.restoreState()

    doc = BaseDocTemplate(buf, pagesize=A4,
                          leftMargin=LEFT, rightMargin=RIGHT, topMargin=TOP, bottomMargin=BOT)

    if layout == "1단":
        TW = inner_w
        frame = Frame(LEFT, BOT, TW, inner_h - HEAD_H, leftPadding=0, rightPadding=0,
                      topPadding=0, bottomPadding=0, id="main")
        doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=bg_with_title)])
        story = []
        for i, spec in enumerate(data["blocks"]):
            blk = make_block(spec, t, TW, acc_idx=i)
            if blk is not None:
                story.append(blk); story.append(Spacer(1, 2.8 * mm))
        doc.build(story)
        buf.seek(0); return buf.read()

    # ── 2단: A4 가운데 기준 좌/우 두 컬럼 ──
    gutter = 6 * mm
    col_w = (inner_w - gutter) / 2
    col_h = inner_h - HEAD_H
    left_frame = Frame(LEFT, BOT, col_w, col_h, leftPadding=0, rightPadding=0,
                       topPadding=0, bottomPadding=0, id="L")
    right_frame = Frame(LEFT + col_w + gutter, BOT, col_w, col_h, leftPadding=0, rightPadding=0,
                        topPadding=0, bottomPadding=0, id="R")
    doc.addPageTemplates([PageTemplate(id="two", frames=[left_frame, right_frame],
                                       onPage=bg_with_title)])

    pairs = []
    for i, spec in enumerate(data["blocks"]):
        blk = make_block(spec, t, col_w, acc_idx=i)
        if blk is not None:
            sp = Spacer(1, 2.6 * mm)
            pairs.append((blk, sp, blk.height + 2.6 * mm))

    total = sum(h for _, _, h in pairs)
    target = total / 2
    cols = [[], []]; ch = [0.0, 0.0]; ci = 0
    for blk, sp, h in pairs:
        if ci == 0 and ch[0] > 0 and (ch[0] + h > target or ch[0] + h > col_h):
            ci = 1
        cols[ci].append(blk); cols[ci].append(sp); ch[ci] += h

    story = cols[0] + [FrameBreak()] + cols[1]
    doc.build(story)
    buf.seek(0)
    return buf.read()


# ── UI ────────────────────────────────────────────────────────────────────────
import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import inject_css, hero, steps_indicator, info_bar

inject_css()
hero("Lecture Notes", "AI가 생성한 블록 노트를 확인하고 원하는 테마로 PDF를 저장하세요.",
     eyebrow="Step 3 — Export")
steps_indicator(3)

note       = st.session_state.get("lecture_note", None)
pdf_result = st.session_state.get("pdf_result", None)
from_app   = pdf_result is not None

if not note:
    st.markdown('<div class="card"><p style="color:#555;margin:0;">AI 요약을 먼저 생성해주세요.</p></div>', unsafe_allow_html=True)
    if st.button("요약 생성하러 가기", type="primary"):
        st.switch_page("pages/summarize_page.py")
    st.stop()

note = normalize_note(note)

file_name_ui = st.session_state.get("file_name", "")
if from_app:
    info_bar(file_name_ui, pdf_result.page_count, pdf_result.ai_mode.mode)

st.markdown("<br>", unsafe_allow_html=True)

# 테마 선택
st.markdown('<p class="section-title">PDF 테마</p>', unsafe_allow_html=True)
theme_labels = list(THEMES.keys())
if "selected_theme" not in st.session_state:
    st.session_state["selected_theme"] = theme_labels[0]

theme_cols = st.columns(len(theme_labels))
for col, label in zip(theme_cols, theme_labels):
    with col:
        selected = st.session_state["selected_theme"] == label
        if st.button(label, use_container_width=True,
                     type="primary" if selected else "secondary"):
            st.session_state["selected_theme"] = label
            st.rerun()

chosen_theme = st.session_state["selected_theme"]

st.markdown("<br>", unsafe_allow_html=True)

# 레이아웃 선택 (2단 = A4 가운데 기준 좌/우 두 공간 모두 사용)
st.markdown('<p class="section-title">레이아웃</p>', unsafe_allow_html=True)
layout_labels = {"2단 (좌·우)": "2단", "1단 (한 칸)": "1단"}
if "selected_layout" not in st.session_state:
    st.session_state["selected_layout"] = "2단 (좌·우)"
lay_cols = st.columns(len(layout_labels))
for col, label in zip(lay_cols, layout_labels):
    with col:
        sel = st.session_state["selected_layout"] == label
        if st.button(label, use_container_width=True,
                     type="primary" if sel else "secondary", key=f"lay_{label}"):
            st.session_state["selected_layout"] = label
            st.rerun()
chosen_layout = layout_labels[st.session_state["selected_layout"]]

st.markdown("<br>", unsafe_allow_html=True)

# 노트 제목
st.markdown(
    f'''<div style="border-left:3px solid #2A2A2A;padding:16px 20px;margin-bottom:24px;">
        <p style="font-size:0.7rem;letter-spacing:0.14em;text-transform:uppercase;
                  color:#444;margin:0 0 8px 0;">{chosen_theme} · {len(note.get("blocks", []))} blocks</p>
        <h2 style="font-family:Georgia,serif;font-size:1.5rem;font-weight:600;
                   color:#E8E8E8;margin:0;letter-spacing:-0.01em;">{note.get("title", "강의 노트")}</h2>
    </div>''',
    unsafe_allow_html=True,
)

# 블록 미리보기 (HTML 카드)
TYPE_LABEL = {
    "text": "TEXT", "chips": "CHIPS", "callout": "CALLOUT", "flow": "FLOW",
    "definitions": "DEFINITIONS", "compare": "COMPARE", "tree": "TREE", "qa": "Q&A",
    "table": "TABLE", "steps": "STEPS", "timeline": "TIMELINE", "pros_cons": "PROS/CONS",
    "bar_chart": "BAR", "quadrant": "QUADRANT", "cycle": "CYCLE", "formula": "FORMULA",
}

def _preview_lines(blk: dict) -> str:
    typ = blk.get("type", "text")
    if typ == "chips":
        return " · ".join(str(i) for i in blk.get("items", []))
    if typ == "flow":
        return "  →  ".join(str(s) for s in blk.get("steps", blk.get("items", [])))
    if typ == "definitions":
        return "<br>".join(f"<b>{i.get('term','')}</b> — {i.get('desc','')}"
                           for i in blk.get("items", []) if isinstance(i, dict))
    if typ == "compare":
        cols = blk.get("columns", [])
        return " &nbsp;|&nbsp; ".join(
            f"<b>{c.get('head','')}</b>: " + ", ".join(str(x) for x in c.get("items", []))
            for c in cols)
    if typ == "tree":
        root = blk.get("root", "")
        parts = [f"<b>{root}</b>"]
        for n in blk.get("nodes", []):
            if isinstance(n, dict):
                ch = ", ".join(str(c.get("label", c) if isinstance(c, dict) else c)
                               for c in n.get("children", []))
                parts.append(f"{n.get('label','')}（{ch}）")
        return " / ".join(parts)
    if typ == "qa":
        return "<br>".join(f"Q. {i.get('q','')}<br>A. {i.get('a','')}"
                           for i in blk.get("items", []) if isinstance(i, dict))
    if typ == "table":
        rows = [" / ".join(str(c) for c in r) for r in blk.get("rows", [])[:4]]
        head = " / ".join(str(h) for h in blk.get("headers", []))
        return (f"<b>{head}</b><br>" if head else "") + "<br>".join(rows)
    if typ == "steps":
        return "<br>".join(f"{n}. {s}" for n, s in enumerate(blk.get("items", []), 1))
    if typ == "timeline":
        return "<br>".join(f"<b>{i.get('time','')}</b> {i.get('desc','')}"
                           for i in blk.get("items", []) if isinstance(i, dict))
    if typ == "pros_cons":
        p = ", ".join(str(x) for x in blk.get("pros", []))
        c = ", ".join(str(x) for x in blk.get("cons", []))
        return f"✓ {p}<br>✗ {c}"
    if typ == "bar_chart":
        return "<br>".join(f"{i.get('label','')} — {i.get('value','')}"
                           for i in blk.get("items", []) if isinstance(i, dict))
    if typ == "quadrant":
        return " &nbsp;|&nbsp; ".join(
            f"<b>{c.get('label','')}</b>: " + ", ".join(str(x) for x in c.get("items", []))
            for c in blk.get("cells", []) if isinstance(c, dict))
    if typ == "cycle":
        return "  ↻  ".join(str(s) for s in blk.get("steps", blk.get("items", [])))
    if typ == "formula":
        return "<br>".join(f"<b>{i.get('expr','')}</b> — {i.get('desc','')}"
                           for i in blk.get("items", []) if isinstance(i, dict))
    # text / callout
    out = []
    for i in blk.get("items", []):
        if isinstance(i, dict):
            mark = {"star": "★ ", "wavy": "〰 ", "highlight": "🖍 "}.get(i.get("emphasis", ""), "• ")
            out.append(mark + str(i.get("text", "")))
        else:
            out.append("• " + str(i))
    return "<br>".join(out)

col_left, col_right = st.columns(2, gap="large")
for idx, blk in enumerate(note.get("blocks", [])):
    target = col_left if idx % 2 == 0 else col_right
    typ = blk.get("type", "text")
    title = blk.get("title", "") or TYPE_LABEL.get(typ, typ.upper())
    body = _preview_lines(blk)
    with target:
        st.markdown(
            f'''<div style="background:#121212;border:1px solid #222;border-radius:8px;
                    padding:16px 18px;margin-bottom:12px;">
                <p style="margin:0 0 8px;display:flex;align-items:center;gap:8px;">
                    <span style="font-size:0.62rem;font-weight:700;letter-spacing:0.1em;
                        color:#0A0A0A;background:#888;padding:2px 7px;border-radius:4px;">
                        {TYPE_LABEL.get(typ, typ.upper())}</span>
                    <span style="color:#DDD;font-size:0.82rem;font-weight:600;">{title}</span>
                </p>
                <div style="color:#999;font-size:0.82rem;line-height:1.7;">{body}</div>
            </div>''',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# 원본 JSON 확인
with st.expander("블록 JSON 보기"):
    st.json(note)

# PDF 생성/다운로드
st.markdown('<p class="section-title">PDF 저장</p>', unsafe_allow_html=True)
with st.spinner("PDF 생성 중..."):
    pdf_bytes = build_pdf(note, chosen_theme, chosen_layout)

safe_title = (note.get("title") or "강의_노트").replace(" ", "_").replace(":", "")
st.download_button(
    label=f"PDF 다운로드  —  {chosen_theme}",
    data=pdf_bytes,
    file_name=f"{safe_title}_{chosen_theme}_노트.pdf",
    mime="application/pdf",
    use_container_width=True,
    type="primary",
)

col_a, col_b = st.columns(2)
with col_a:
    if st.button("← 요약 다시하기", use_container_width=True):
        st.switch_page("pages/summarize_page.py")
with col_b:
    if st.button("처음으로", use_container_width=True):
        st.switch_page("app.py")
