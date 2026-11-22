"""把磁铁知识渲染为 SVG 与可打印的 HTML 页面。

所有动态文本都会经过 :func:`html.escape`，页面内置 A4 打印样式。
"""

from __future__ import annotations

import html
from collections.abc import Sequence as _ABCSequence
from typing import Dict, List, Optional, Sequence, Tuple

from .model import (
    MAGNETIC_KINDS,
    all_materials,
    find_material,
    interact,
    magnet_info,
    magnet_kinds,
    normalize_pole,
)

__all__ = [
    "bar_magnet_svg",
    "poles_svg",
    "poster_html",
    "quiz_html",
    "match_html",
]

_POLE_COLORS: Dict[str, str] = {"N": "#d64545", "S": "#2f6fdb"}
_FONT: str = "PingFang SC, Microsoft YaHei, Noto Sans CJK SC, sans-serif"


def _require_title(title: str) -> str:
    """校验标题并返回去空白后的值。"""
    if not isinstance(title, str):
        raise TypeError("标题必须是字符串")
    value = title.strip()
    if not value:
        raise ValueError("标题不能为空")
    return value


def _escape(value: object) -> str:
    """把任意文本安全地放入 HTML。"""
    return html.escape(str(value), quote=True)


def _opposite(pole: str) -> str:
    """返回相反磁极。"""
    return "S" if pole == "N" else "N"


def bar_magnet_svg() -> str:
    """生成一根条形磁铁，N 红 S 蓝，外部磁场线箭头由 N 指向 S。"""
    arrow = "#7b8794"
    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 320" '
        'width="520" height="320" role="img" '
        'aria-label="条形磁铁，N 极在左为红色，S 极在右为蓝色，外部磁场线从 N 极指向 S 极">',
        "<defs>",
        '<marker id="bar-field-arrow" markerWidth="10" markerHeight="8" refX="9" '
        'refY="4" orient="auto" markerUnits="strokeWidth">',
        '<path d="M0,0 L10,4 L0,8 z" fill="%s"/>' % arrow,
        "</marker>",
        "</defs>",
        '<rect x="0" y="0" width="520" height="320" rx="18" fill="#f7f9ff"/>',
        '<text x="260" y="42" text-anchor="middle" font-family="%s" '
        'font-size="22" font-weight="700" fill="#1f2933">条形磁铁的外部磁场</text>'
        % _FONT,
        '<rect x="160" y="110" width="100" height="80" rx="8" fill="%s"/>'
        % _POLE_COLORS["N"],
        '<rect x="260" y="110" width="100" height="80" rx="8" fill="%s"/>'
        % _POLE_COLORS["S"],
        '<text x="210" y="162" text-anchor="middle" font-family="%s" '
        'font-size="38" font-weight="700" fill="#ffffff">N</text>' % _FONT,
        '<text x="310" y="162" text-anchor="middle" font-family="%s" '
        'font-size="38" font-weight="700" fill="#ffffff">S</text>' % _FONT,
        '<path d="M185 110 C 180 30, 340 30, 335 110" fill="none" stroke="%s" '
        'stroke-width="3" marker-end="url(#bar-field-arrow)"/>' % arrow,
        '<path d="M185 190 C 180 270, 340 270, 335 190" fill="none" stroke="%s" '
        'stroke-width="3" marker-end="url(#bar-field-arrow)"/>' % arrow,
        '<text x="260" y="250" text-anchor="middle" font-family="%s" '
        'font-size="18" font-weight="700" fill="#334e68">外部磁场方向：N → S</text>'
        % _FONT,
        '<text x="260" y="282" text-anchor="middle" font-family="%s" '
        'font-size="14" fill="#52606d">磁感线从 N 极出发，绕过外部回到 S 极。</text>'
        % _FONT,
        "</svg>",
    ]
    return "".join(parts)


def poles_svg(pole_a: str, pole_b: str) -> str:
    """生成两块磁铁相对时的 SVG，吸引或排斥箭头示意。"""
    first = normalize_pole(pole_a)
    second = normalize_pole(pole_b)
    result = interact(first, second)
    first_opposite = _opposite(first)
    second_opposite = _opposite(second)
    explanation = (
        "同名磁极相互排斥" if result == "排斥" else "异名磁极相互吸引"
    )
    arrow_color = "#2f6fdb" if result == "吸引" else "#d64545"
    aria = "%s 极与 %s 极靠近时相互%s" % (first, second, result)

    if result == "吸引":
        left_arrow = (
            '<line x1="192" y1="214" x2="246" y2="214" stroke="%s" '
            'stroke-width="4" marker-end="url(#pole-arrowhead)"/>' % arrow_color
        )
        right_arrow = (
            '<line x1="328" y1="214" x2="274" y2="214" stroke="%s" '
            'stroke-width="4" marker-end="url(#pole-arrowhead)"/>' % arrow_color
        )
    else:
        left_arrow = (
            '<line x1="246" y1="214" x2="192" y2="214" stroke="%s" '
            'stroke-width="4" marker-end="url(#pole-arrowhead)"/>' % arrow_color
        )
        right_arrow = (
            '<line x1="274" y1="214" x2="328" y2="214" stroke="%s" '
            'stroke-width="4" marker-end="url(#pole-arrowhead)"/>' % arrow_color
        )

    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 300" '
        'width="460" height="300" role="img" aria-label="%s">' % _escape(aria),
        "<defs>",
        '<marker id="pole-arrowhead" markerWidth="10" markerHeight="8" refX="9" '
        'refY="4" orient="auto" markerUnits="strokeWidth">',
        '<path d="M0,0 L10,4 L0,8 z" fill="%s"/>' % arrow_color,
        "</marker>",
        "</defs>",
        '<rect x="0" y="0" width="460" height="300" rx="18" fill="#f7f9ff"/>',
        '<text x="230" y="42" text-anchor="middle" font-family="%s" '
        'font-size="22" font-weight="700" fill="#1f2933">磁极相互作用</text>' % _FONT,
        '<text x="230" y="70" text-anchor="middle" font-family="%s" '
        'font-size="15" fill="#52606d">%s 极 与 %s 极：%s</text>'
        % (_FONT, _escape(first), _escape(second), _escape(result)),
        '<rect x="24" y="110" width="82" height="76" rx="10" fill="%s"/>'
        % _POLE_COLORS[first_opposite],
        '<rect x="106" y="110" width="84" height="76" rx="10" fill="%s"/>'
        % _POLE_COLORS[first],
        '<rect x="270" y="110" width="84" height="76" rx="10" fill="%s"/>'
        % _POLE_COLORS[second],
        '<rect x="354" y="110" width="82" height="76" rx="10" fill="%s"/>'
        % _POLE_COLORS[second_opposite],
        '<text x="65" y="158" text-anchor="middle" font-size="32" font-weight="700" '
        'fill="#ffffff" font-family="%s">%s</text>'
        % (_FONT, _escape(first_opposite)),
        '<text x="148" y="158" text-anchor="middle" font-size="32" font-weight="700" '
        'fill="#ffffff" font-family="%s">%s</text>' % (_FONT, _escape(first)),
        '<text x="312" y="158" text-anchor="middle" font-size="32" font-weight="700" '
        'fill="#ffffff" font-family="%s">%s</text>' % (_FONT, _escape(second)),
        '<text x="395" y="158" text-anchor="middle" font-size="32" font-weight="700" '
        'fill="#ffffff" font-family="%s">%s</text>'
        % (_FONT, _escape(second_opposite)),
        left_arrow,
        right_arrow,
        '<text x="230" y="258" text-anchor="middle" font-family="%s" '
        'font-size="22" font-weight="700" fill="%s">%s</text>'
        % (_FONT, arrow_color, _escape(result)),
        '<text x="230" y="284" text-anchor="middle" font-family="%s" '
        'font-size="14" fill="#52606d">%s</text>' % (_FONT, _escape(explanation)),
        "</svg>",
    ]
    return "".join(parts)


def _page_style() -> str:
    """返回海报与练习页共用的基础样式。"""
    return (
        ":root{--ink:#1f2933;--muted:#52606d;--line:#d9e2ec;--blue:#2f6fdb;"
        "--red:#d64545;--bg:#f4f6fb;}"
        "*{box-sizing:border-box;}"
        'body{margin:0;background:var(--bg);color:var(--ink);'
        'font-family:-apple-system,"PingFang SC","Hiragino Sans GB",'
        '"Microsoft YaHei","Noto Sans CJK SC",sans-serif;line-height:1.7;}'
        ".page{width:210mm;min-height:297mm;margin:0 auto;padding:14mm 16mm;"
        "background:#fff;box-shadow:0 6px 24px rgba(15,23,42,.12);}"
        "h1{margin:0 0 6px;font-size:26px;letter-spacing:.5px;}"
        "h2{margin:24px 0 10px;font-size:19px;border-left:6px solid var(--blue);"
        "padding-left:10px;}"
        ".meta{color:var(--muted);font-size:13px;margin-bottom:14px;}"
        ".badge{display:inline-block;padding:2px 9px;border-radius:999px;"
        "font-size:12px;font-weight:600;}"
        ".badge.yes{background:#fde8e8;color:#a61b1b;}"
        ".badge.mid{background:#fff4d6;color:#8a5a00;}"
        ".badge.no{background:#e6f0ff;color:#1d4ed8;}"
        ".card{background:#f8fafc;border:1px solid var(--line);border-radius:12px;"
        "padding:14px 18px;}"
        ".card ul{margin:6px 0 0;padding-left:20px;}"
        ".card li{margin:4px 0;}"
        ".kind-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));"
        "gap:12px;}"
        ".kind-card{background:#f8fafc;border:1px solid var(--line);"
        "border-radius:12px;padding:12px 16px;}"
        ".kind-card h3{margin:0 0 6px;font-size:16px;color:#243b53;}"
        ".kind-card p{margin:4px 0;font-size:13px;color:#334e68;}"
        "table{width:100%;border-collapse:collapse;font-size:13px;}"
        "th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;"
        "vertical-align:top;}"
        "th{background:#eef3fb;font-weight:700;}"
        "tbody tr:nth-child(even){background:#fafcff;}"
        ".tip{color:var(--muted);font-size:12px;margin-top:8px;}"
        "@media print{"
        "body{background:#fff;-webkit-print-color-adjust:exact;"
        "print-color-adjust:exact;}"
        ".page{width:auto;min-height:auto;margin:0;padding:0;box-shadow:none;}"
        "h2{page-break-after:avoid;}"
        "tr,.quiz-item,.pair-row,.kind-card{page-break-inside:avoid;}"
        "}"
        "@page{size:A4;margin:12mm;}"
    )


def _page_head(title: str) -> str:
    """构造 HTML 文档头。"""
    return (
        "<!DOCTYPE html>"
        '<html lang="zh-CN">'
        "<head>"
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>%s</title>"
        "<style>%s</style>"
        "</head>"
        "<body>"
        '<main class="page">'
        % (_escape(title), _page_style())
    )


def _resolve_materials(
    materials: Optional[Sequence[str]],
) -> List[Dict[str, object]]:
    """把材料名称列表解析为记录列表；为空时使用全部材料。"""
    if materials is None:
        return all_materials()
    if isinstance(materials, (str, bytes)) or not isinstance(
        materials, _ABCSequence
    ):
        raise TypeError("材料列表必须是字符串序列")
    names = list(materials)
    if not names:
        raise ValueError("材料列表不能为空")
    records: List[Dict[str, object]] = []
    seen: Dict[str, bool] = {}
    for index, name in enumerate(names):
        if not isinstance(name, str):
            raise TypeError("第 %d 个材料名称必须是字符串" % (index + 1))
        record = find_material(name)
        key = str(record["name"])
        if key in seen:
            raise ValueError("材料重复：%s" % key)
        seen[key] = True
        records.append(record)
    return records


def poster_html(
    materials: Optional[Sequence[str]] = None,
    title: str = "磁铁与磁场",
) -> str:
    """生成包含磁极规则、材料分类表与磁铁类型卡片的可打印海报。"""
    heading = _require_title(title)
    records = _resolve_materials(materials)

    counts: Dict[str, int] = {kind: 0 for kind in MAGNETIC_KINDS}
    for record in records:
        counts[str(record["kind"])] += 1

    rows: List[str] = []
    for record in records:
        kind = str(record["kind"])
        if kind == "铁磁性":
            badge = '<span class="badge yes">铁磁性</span>'
        elif kind == "顺磁性":
            badge = '<span class="badge mid">顺磁性</span>'
        else:
            badge = '<span class="badge no">抗磁性</span>'
        rows.append(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (
                _escape(record["name"]),
                _escape(record["category"]),
                badge,
                _escape(record["note"]),
            )
        )

    cards: List[str] = []
    for kind in magnet_kinds():
        info = magnet_info(kind)
        cards.append(
            '<article class="kind-card"><h3>%s</h3>'
            "<p><strong>特点：</strong>%s</p>"
            "<p><strong>用途：</strong>%s</p>"
            "<p>%s</p></article>"
            % (
                _escape(info["kind"]),
                _escape(info["feature"]),
                _escape(info["use"]),
                _escape(info["note"]),
            )
        )

    return (
        _page_head(heading)
        + '<header class="card">'
        + "<h1>%s</h1>" % _escape(heading)
        + '<p class="meta">磁铁与磁场 · 磁极相互作用、材料磁性判断与磁铁种类</p>'
        + '<p class="meta">本次收录 %d 种材料：铁磁性 %d 种，顺磁性 %d 种，抗磁性 %d 种。</p>'
        % (
            len(records),
            counts["铁磁性"],
            counts["顺磁性"],
            counts["抗磁性"],
        )
        + "</header>"
        + "<h2>磁极规律</h2>"
        + '<section class="card"><ul>'
        + "<li><strong>同名磁极相互排斥</strong>：N 与 N、S 与 S 靠近时会互相推开。</li>"
        + "<li><strong>异名磁极相互吸引</strong>：N 与 S 靠近时会互相吸住。</li>"
        + "<li><strong>N 极指向北</strong>：能自由转动的磁针静止时，N 极指向地理北方。</li>"
        + "<li><strong>S 极指向南</strong>：磁针的 S 极指向地理南方。</li>"
        + "<li><strong>磁极成对出现</strong>：把磁铁切成两段，每段仍然有 N 极和 S 极。</li>"
        + "</ul></section>"
        + "<h2>材料分类表</h2>"
        + "<table><thead><tr><th>材料</th><th>材料类别</th>"
        + "<th>磁性类别</th><th>备注</th></tr></thead>"
        + "<tbody>%s</tbody></table>" % "".join(rows)
        + '<p class="tip">提示：只有铁磁性材料会被磁铁明显吸引；顺磁性、抗磁性材料几乎不被吸引。</p>'
        + "<h2>磁铁类型</h2>"
        + '<section class="kind-grid">%s</section>' % "".join(cards)
        + '<p class="tip">Math &amp; Physics Lab · MIT © 2026 eastyou</p>'
        + "</main></body></html>"
    )


def _validate_quiz_items(
    items: Sequence[Dict[str, object]],
) -> List[Dict[str, object]]:
    """校验题目数据结构，返回浅拷贝列表。"""
    if isinstance(items, (str, bytes)) or not isinstance(items, _ABCSequence):
        raise TypeError("题目列表必须是序列")
    records = list(items)
    if not records:
        raise ValueError("题目列表不能为空")
    checked: List[Dict[str, object]] = []
    for position, item in enumerate(records):
        if not isinstance(item, dict):
            raise TypeError("第 %d 道题必须是字典" % (position + 1))
        question = item.get("question")
        options = item.get("options")
        answer = item.get("answer")
        if not isinstance(question, str) or not question.strip():
            raise ValueError("第 %d 道题缺少有效的问题" % (position + 1))
        if isinstance(options, (str, bytes)) or not isinstance(
            options, _ABCSequence
        ):
            raise ValueError("第 %d 道题的选项必须是序列" % (position + 1))
        option_list = list(options)
        if not option_list:
            raise ValueError("第 %d 道题的选项不能为空" % (position + 1))
        for option in option_list:
            if not isinstance(option, str) or not option.strip():
                raise ValueError("第 %d 道题存在空选项" % (position + 1))
        if not isinstance(answer, str) or answer not in option_list:
            raise ValueError("第 %d 道题的答案必须位于选项中" % (position + 1))
        checked.append(dict(item))
    return checked


def quiz_html(
    items: Sequence[Dict[str, object]],
    title: str,
    with_answers: bool = False,
) -> str:
    """生成可打印的测验页；``with_answers`` 为真时附答案与解析。"""
    if not isinstance(with_answers, bool):
        raise TypeError("with_answers 必须是布尔值")
    heading = _require_title(title)
    records = _validate_quiz_items(items)

    cards: List[str] = []
    for record in records:
        option_list = list(record["options"])
        options_html = "".join(
            '<li><span class="opt-key">%s</span>%s</li>'
            % (chr(ord("A") + offset), _escape(option))
            for offset, option in enumerate(option_list)
        )
        answer_html = ""
        if with_answers:
            answer_html = (
                '<div class="answer"><strong>答案：</strong>%s'
                "<div><strong>解析：</strong>%s</div></div>"
                % (_escape(record["answer"]), _escape(record.get("explanation", "")))
            )
        cards.append(
            '<li class="quiz-item"><p class="question">%s. %s</p>'
            '<ol class="options">%s</ol>%s</li>'
            % (
                _escape(record.get("index", "")),
                _escape(record["question"]),
                options_html,
                answer_html,
            )
        )

    extra_style = (
        ".quiz-item{margin:0 0 14px;padding:12px 16px;border:1px solid var(--line);"
        "border-radius:12px;background:#fbfcff;list-style:none;}"
        ".question{margin:0 0 8px;font-weight:600;}"
        ".options{list-style:none;margin:0;padding:0;display:grid;"
        "grid-template-columns:1fr 1fr;gap:6px 18px;}"
        ".opt-key{display:inline-block;width:22px;height:22px;line-height:22px;"
        "text-align:center;border-radius:50%;background:#e8effc;color:#1d4ed8;"
        "font-size:12px;font-weight:700;margin-right:6px;}"
        ".answer{margin-top:8px;padding:8px 10px;border-left:4px solid var(--blue);"
        "background:#eef5ff;font-size:13px;color:#243b53;}"
        ".quiz-list{padding-left:0;margin:0;}"
        "@media print{.options{grid-template-columns:1fr 1fr;}}"
    )

    return (
        _page_head(heading)
        + "<h1>%s</h1>" % _escape(heading)
        + '<p class="meta">共 %d 题 · %s</p>'
        % (len(records), "含答案与解析" if with_answers else "闭卷练习")
        + "<style>%s</style>" % extra_style
        + '<ol class="quiz-list">%s</ol>' % "".join(cards)
        + '<p class="tip">Math &amp; Physics Lab · MIT © 2026 eastyou</p>'
        + "</main></body></html>"
    )


def _validate_pairs(pairs: Sequence[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """校验配对数据，返回字符串二元组列表。"""
    if isinstance(pairs, (str, bytes)) or not isinstance(pairs, _ABCSequence):
        raise TypeError("配对列表必须是序列")
    records = list(pairs)
    if not records:
        raise ValueError("配对列表不能为空")
    checked: List[Tuple[str, str]] = []
    for position, pair in enumerate(records):
        if (
            isinstance(pair, (str, bytes))
            or not isinstance(pair, _ABCSequence)
            or len(pair) != 2
        ):
            raise TypeError("第 %d 组配对必须是两个元素的元组" % (position + 1))
        left, right = pair[0], pair[1]
        if not isinstance(left, str) or not left.strip():
            raise ValueError("第 %d 组配对的左侧不能为空" % (position + 1))
        if not isinstance(right, str) or not right.strip():
            raise ValueError("第 %d 组配对的右侧不能为空" % (position + 1))
        checked.append((left, right))
    return checked


def match_html(pairs: Sequence[Tuple[str, str]], title: str) -> str:
    """生成材料—磁性、磁铁—用途的配对练习表（含参考答案）。"""
    heading = _require_title(title)
    records = _validate_pairs(pairs)

    rows: List[str] = []
    for offset, pair in enumerate(records):
        rows.append(
            '<tr class="pair-row"><td class="num">%d</td><td>%s</td><td>%s</td></tr>'
            % (offset + 1, _escape(pair[0]), _escape(pair[1]))
        )

    extra_style = (
        ".match-table td{padding:9px 10px;}"
        ".match-table td.num{width:44px;text-align:center;color:var(--muted);}"
        ".match-table th:nth-child(1){width:44px;text-align:center;}"
        ".hint{font-size:13px;color:var(--muted);}"
    )

    return (
        _page_head(heading)
        + "<h1>%s</h1>" % _escape(heading)
        + '<p class="meta">共 %d 组配对 · 先独立完成，再对照右列检查。</p>'
        % len(records)
        + "<style>%s</style>" % extra_style
        + '<p class="hint">左列是材料或磁铁，右列是磁性类别或用途（参考答案）。</p>'
        + '<table class="match-table"><thead><tr><th>序号</th><th>左侧</th>'
        + "<th>对应结果</th></tr></thead>"
        + "<tbody>%s</tbody></table>" % "".join(rows)
        + '<p class="tip">Math &amp; Physics Lab · MIT © 2026 eastyou</p>'
        + "</main></body></html>"
    )
