COMP6704 Group 9 — 四算法代码、实验结果与报告
版本：2026-11-06（新增 ADMM 并重新运行全部比较）

1. 当前报告与目录

正式报告：../02_Report/Lasso_Project_Report.pdf（四算法版）
报告源：report.tex
英文模板：templates/report_four_solver_template.tex
参考文献：templates/references.tex
求解器：src/optimizers.py（ISTA、标准 FISTA、循环 CD、scaled ADMM）
测试：tests/test_optimizers.py
最新实验：results/2026-11-06-four-solvers/{main,extended,sensitivity}
最新图：output/figures/four_solvers/；同步镜像 ../04_Figures/four_solvers/

历史 results/2026-10-06 与 results/2026-10-07-extended 保留，不与新主机计时混合。
修改前源文件、文档和原报告备份位于 output/archive/pre-admm-2026-11-06/。
01_Chinese_Guide 仍是历史三算法辅助稿，不是本次四算法报告的同步讲稿。

2. 环境安装与数值测试

本次实际运行：Python 3.10.12，NumPy 2.2.6，SciPy 1.15.3，scikit-learn 1.7.2，
Matplotlib 3.10.9，threadpoolctl 3.8.0；x86_64 Linux/WSL2。
requirements-admm.txt 完整固定本次环境；requirements.txt 与其内容一致。
原环境依赖保留在归档和历史运行快照中。

在本目录创建独立环境后运行：

python -m pip install -r requirements-admm.txt
python -m unittest discover -s tests -v

六项测试包括正交解析解、ADMM 归一化和返回向量、跨 beta 的独立参考、
lambda_max 的零解、秩亏/欠定输入，以及无效 beta 检查。
测试验证数值正确性，不用来判断速度。

3. 复现全部数值实验

python scripts/reproduce_four_solver_study.py --output results/reproduction-01

目标目录必须尚不存在，脚本不会覆盖已保存结果。
依次运行主比较、相关性/维度实验与 ADMM 算法参数敏感性实验。
也可分别运行（各参数路径按需要改为新目录）：

python scripts/run_experiments.py --output results/reproduction-02/main
python scripts/run_extended_experiments.py --output results/reproduction-02/extended
python scripts/run_admm_sensitivity.py --output results/reproduction-02/sensitivity --extended-inputs results/reproduction-02/extended/inputs

原始四个 CSV 的 split 字段与 SHA-256 必须保留。扩展实验保留原成对生成设计，
实际使用的 NPZ 输入随运行保存。跨平台浮点舍入可能令再生成数组有机器精度差异；
本次与历史输入的比较保存在 controlled_input_comparison.json。
所有四算法在每次比较中接收完全相同的当前数组。

4. 从保存结果重画图、重建报告（不重新拟合）

python scripts/plot_four_solver_results.py
python scripts/build_four_solver_report.py

默认读取 results/2026-11-06-four-solvers。
如果使用上一步的新实验：

python scripts/plot_four_solver_results.py --results results/reproduction-01
python scripts/build_four_solver_report.py --results results/reproduction-01

这两步会用指定结果刷新当前图和 report.tex。图和报告应一起更新。
绘图脚本生成 11 组图，每组有 PNG（220 dpi）、SVG、矢量 PDF，并同步到 04_Figures。
figure_manifest.json 记录每个数值输入和输出文件的 SHA-256。
report_four_solver_evidence.json 记录报告自动填入的表格、数值与结果目录。

5. 编译报告

report.tex 引用 output/figures/four_solvers 下的矢量 PDF。
使用带常规宏包的 TeX 发行版或 Tectonic，在本目录执行：

tectonic --keep-logs --outdir ../02_Report report.tex

会产生 ../02_Report/report.pdf；审核后可保存为 Lasso_Project_Report.pdf。
修改模板后，先运行 build_four_solver_report.py 再编译；直接改 report.tex 会在下次构建时覆盖。
GitHub 链接可替换模板中的 projectrepository 宏，再构建并编译。
提交前必须核对总页数（包括参考文献）不超过 15 页。

6. ADMM 与比较口径

共同目标：||Xw-y||^2/(2n) + lambda*||w||_1。
ADMM 用 loss(x)+lambda||z||_1, x=z，返回 w=z；报告目标和公共 R 都在 z 上计算。
正文用 beta 表示 ADMM 参数，API/CSV 使用 admm_rho/rho，避免与相关性 rho 混淆。
默认 beta=1，敏感性 beta=0.1/1/10；不根据敏感性结果反向调整主比较。
每个冷启动都把 Gram 构建与 Cholesky 分解计入总时间；分解只在该次求解内复用。
统一 R<=1e-6、10,000 轮上限；同时记录 ADMM 原始/对偶残差作为诊断。
共同谱范数计算、加载、预处理和绘图排除在求解器计时外，但谱范数成本另行保存。
CD 的一轮是完整坐标扫描，不能把轮数直接当作等成本时间。

7. 保存的证据

main/：80 次计时，16 行实例-方法汇总，16 次 CD 惩罚拟合；
validation.json、运行环境、输入哈希、源码快照、系数、代表轨迹、ADMM 诊断。
extended/：480 次计时，96 行实例-方法汇总，68 次 CD 路径拟合，24 个实际输入；
完整轨迹、ADMM 诊断、系数、环境、配置、来源快照与输入校验。
sensitivity/：45 次计时，15 行参数设定汇总，代表轨迹与原始/对偶残差。
analysis_summary.json：保存结果的机器可读汇总。
output/four_solver_independent_audit.json：独立复核结果和需要保留的结论限制。

实验后的兼容性修改仅限历史绘图/教学辅助函数；原运行源快照保留，
差异见 results/2026-11-06-four-solvers/post_run_source_note.txt。
历史 update_report_extended_figures.py 只适用于旧三算法 TikZ 报告，
不要对当前四算法 report.tex 执行它；新报告使用 build_four_solver_report.py。

8. 提交前事项

GitHub URL 按小组要求暂留明确占位，须补入实际仓库链接后重新构建 PDF。
四种算法本身不能证明每个人独立实现；请据真实工作记录个人实现、验证与讲解分工。
现有 PPT 和中文讲稿没有自动改成四算法版，需要与新报告同步后再合并提交。
作业要求 30 分钟展示、10 分钟 Q&A，四位成员均参与。
