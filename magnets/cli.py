"""命令行入口：磁极判断、材料查询、磁铁信息、磁场方向与练习导出。"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, List, Optional, Sequence, Tuple

from . import __version__
from .model import (
    MAX_MATCH,
    MAX_QUIZ,
    field_at,
    find_material,
    interact,
    is_attracted,
    magnet_info,
    match_items,
    normalize_pole,
    quiz_items,
)
from .render import match_html, poster_html, quiz_html

__all__ = ["main"]

_DEFAULT_QUIZ_TITLE: str = "磁铁与磁场小测"
_DEFAULT_MATCH_TITLE: str = "材料与磁铁配对练习"
_DEFAULT_POSTER_TITLE: str = "磁铁与磁场"


def _ensure_utf8_console() -> None:
    """尽量把标准输出与标准错误切换为 UTF-8，失败时保持原样。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if not callable(reconfigure):
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            continue


def _build_parser() -> argparse.ArgumentParser:
    """构造命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="magnets",
        description="磁铁与磁场：磁极相互作用、材料磁性判断与可打印练习",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="magnets %s" % __version__,
        help="显示版本号并退出",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="命令")

    poles_parser = subparsers.add_parser("poles", help="判断两个磁极的相互作用")
    poles_parser.add_argument("pole_a", help="第一个磁极，如 N、S、北极、南")
    poles_parser.add_argument("pole_b", help="第二个磁极，如 N、S、北极、南")

    material_parser = subparsers.add_parser("material", help="查询一种材料的磁性")
    material_parser.add_argument("name", help="材料名称，如 铁、铜、塑料")

    kind_parser = subparsers.add_parser("kind", help="查询一种磁铁的特点与用途")
    kind_parser.add_argument("kind", help="磁铁类型，如 条形、蹄形、电磁铁")

    field_parser = subparsers.add_parser("field", help="查询简化模型下的磁场方向")
    field_parser.add_argument("magnet", help="磁铁类型，如 条形、蹄形、磁针")
    field_parser.add_argument("position", help="位置，如 外部、内部、N极、S极")

    quiz_parser = subparsers.add_parser("quiz", help="生成选择题测验")
    quiz_parser.add_argument(
        "--count", type=int, required=True, help="题目数量 1~%d" % MAX_QUIZ
    )
    quiz_parser.add_argument("--seed", type=int, default=None, help="随机种子")
    quiz_parser.add_argument("-o", "--output", default=None, help="导出 HTML 文件路径")

    match_parser = subparsers.add_parser("match", help="生成配对练习")
    match_parser.add_argument(
        "--count", type=int, required=True, help="配对数量 1~%d" % MAX_MATCH
    )
    match_parser.add_argument("--seed", type=int, default=None, help="随机种子")
    match_parser.add_argument("-o", "--output", default=None, help="导出 HTML 文件路径")

    poster_parser = subparsers.add_parser("poster", help="生成可打印海报")
    poster_parser.add_argument("-o", "--output", default=None, help="导出 HTML 文件路径")

    return parser


def _write_output(path: str, content: str) -> None:
    """以 UTF-8 写入文本文件，失败时转换为中文 ``ValueError``。"""
    if not isinstance(path, str):
        raise TypeError("输出路径必须是字符串")
    target = path.strip()
    if not target:
        raise ValueError("输出路径不能为空")
    parent = os.path.dirname(os.path.abspath(target))
    try:
        if parent and not os.path.isdir(parent):
            os.makedirs(parent, exist_ok=True)
        with open(target, "w", encoding="utf-8") as handle:
            handle.write(content)
    except OSError as exc:
        raise ValueError("无法写入文件 %s：%s" % (target, exc)) from exc


def _format_quiz(items: List[Dict[str, object]]) -> str:
    """把题目渲染为便于终端阅读的文本。"""
    lines: List[str] = []
    for item in items:
        lines.append("%s. %s" % (item["index"], item["question"]))
        options = item["options"]
        if isinstance(options, (list, tuple)):
            labels = [
                "%s. %s" % (chr(ord("A") + offset), option)
                for offset, option in enumerate(options)
            ]
            lines.append("   " + "   ".join(labels))
        lines.append("   答案：%s" % item["answer"])
        lines.append("   解析：%s" % item["explanation"])
    return "\n".join(lines)


def _format_match(pairs: List[Tuple[str, str]]) -> str:
    """把配对练习渲染为终端文本。"""
    lines: List[str] = []
    for offset, pair in enumerate(pairs):
        lines.append("%d. %s —— %s" % (offset + 1, pair[0], pair[1]))
    return "\n".join(lines)


def _run(args: argparse.Namespace) -> int:
    """执行具体子命令，返回退出码。"""
    command = args.command
    if command is None:
        _build_parser().print_help()
        return 2

    if command == "poles":
        first = normalize_pole(args.pole_a)
        second = normalize_pole(args.pole_b)
        print("%s 与 %s：%s" % (first, second, interact(first, second)))
        return 0

    if command == "material":
        record = find_material(args.name)
        print("名称：%s" % record["name"])
        print("材料类别：%s" % record["category"])
        print("磁性类别：%s" % record["kind"])
        print("是否被吸引：%s" % ("是" if is_attracted(str(record["name"])) else "否"))
        print("说明：%s" % record["note"])
        return 0

    if command == "kind":
        info = magnet_info(args.kind)
        print("类型：%s" % info["kind"])
        print("特点：%s" % info["feature"])
        print("用途：%s" % info["use"])
        print("备注：%s" % info["note"])
        return 0

    if command == "field":
        print("%s · %s：%s" % (args.magnet, args.position, field_at(args.magnet, args.position)))
        return 0

    if command == "quiz":
        items = quiz_items(args.count, args.seed)
        if args.output:
            content = quiz_html(items, _DEFAULT_QUIZ_TITLE, with_answers=True)
            _write_output(args.output, content)
            print("已生成：%s" % args.output)
        else:
            print(_format_quiz(items))
        return 0

    if command == "match":
        pairs = match_items(args.count, args.seed)
        if args.output:
            content = match_html(pairs, _DEFAULT_MATCH_TITLE)
            _write_output(args.output, content)
            print("已生成：%s" % args.output)
        else:
            print(_format_match(pairs))
        return 0

    if command == "poster":
        content = poster_html(title=_DEFAULT_POSTER_TITLE)
        if args.output:
            _write_output(args.output, content)
            print("已生成：%s" % args.output)
        else:
            print(content)
        return 0

    raise ValueError("未知命令：%s" % command)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """命令行主函数，返回进程退出码。"""
    _ensure_utf8_console()
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        return _run(args)
    except (TypeError, ValueError) as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
