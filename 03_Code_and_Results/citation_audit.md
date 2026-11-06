# 报告引用核查

核查日期：2026-10-07。对象为 report.tex 的十八篇论文、一本教材和一项官方软件文档。此次复核作者、题名、年份、期刊与 DOI，并将正文用途与已有正文阅读记录 references.md 对照。未发现虚构条目；这不等于逐页重新核验所有证明。

| 文献 | 原始来源 | 正文用途 |
| --- | --- | --- |
| Tibshirani (1996) | [出版商 DOI](https://doi.org/10.1111/j.2517-6161.1996.tb02080.x) | Lasso、稀疏性、几何解释 |
| Daubechies, Defrise and De Mol (2004) | [Wiley](https://onlinelibrary.wiley.com/doi/10.1002/cpa.20042) | 迭代阈值的历史与机制 |
| Beck and Teboulle (2009) | [SIAM DOI](https://doi.org/10.1137/080716542) | ISTA/FISTA 更新及目标误差界 |
| Friedman, Hastie and Tibshirani (2010) | [JSS 官方文章](https://www.jstatsoft.org/article/view/v033i01) | 回归坐标更新、残差维护 |
| Parikh and Boyd (2014) | [Stanford 作者页](https://stanford.edu/~boyd/papers/prox_algs.html) · [作者全文](https://stanford.edu/~boyd/papers/pdf/prox_algs.pdf) | 近端算子、软阈值、最优性条件 |
| Wright (2015) | [Springer](https://link.springer.com/article/10.1007/s10107-015-0892-3) | 坐标规则与条件区别 |
| Efron, Hastie, Johnstone and Tibshirani (2004) | [作者提交的期刊重印](https://arxiv.org/pdf/math/0406456) | LARS 背景、Diabetes 数据出处 |
| Ryan J. Tibshirani (2013) | [作者保存的期刊全文](https://www.stat.cmu.edu/~ryantibs/papers/lassounique-ejs.pdf) | 系数唯一性与拟合值区别 |
| Tseng (2001) | [Springer](https://link.springer.com/article/10.1023/A:1017501703105) · [作者存档全文](https://www.mit.edu/~dimitrib/PTseng/papers/archive/bcr_jota.pdf) | 可分非光滑项、坐标下降条件 |
| Wu and Lange (2008) | [作者提交的期刊重印](https://arxiv.org/pdf/0803.3876) | 平方误差 Lasso 的循环坐标下降 |
| Zhao and Yu (2006) | [JMLR](https://jmlr.org/papers/v7/zhao06a.html) · [全文](https://jmlr.org/papers/volume7/zhao06a/zhao06a.pdf) | 模型选择一致性、协方差条件 |
| Zou and Hastie (2005) | [期刊 DOI](https://doi.org/10.1111/j.1467-9868.2005.00503.x) · [作者全文](https://web.stanford.edu/~hastie/Papers/elasticnet.pdf) | 相关特征、elastic net 分组背景 |
| scikit-learn 官方文档 | [Lasso](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html) · [load_diabetes](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_diabetes.html) | 实际数据分发和参考实现的目标归一化 |

## 已处理的元数据问题

- 年份采用期刊年份：Daubechies 等为 2004，Friedman 等为 2010；不采用预印本日期。
- Efron 等列全四名作者，主论文为 32(2):407–451，不将含讨论的更大页码范围当作主论文。
- Parikh–Boyd 作者页与出版商页码不同，详见 references.md。报告仅列期刊、卷期、年份和 DOI，不强行选择页码。
- 正文用作者—年份引用；参考文献按第一作者排序，题名链接到 DOI 或官方页面。软件文档单列为官方文档，不伪装成论文。

## 论断边界

- ISTA 的 O(1/k) 与标准 FISTA 的 O(1/k²) 是条件成立时的目标误差上界，不是时间或残差的保证。
- 标准 FISTA 没有被写成每轮目标单调下降；本项目没有改成重启版本。
- Wright 的随机坐标速率没有被转移成循环 Lasso CD 的通用速率。表中留空表示不作该保证。
- 稀疏性不等于正确支持恢复，真实 Diabetes 数据也没有已知正确支持集合。
- 实验数值来自 results/2026-10-06 与保存结果的分析，不从论文中借用成绩。此次排版修改没有重新运行或改写原始实验。

## 核查限制

此次打开并复核了 JSS、Springer、Stanford 作者全文和 Efron 期刊重印；Tibshirani、Daubechies 和 Beck 的出版信息也通过出版商来源核对。Beck 作者 PDF 链接本次未能重新打开，详细理论定位沿用 references.md 中先前的正文阅读记录。

另尝试 Crossref 元数据复核：Beck、Friedman、Wright 返回成功，其余四项返回 HTTP 429。响应保存于 output/citation_metadata_checked.json；这些失败项没有被标记为 Crossref 核查成功。

## 本次新增五篇的核查范围

已打开五篇全文，核读首页、摘要及相应段落：Tibshirani §1–2 的唯一性与拟合值；Tseng §1 的可分结构；Wu–Lange §2 的平方误差循环更新；Zhao–Yu §1–2 的一致性定义与设计条件；Zou–Hastie §2.3 的分组动机。未声称完整重审全部证明。

Tibshirani 的作者为 **Ryan J. Tibshirani**，与 1996 年原始 Lasso 论文的 **Robert Tibshirani** 区分。Wu–Lange DOI 含 07，但期刊首页标明 2008；Zou–Hastie 作者稿标明 2003/2004，正式引用使用出版商的 2005 年及 67(2):301–320。Zhao–Yu 无需编造 DOI，题名直接链接 JMLR 官方页面。新增条目均在正文使用。

## 进一步扩展综述与作者声明

新增 Hoerl–Kennard (1970)、Zou (2006)、Kim et al. (2007)、Boyd et al. (2011)、O’Donoghue–Candès (2015)、Ndiaye et al. (2017)，均在正文使用。完整元数据、实际核读范围和版本差异见 [本次六篇证据记录](evidence/literature_expansion_2026-10-06.md)。核查以出版商、期刊全文和作者存档为依据，未使用第三方综述代替原始证据。

- Gap Safe 使用 JMLR 的准确题名 *Gap Safe Screening Rules for Sparsity Enforcing Penalties*。不虚构 DOI。安全筛选需要有效区域与对偶可行性；不把小 gap 说成精确系数解或生成变量恢复。
- ADMM 采用当前出版商与作者页的 2011 年，保留较早 PDF 的 2010 卷标差异。其算法参数与模型 λ 区分；未宣称本项目测得 ADMM 更快。
- Restart 采用正式期刊年份 2015，区别于在线发表 2013 和预印本 2012。未将经验动机写成所有 Lasso 问题的线性收敛保证。
- 相关惩罚和扩展求解方法只增加综述，没有增加或更改实验。
- 四位成员的相同贡献声明由用户明确提供，姓名按 CAI、XUE、ZHANG、ZHOU 排列，共享一条脚注。

## 2026-10-07 课堂教材补充

新增 Boyd and Vandenberghe (2004), *Convex Optimization*, Cambridge University Press。课程讲义与两份凸优化 tutorial 指定此教材；在 [官方全文](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf) 核对版权页（PDF 第 4 页）的 2004 首版信息与目录中的 4.4、5.5 节定位。正文用于凸 QP 定义、Slater 与 KKT 的基础联系。本次核查教材元数据、目录以及已读讲义的对应内容，不声称通读整本教材。现有 20 个条目：十八篇论文、一本教材、一项官方软件文档。
