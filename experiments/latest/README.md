# 最新实验入口

这里索引当前已完成的 RG-MTM 实验、评价复算与图片。数值文件保留原实验身份；整理目录、重新绘图或上传不代表重新运行实验。论文正文、附录和写作源码不在发布范围内。

| 实验/结果 | 规模与口径 | 文件入口 |
|---|---|---|
| 六数据集主实验 | ERA5 118 帧、Fire 30 帧、OLR 60 帧、PM2.5 30 帧、Ring 40 帧、Gaussians 64 帧，共 342 帧 | [完整精度对比 CSV](../../results/publication2027/main_comparison.csv)、[实验记录](../../results/publication2027/README.md) |
| 公共几何与稳定性指标 | SNS、TW、TD；与主实验相同的四个固定配置 | [汇总 CSV](../../results/public_metrics_20261016/summary.csv)、[指标协议](../../results/public_metrics_20261016/protocol.json) |
| 排序与运动任务指标 | Kendall、Spearman；三分类平衡准确率、Macro-F1；不是用户实验 | [排序结果](../../results/public_metrics_20261016/reference_tasks/rank_summary.csv)、[运动结果](../../results/public_metrics_20261016/reference_tasks/motion_summary.csv) |
| 垂直平分线控制 | 241×241，64 帧；TMTM、ST-MTM 与 RG-MTM-R | [逐帧指标](../../results/publication2027/bisector_control/bisector_highres_metrics.csv)、[实验记录](../../results/publication2027/bisector_control/bisector_highres_x_three_methods.json) |
| 当前实验图片 | 11 组，PNG 和可编辑 SVG | [图片索引](../../results/figures/README.md) |

主实验定义在 [dataset_suite.py](../../analysis/dataset_suite.py)。原始方法键 `A`、`R 20%` 对应 RG-MTM-P、RG-MTM-R；不重写历史记录。Gaussians 在默认清晰事件口径下的 ME 未定义；PM2.5 的 7 个事件属于探索性案例。位置、运动及几何/稳定性结果分别报告。

从仓库根目录核验已保存的结果，无需原始观测数据：

```sh
PYTHONPATH=src python -m unittest discover -s tests -q
PYTHONPATH=src python experiments/publication2027/validate.py
PYTHONPATH=src python tools/verify_rgmtm_migration.py
python tools/build_latest_experiment_index.py --check
python tools/check_public_export.py
```

从已保存数组重建当前图片：

```sh
PYTHONPATH=src python tools/build_rgmtm_figures.py
```

重新进行科学计算的输入要求、阶段和命令见 [复现说明](../publication2027/REPRODUCING.md)。公共指标的计算入口为 [evaluate_public_metrics.py](../../tools/evaluate_public_metrics.py)，排序/运动复算入口为 [evaluate_reference_task_metrics.py](../../tools/evaluate_reference_task_metrics.py)；这些命令会重新计算结果，应与上述只读核验区分。

[manifest.json](manifest.json) 保存公开实验代码、结果与图片的 SHA-256 和文件大小。若实验或图片发生变化，先检查原因，再运行 `python tools/build_latest_experiment_index.py` 更新清单并一起提交。
