"""磁铁与磁场的核心模型。

覆盖磁极相互作用、材料磁性分类、磁铁种类、简化磁场方向，
以及练习题与配对练习的生成。只依赖 Python 标准库，兼容 3.9 及以上版本。
"""

from __future__ import annotations

import random
from collections.abc import Sequence as _ABCSequence
from typing import Dict, List, Optional, Sequence, Tuple

__all__ = [
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
]

MAX_QUIZ: int = 40
MAX_MATCH: int = 20

MAGNETIC_KINDS: Tuple[str, str, str] = ("铁磁性", "顺磁性", "抗磁性")

_POLE_ALIASES: Dict[str, str] = {
    "N": "N",
    "n": "N",
    "北极": "N",
    "北": "N",
    "S": "S",
    "s": "S",
    "南极": "S",
    "南": "S",
}


def _require_int(value: object, label: str) -> int:
    """校验整数参数，明确排除 bool（bool 是 int 的子类）。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("%s必须是整数" % label)
    return value


def _require_text(value: object, label: str) -> str:
    """校验非空字符串，返回去掉首尾空白后的文本。"""
    if not isinstance(value, str):
        raise TypeError("%s必须是字符串" % label)
    text = value.strip()
    if not text:
        raise ValueError("%s不能为空" % label)
    return text


def normalize_pole(pole: str) -> str:
    """把各种写法的磁极统一为 ``"N"`` 或 ``"S"``。

    支持 ``N/S``、``n/s``、``北极/南极``、``北/南``，并忽略首尾空白。
    """
    key = _require_text(pole, "磁极")
    normalized = _POLE_ALIASES.get(key)
    if normalized is None:
        raise ValueError("未知磁极：%s（可用 N/S、北极/南极、北/南）" % pole)
    return normalized


def interact(pole_a: str, pole_b: str) -> str:
    """返回两个磁极靠近时的作用：``"吸引"`` 或 ``"排斥"``。"""
    first = normalize_pole(pole_a)
    second = normalize_pole(pole_b)
    if first == second:
        return "排斥"
    return "吸引"


def pole_summary() -> Dict[str, str]:
    """返回磁极方向与相互作用规律的说明。"""
    return {
        "N": "N 极（北极）指向地理北方，磁感线从 N 极附近出发。",
        "S": "S 极（南极）指向地理南方，磁感线回到 S 极附近。",
        "规律": "同名磁极相互排斥，异名磁极相互吸引。",
    }


def _material(name: str, kind: str, category: str, note: str) -> Dict[str, object]:
    """构造一条材料记录，字段固定为名称、磁性类别、材料类别与备注。"""
    return {
        "name": name,
        "kind": kind,
        "category": category,
        "note": note,
    }


_MATERIALS: Tuple[Dict[str, object], ...] = (
    _material("铁", "铁磁性", "金属", "最常见的铁磁性金属，能被磁铁强烈吸引。"),
    _material("钴", "铁磁性", "金属", "铁磁性金属，常用于耐高温磁体。"),
    _material("镍", "铁磁性", "金属", "铁磁性金属，常用于不锈钢与合金。"),
    _material("钢", "铁磁性", "合金", "以铁为主的合金，通常具有铁磁性。"),
    _material("铸铁", "铁磁性", "合金", "含碳量高的铁合金，具有铁磁性。"),
    _material("硅钢", "铁磁性", "合金", "电工钢，常用于电机和变压器铁芯。"),
    _material("坡莫合金", "铁磁性", "合金", "镍铁合金，磁导率很高。"),
    _material("钕铁硼", "铁磁性", "合金", "稀土永磁材料，磁性强，常用于扬声器。"),
    _material("钐钴合金", "铁磁性", "合金", "稀土永磁材料，耐高温性能好。"),
    _material("马氏体不锈钢", "铁磁性", "合金", "含铬不锈钢的一类，通常具有铁磁性。"),
    _material(
        "铁氧体",
        "铁磁性",
        "陶瓷",
        "常见的磁性陶瓷（亚铁磁性，此处按铁磁性简化），用于扬声器。",
    ),
    _material(
        "四氧化三铁",
        "铁磁性",
        "矿物",
        "磁铁矿的主要成分，天然具有较强磁性。",
    ),
    _material("铝", "顺磁性", "金属", "顺磁性金属，被磁铁吸引的力非常微弱。"),
    _material("铂", "顺磁性", "金属", "顺磁性金属，常温下几乎看不出吸引。"),
    _material("钛", "顺磁性", "金属", "轻而坚固，呈弱顺磁性。"),
    _material("锰", "顺磁性", "金属", "顺磁性金属，常见于合金添加剂。"),
    _material("镁", "顺磁性", "金属", "轻质金属，呈弱顺磁性。"),
    _material("钨", "顺磁性", "金属", "熔点很高，呈弱顺磁性。"),
    _material("空气", "顺磁性", "气体", "氧气分子具有顺磁性，整体吸引极弱。"),
    _material("304不锈钢", "顺磁性", "合金", "奥氏体不锈钢通常呈顺磁性，不被磁铁明显吸引。"),
    _material("铜", "抗磁性", "金属", "抗磁性金属，不能被磁铁吸引。"),
    _material("金", "抗磁性", "金属", "化学性质稳定，呈抗磁性。"),
    _material("银", "抗磁性", "金属", "导电性最好的金属，呈抗磁性。"),
    _material("锌", "抗磁性", "金属", "常见镀层金属，呈抗磁性。"),
    _material("铅", "抗磁性", "金属", "密度大，呈抗磁性。"),
    _material("水", "抗磁性", "液体", "水分子呈抗磁性，不能被磁铁吸引。"),
    _material("塑料", "抗磁性", "高分子", "高分子材料，非磁性。"),
    _material("木头", "抗磁性", "非金属", "天然材料，非磁性。"),
    _material("玻璃", "抗磁性", "非金属", "透明非晶材料，非磁性。"),
    _material("橡胶", "抗磁性", "高分子", "弹性材料，非磁性。"),
    _material("纸", "抗磁性", "非金属", "纤维素材料，非磁性。"),
    _material("棉布", "抗磁性", "非金属", "天然纤维织物，非磁性。"),
    _material("陶瓷", "抗磁性", "陶瓷", "普通陶瓷非磁性（铁氧体除外）。"),
    _material("石墨", "抗磁性", "非金属", "碳的单质，呈抗磁性。"),
    _material("二氧化硅", "抗磁性", "化合物", "沙子和石英的主要成分，非磁性。"),
    _material("尼龙", "抗磁性", "高分子", "合成纤维，非磁性。"),
    _material("聚乙烯", "抗磁性", "高分子", "常见塑料，非磁性。"),
    _material("混凝土", "抗磁性", "非金属", "建筑材料，非磁性。"),
    _material("食盐", "抗磁性", "化合物", "氯化钠晶体，非磁性。"),
    _material("酒精", "抗磁性", "化合物", "乙醇液体，非磁性。"),
)

_MATERIAL_INDEX: Dict[str, Dict[str, object]] = {
    str(record["name"]): record for record in _MATERIALS
}

_MATERIALS_BY_KIND: Dict[str, Tuple[Dict[str, object], ...]] = {
    kind: tuple(record for record in _MATERIALS if record["kind"] == kind)
    for kind in MAGNETIC_KINDS
}


def _check_records(records: Sequence[Dict[str, object]]) -> None:
    """校验材料数据：名称唯一、类别合法、备注非空。"""
    if isinstance(records, (str, bytes)) or not isinstance(records, _ABCSequence):
        raise TypeError("材料数据必须是序列")
    if not records:
        raise ValueError("材料数据不能为空")
    seen: Dict[str, bool] = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError("第 %d 条材料必须是字典" % (index + 1))
        name = record.get("name")
        kind = record.get("kind")
        category = record.get("category")
        note = record.get("note")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("第 %d 条材料缺少有效名称" % (index + 1))
        if kind not in MAGNETIC_KINDS:
            raise ValueError(
                "材料“%s”的磁性类别必须是铁磁性、顺磁性或抗磁性" % name
            )
        if not isinstance(category, str) or not category.strip():
            raise ValueError("材料“%s”的材料类别不能为空" % name)
        if not isinstance(note, str) or not note.strip():
            raise ValueError("材料“%s”的备注不能为空" % name)
        key = name.strip()
        if key in seen:
            raise ValueError("材料名称重复：%s" % key)
        seen[key] = True


_check_records(_MATERIALS)


def all_materials() -> List[Dict[str, object]]:
    """返回全部材料记录的副本列表。"""
    return [dict(record) for record in _MATERIALS]


def find_material(name: str) -> Dict[str, object]:
    """按名称查找材料，返回记录副本；未知材料抛出 ``ValueError``。"""
    key = _require_text(name, "材料名称")
    record = _MATERIAL_INDEX.get(key)
    if record is None:
        raise ValueError("未知材料：%s" % name)
    return dict(record)


def magnetic_kind(material: str) -> str:
    """返回材料的磁性类别：铁磁性、顺磁性或抗磁性。"""
    return str(find_material(material)["kind"])


def is_attracted(material: str) -> bool:
    """判断材料是否会被磁铁吸引（仅铁磁性材料返回真）。"""
    return magnetic_kind(material) == "铁磁性"


def materials_by_kind(kind: str) -> List[str]:
    """按磁性类别列出材料名称，保持原始数据顺序。"""
    key = _require_text(kind, "磁性类别")
    if key not in MAGNETIC_KINDS:
        raise ValueError(
            "未知磁性类别：%s（可选铁磁性、顺磁性、抗磁性）" % kind
        )
    return [str(record["name"]) for record in _MATERIALS_BY_KIND[key]]


_MAGNETS: Tuple[Dict[str, object], ...] = (
    {
        "kind": "条形磁铁",
        "feature": "长条形，两端各有一个磁极，磁极在两端最强。",
        "use": "演示磁极相互作用和磁感线分布",
        "note": "实验室里最常见的磁铁，常涂成红蓝两色。",
    },
    {
        "kind": "蹄形磁铁",
        "feature": "弯成 U 形（马蹄形），两个磁极靠得较近。",
        "use": "提供较强且集中的磁场，常用于电动机和扬声器",
        "note": "两极之间磁场较强，适合放置线圈。",
    },
    {
        "kind": "环形磁铁",
        "feature": "圆环状，一面是 N 极、另一面是 S 极。",
        "use": "扬声器、传感器和磁吸固定",
        "note": "中心孔内的磁场方向与外部相反。",
    },
    {
        "kind": "圆片磁铁",
        "feature": "扁圆片状，体积小、磁力集中。",
        "use": "冰箱贴、包装磁扣和手工制作",
        "note": "两个圆片磁铁吸合时很难分开，注意安全。",
    },
    {
        "kind": "磁针",
        "feature": "细小的针形磁体，能绕支点自由转动。",
        "use": "制作指南针，判断地理方向",
        "note": "静止时 N 极指向地理北方。",
    },
    {
        "kind": "电磁铁",
        "feature": "通电线圈加铁芯，通电有磁性、断电无磁性。",
        "use": "起重机、门锁和继电器，可控制磁性强弱",
        "note": "磁性强弱与电流大小、线圈匝数有关。",
    },
)

_MAGNET_ALIASES: Dict[str, str] = {
    "条形磁铁": "条形磁铁",
    "条形磁体": "条形磁铁",
    "条形": "条形磁铁",
    "蹄形磁铁": "蹄形磁铁",
    "蹄形磁体": "蹄形磁铁",
    "蹄形": "蹄形磁铁",
    "u形磁铁": "蹄形磁铁",
    "U形磁铁": "蹄形磁铁",
    "马蹄形磁铁": "蹄形磁铁",
    "环形磁铁": "环形磁铁",
    "圆环磁铁": "环形磁铁",
    "环形": "环形磁铁",
    "圆片磁铁": "圆片磁铁",
    "圆磁片": "圆片磁铁",
    "圆片": "圆片磁铁",
    "磁针": "磁针",
    "小磁针": "磁针",
    "指南针": "磁针",
    "电磁铁": "电磁铁",
}

_MAGNET_INDEX: Dict[str, Dict[str, object]] = {
    str(record["kind"]): record for record in _MAGNETS
}


def magnet_kinds() -> List[str]:
    """返回全部磁铁种类名称。"""
    return [str(record["kind"]) for record in _MAGNETS]


def _resolve_magnet(kind: str) -> str:
    """把磁铁名称或别名统一为标准名称。"""
    key = _require_text(kind, "磁铁类型")
    name = _MAGNET_ALIASES.get(key)
    if name is None:
        raise ValueError("未知磁铁类型：%s（可用条形、蹄形、环形、圆片、磁针、电磁铁）" % kind)
    return name


def magnet_info(kind: str) -> Dict[str, object]:
    """返回磁铁种类的特点与用途，未知类型抛出 ``ValueError``。"""
    name = _resolve_magnet(kind)
    return dict(_MAGNET_INDEX[name])


_POSITION_ALIASES: Dict[str, str] = {
    "外部": "外部",
    "外面": "外部",
    "外部空间": "外部",
    "磁体外部": "外部",
    "内部": "内部",
    "里面": "内部",
    "磁体内部": "内部",
    "N极": "N极",
    "n极": "N极",
    "北极": "N极",
    "N": "N极",
    "n": "N极",
    "S极": "S极",
    "s极": "S极",
    "南极": "S极",
    "S": "S极",
    "s": "S极",
    "N极附近": "N极附近",
    "n极附近": "N极附近",
    "北极附近": "N极附近",
    "S极附近": "S极附近",
    "s极附近": "S极附近",
    "南极附近": "S极附近",
    "两极之间": "两极之间",
    "极间": "两极之间",
    "中心": "中心",
    "孔内": "孔内",
    "铁芯": "铁芯",
    "铁芯内部": "铁芯内部",
}

_COMMON_FIELD: Dict[str, str] = {
    "外部": "N → S（磁感线从 N 极出发，回到 S 极）",
    "内部": "S → N（磁体内部由 S 极指向 N 极）",
    "N极": "由 N 极向外发散",
    "S极": "从外部汇入 S 极",
    "N极附近": "由 N 极向外发散",
    "S极附近": "从外部汇入 S 极",
}

_FIELD_RULES: Dict[str, Dict[str, str]] = {
    "条形磁铁": dict(_COMMON_FIELD),
    "蹄形磁铁": dict(
        _COMMON_FIELD,
        **{
            "外部": "N → S（两极之间由 N 极指向 S 极）",
            "两极之间": "N → S（由 N 极指向 S 极）",
        }
    ),
    "环形磁铁": dict(
        _COMMON_FIELD,
        **{
            "中心": "S → N（中心孔内与外部方向相反）",
            "孔内": "S → N（中心孔内与外部方向相反）",
        }
    ),
    "圆片磁铁": dict(_COMMON_FIELD),
    "磁针": dict(
        _COMMON_FIELD,
        **{
            "外部": "指向地理北方（N 极指北）",
            "N极": "指向地理北方",
            "S极": "指向地理南方",
            "N极附近": "指向地理北方",
            "S极附近": "指向地理南方",
        }
    ),
    "电磁铁": dict(
        _COMMON_FIELD,
        **{
            "铁芯": "S → N（铁芯内部由 S 极指向 N 极）",
            "铁芯内部": "S → N（铁芯内部由 S 极指向 N 极）",
        }
    ),
}


def field_at(magnet: str, position: str) -> str:
    """返回简化模型下指定磁铁在某个位置的磁场方向描述。

    位置支持外部、内部、N 极、S 极、两极之间、中心孔内等写法；
    未知磁铁或未知位置抛出 ``ValueError``。
    """
    name = _resolve_magnet(magnet)
    key = _require_text(position, "位置")
    normalized = _POSITION_ALIASES.get(key)
    if normalized is None:
        raise ValueError(
            "未知位置：%s（可用外部、内部、N极、S极、两极之间等）" % position
        )
    rule = _FIELD_RULES[name].get(normalized)
    if rule is None:
        raise ValueError("磁铁“%s”不支持位置：%s" % (name, position))
    return rule


def _make_pole_quiz(index: int, rng: random.Random) -> Dict[str, object]:
    """生成一道“两磁极靠近会怎样”的选择题。"""
    first, second = rng.choice(
        [("N", "N"), ("S", "S"), ("N", "S"), ("S", "N")]
    )
    result = interact(first, second)
    same = first == second
    options: List[str] = ["吸引", "排斥", "没有相互作用", "先吸引后排斥"]
    rng.shuffle(options)
    relation = "同名磁极" if same else "异名磁极"
    return {
        "index": index,
        "kind": "pole",
        "question": "把 %s 极与 %s 极靠近，会发生什么？" % (first, second),
        "options": options,
        "answer": result,
        "explanation": "同名磁极相互排斥，异名磁极相互吸引；%s 极与 %s 极属于%s，因此相互%s。"
        % (first, second, relation, result),
    }


def _make_material_quiz(index: int, rng: random.Random) -> Dict[str, object]:
    """生成一道“哪种材料能被磁铁吸引”的选择题。"""
    ferromagnetic = _MATERIALS_BY_KIND["铁磁性"]
    others = _MATERIALS_BY_KIND["顺磁性"] + _MATERIALS_BY_KIND["抗磁性"]
    target = rng.choice(list(ferromagnetic))
    distractors = rng.sample(list(others), 3)
    options: List[str] = [str(target["name"])]
    options.extend(str(record["name"]) for record in distractors)
    rng.shuffle(options)
    distractor_names = "、".join(str(record["name"]) for record in distractors)
    return {
        "index": index,
        "kind": "material",
        "question": "下列哪种材料能被磁铁吸引？",
        "options": options,
        "answer": str(target["name"]),
        "explanation": "%s 属于铁磁性材料（%s），能被磁铁吸引；%s 都不是铁磁性材料。"
        % (target["name"], target["note"], distractor_names),
    }


def _make_magnet_quiz(index: int, rng: random.Random) -> Dict[str, object]:
    """生成一道“磁铁类型与用途”的选择题。"""
    names = magnet_kinds()
    target = rng.choice(list(_MAGNETS))
    distractors = rng.sample(
        [name for name in names if name != target["kind"]], 3
    )
    options: List[str] = [str(target["kind"])]
    options.extend(distractors)
    rng.shuffle(options)
    return {
        "index": index,
        "kind": "magnet",
        "question": "下列哪种磁铁常用于%s？" % target["use"],
        "options": options,
        "answer": str(target["kind"]),
        "explanation": "%s 的特点是：%s" % (target["kind"], target["feature"]),
    }


def quiz_items(count: int, seed: Optional[int] = None) -> List[Dict[str, object]]:
    """生成混合三类题目的选择题，题量范围 1~40。"""
    total = _require_int(count, "题目数量")
    if seed is not None:
        _require_int(seed, "随机种子")
    if total < 1 or total > MAX_QUIZ:
        raise ValueError("题目数量必须在 1 到 %d 之间" % MAX_QUIZ)
    rng = random.Random(seed)
    makers = (_make_pole_quiz, _make_material_quiz, _make_magnet_quiz)
    items: List[Dict[str, object]] = []
    for offset in range(total):
        maker = makers[offset % 3]
        items.append(maker(offset + 1, rng))
    return items


def match_items(count: int, seed: Optional[int] = None) -> List[Tuple[str, str]]:
    """生成配对练习：材料—磁性类别，或磁铁—用途，数量范围 1~20。"""
    total = _require_int(count, "配对数量")
    if seed is not None:
        _require_int(seed, "随机种子")
    if total < 1 or total > MAX_MATCH:
        raise ValueError("配对数量必须在 1 到 %d 之间" % MAX_MATCH)
    rng = random.Random(seed)
    material_pairs: List[Tuple[str, str]] = [
        (str(record["name"]), str(record["kind"])) for record in _MATERIALS
    ]
    magnet_pairs: List[Tuple[str, str]] = [
        (str(record["kind"]), str(record["use"])) for record in _MAGNETS
    ]
    if total == 1:
        return rng.sample(material_pairs + magnet_pairs, 1)
    chosen: List[Tuple[str, str]] = [
        rng.choice(material_pairs),
        rng.choice(magnet_pairs),
    ]
    pool = [
        pair
        for pair in material_pairs + magnet_pairs
        if pair not in chosen
    ]
    chosen.extend(rng.sample(pool, total - 2))
    rng.shuffle(chosen)
    return chosen
