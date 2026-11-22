"""magnets：磁铁与磁场知识、材料磁性判断与可打印练习。

面向师生的 Python 标准库小项目，零第三方依赖，兼容 Python 3.9 及以上版本。
"""

from __future__ import annotations

from typing import List

from .model import (
    MAX_MATCH,
    MAX_QUIZ,
    MAGNETIC_KINDS,
    all_materials,
    field_at,
    find_material,
    interact,
    is_attracted,
    magnet_info,
    magnet_kinds,
    magnetic_kind,
    match_items,
    materials_by_kind,
    normalize_pole,
    pole_summary,
    quiz_items,
)
from .render import bar_magnet_svg, match_html, poles_svg, poster_html, quiz_html

__version__: str = "0.1.0"

__all__: List[str] = [
    "__version__",
    "MAX_QUIZ",
    "MAX_MATCH",
    "MAGNETIC_KINDS",
    "normalize_pole",
    "interact",
    "pole_summary",
    "all_materials",
    "find_material",
    "magnetic_kind",
    "is_attracted",
    "materials_by_kind",
    "magnet_kinds",
    "magnet_info",
    "field_at",
    "quiz_items",
    "match_items",
    "bar_magnet_svg",
    "poles_svg",
    "poster_html",
    "quiz_html",
    "match_html",
]
