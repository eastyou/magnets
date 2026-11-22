# magnets · 磁铁与磁场

[![CI](https://github.com/eastyou/magnets/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/magnets/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.15-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

面向师生的 Python 标准库开源小项目：判断磁极相互作用、识别材料磁性、查询磁铁种类与简化磁场方向，并能生成可直接打印的 A4 练习页与知识海报。零第三方依赖，适合课堂教学、课后练习与物理启蒙。

## 功能特性

- **磁极相互作用**：支持 `N/S`、`n/s`、`北极/南极`、`北/南` 等写法，返回「吸引」或「排斥」。
- **材料磁性分类**：内置 40 种常见材料，区分「铁磁性 / 顺磁性 / 抗磁性」，只有铁磁性材料会被磁铁明显吸引。
- **磁铁种类**：条形、蹄形、环形、圆片、磁针、电磁铁，包含特点与用途。
- **简化磁场方向**：按磁铁与位置查询磁场方向，例如条形磁铁外部为 `N → S`。
- **练习生成**：混合「磁极作用」「材料是否被吸引」「磁铁类型用途」三类题目，数量、随机种子可控且结果可复现。
- **可打印输出**：SVG 示意图与 HTML 海报 / 测验 / 配对练习，全部内置 `@media print` 与 A4 页面规则。
- **健壮性**：所有公开函数都有类型注解、参数校验与中文错误提示；文件写入固定 UTF-8。

## 安装

要求 Python 3.9 及以上版本，仅使用标准库。

```bash
git clone https://github.com/eastyou/magnets.git
cd magnets
python3 -m pip install -e .
```

也可以不安装，直接在仓库根目录运行：

```bash
python3 -m magnets --help
```

## CLI 示例

```bash
python3 -m magnets poles N S
# N 与 S：吸引

python3 -m magnets material 铜
# 名称：铜
# 材料类别：金属
# 磁性类别：抗磁性
# 是否被吸引：否
# 说明：抗磁性金属，不能被磁铁吸引。

python3 -m magnets kind 蹄形
# 类型：蹄形磁铁
# 特点：弯成 U 形（马蹄形），两个磁极靠得较近。
# 用途：提供较强且集中的磁场，常用于电动机和扬声器
# 备注：两极之间磁场较强，适合放置线圈。

python3 -m magnets field 条形 外部
# 条形 · 外部：N → S（磁感线从 N 极出发，回到 S 极）

python3 -m magnets quiz --count 10 --seed 5 -o examples/quiz.html
# 已生成：examples/quiz.html

python3 -m magnets match --count 8 --seed 3 -o examples/match.html
# 已生成：examples/match.html

python3 -m magnets poster -o examples/poster.html
# 已生成：examples/poster.html
```

全部子命令：

| 命令 | 说明 |
| --- | --- |
| `poles <磁极A> <磁极B>` | 判断两个磁极的相互作用 |
| `material <材料>` | 查询材料类别、磁性类别与说明 |
| `kind <磁铁类型>` | 查询磁铁的特点与用途 |
| `field <磁铁> <位置>` | 查询简化模型下的磁场方向 |
| `quiz --count N --seed S [-o 文件]` | 生成 1~40 道选择题 |
| `match --count N --seed S [-o 文件]` | 生成 1~20 组配对练习 |
| `poster [-o 文件]` | 生成可打印知识海报 |

## 库用法

```python
from magnets import (
    field_at,
    interact,
    is_attracted,
    magnet_info,
    magnetic_kind,
    quiz_items,
)

interact("N", "S")                 # "吸引"
interact("北极", "南")             # "吸引"
magnetic_kind("铜")                # "抗磁性"
is_attracted("铁")                 # True
magnet_info("蹄形")["use"]         # "提供较强且集中的磁场，常用于电动机和扬声器"
field_at("条形", "外部")           # "N → S（磁感线从 N 极出发，回到 S 极）"

items = quiz_items(5, seed=7)
print(items[0]["question"], items[0]["options"], items[0]["answer"])
```

## 示例文件

以下页面均由 CLI 真实生成，可直接用浏览器打开并打印为 A4：

- [examples/poster.html](examples/poster.html) —— 磁极规则、材料分类表与磁铁类型卡片
- [examples/quiz.html](examples/quiz.html) —— 10 道选择题（含答案与解析）
- [examples/match.html](examples/match.html) —— 8 组配对练习

## 测试

所有测试均基于标准库 `unittest`，实测结果：

| Python 版本 | 结果 |
| --- | --- |
| 3.9.6（`/usr/bin/python3`） | 184 个测试全部通过 |
| 3.15.2（`python3`） | 184 个测试全部通过 |

本地运行：

```bash
python3 -m unittest discover -s tests -v
```

## 项目结构

```
magnets/
├── magnets/            # 包：model / render / cli
├── tests/              # unittest 测试
├── examples/           # 由 CLI 生成的 HTML 示例
├── .github/workflows/  # GitHub Actions 跨平台 CI
├── pyproject.toml
├── LICENSE
└── README.md
```

## 许可证

MIT © 2026 eastyou
