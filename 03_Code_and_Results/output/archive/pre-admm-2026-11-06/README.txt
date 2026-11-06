COMP6704 Group 9 — 代码、数据与结果

数值目标：||Xw-y||^2/(2n) + lambda*||w||_1。
方法：ISTA、标准 FISTA、循环 CD。
统一零初始点与 R<=1e-6；完整配置见 experiment_plan.md。

1. 运行（在本目录，Python 3.12）

python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/run_experiments.py --output results/reproduction-01
.venv/bin/python scripts/run_extended_experiments.py --output results/extended-reproduction-01

Windows 的对应解释器路径为 .venv\Scripts\python.exe。
已保存结果目录不可覆盖。代码直接读取随包输入，不必再次下载 / 生成。prepare_data.py 仅用于重新准备原始输入，日常复现不要先运行它。扩展实验使用固定种子重新生成受控输入，并保存实际 NPZ 文件。

2. 已保存结果

results/2026-10-06/：60 次主比较计时、12 行逐实例汇总、16 次正则化拟合；轨迹、系数、解析 / 参考检查、运行环境和源快照。
results/2026-10-07-extended/：360 次计时、72 行逐实例方法结果、68 次路径拟合；24 个实际 NPZ 输入、72 条轨迹、路径 / 二维图数据、配置和源快照。

源快照与 report_before_experiments.tex 记录运行当时状态，可能早于目前报告和图的样式。实验之后调整过绘图样式；当前脚本与快照的差异不表示原始数据被改动。数字记录以 CSV / JSON / NPZ 为准。

3. 刷新图和报告

.venv/bin/python scripts/refresh_extended_figures.py

只读已保存扩展结果，更新 output/figures/extended/ 的四组 PNG / SVG，不重新拟合。

.venv/bin/python scripts/update_report_extended_figures.py

把已保存的扩展数值写入本目录 report.tex；会改报告源，但不会自动更新交付包 02_Report 的 PDF。report.tex 含所有绘图数据，可在 LaTeX 编辑器编译；排版源不依赖独立图片或会议 .sty。正式报告 PDF 位于 ../02_Report。

4. 数据与引用

data/manifest.json 记录原始输入与固定划分，data/README.md 记录数据来源。扩展 input_sha256 位于结果目录 environment.json。references.md、citation_audit.md、evidence/ 记录文献核查；中文理论辅助稿为 literature_review.md。当前中文讲解以 ../01_Chinese_Guide 的 PDF 为准。

5. 时间与范围

每实例五次计时取中位数，再跨三个合成实例算均值 / 样本标准差。Diabetes 仅一个划分。原始和扩展计时单独保存，不能混成一次实验。新的绝对时间会随主机变化。R 是最优性残差，非目标误差上界；同一模型目标下不以微小 MSE 差为求解器预测能力排名。

依赖文件仅固定数值实验环境；没有打包 .venv、缓存或课程其他组名单。
