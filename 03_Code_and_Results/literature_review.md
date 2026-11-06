# Lasso 回归的经典优化算法综述初稿

> 本文用于理解课程报告的背景与方法。以下算法性质来自理论和更新机制；实验已完成，实测结论见 [结果表与讨论](experiment_tables.md)。英文报告整合了两部分。

## 问题与综述范围

在线性回归中，普通最小二乘主要追求拟合误差小。当候选特征很多时，研究者还希望用较少的特征解释和预测响应。Tibshirani 提出的 Lasso 将系数绝对值之和限制在一定范围内，使回归同时具有系数收缩和变量选择的作用。本项目研究平方损失下的 Lasso，不扩展到广义线性模型或其他稀疏正则化模型。[Tibshirani, 1996](https://doi.org/10.1111/j.2517-6161.1996.tb02080.x)

统一采用惩罚形式：

$$
\min_{w\in\mathbb R^d}F(w)
=\underbrace{\frac{1}{2n}\|Xw-y\|_2^2}_{f(w)}
+\underbrace{\lambda\|w\|_1}_{g(w)},\qquad\lambda>0.
$$

其中 $X\in\mathbb R^{n\times d}$ 是特征矩阵，$y\in\mathbb R^n$ 是响应，$w$ 是系数。为简化公式，假设特征与响应已中心化；实际数据的中心化和标准化参数应仅从训练集估计，预测时恢复未受惩罚的截距。特征尺度会改变同一系数惩罚的相对影响，因此三种算法必须使用相同预处理。

综述按更新机制组织：近端梯度法 ISTA、加速近端梯度法 FISTA、循环坐标下降。项目要回答：**针对同一个 Lasso 目标，三种经典算法达到相同优化精度时，计算效率和收敛表现有何区别？**

这些文献承担不同角色。Lasso 原始论文解释模型为何值得研究；迭代阈值论文解释不可微惩罚怎样进入更新；FISTA 论文比较基础更新与加速更新；坐标下降论文强调回归问题的可分结构；近端算法综述提供统一记号。本报告据此连接模型、数学性质和求解方法，而不把每篇论文的全部应用和证明逐一复述。

## Lasso 的模型性质

Ridge 使用平方 $L_2$ 惩罚，通常连续收缩系数；Lasso 使用 $L_1$ 惩罚，可以将部分系数压到零。二维约束图中，$L_1$ 球有位于坐标轴上的角点，能够解释零系数的产生；$L_2$ 球的边界光滑。不过，产生稀疏解不等于必然找到全部真实有效特征，也不保证测试误差优于 ridge。原始论文通过不同信号结构的模拟比较了这些差别。[Tibshirani, 1996](https://academic.oup.com/jrsssb/article-pdf/58/1/267/49098631/jrsssb_58_1_267.pdf)

平方损失满足

$$
\nabla f(w)=\frac{X^\top(Xw-y)}{n},\qquad
\nabla^2f(w)=\frac{X^\top X}{n}\succeq0.
$$

因此 $f$ 凸；$L_1$ 范数也凸，故 $F$ 是凸函数。$\lambda>0$ 时目标在系数趋于无穷时也趋于无穷，存在最优解。凸性并不自动意味着系数解唯一：满列秩的 $X$ 足以使平方损失强凸，但变量数大于样本数时不能直接使用这一条件。

困难在于绝对值在零点不可微。令 $h=\nabla f(w)$，最优性条件是

$$
0\in h+\lambda\partial\|w\|_1.
$$

逐坐标看，非零系数要求 $h_j=-\lambda\operatorname{sign}(w_j)$，零系数要求 $|h_j|\leq\lambda$。这既解释零系数如何成立，也能用于后续检查算法是否接近最优解。[Parikh & Boyd, 2014, §4.2](https://stanford.edu/~boyd/papers/pdf/prox_algs.pdf)

## 近端梯度法 ISTA

ISTA 对平方损失进行梯度更新，再通过一个简单子问题处理 $L_1$ 惩罚。其基础是软阈值算子：

$$
S_\tau(v)_j=\operatorname{sign}(v_j)\max(|v_j|-\tau,0).
$$

简要推导是求解标量问题 $\min_z\frac12(z-v)^2+\tau|z|$：当 $z>0$ 时，一阶条件给出 $z=v-\tau$；当 $z<0$ 时给出 $z=v+\tau$；当 $|v|\leq\tau$ 时零点满足次梯度条件。各坐标相互独立，因此向量形式仍是逐元素软阈值。[Parikh & Boyd, 2014, §6.1.3](https://stanford.edu/~boyd/papers/pdf/prox_algs.pdf)

令 $L=\|X\|_2^2/n$，这里 $\|X\|_2$ 是矩阵谱范数。$L$ 是 $\nabla f$ 的 Lipschitz 常数。固定步长 $0<\eta\leq1/L$ 时，更新为

$$
w^{k+1}=S_{\eta\lambda}\!\left(w^k-\eta\frac{X^\top(Xw^k-y)}n\right).
$$

它来自将平方损失替换成局部线性近似加二次上界，再精确保留 $L_1$ 项。Daubechies、Defrise 和 De Mol 研究了线性逆问题中的迭代阈值方法，并证明相应条件下的收敛。本项目借用其更新思想，不涉及无限维空间的证明细节。[Daubechies et al., 2004；2003 预印本 §2–3](https://arxiv.org/pdf/math/0307152)

ISTA 的优点是更新清楚、易于实现；适当步长下目标值非增。其限制是基本方法的目标误差上界为 $O(1/k)$，可能需要较多轮更新。步长太小也会增加计算时间。[Beck & Teboulle, 2009, §3](https://www.tau.ac.il/~becka/FISTA.pdf)

## 加速近端梯度法 FISTA

FISTA 在外推点而非上一轮系数处执行近端更新。取 $z^1=w^0$、$t_1=1$、$\eta=1/L$，对 $k\geq1$：

$$
\begin{aligned}
w^k&=S_{\eta\lambda}(z^k-\eta\nabla f(z^k)),\\
t_{k+1}&=\frac{1+\sqrt{1+4t_k^2}}2,\\
z^{k+1}&=w^k+\frac{t_k-1}{t_{k+1}}(w^k-w^{k-1}).
\end{aligned}
$$

在凸复合目标、光滑部分的梯度为 Lipschitz 连续、存在最优解，以及正确步长和精确近端更新等条件下，ISTA 和标准 FISTA 分别满足

$$
F(w^k)-F^\star\leq\frac{L\|w^0-w^\star\|^2}{2k},\qquad
F(w^k)-F^\star\leq\frac{2L\|w^0-w^\star\|^2}{(k+1)^2}.
$$

这是目标误差的最坏情况上界，既不是参数误差，也不是所有实例上的实际下降速度。FISTA 的额外工作主要是向量外推，但标准版本不保证每轮目标都下降；理论加速是否转化为运行时间收益，仍需实验验证。[Beck & Teboulle, 2009, §2–4](https://www.tau.ac.il/~becka/FISTA.pdf)

## 循环坐标下降

坐标下降固定其他系数，每次精确求解一个系数。设 $x_j$ 为第 $j$ 列，使用当前最新系数计算部分残差

$$
r^{(j)}=y-\sum_{\ell\ne j}x_\ell w_\ell.
$$

标量子问题为 $\min_u\frac1{2n}\|r^{(j)}-x_ju\|^2+\lambda|u|$，从而

$$
w_j\leftarrow
\frac{S_\lambda(x_j^\top r^{(j)}/n)}{\|x_j\|_2^2/n}.
$$

对标准化至 $\|x_j\|^2/n=1$ 的列，分母为一；零方差特征应在预处理时去除。按固定顺序依次更新全部坐标，构成一次完整扫描（sweep）。Friedman、Hastie 和 Tibshirani 系统讨论了正则化回归的循环坐标下降，包括部分残差、尺度处理和实现效率。[Friedman et al., 2010, §2](https://web.stanford.edu/~hastie/Papers/glmnet.pdf)

该方法不需要选择一个全局梯度步长，单坐标更新也简单。但更新有顺序依赖；相关特征之间可能需要反复调整，这是后续可检验的表现，而非这里的实测结论。完整扫描的成本不能与 ISTA 的单轮成本按“一个坐标算一次迭代”直接比较。

## 比较维度与结论边界

在稠密矩阵、不预计算 Gram 矩阵的实现中，ISTA 每轮主要是两次矩阵向量乘法，成本为 $O(nd)$；FISTA 多出 $O(d)$ 外推。若维护残差，坐标下降单坐标更新为 $O(n)$，完整扫描为 $O(nd)$。实际时间还受向量化和数据布局影响，同阶复杂度不代表耗时相同。[Parikh & Boyd, 2014, §7.1.1](https://stanford.edu/~boyd/papers/pdf/prox_algs.pdf)、[Friedman et al., 2010, §2.1](https://web.stanford.edu/~hastie/Papers/glmnet.pdf)

| 方法 | 机制上的优势 | 需要观察的限制 |
|---|---|---|
| ISTA | 简单；适当步长下目标非增 | 基础收敛率较慢；依赖步长 |
| FISTA | 增加较少向量运算获得更好的理论误差上界 | 标准版本可能出现目标振荡 |
| 循环坐标下降 | 单坐标子问题有闭式解；便于维护残差 | 扫描顺序、特征相关性和实现方式影响表现 |

稀疏性首先是 Lasso 模型和 $\lambda$ 的性质。固定同一目标后，算法主要改变求解过程，不能预设某算法天然具有更好的预测误差。若最优系数不唯一，即使充分收敛，系数也未必完全一致。因此实验应先比较目标值、统一最优性条件和运行时间，再报告测试均方误差与非零系数数量。综述支持这些比较维度；最终优劣判断须在实验后填写。

本项目选择三种方法的原因是它们分别代表全向量更新、历史信息外推和逐坐标求解。它们既足够简单，又能形成机制比较。没有必要为了增加算法数量引入更复杂的框架；本项目也不以提出新方法或证明新的收敛定理为目标。

后续实验可用已知少量有效特征的合成回归数据展示稀疏系数，再用一个真实回归数据集检查训练表现。三种算法应从同一初值出发，使用同一 $\lambda$ 和统一停止精度。额外比较不同 $\lambda$ 时，要单独说明那是在观察模型的拟合与稀疏性权衡。若某算法较快，应结合曲线形状、每轮工作量和实现方式解释；若差别不明显，也应如实报告，而不通过挑选精度或样本制造排名。

## 参考文献与阅读重点

| 编号 | 可靠元数据与来源 | 本次实际阅读重点 |
|---|---|---|
| 1 | Tibshirani, R. (1996). *Regression Shrinkage and Selection via the Lasso*. Journal of the Royal Statistical Society: Series B (Methodological), 58(1), 267–288. [DOI](https://doi.org/10.1111/j.2517-6161.1996.tb02080.x)；[出版商全文](https://academic.oup.com/jrsssb/article-pdf/58/1/267/49098631/jrsssb_58_1_267.pdf) | §2 定义、标准化、正交设计下收缩，以及 Lasso/ridge 几何图；未将原文模拟结果当成本项目结果。 |
| 2 | Daubechies, I., Defrise, M., & De Mol, C. (2004). *An Iterative Thresholding Algorithm for Linear Inverse Problems with a Sparsity Constraint*. Communications on Pure and Applied Mathematics, 57(11), 1413–1457. [DOI](https://doi.org/10.1002/cpa.20042)；[作者 2003 预印本 v2](https://arxiv.org/pdf/math/0307152) | 预印本 §2 阈值更新、§3 收敛定理及假设；2003 为预印本年份，2004 为期刊年份。 |
| 3 | Beck, A., & Teboulle, M. (2009). *A Fast Iterative Shrinkage-Thresholding Algorithm for Linear Inverse Problems*. SIAM Journal on Imaging Sciences, 2(1), 183–202. [DOI](https://doi.org/10.1137/080716542)；[作者全文](https://www.tau.ac.il/~becka/FISTA.pdf) | §2 假设与局部上界；§3 ISTA；§4 FISTA 递推及定理 4.4。 |
| 4 | Friedman, J., Hastie, T., & Tibshirani, R. (2010). *Regularization Paths for Generalized Linear Models via Coordinate Descent*. Journal of Statistical Software, 33(1), 1–22. [期刊页面](https://www.jstatsoft.org/article/view/v033i01)；[作者全文](https://web.stanford.edu/~hastie/Papers/glmnet.pdf) | §2 更新公式、标准化、部分残差，以及单坐标与完整扫描的成本。作者 PDF 是预发表版本，分页与期刊版不同。 |
| 5 | Parikh, N., & Boyd, S. (2014). *Proximal Algorithms*. Foundations and Trends in Optimization, 1(3). DOI: 10.1561/2400000003。作者版与当前出版商页码存在差异，见 [证据记录](references.md)。 [作者主页](https://web.stanford.edu/~boyd/papers/prox_algs.html)；[全文](https://stanford.edu/~boyd/papers/pdf/prox_algs.pdf) | §4.2 近端梯度与最优性条件；§6.1.3、§6.5.2 软阈值；§7.1.1 Lasso 的每轮计算。 |

核查日期：2026-10-05。以上五篇均读取了列明的正文部分；综述采用本项目的 $1/(2n)$ 尺度重写公式，不直接混用不同文献中的损失归一化。
