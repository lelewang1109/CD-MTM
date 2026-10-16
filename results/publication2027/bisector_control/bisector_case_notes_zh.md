> 按用户要求恢复三方法并排的紧凑版本，撤回上下堆叠、贯穿时间线和新增身份色标记。当前PDF精确恢复自备份，PNG同步重新渲染；新版对齐布局的脚本与SVG保留在scripts/bisector_projection_time_aligned.py及qa目录中，便于后续恢复。科学数据和数值未改变。

> 时间与颜色对应更新：六个原始场及d轴投影中心与三幅时序地图的t=0/12/25/38/51/63严格竖向对齐，脚本逐项验证坐标变换一致。每幅原始场、每个投影以及地图对应时刻的实际锚点均采用A蓝、B橙、C紫的同一身份色；全图文字黑色。标量背景使用统一渐变与统一标量值域，身份颜色属于标记/轨迹叠加，不改变标量数据。

> 紧凑排版更新：图中文字全部为黑色，删除说明段落、图下注释和固定位置的小字，只保留主要标题、方法名、A/B/C、时间、参考方向与必要坐标。高度从7.3英寸降至5.6英寸，原始场、d轴投影、三方法地图紧密对齐。TMTM/ST-MTM仍为重实现，该来源信息保留在本说明与JSON中，图标题仅显示方法名称。数据、参考位置和布局结果均未更改。

> 配色更新：浅白底、薄荷到湖蓝标量渐变，A/B/C采用蓝/橙/紫；只修改可视化样式，数据与指标不变。飞书参考图链接受访问限制，未能读取，因此此版按“清新浅色”方向设计。

# 高分辨率更新（2026-10-15）

当前PDF/PNG/SVG及逐帧投影使用241×241输入场，原始空间间隔从2降到0.5。高斯函数、64个时间步、峰运动、参考方向、布局规则与方法参数保持一致；三个方法全部重新构树、求解和填充。橙色轨迹连接实际离散锚点，没有进行移动平均、样条或其他轨迹平滑。

61网格时参考B横坐标只有21个不同值，64帧中的43次相邻帧位置重复。新网格参考B横坐标有64个不同值；CD-MTM实际锚点也有64个不同值，两者相邻帧均无位置重复，且B的实际锚点严格递增。采样坐标依旧有0.5单位量化，不应声称使用连续解析真值；解析峰中心只用于核对采样误差。

第63帧P：TMTM16.67%、ST-MTM16.67%、CD-MTM0.84%。端点extrema Stress为0.053 / 0.053 / 0.264，三个方法的实际合并高度误差均为0。主图没有指标曲线，完整新数值保存在bisector_highres_metrics.csv与bisector_highres_x_three_methods.json，数据为bisector_highres_x_three_methods.npz。

重现当前高分辨率主图：

```sh
python3 -W ignore output/pdf/three_method_position_comparison/scripts/prepare_bisector_highres.py bisector_highres x
python3 output/pdf/three_method_position_comparison/scripts/bisector_projection.py
```

以下保留低分辨率版本的构型设计与指标解释；其中61×61、离散投影整数以及旧重现命令针对旧版，不是当前主图。

---

# 中垂线镜像案例：优化后的定性图

## 设计

固定 A=(20,20)、C=(100,100)，令 B 从 (40,80) 移到 (80,40)，始终沿 AC 的中垂线 x+y=120 运动。参考方向 d=(1,0)，q=x。

左右两个端点都满足 AB=BC=√4000≈63.25，AC=√12800≈113.14。三点的两两距离矩阵相同，但 B 的横坐标由40变成80。因此只有两两距离不能辨别 B 在中垂线的哪一侧；固定世界参考可以区分。这是距离信息的镜像歧义，不是“全过程所有相对距离不变”。途中 AB/BC 先减小再增大。

将 AC 从竖直方向倾斜，避免 A、C 在 x 投影上重合。沿用相同构图算法及宽度/间隙规则，未靠修改优化器或挑选更差基线来形成差异。原始竖直版本数据保存在bisector_x_three_methods.npz，优化版数据在bisector_diagonal_x_three_methods.npz。

## 图的阅读

六帧原始场及逐帧 d 轴映射在上方，A/C分别固定在x=20/100，B依次投影到x=40、48、56、64、72、80（离散极值位置）。各投影采用相同0–120坐标尺。下方为实际重新运行的TMTM/ST-MTM重实现与CD-MTM标量地图，橙色只标移动峰B的实际锚点，不是手绘的预期曲线。前两方法展示内部单位地图坐标；CD-MTM直接标定为原始x坐标。空心圈标B的参考端点，虚线标固定A/C参考位置。

主图按用户要求去掉指标曲线，定位为定性机制图。实验数值仍保留于JSON和bisector_diagonal_metrics.csv，不能把删除曲线理解为指标整体更优。

## 可量化的取舍

| 第63帧 | 最大位置误差 (%L) ↓ | Extrema Stress ↓ | 合并高度误差 (%range) ↓ |
|---|---:|---:|---:|
| TMTM | 16.65 | 0.053 | 0 |
| ST-MTM | 16.64 | 0.053 | 0 |
| CD-MTM | 0.84 | 0.264 | 0 |

旧竖直案例的CD-MTM端点Stress为0.628，本优化案例为0.264，仍高于两种相对几何基线。主图的论点是固定参考位置可读性与运动方向辨识，不是CD-MTM在相对Stress上胜出。A/C/B的实际坐标允许小位置偏差，不能写成精确保证。该案例没有使用层级放松（测得拓扑误差0），应作为绝对锚定的控制案例；层级放松的必要性另用已生成的层级/参考顺序冲突案例论证。

## 科学实现与重现

每帧61×61网格，64帧，三峰高斯σ=4，峰值分别A=1、B=1.05、C=0.95，不加入连接脊；全部64帧恰有3个极值。ST-MTM参数uniform/K65/r0.95/λ1.5/L4096/Start0。此为自建案例，未声称复现原论文Gaussian图。ST内部距离采用叶支撑区域质心；理想/实际极值点的端点距离矩阵精确相同，有限网格下的支撑质心距离差另记录于JSON。位置指标给每个基线完整序列上的一次最优固定仿射校准，不允许逐帧重新对齐。图上基线地图使用内部坐标，与误差指标的事后坐标校准分开说明。

```sh
python3 -W ignore output/pdf/three_method_position_comparison/scripts/prepare_bisector_diagonal.py bisector_diagonal x
python3 output/pdf/three_method_position_comparison/scripts/bisector_projection.py
```

## 论文图注建议

A perpendicular-bisector control for absolute reference positioning. A and C remain fixed while B moves from (40,80) to (80,40) on their perpendicular bisector. The mirror endpoints have identical pairwise distances, yet B changes its world x coordinate from 40 to 80. Per-frame reference projections below the scalar fields expose this change explicitly. The temporal maps use the same data; only the moving B anchor is overlaid. TMTM and ST-MTM show little displacement of B, whereas CD-MTM follows its fixed x reference. This example illustrates absolute anchoring rather than improved relative-distance stress or a need for hierarchy relaxation.
