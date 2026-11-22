"""cli 模块的单元测试。"""

from __future__ import annotations

import argparse
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from magnets import cli, model


class _FakeStream:
    """用于验证 UTF-8 控制台适配的假流对象。"""

    def __init__(self, error: Optional[BaseException] = None) -> None:
        self.error = error
        self.calls: List[Dict[str, str]] = []

    def reconfigure(self, encoding: str = "", errors: str = "") -> None:
        self.calls.append({"encoding": encoding, "errors": errors})
        if self.error is not None:
            raise self.error


class TestCliCommands(unittest.TestCase):
    """命令行各子命令。"""

    def _invoke(self, argv: List[str]) -> Tuple[int, str, str]:
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_help_exits_zero(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            with self.assertRaises(SystemExit) as context:
                cli.main(["--help"])
        self.assertEqual(context.exception.code, 0)
        self.assertIn("poles", out.getvalue())

    def test_version_exits_zero(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            with self.assertRaises(SystemExit) as context:
                cli.main(["--version"])
        self.assertEqual(context.exception.code, 0)
        self.assertIn("magnets", out.getvalue())

    def test_poles_success(self) -> None:
        code, out, err = self._invoke(["poles", "N", "S"])
        self.assertEqual(code, 0)
        self.assertIn("N 与 S：吸引", out)
        self.assertEqual(err, "")

    def test_poles_aliases(self) -> None:
        code, out, _ = self._invoke(["poles", "北极", "南"])
        self.assertEqual(code, 0)
        self.assertIn("N 与 S：吸引", out)

    def test_poles_repel(self) -> None:
        code, out, _ = self._invoke(["poles", "S", "S"])
        self.assertEqual(code, 0)
        self.assertIn("S 与 S：排斥", out)

    def test_poles_invalid(self) -> None:
        code, out, err = self._invoke(["poles", "X", "N"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("错误：", err)
        self.assertIn("未知磁极", err)

    def test_material_success(self) -> None:
        code, out, _ = self._invoke(["material", "铁"])
        self.assertEqual(code, 0)
        self.assertIn("名称：铁", out)
        self.assertIn("磁性类别：铁磁性", out)
        self.assertIn("是否被吸引：是", out)

    def test_material_not_attracted(self) -> None:
        code, out, _ = self._invoke(["material", "铜"])
        self.assertEqual(code, 0)
        self.assertIn("磁性类别：抗磁性", out)
        self.assertIn("是否被吸引：否", out)

    def test_material_unknown(self) -> None:
        code, _, err = self._invoke(["material", "不存在的材料"])
        self.assertEqual(code, 2)
        self.assertIn("未知材料", err)

    def test_kind_success(self) -> None:
        code, out, _ = self._invoke(["kind", "蹄形"])
        self.assertEqual(code, 0)
        self.assertIn("类型：蹄形磁铁", out)
        self.assertIn("特点：", out)
        self.assertIn("用途：", out)

    def test_kind_alias(self) -> None:
        code, out, _ = self._invoke(["kind", "指南针"])
        self.assertEqual(code, 0)
        self.assertIn("类型：磁针", out)

    def test_kind_unknown(self) -> None:
        code, _, err = self._invoke(["kind", "超级磁铁"])
        self.assertEqual(code, 2)
        self.assertIn("未知磁铁类型", err)

    def test_field_success(self) -> None:
        code, out, _ = self._invoke(["field", "条形", "外部"])
        self.assertEqual(code, 0)
        self.assertIn("N → S", out)

    def test_field_internal(self) -> None:
        code, out, _ = self._invoke(["field", "环形", "中心"])
        self.assertEqual(code, 0)
        self.assertIn("S → N", out)

    def test_field_unknown_position(self) -> None:
        code, _, err = self._invoke(["field", "条形", "侧面"])
        self.assertEqual(code, 2)
        self.assertIn("未知位置", err)

    def test_field_unknown_magnet(self) -> None:
        code, _, err = self._invoke(["field", "超级磁铁", "外部"])
        self.assertEqual(code, 2)
        self.assertIn("未知磁铁类型", err)

    def test_quiz_stdout(self) -> None:
        code, out, _ = self._invoke(["quiz", "--count", "3", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertIn("1. ", out)
        self.assertIn("答案：", out)
        self.assertIn("解析：", out)

    def test_quiz_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "quiz.html"
            code, out, _ = self._invoke(
                ["quiz", "--count", "3", "--seed", "5", "-o", str(target)]
            )
            self.assertEqual(code, 0)
            self.assertIn("已生成：%s" % target, out)
            self.assertTrue(target.is_file())
            content = target.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("<!DOCTYPE html>"))
            self.assertIn("答案：", content)

    def test_quiz_count_error(self) -> None:
        code, _, err = self._invoke(["quiz", "--count", "0", "--seed", "1"])
        self.assertEqual(code, 2)
        self.assertIn("题目数量必须在 1 到", err)

    def test_quiz_count_too_large(self) -> None:
        code, _, err = self._invoke(
            ["quiz", "--count", str(model.MAX_QUIZ + 1), "--seed", "1"]
        )
        self.assertEqual(code, 2)
        self.assertIn("题目数量必须在 1 到", err)

    def test_match_stdout(self) -> None:
        code, out, _ = self._invoke(["match", "--count", "3", "--seed", "2"])
        self.assertEqual(code, 0)
        self.assertIn("——", out)

    def test_match_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "match.html"
            code, out, _ = self._invoke(
                ["match", "--count", "4", "--seed", "2", "-o", str(target)]
            )
            self.assertEqual(code, 0)
            self.assertIn("已生成：%s" % target, out)
            self.assertTrue(target.is_file())
            self.assertIn("配对", target.read_text(encoding="utf-8"))

    def test_match_count_error(self) -> None:
        code, _, err = self._invoke(["match", "--count", "0", "--seed", "1"])
        self.assertEqual(code, 2)
        self.assertIn("配对数量必须在 1 到", err)

    def test_poster_stdout(self) -> None:
        code, out, _ = self._invoke(["poster"])
        self.assertEqual(code, 0)
        self.assertTrue(out.lstrip().startswith("<!DOCTYPE html>"))
        self.assertIn("磁极规律", out)

    def test_poster_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "poster.html"
            code, out, _ = self._invoke(["poster", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertIn("已生成：%s" % target, out)
            self.assertTrue(target.is_file())
            self.assertIn("材料分类表", target.read_text(encoding="utf-8"))

    def test_poster_creates_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "nested" / "poster.html"
            code, _, _ = self._invoke(["poster", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.is_file())

    def test_no_command_prints_help(self) -> None:
        code, out, _ = self._invoke([])
        self.assertEqual(code, 2)
        self.assertIn("usage:", out)

    def test_unknown_command_raises(self) -> None:
        with self.assertRaises(ValueError):
            cli._run(argparse.Namespace(command="unknown"))

    def test_write_output_rejects_empty_path(self) -> None:
        with self.assertRaises(ValueError):
            cli._write_output("   ", "内容")

    def test_write_output_rejects_non_string_path(self) -> None:
        with self.assertRaises(TypeError):
            cli._write_output(123, "内容")  # type: ignore[arg-type]


class TestEnsureUtf8Console(unittest.TestCase):
    """UTF-8 控制台适配。"""

    def test_reconfigures_stdout_and_stderr(self) -> None:
        fake_out = _FakeStream()
        fake_err = _FakeStream()
        original_out, original_err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = fake_out, fake_err  # type: ignore[assignment]
        try:
            cli._ensure_utf8_console()
        finally:
            sys.stdout, sys.stderr = original_out, original_err
        self.assertEqual(
            fake_out.calls, [{"encoding": "utf-8", "errors": "replace"}]
        )
        self.assertEqual(
            fake_err.calls, [{"encoding": "utf-8", "errors": "replace"}]
        )

    def test_swallows_value_error(self) -> None:
        fake = _FakeStream(error=ValueError("不支持"))
        original = sys.stdout
        sys.stdout = fake  # type: ignore[assignment]
        try:
            cli._ensure_utf8_console()
        finally:
            sys.stdout = original
        self.assertEqual(len(fake.calls), 1)

    def test_swallows_os_error(self) -> None:
        fake = _FakeStream(error=OSError("已关闭"))
        original = sys.stderr
        sys.stderr = fake  # type: ignore[assignment]
        try:
            cli._ensure_utf8_console()
        finally:
            sys.stderr = original
        self.assertEqual(len(fake.calls), 1)

    def test_ignores_stream_without_reconfigure(self) -> None:
        original = sys.stdout
        sys.stdout = io.StringIO()  # type: ignore[assignment]
        try:
            cli._ensure_utf8_console()
        finally:
            sys.stdout = original


if __name__ == "__main__":
    unittest.main()
