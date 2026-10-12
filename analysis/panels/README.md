# 论文子图：独立代码与独立画布

## 简洁子图导出

所有独立子图在保存时使用 `common.clean_axes`：不输出标题、图例、文字、
坐标轴、刻度或额外箭头。二维标量场只保留色彩图；地理快照另外保留海岸线，
去掉经纬网、特征圆圈、方向箭头、轨迹、竖线、编号及其他叠加标记。
折线、柱状图、树和布局示意图保留主体几何图元。原始数据计算和各子图
绘图方式没有重写。简洁导出仅用于独立子图，供作者自行组合与添加标注。

## 确认不是截图或裁图

`tools/verify_independent_panels.py` 在运行所有子图时禁止读取项目内的
PDF、PNG、JPEG、TIFF，检查每个子图只有一个独立坐标系，记录实际参与
绘图的二维数值矩阵尺寸、线条及柱形等图元数量。运行命令：

```sh
../.venv/bin/python -W ignore tools/verify_independent_panels.py
```

验证图及记录保存在 `tmp/independent-panel-verification/`，不覆盖论文图。
二维图的 `imshow` 接收的是算法计算出的标量矩阵（例如
`mapsA` 或 `sc['fields_smooth'][tt_]`），没有读取已生成图文件。

`figures/standalone_panel_code.zip` 仅包含源代码、运行说明、数值 JSON
及海岸线坐标，不含任何 PNG、PDF 或截图。包内保留项目目录结构；在
当前项目根目录解压即可使用已有环境与原始数据。独立代码仍依赖项目的
算法模块、Python 依赖和原始 ERA5/火灾数据；它不是无数据依赖的单文件。

每个 `.py` 文件直接绘制自己的子图并建立独立 Matplotlib 画布。
没有读取整张论文图、裁切组合图或从组合图复制像素。
`common.py` 共享的是数据加载与科学计算；绘图语句、尺寸、标记和标题位于对应子图文件。
正式组合图仍由原来的 `analysis/fig_*.py` 生成。

## 运行与输出

从 CD-MTM 根目录运行，使用原有 Python 环境及项目数据：

```sh
../.venv/bin/python -W ignore analysis/panels/fig1/middle_tree_kept.py
../.venv/bin/python -W ignore analysis/panels/build_all.py
```

单图示例只保存指定子图。批量脚本在同一进程中复用计算，以免反复求解布局。
输出在 `paper/pacificvis2027/figures/panels/<组名>/`，每个子图均有 PDF 和 300 dpi PNG。
修改每个文件中的 `canvas(width, height)` 可调整画布，单位为英寸。
修改对应文件的绘图语句可独立配置字体、标题、坐标、图例和标记。

## 图 1：12 个子图

| 位置 | 文件 |
| --- | --- |
| 上方 1：ST-MTM 误差统计 | `fig1/top_stmtm.py` |
| 上方 2：保持树的 certificate | `fig1/top_tree_kept.py` |
| 上方 3：放松后的位移误差 | `fig1/top_relaxed_position.py` |
| 上方 4：放松后的拓扑代价 | `fig1/top_relaxed_topology.py` |
| 中间 1：ST-MTM 时空图 | `fig1/middle_stmtm.py` |
| 中间 2：保持树的时空图 | `fig1/middle_tree_kept.py` |
| 中间 3：放松后的时空图 | `fig1/middle_relaxed.py` |
| 下方 1--5：地理快照 | `fig1/bottom_snapshot_1.py` -- `bottom_snapshot_5.py` |

## 其他组合图

| 组名 | 对应论文图 | 独立子图数 |
| --- | --- | ---: |
| fig2 | 概念图：场、树、布局、单列 map | 4 |
| fig3 | 拓扑代价：保持树、LCA、最优填充、trade-off | 4 |
| fig4 | RQ1：三个真实数据集 | 3 |
| fig5 | exact frontier：五个数据集 | 5 |
| fig6 | winter witness：三个统计 strip、两个时空图、地理场、位置对照 | 7 |
| supp_pipeline | 原附加流程图：五个步骤、map、error strip | 7 |
| supp_dendrogram | 原附加 dendrogram：两张热力图与两张位移图 | 4 |
| supp_toy | 原附加三叶示例：三种布局 | 3 |

共 49 个独立子图：正文 35 个，附加 14 个。

## 配色范围

只修改二维标量场/热力图的配色。气压图、时空标量图和概念标量图使用
`figstyle.FIELD_CMAP` 中的低饱和蓝--白--红发散色图。
其数值范围与既有图保持一致，不把绝对气压改写为气压异常。
火灾热力图为非负量，使用同一蓝色系的顺序色图 `Blues`。
折线、柱状图、树线、散点及分类标记保留论文原来的配色。
