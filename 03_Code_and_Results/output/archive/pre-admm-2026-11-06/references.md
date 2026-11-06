# Lasso 项目：核心文献与证据记录

核查日期：2026-10-05。范围为平方损失 Lasso、ISTA、标准 FISTA、循环坐标下降；LARS 仅用于历史背景、正则化路径和 Diabetes 数据出处。已读取下列文献列明的正文部分，不声称逐页通读所有证明。本文不包含算法实验结果。

统一项目记号为 \(F(w)=\frac1{2n}\|Xw-y\|^2+\lambda\|w\|_1\)。不同论文中的损失系数、标准化和正则化参数不能直接混用。

## 1. Tibshirani (1996)：Lasso 模型与稀疏性

**完整引用：** Robert Tibshirani. “Regression Shrinkage and Selection via the Lasso.” *Journal of the Royal Statistical Society: Series B (Methodological)*, 58(1), 267–288, 1996. DOI：[10.1111/j.2517-6161.1996.tb02080.x](https://doi.org/10.1111/j.2517-6161.1996.tb02080.x)。

**正文来源与阅读：** [出版商 PDF](https://academic.oup.com/jrsssb/article-pdf/58/1/267/49098631/jrsssb_58_1_267.pdf)，§2.1 定义与标准化、§2.2 正交设计、§2.3 几何解释；另读 §11 对模拟情形的总结。

**可支持的表述：** Lasso 将平方误差最小化与系数的绝对值约束结合；部分系数可以精确为零。正交设计下，Lasso 呈软阈值收缩，ridge 呈比例收缩。二维几何图解释稀疏性。

**边界：** 原文的模型比较不能写成“Lasso 总比 ridge 预测更好”；稀疏性不保证正确恢复所有真实特征。1996 是期刊年份；当前出版商迁移页面可能显示较晚的在线日期，不能据此改成年份 2018。

## 2. Daubechies, Defrise and De Mol (2004)：迭代阈值

**完整引用：** Ingrid Daubechies, Michel Defrise, and Christine De Mol. “An Iterative Thresholding Algorithm for Linear Inverse Problems with a Sparsity Constraint.” *Communications on Pure and Applied Mathematics*, 57(11), 1413–1457, 2004. DOI：[10.1002/cpa.20042](https://doi.org/10.1002/cpa.20042)。

**正文来源与阅读：** [作者 arXiv 预印本 math/0307152v2](https://arxiv.org/pdf/math/0307152)，2003-11-02 版本；§2 surrogate 与 shrinkage 更新，§3 定理 3.1 及其假设。期刊元数据由 [Wiley](https://onlinelibrary.wiley.com/doi/10.1002/cpa.20042) 核查。

**可支持的表述：** 梯度式 Landweber 更新后施加阈值，可以求解带稀疏惩罚的线性逆问题。文中在算子范数严格小于一、惩罚权重有正下界等条件下分析迭代收敛。

**边界：** 2003 是预印本年份，2004 是期刊年份，分页不同。不要把该无限维框架的全部条件或证明搬进课程报告。项目中的 \(1/(2n)\) 归一化和步长用 Beck–Teboulle/近端梯度框架统一；ISTA 的 \(O(1/k)\) 目标误差上界在本报告引用下一篇，而不靠这篇推断。

## 3. Beck and Teboulle (2009)：ISTA 与 FISTA

**完整引用：** Amir Beck and Marc Teboulle. “A Fast Iterative Shrinkage-Thresholding Algorithm for Linear Inverse Problems.” *SIAM Journal on Imaging Sciences*, 2(1), 183–202, 2009. DOI：[10.1137/080716542](https://doi.org/10.1137/080716542)。

**正文来源与阅读：** [作者官方全文](https://www.tau.ac.il/~becka/FISTA.pdf)，§2.2 假设、§2.3 二次上界、§3 ISTA 与定理 3.1、§4 标准 FISTA 递推与定理 4.4。PDF 首页标明期刊卷页与 DOI；SIAM 入口偶尔无法打开。

**可支持的表述：** 目标分解为具有 Lipschitz 连续梯度的光滑凸部分与凸非光滑部分，且最优解存在，精确近端步骤和正确步长下，ISTA 的目标误差上界为 \(O(1/k)\)，标准 FISTA 为 \(O(1/k^2)\)。在项目尺度，\(L=\|X\|_2^2/n\)，固定 \(\eta=1/L\)；ISTA 可用 \(0<\eta\leq1/L\)。FISTA 外推递推是 \(t_{k+1}=(1+\sqrt{1+4t_k^2})/2\)。

**边界：** 这些是目标误差上界，不是参数误差或每个实例的精确下降率。标准 FISTA 不保证每轮目标非增；不因上界更好就预写“在本实验最快”。原论文部分例子用无 \(1/2\) 的平方损失，其 Lipschitz 常数含二倍因子，不能照抄到项目目标。

## 4. Friedman, Hastie and Tibshirani (2010)：回归坐标下降

**完整引用：** Jerome H. Friedman, Trevor Hastie, and Rob Tibshirani. “Regularization Paths for Generalized Linear Models via Coordinate Descent.” *Journal of Statistical Software*, 33(1), 1–22, 2010. DOI：[10.18637/jss.v033.i01](https://doi.org/10.18637/jss.v033.i01)。作者全名按 [JSS 官方引用导出](https://www.jstatsoft.org/citationstylelanguage/get/chicago-author-date?publicationId=1756&submissionId=1757) 记录。

**正文来源与阅读：** [Hastie 作者版全文](https://web.stanford.edu/~hastie/Papers/glmnet.pdf)，首页日期 2009-04-29，24 个 PDF 页；§2、§2.1–2.3 更新与计算、§2.5 正则化路径、§2.6 截距。期刊版年份 2010，页码 1–22，不以作者版 PDF 总页数替代。

**可支持的表述：** Lasso 单坐标更新可用部分残差及软阈值；非标准化列需要平方范数分母。维持残差时，稠密数据一个坐标更新为 \(O(n)\)，一次全部 \(p\) 坐标扫描为 \(O(np)\)。论文还讨论 warm start 和其他工程优化。

**边界：** 报告实现只比较基础循环坐标下降，不应把完整 glmnet 的优化性能归给简化实现。论文的性能实验不是本项目结果。原文主要给出实现，引用已有条件收敛理论；不据此宣称任何循环坐标下降在任意凸函数上均收敛或必然最快。

## 5. Parikh and Boyd (2014)：近端算子统一解释

**完整引用（当前出版商元数据）：** Neal Parikh and Stephen Boyd. “Proximal Algorithms.” *Foundations and Trends in Optimization*, 1(3), 127–239, 2014. DOI：[10.1561/2400000003](https://doi.org/10.1561/2400000003)。[当前出版商页面](https://www.emerald.com/ftopt/article-abstract/1/3/127/1324789/Proximal-Algorithms) 明确给出此卷期、页码和年份。

**正文来源与阅读：** [作者主页](https://web.stanford.edu/~boyd/papers/prox_algs.html) 及 [作者 PDF](https://stanford.edu/~boyd/papers/pdf/prox_algs.pdf)，§4.2 近端梯度与最优性条件、§6.1.3 和 §6.5.2 软阈值、§7.1.1 Lasso 每轮运算。

**版本差异：** 作者主页写 2014、123–231；作者 PDF 首页写 2013、123–231、DOI 占位符 “xxx”。这与当前出版商 127–239 不一致。此记录保留该差异，不假称作者 PDF 就是最终排版。正式引用可采用上面的当前出版商元数据，或仅给卷期、年份与 DOI；章节定位沿用实际读过的作者版。

**可支持的表述：** \(L_1\) 近端算子是逐元素软阈值；最优性条件 \(0\in\nabla f+\partial g\) 等价于近端梯度固定点。Lasso 基础近端梯度步骤主要需要一次 \(X\) 和一次 \(X^\top\) 的矩阵向量乘法。

**边界：** 不需引入该综述中的全部框架。由乘法成本得到稠密 \(O(np)\) 属于基础运算量分析，不等于实测时间；若预计算 Gram 矩阵，则成本结构改变。

## 6. Wright (2015)：坐标下降条件与机制

**完整引用：** Stephen J. Wright. “Coordinate Descent Algorithms.” *Mathematical Programming*, Series B, 151(1), 3–34, 2015. DOI：[10.1007/s10107-015-0892-3](https://doi.org/10.1007/s10107-015-0892-3)。[Springer 页面](https://link.springer.com/article/10.1007/s10107-015-0892-3) 核查作者、卷、页、年份。

**正文来源与阅读：** [作者 arXiv 全文 1502.04759](https://arxiv.org/pdf/1502.04759)，32 个 PDF 页，内部分页从 1 起；§1 可分正则与坐标规则、§3.2 假设、§3.6 循环变体定理 3、§3.7 可分正则随机变体定理 4。

**可支持的表述：** 坐标下降是一类方法，选择规则、问题可分结构、曲率及实现共同影响其表现。收敛率需要指定问题假设与算法变体。

**重要边界：** §3.6 的循环结果针对光滑凸目标与规定步长；§3.7 的可分非光滑正则结果针对强凸光滑部分和独立均匀随机坐标，给出期望收敛率。不能把它们直接称为本项目“精确循环 Lasso 坐标下降的通用线性收敛保证”。这里可写：Lasso 具有适合坐标更新的结构，每次精确单坐标最小化使目标非增；进一步理论需匹配条件。报告无须额外证明速率。

## 7. Efron, Hastie, Johnstone and Tibshirani (2004)：LARS 与 Diabetes

**完整引用：** Bradley Efron, Trevor Hastie, Iain Johnstone, and Robert Tibshirani. “Least Angle Regression.” *The Annals of Statistics*, 32(2), 407–451, 2004. DOI：[10.1214/009053604000000067](https://doi.org/10.1214/009053604000000067)。

**正文来源与阅读：** [作者提交的期刊电子重印 arXiv:math/0406456v2](https://arxiv.org/pdf/math/0406456)，首页明确 32(2):407–451，并说明重印版排版与分页不同；§1 与 Table 1 数据、§3.1 Lasso modification 与定理 1。另核对 [Stanford 较早作者版](https://web.stanford.edu/~hastie/Papers/LARS/LeastAngle_2002.pdf) 对应部分。DOI 的 Project Euclid 页面在本次浏览中未提供正文。

**可支持的表述：** Diabetes 示例有 442 位患者和 10 个基线变量：年龄、性别、BMI、平均血压和六项血清指标。响应是基线一年后的连续疾病进展量，因此是回归而非二分类任务。LARS 的 Lasso 修改可在文中相应条件下追踪 Lasso 解路径。

**边界：** 原始 LARS 与 LARS-Lasso 不完全相同；路径计算与固定 \(\lambda\) 的三算法迭代比较也不同，只放在背景。电子重印首页的主论文范围是 407–451；常见 407–499 引用范围包含讨论相关材料，这里只引主论文。该论文是数据的研究出处；实际分发文件、软件提供方及后续训练划分应另行记录，不凭论文推断已下载了哪个版本。

## 可直接用于英文 thebibliography 的条目

下面只提供元数据，不创建或修改报告。Parikh–Boyd 页码按当前出版商记录；上文保留作者版差异。

```latex
\bibitem{tibshirani1996}
R. Tibshirani, ``Regression shrinkage and selection via the lasso,''
\emph{Journal of the Royal Statistical Society: Series B (Methodological)},
vol. 58, no. 1, pp. 267--288, 1996.
\url{https://doi.org/10.1111/j.2517-6161.1996.tb02080.x}.

\bibitem{daubechies2004}
I. Daubechies, M. Defrise, and C. De Mol,
``An iterative thresholding algorithm for linear inverse problems with a sparsity constraint,''
\emph{Communications on Pure and Applied Mathematics},
vol. 57, no. 11, pp. 1413--1457, 2004.
\url{https://doi.org/10.1002/cpa.20042}.

\bibitem{beck2009}
A. Beck and M. Teboulle,
``A fast iterative shrinkage-thresholding algorithm for linear inverse problems,''
\emph{SIAM Journal on Imaging Sciences}, vol. 2, no. 1, pp. 183--202, 2009.
\url{https://doi.org/10.1137/080716542}.

\bibitem{friedman2010}
J. H. Friedman, T. Hastie, and R. Tibshirani,
``Regularization paths for generalized linear models via coordinate descent,''
\emph{Journal of Statistical Software}, vol. 33, no. 1, pp. 1--22, 2010.
\url{https://doi.org/10.18637/jss.v033.i01}.

\bibitem{parikh2014}
N. Parikh and S. Boyd, ``Proximal algorithms,''
\emph{Foundations and Trends in Optimization}, vol. 1, no. 3, pp. 127--239, 2014.
\url{https://doi.org/10.1561/2400000003}.

\bibitem{wright2015}
S. J. Wright, ``Coordinate descent algorithms,''
\emph{Mathematical Programming}, vol. 151, no. 1, pp. 3--34, 2015.
\url{https://doi.org/10.1007/s10107-015-0892-3}.

\bibitem{efron2004}
B. Efron, T. Hastie, I. Johnstone, and R. Tibshirani,
``Least angle regression,'' \emph{The Annals of Statistics},
vol. 32, no. 2, pp. 407--451, 2004.
\url{https://doi.org/10.1214/009053604000000067}.
```

## 写作时的证据检查

- 理论与预期写成条件性陈述；尚未运行的实验不出现数值或排名。
- 同一目标固定 \(\lambda\) 后比较求解效率；变化 \(\lambda\) 时比较模型的稀疏性与预测权衡。
- 一次 CD 单坐标更新与一次完整扫描分开标记；主要效率比较用真实时间和统一最优性精度。
- 真实数据不提供已知的正确支持集合；真实数据特征选择不写成恢复准确率。
- 数据文件来源、划分与训练集预处理需要在准备材料中单独记录，本证据文档没有运行或生成数据。


## 2026-10-06 补充文献

以下五篇已加入英文正文，用于限定结论或补充算法背景；不改变实验目标。

| 完整条目 | 原始正文 | 使用位置 |
| --- | --- | --- |
| Ryan J. Tibshirani. 2013. *The lasso problem and uniqueness*. Electronic Journal of Statistics, 7:1456–1490. DOI: 10.1214/13-EJS815. | [期刊全文](https://www.stat.cmu.edu/~ryantibs/papers/lassounique-ejs.pdf), §1–2 | 凸性与唯一性 |
| Paul Tseng. 2001. *Convergence of a block coordinate descent method for nondifferentiable minimization*. Journal of Optimization Theory and Applications, 109(3):475–494. DOI: 10.1023/A:1017501703105. | [作者存档](https://www.mit.edu/~dimitrib/PTseng/papers/archive/bcr_jota.pdf), §1 | 坐标下降条件 |
| Tong Tong Wu and Kenneth Lange. 2008. *Coordinate descent algorithms for lasso penalized regression*. The Annals of Applied Statistics, 2(1):224–244. DOI: 10.1214/07-AOAS147. | [期刊电子重印](https://arxiv.org/pdf/0803.3876), §2 | 循环坐标更新 |
| Peng Zhao and Bin Yu. 2006. *On model selection consistency of Lasso*. Journal of Machine Learning Research, 7(90):2541–2563. | [JMLR 全文](https://jmlr.org/papers/volume7/zhao06a/zhao06a.pdf), §1–2 | 稀疏性与支持恢复 |
| Hui Zou and Trevor Hastie. 2005. *Regularization and variable selection via the elastic net*. Journal of the Royal Statistical Society: Series B (Statistical Methodology), 67(2):301–320. DOI: 10.1111/j.1467-9868.2005.00503.x. | [作者版](https://web.stanford.edu/~hastie/Papers/elasticnet.pdf), §2.3 | 相关特征的局限 |

完整元数据和版本差异见 citation_audit.md。本次使用基础结论与机制解释，不在报告增加条件定理的完整证明，也不增加 elastic net 实验。

## 2026-10-06 综述范围扩展

新增六篇覆盖相关惩罚、内点法、ADMM、重启与安全筛选的原始文献，英文正文与参考文献均已使用。来源、阅读定位和版本差异集中在 [六篇补充文献记录](evidence/literature_expansion_2026-10-06.md)，不重复整段论文摘要。全文现有十八篇论文及一项官方软件文档。

## 2026-10-07 课堂教材

Stephen Boyd and Lieven Vandenberghe. *Convex Optimization*. Cambridge University Press, 2004. [作者官方页面](https://web.stanford.edu/~boyd/cvxbook/)；[官方全文](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf)。核对全文版权页与目录，基础 QP、Slater、KKT 内容与课程对应页面交叉核读；未逐页通读全书。报告用该教材支持标准凸建模与最优性条件，未据此增加求解器或新的实验保证。
