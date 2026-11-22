"""render 模块的单元测试。"""

from __future__ import annotations

import unittest
from typing import Dict, List, Tuple

from magnets import model
from magnets.render import (
    bar_magnet_svg,
    match_html,
    poles_svg,
    poster_html,
    quiz_html,
)


def _assert_svg_shape(test: unittest.TestCase, svg: str) -> None:
    """检查 SVG 的基本结构，避免依赖本机可能缺失的 XML 解析器。"""
    test.assertTrue(svg.startswith("<svg"))
    test.assertTrue(svg.endswith("</svg>"))
    test.assertEqual(svg.count("<svg"), 1)
    test.assertEqual(svg.count("</svg>"), 1)
    test.assertNotIn("<script", svg)


class TestBarMagnetSvg(unittest.TestCase):
    """条形磁铁 SVG。"""

    def test_returns_svg_document(self) -> None:
        _assert_svg_shape(self, bar_magnet_svg())

    def test_contains_pole_labels(self) -> None:
        svg = bar_magnet_svg()
        self.assertIn(">N<", svg)
        self.assertIn(">S<", svg)

    def test_uses_red_for_north_and_blue_for_south(self) -> None:
        svg = bar_magnet_svg()
        self.assertIn("#d64545", svg)
        self.assertIn("#2f6fdb", svg)

    def test_field_direction_text(self) -> None:
        self.assertIn("N → S", bar_magnet_svg())

    def test_has_field_arrows(self) -> None:
        svg = bar_magnet_svg()
        self.assertIn("marker-end", svg)
        self.assertGreaterEqual(svg.count("<path"), 3)

    def test_accessible_label(self) -> None:
        svg = bar_magnet_svg()
        self.assertIn('role="img"', svg)
        self.assertIn("aria-label=", svg)

    def test_mentions_bar_magnet(self) -> None:
        self.assertIn("条形磁铁", bar_magnet_svg())


class TestPolesSvg(unittest.TestCase):
    """两块磁铁相互作用的 SVG。"""

    def test_returns_svg_document(self) -> None:
        _assert_svg_shape(self, poles_svg("N", "S"))

    def test_opposite_poles_attract(self) -> None:
        svg = poles_svg("N", "S")
        self.assertIn("吸引", svg)
        self.assertIn("异名磁极相互吸引", svg)

    def test_same_poles_repel(self) -> None:
        svg = poles_svg("N", "N")
        self.assertIn("排斥", svg)
        self.assertIn("同名磁极相互排斥", svg)

    def test_contains_pole_labels(self) -> None:
        svg = poles_svg("北极", "南")
        self.assertIn(">N<", svg)
        self.assertIn(">S<", svg)

    def test_contains_two_arrows(self) -> None:
        self.assertEqual(poles_svg("S", "S").count("<line "), 2)

    def test_accessible_label(self) -> None:
        svg = poles_svg("N", "S")
        self.assertIn('role="img"', svg)
        self.assertIn("aria-label=", svg)

    def test_all_four_combinations(self) -> None:
        for first, second in (("N", "N"), ("S", "S"), ("N", "S"), ("S", "N")):
            with self.subTest(pair=(first, second)):
                _assert_svg_shape(self, poles_svg(first, second))

    def test_invalid_pole(self) -> None:
        with self.assertRaises(ValueError):
            poles_svg("X", "N")

    def test_non_string_pole(self) -> None:
        with self.assertRaises(TypeError):
            poles_svg(1, "N")  # type: ignore[arg-type]

    def test_empty_pole(self) -> None:
        with self.assertRaises(ValueError):
            poles_svg("   ", "N")


class TestPosterHtml(unittest.TestCase):
    """可打印海报。"""

    def test_default_title(self) -> None:
        page = poster_html()
        self.assertIn("<title>磁铁与磁场</title>", page)
        self.assertIn("<h1>磁铁与磁场</h1>", page)

    def test_custom_title(self) -> None:
        page = poster_html(title="磁铁入门")
        self.assertIn("<title>磁铁入门</title>", page)
        self.assertIn("<h1>磁铁入门</h1>", page)

    def test_required_sections(self) -> None:
        page = poster_html()
        for heading in ("磁极规律", "材料分类表", "磁铁类型"):
            with self.subTest(heading=heading):
                self.assertIn(heading, page)

    def test_contains_every_material_by_default(self) -> None:
        page = poster_html()
        for record in model.all_materials():
            self.assertIn(str(record["name"]), page)

    def test_selected_materials_only(self) -> None:
        page = poster_html(["铁", "铜"])
        self.assertIn("铁", page)
        self.assertIn("铜", page)
        self.assertNotIn("钕铁硼", page)

    def test_contains_material_table(self) -> None:
        page = poster_html()
        self.assertIn("<table>", page)
        self.assertGreaterEqual(page.count("<tr>"), len(model.all_materials()))

    def test_contains_magnet_cards(self) -> None:
        page = poster_html()
        for kind in model.magnet_kinds():
            self.assertIn(kind, page)
        self.assertIn("kind-card", page)

    def test_escapes_title(self) -> None:
        page = poster_html(title="<script>alert(1)</script>")
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)

    def test_print_and_a4_rules(self) -> None:
        page = poster_html()
        self.assertIn("@media print", page)
        self.assertIn("@page", page)
        self.assertIn("size:A4", page)

    def test_document_metadata(self) -> None:
        page = poster_html()
        self.assertIn('lang="zh-CN"', page)
        self.assertIn('charset="utf-8"', page)
        self.assertTrue(page.startswith("<!DOCTYPE html>"))

    def test_empty_title(self) -> None:
        with self.assertRaises(ValueError):
            poster_html(title="   ")

    def test_non_string_title(self) -> None:
        with self.assertRaises(TypeError):
            poster_html(title=None)  # type: ignore[arg-type]

    def test_non_sequence_materials(self) -> None:
        with self.assertRaises(TypeError):
            poster_html("铁")  # type: ignore[arg-type]

    def test_empty_materials(self) -> None:
        with self.assertRaises(ValueError):
            poster_html([])

    def test_unknown_material(self) -> None:
        with self.assertRaises(ValueError):
            poster_html(["不存在的材料"])

    def test_duplicate_material(self) -> None:
        with self.assertRaises(ValueError):
            poster_html(["铁", "铁"])

    def test_non_string_material(self) -> None:
        with self.assertRaises(TypeError):
            poster_html([1])  # type: ignore[list-item]


class TestQuizHtml(unittest.TestCase):
    """测验页。"""

    def _items(self) -> List[Dict[str, object]]:
        return model.quiz_items(4, 2)

    def test_contains_questions_and_options(self) -> None:
        items = self._items()
        page = quiz_html(items, "小测")
        for item in items:
            self.assertIn(str(item["question"]), page)
            for option in item["options"]:
                self.assertIn(str(option), page)

    def test_answers_hidden_by_default(self) -> None:
        page = quiz_html(self._items(), "小测")
        self.assertNotIn("答案：", page)
        self.assertNotIn("解析：", page)

    def test_answers_shown_when_requested(self) -> None:
        page = quiz_html(self._items(), "小测", with_answers=True)
        self.assertIn("答案：", page)
        self.assertIn("解析：", page)

    def test_shows_question_count(self) -> None:
        self.assertIn("共 4 题", quiz_html(self._items(), "小测"))

    def test_escapes_dynamic_text(self) -> None:
        items: List[Dict[str, object]] = [
            {
                "index": 1,
                "kind": "pole",
                "question": "<script>alert(1)</script>",
                "options": ["A&B", "<b>", "C", "D"],
                "answer": "A&B",
                "explanation": "<img src=x>",
            }
        ]
        page = quiz_html(items, "<小测>", with_answers=True)
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertIn("A&amp;B", page)
        self.assertIn("&lt;img src=x&gt;", page)
        self.assertIn("&lt;小测&gt;", page)

    def test_empty_items(self) -> None:
        with self.assertRaises(ValueError):
            quiz_html([], "小测")

    def test_non_sequence_items(self) -> None:
        for value in ("abc", 123, None):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    quiz_html(value, "小测")  # type: ignore[arg-type]

    def test_non_dict_item(self) -> None:
        with self.assertRaises(TypeError):
            quiz_html(["题目"], "小测")  # type: ignore[list-item]

    def test_missing_question(self) -> None:
        with self.assertRaises(ValueError):
            quiz_html([{"options": ["A"], "answer": "A"}], "小测")

    def test_invalid_options(self) -> None:
        with self.assertRaises(ValueError):
            quiz_html([{"question": "q", "options": "A", "answer": "A"}], "小测")

    def test_empty_options(self) -> None:
        with self.assertRaises(ValueError):
            quiz_html([{"question": "q", "options": [], "answer": "A"}], "小测")

    def test_empty_option_text(self) -> None:
        with self.assertRaises(ValueError):
            quiz_html(
                [{"question": "q", "options": ["A", "  "], "answer": "A"}],
                "小测",
            )

    def test_answer_outside_options(self) -> None:
        with self.assertRaises(ValueError):
            quiz_html(
                [{"question": "q", "options": ["A", "B"], "answer": "C"}],
                "小测",
            )

    def test_with_answers_must_be_bool(self) -> None:
        with self.assertRaises(TypeError):
            quiz_html(self._items(), "小测", with_answers="yes")  # type: ignore[arg-type]

    def test_empty_title(self) -> None:
        with self.assertRaises(ValueError):
            quiz_html(self._items(), "")

    def test_non_string_title(self) -> None:
        with self.assertRaises(TypeError):
            quiz_html(self._items(), 1)  # type: ignore[arg-type]

    def test_print_media_query(self) -> None:
        self.assertIn("@media print", quiz_html(self._items(), "小测"))


class TestMatchHtml(unittest.TestCase):
    """配对练习页。"""

    def _pairs(self) -> List[Tuple[str, str]]:
        return [("铁", "铁磁性"), ("铜", "抗磁性"), ("磁针", "制作指南针")]

    def test_contains_pairs(self) -> None:
        page = match_html(self._pairs(), "配对")
        for left, right in self._pairs():
            self.assertIn(left, page)
            self.assertIn(right, page)

    def test_shows_pair_count(self) -> None:
        self.assertIn("共 3 组配对", match_html(self._pairs(), "配对"))

    def test_escapes_dynamic_text(self) -> None:
        page = match_html([("<b>铁</b>", "铁磁性")], "<配对>")
        self.assertNotIn("<b>铁</b>", page)
        self.assertIn("&lt;b&gt;铁&lt;/b&gt;", page)
        self.assertIn("&lt;配对&gt;", page)

    def test_empty_pairs(self) -> None:
        with self.assertRaises(ValueError):
            match_html([], "配对")

    def test_non_sequence(self) -> None:
        for value in ("abc", 123, None):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    match_html(value, "配对")  # type: ignore[arg-type]

    def test_bad_pair_shape(self) -> None:
        for pair in (("铁",), ("铁", "铁磁性", "多"), "铁"):
            with self.subTest(pair=pair):
                with self.assertRaises(TypeError):
                    match_html([pair], "配对")  # type: ignore[list-item]

    def test_empty_side(self) -> None:
        with self.assertRaises(ValueError):
            match_html([("   ", "铁磁性")], "配对")
        with self.assertRaises(ValueError):
            match_html([("铁", "  ")], "配对")

    def test_empty_title(self) -> None:
        with self.assertRaises(ValueError):
            match_html(self._pairs(), "  ")

    def test_non_string_title(self) -> None:
        with self.assertRaises(TypeError):
            match_html(self._pairs(), 123)  # type: ignore[arg-type]

    def test_print_media_query(self) -> None:
        self.assertIn("@media print", match_html(self._pairs(), "配对"))


if __name__ == "__main__":
    unittest.main()
