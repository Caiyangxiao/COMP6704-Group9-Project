COMP6704 Group 9 — 四算法展示稿

COMP6704_Group9_Lasso_Presentation.pptx：可编辑PPT，含逐页中英双语备注。
COMP6704_Group9_Lasso_Presentation.pdf：34页纯幻灯片PDF，不含备注页。
Speaker_Notes_Bilingual.txt：与PPT逐页一致的独立讲稿。
Presentation_Timing.csv：逐页时间、主讲人及累计时间。

主讲内容为第1–30页，总计划30分钟：
ZHANG Kejia（26049131R）：引言、简短工作概述，1分30秒。
CAI Yangxiao（26023041R）：Part I，6分钟。
XUE Pengyu（26022951R）：Part II，10分钟。
ZHOU Xiyu（26025265R）：Part III，12分30秒。
第31页：独立10分钟Q&A，四人共同参与。
第32–34页：诊断、原始计时和参考文献备份，不计入主讲30分钟。
英文与中文备注为替代讲稿，演讲时选择一种语言；按照建议时间排练并保留讲图停顿。

确认分工：
PPT制作：ZHANG Kejia。
ISTA实现：ZHOU Xiyu；FISTA实现：XUE Pengyu；循环CD实现：ZHANG Kejia；ADMM实现：CAI Yangxiao。
论文撰写与修改、实验设计与评估均为四人共同协作。

最终合并提交文件：../05_Submission/Group9.pdf（报告在前、PPT在后）。

重建PPT（在02_Code_and_Results目录）：
python -m pip install -r requirements-presentation.txt
python scripts/plot_presentation_assets.py
python scripts/build_presentation.py

标题、备注、时间和主讲人：presentation/slide_content.json。
成员确认分工：presentation/team_roles.json。
页面布局、可编辑正文及表格：scripts/build_presentation.py。
图表与透明公式：scripts/plot_presentation_assets.py，仅读取保存结果。
Windows安装PowerPoint时可导出：
powershell -NoProfile -File scripts/export_presentation.ps1
随后合并：python scripts/combine_submission.py

手动编辑PPT后请同步备注和时间；重新运行构建脚本会使用源文件重建PPT。
历史23分钟三算法稿已备份至02_Code_and_Results/output/archive/pre-presentation-2026-11-06/。
