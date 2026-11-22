"""model 模块的单元测试。"""

from __future__ import annotations

import unittest
from typing import Dict, List

from magnets import model


class TestPoleNormalization(unittest.TestCase):
    """磁极规范化。"""

    def test_uppercase_letters(self) -> None:
        self.assertEqual(model.normalize_pole("N"), "N")
        self.assertEqual(model.normalize_pole("S"), "S")

    def test_lowercase_letters(self) -> None:
        self.assertEqual(model.normalize_pole("n"), "N")
        self.assertEqual(model.normalize_pole("s"), "S")

    def test_north_words(self) -> None:
        self.assertEqual(model.normalize_pole("北极"), "N")
        self.assertEqual(model.normalize_pole("北"), "N")

    def test_south_words(self) -> None:
        self.assertEqual(model.normalize_pole("南极"), "S")
        self.assertEqual(model.normalize_pole("南"), "S")

    def test_strips_whitespace(self) -> None:
        self.assertEqual(model.normalize_pole("  N  "), "N")
        self.assertEqual(model.normalize_pole("\t南极\n"), "S")

    def test_invalid_value(self) -> None:
        for value in ("X", "东", "NS", "north"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    model.normalize_pole(value)

    def test_empty_value(self) -> None:
        for value in ("", "   ", "\n"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    model.normalize_pole(value)

    def test_non_string(self) -> None:
        for value in (123, 1.5, None, ["N"], True):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    model.normalize_pole(value)  # type: ignore[arg-type]


class TestInteract(unittest.TestCase):
    """磁极相互作用。"""

    def test_same_north_repels(self) -> None:
        self.assertEqual(model.interact("N", "N"), "排斥")

    def test_same_south_repels(self) -> None:
        self.assertEqual(model.interact("S", "S"), "排斥")

    def test_opposite_attracts(self) -> None:
        self.assertEqual(model.interact("N", "S"), "吸引")
        self.assertEqual(model.interact("S", "N"), "吸引")

    def test_aliases(self) -> None:
        self.assertEqual(model.interact("北极", "南"), "吸引")
        self.assertEqual(model.interact("北", "北"), "排斥")

    def test_invalid_pole(self) -> None:
        with self.assertRaises(ValueError):
            model.interact("X", "N")

    def test_non_string_pole(self) -> None:
        with self.assertRaises(TypeError):
            model.interact(None, "N")  # type: ignore[arg-type]


class TestPoleSummary(unittest.TestCase):
    """磁极说明。"""

    def test_has_expected_keys(self) -> None:
        self.assertEqual(set(model.pole_summary().keys()), {"N", "S", "规律"})

    def test_mentions_rules(self) -> None:
        summary = model.pole_summary()
        self.assertIn("北", summary["N"])
        self.assertIn("南", summary["S"])
        self.assertIn("排斥", summary["规律"])
        self.assertIn("吸引", summary["规律"])


class TestMaterials(unittest.TestCase):
    """材料数据、分类与查询。"""

    def test_at_least_twenty_materials(self) -> None:
        self.assertGreaterEqual(len(model.all_materials()), 20)

    def test_names_are_unique(self) -> None:
        names = [str(record["name"]) for record in model.all_materials()]
        self.assertEqual(len(names), len(set(names)))

    def test_required_fields(self) -> None:
        for record in model.all_materials():
            with self.subTest(name=record.get("name")):
                self.assertEqual(
                    set(record.keys()), {"name", "kind", "category", "note"}
                )
                self.assertIsInstance(record["name"], str)
                self.assertIsInstance(record["kind"], str)
                self.assertIsInstance(record["category"], str)
                self.assertIsInstance(record["note"], str)

    def test_kinds_are_limited(self) -> None:
        for record in model.all_materials():
            with self.subTest(name=record["name"]):
                self.assertIn(record["kind"], model.MAGNETIC_KINDS)

    def test_all_three_kinds_present(self) -> None:
        kinds = {str(record["kind"]) for record in model.all_materials()}
        self.assertEqual(kinds, set(model.MAGNETIC_KINDS))

    def test_core_ferromagnetic_metals(self) -> None:
        for name in ("铁", "钴", "镍"):
            with self.subTest(name=name):
                self.assertEqual(model.magnetic_kind(name), "铁磁性")
                self.assertTrue(model.is_attracted(name))

    def test_common_diamagnetic_materials(self) -> None:
        for name in ("铜", "铝", "金", "银", "塑料", "木头"):
            with self.subTest(name=name):
                self.assertFalse(model.is_attracted(name))

    def test_paramagnetic_materials(self) -> None:
        for name in ("铝", "铂", "钛"):
            with self.subTest(name=name):
                self.assertEqual(model.magnetic_kind(name), "顺磁性")
                self.assertFalse(model.is_attracted(name))

    def test_diamagnetic_materials(self) -> None:
        for name in ("铜", "金", "水", "玻璃"):
            with self.subTest(name=name):
                self.assertEqual(model.magnetic_kind(name), "抗磁性")
                self.assertFalse(model.is_attracted(name))

    def test_only_ferromagnetic_is_attracted(self) -> None:
        for record in model.all_materials():
            with self.subTest(name=record["name"]):
                expected = record["kind"] == "铁磁性"
                self.assertEqual(
                    model.is_attracted(str(record["name"])), expected
                )

    def test_materials_by_kind(self) -> None:
        for kind in model.MAGNETIC_KINDS:
            with self.subTest(kind=kind):
                names = model.materials_by_kind(kind)
                self.assertTrue(names)
                for name in names:
                    self.assertEqual(model.magnetic_kind(name), kind)

    def test_materials_by_kind_covers_all(self) -> None:
        total = sum(
            len(model.materials_by_kind(kind)) for kind in model.MAGNETIC_KINDS
        )
        self.assertEqual(total, len(model.all_materials()))

    def test_materials_by_kind_rejects_unknown(self) -> None:
        with self.assertRaises(ValueError):
            model.materials_by_kind("超磁性")

    def test_materials_by_kind_rejects_non_string(self) -> None:
        with self.assertRaises(TypeError):
            model.materials_by_kind(1)  # type: ignore[arg-type]

    def test_find_material_returns_fields(self) -> None:
        record = model.find_material("铁")
        self.assertEqual(record["name"], "铁")
        self.assertEqual(record["kind"], "铁磁性")
        self.assertTrue(str(record["note"]).strip())

    def test_find_material_strips_whitespace(self) -> None:
        self.assertEqual(model.find_material("  铜  ")["name"], "铜")

    def test_find_material_returns_copy(self) -> None:
        record = model.find_material("铁")
        record["name"] = "被修改"
        self.assertEqual(model.find_material("铁")["name"], "铁")

    def test_all_materials_returns_copies(self) -> None:
        records = model.all_materials()
        records[0]["name"] = "被修改"
        self.assertNotEqual(model.all_materials()[0]["name"], "被修改")

    def test_unknown_material(self) -> None:
        with self.assertRaises(ValueError):
            model.find_material("不存在的材料")

    def test_empty_material_name(self) -> None:
        with self.assertRaises(ValueError):
            model.find_material("   ")

    def test_non_string_material_name(self) -> None:
        for value in (123, None, True, ["铁"]):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    model.find_material(value)  # type: ignore[arg-type]


class TestMagnetInfo(unittest.TestCase):
    """磁铁种类信息。"""

    def test_at_least_six_kinds(self) -> None:
        self.assertGreaterEqual(len(model.magnet_kinds()), 6)

    def test_expected_kinds(self) -> None:
        kinds = model.magnet_kinds()
        for name in ("条形磁铁", "蹄形磁铁", "环形磁铁", "圆片磁铁", "磁针", "电磁铁"):
            with self.subTest(name=name):
                self.assertIn(name, kinds)

    def test_info_fields(self) -> None:
        info = model.magnet_info("条形")
        self.assertEqual(
            set(info.keys()), {"kind", "feature", "use", "note"}
        )
        for key in ("kind", "feature", "use", "note"):
            self.assertIsInstance(info[key], str)
            self.assertTrue(str(info[key]).strip())

    def test_aliases(self) -> None:
        self.assertEqual(model.magnet_info("马蹄形磁铁")["kind"], "蹄形磁铁")
        self.assertEqual(model.magnet_info("指南针")["kind"], "磁针")

    def test_usable_info_for_every_kind(self) -> None:
        for kind in model.magnet_kinds():
            with self.subTest(kind=kind):
                info = model.magnet_info(kind)
                self.assertEqual(info["kind"], kind)
                self.assertTrue(str(info["use"]).strip())
                self.assertTrue(str(info["feature"]).strip())

    def test_returns_copy(self) -> None:
        info = model.magnet_info("磁针")
        info["kind"] = "被修改"
        self.assertEqual(model.magnet_info("磁针")["kind"], "磁针")

    def test_unknown_kind(self) -> None:
        with self.assertRaises(ValueError):
            model.magnet_info("超级磁铁")

    def test_empty_kind(self) -> None:
        with self.assertRaises(ValueError):
            model.magnet_info("  ")

    def test_non_string_kind(self) -> None:
        for value in (1, None, True):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    model.magnet_info(value)  # type: ignore[arg-type]


class TestFieldAt(unittest.TestCase):
    """简化磁场方向。"""

    def test_bar_external(self) -> None:
        self.assertIn("N → S", model.field_at("条形", "外部"))

    def test_bar_internal(self) -> None:
        self.assertIn("S → N", model.field_at("条形磁铁", "内部"))

    def test_bar_poles(self) -> None:
        self.assertIn("N 极", model.field_at("条形", "N极"))
        self.assertIn("S 极", model.field_at("条形", "S极"))

    def test_bar_surrounding(self) -> None:
        for position in ("N极附近", "S极附近"):
            with self.subTest(position=position):
                self.assertTrue(model.field_at("条形", position))

    def test_horseshoe_between_poles(self) -> None:
        self.assertIn("N → S", model.field_at("蹄形", "两极之间"))

    def test_ring_center(self) -> None:
        self.assertIn("S → N", model.field_at("环形", "中心"))
        self.assertIn("S → N", model.field_at("环形", "孔内"))

    def test_needle(self) -> None:
        self.assertIn("北", model.field_at("磁针", "外部"))
        self.assertIn("南", model.field_at("磁针", "S极"))

    def test_electromagnet_core(self) -> None:
        self.assertIn("S → N", model.field_at("电磁铁", "铁芯"))

    def test_position_aliases(self) -> None:
        self.assertEqual(
            model.field_at("条形", "磁体外部"),
            model.field_at("条形", "外部"),
        )
        self.assertEqual(
            model.field_at("条形", "北极"),
            model.field_at("条形", "N极"),
        )

    def test_unknown_position(self) -> None:
        with self.assertRaises(ValueError):
            model.field_at("条形", "侧面")

    def test_unsupported_position(self) -> None:
        with self.assertRaises(ValueError):
            model.field_at("条形", "中心")

    def test_unknown_magnet(self) -> None:
        with self.assertRaises(ValueError):
            model.field_at("超级磁铁", "外部")

    def test_non_string_arguments(self) -> None:
        with self.assertRaises(TypeError):
            model.field_at(1, "外部")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            model.field_at("条形", 1)  # type: ignore[arg-type]

    def test_empty_position(self) -> None:
        with self.assertRaises(ValueError):
            model.field_at("条形", "   ")


class TestQuiz(unittest.TestCase):
    """选择题生成。"""

    def test_count_one(self) -> None:
        items = model.quiz_items(1, 1)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["kind"], "pole")

    def test_count_maximum(self) -> None:
        items = model.quiz_items(model.MAX_QUIZ, 2)
        self.assertEqual(len(items), model.MAX_QUIZ)

    def test_indexes_are_sequential(self) -> None:
        items = model.quiz_items(10, 5)
        self.assertEqual([item["index"] for item in items], list(range(1, 11)))

    def test_three_kinds_cycle(self) -> None:
        items = model.quiz_items(9, 5)
        self.assertEqual(
            [item["kind"] for item in items],
            ["pole", "material", "magnet"] * 3,
        )

    def test_seed_is_deterministic(self) -> None:
        self.assertEqual(model.quiz_items(10, 9), model.quiz_items(10, 9))

    def test_different_seeds_differ(self) -> None:
        self.assertNotEqual(model.quiz_items(10, 1), model.quiz_items(10, 2))

    def test_seed_none_works(self) -> None:
        self.assertEqual(len(model.quiz_items(3)), 3)

    def test_count_lower_bound(self) -> None:
        for value in (0, -1, -30):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    model.quiz_items(value)

    def test_count_upper_bound(self) -> None:
        for value in (model.MAX_QUIZ + 1, 100):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    model.quiz_items(value)

    def test_count_type_errors(self) -> None:
        for value in (True, "3", 3.0, None):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    model.quiz_items(value)  # type: ignore[arg-type]

    def test_seed_type_errors(self) -> None:
        for value in ("1", 1.5, True):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    model.quiz_items(3, value)  # type: ignore[arg-type]

    def test_item_structure(self) -> None:
        for item in model.quiz_items(model.MAX_QUIZ, 7):
            with self.subTest(index=item["index"]):
                self.assertEqual(
                    set(item.keys()),
                    {"index", "kind", "question", "options", "answer", "explanation"},
                )
                self.assertIn(item["kind"], ("pole", "material", "magnet"))
                self.assertTrue(str(item["question"]).strip())

    def test_options_are_unique(self) -> None:
        for item in model.quiz_items(model.MAX_QUIZ, 4):
            with self.subTest(index=item["index"]):
                options = item["options"]
                self.assertIsInstance(options, list)
                self.assertEqual(len(options), 4)
                self.assertEqual(len(set(options)), 4)
                self.assertIn(item["answer"], options)
                self.assertTrue(str(item["explanation"]).strip())

    def test_pole_answers(self) -> None:
        for item in model.quiz_items(model.MAX_QUIZ, 3):
            if item["kind"] == "pole":
                self.assertIn(item["answer"], ("吸引", "排斥"))

    def test_material_answers(self) -> None:
        for item in model.quiz_items(model.MAX_QUIZ, 3):
            if item["kind"] == "material":
                self.assertTrue(model.is_attracted(str(item["answer"])))

    def test_material_has_exactly_one_attracted_option(self) -> None:
        for item in model.quiz_items(model.MAX_QUIZ, 4):
            if item["kind"] == "material":
                options = item["options"]
                flags = [model.is_attracted(str(option)) for option in options]
                self.assertEqual(sum(1 for flag in flags if flag), 1)

    def test_magnet_answers(self) -> None:
        kinds = model.magnet_kinds()
        for item in model.quiz_items(model.MAX_QUIZ, 6):
            if item["kind"] == "magnet":
                self.assertIn(item["answer"], kinds)


class TestMatch(unittest.TestCase):
    """配对练习生成。"""

    def test_count_one(self) -> None:
        pairs = model.match_items(1, 1)
        self.assertEqual(len(pairs), 1)

    def test_count_maximum(self) -> None:
        pairs = model.match_items(model.MAX_MATCH, 2)
        self.assertEqual(len(pairs), model.MAX_MATCH)

    def test_seed_is_deterministic(self) -> None:
        self.assertEqual(model.match_items(10, 8), model.match_items(10, 8))

    def test_different_seeds_differ(self) -> None:
        self.assertNotEqual(model.match_items(10, 8), model.match_items(10, 9))

    def test_count_bounds(self) -> None:
        for value in (0, -1, model.MAX_MATCH + 1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    model.match_items(value)

    def test_count_type_errors(self) -> None:
        for value in (True, "3", 2.5, None):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    model.match_items(value)  # type: ignore[arg-type]

    def test_seed_type_error(self) -> None:
        with self.assertRaises(TypeError):
            model.match_items(3, True)  # type: ignore[arg-type]

    def test_pairs_are_string_tuples(self) -> None:
        for pair in model.match_items(model.MAX_MATCH, 6):
            self.assertIsInstance(pair, tuple)
            self.assertEqual(len(pair), 2)
            self.assertIsInstance(pair[0], str)
            self.assertIsInstance(pair[1], str)
            self.assertTrue(pair[0].strip())
            self.assertTrue(pair[1].strip())

    def test_left_sides_are_unique(self) -> None:
        pairs = model.match_items(model.MAX_MATCH, 6)
        lefts = [left for left, _ in pairs]
        self.assertEqual(len(lefts), len(set(lefts)))

    def test_contains_both_pair_types(self) -> None:
        pairs = model.match_items(model.MAX_MATCH, 6)
        material_rights = {"铁磁性", "顺磁性", "抗磁性"}
        self.assertTrue(any(right in material_rights for _, right in pairs))
        self.assertTrue(any(right not in material_rights for _, right in pairs))

    def test_material_pairs_are_consistent(self) -> None:
        kinds = {"铁磁性", "顺磁性", "抗磁性"}
        for left, right in model.match_items(model.MAX_MATCH, 6):
            if right in kinds:
                self.assertEqual(right, model.magnetic_kind(left))

    def test_magnet_pairs_are_consistent(self) -> None:
        for left, right in model.match_items(model.MAX_MATCH, 6):
            if left in model.magnet_kinds():
                self.assertEqual(right, str(model.magnet_info(left)["use"]))


if __name__ == "__main__":
    unittest.main()
