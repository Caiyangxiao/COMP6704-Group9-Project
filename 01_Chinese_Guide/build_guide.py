"""Create the Chinese reading guide from saved experiment outputs (no fitting)."""
from pathlib import Path
import argparse, json, math
from xml.sax.saxutils import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

NAVY='#153552'; BLUE='#2563A6'; GRAY='#526273'; LIGHT='#EFF4F7'
def build(root, output, font):
    pdfmetrics.registerFont(TTFont('CJK', str(font)))
    styles={
        'title':ParagraphStyle('title',fontName='CJK',fontSize=24,leading=34,textColor=colors.HexColor(NAVY),spaceAfter=16),
        'h1':ParagraphStyle('h1',fontName='CJK',fontSize=18,leading=25,textColor=colors.HexColor(NAVY),spaceAfter=15),
        'h2':ParagraphStyle('h2',fontName='CJK',fontSize=12,leading=19,textColor=colors.HexColor(BLUE),spaceBefore=12,spaceAfter=7),
        'body':ParagraphStyle('body',fontName='CJK',fontSize=10,leading=17,wordWrap='CJK',alignment=4,spaceAfter=9),
        'small':ParagraphStyle('small',fontName='CJK',fontSize=8.8,leading=14,wordWrap='CJK',textColor=colors.HexColor(GRAY),spaceAfter=7),
        'cell':ParagraphStyle('cell',fontName='CJK',fontSize=9,leading=14,wordWrap='CJK'),
        'code':ParagraphStyle('code',fontName='Courier',fontSize=8,leading=12,spaceAfter=7),
    }
    W=A4[0]-96; story=[]; temp=output.parent/'guide_assets';temp.mkdir(parents=True,exist_ok=True)
    def p(s,style='body'): story.append(Paragraph(s,styles[style]))
    def heading(s): p(s,'h2')
    def page(n,t):
        if story:story.append(PageBreak())
        p(f'{n:02d} / {t}','h1')
    def table(rows,widths=None):
        content=[[Paragraph(escape(str(x)),styles['cell']) for x in row] for row in rows]
        t=Table(content,colWidths=widths or [W/len(rows[0])]*len(rows[0]),hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor(LIGHT)),
            ('TEXTCOLOR',(0,0),(-1,0),colors.HexColor(NAVY)),
            ('LINEABOVE',(0,0),(-1,0),.9,colors.HexColor(NAVY)),
            ('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#A8B6C3')),
            ('LINEBELOW',(0,-1),(-1,-1),.8,colors.HexColor(NAVY)),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F7F9FB')]),
            ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),
            ('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ]));story.extend([t,Spacer(1,10)])
    def img(path,maxh=228):
        from PIL import Image as PILImage
        with PILImage.open(path) as im:iw,ih=im.size
        k=min(W/iw,maxh/ih);a=Image(str(path),width=iw*k,height=ih*k);a.hAlign='CENTER';story.extend([a,Spacer(1,9)])
    def eq(s,name):
        fig=plt.figure(figsize=(8,1));fig.text(.5,.5,'$'+s+'$',ha='center',va='center',fontsize=15,color=NAVY)
        dest=temp/(name+'.png');fig.savefig(dest,dpi=250,bbox_inches='tight',pad_inches=.08,transparent=True);plt.close(fig)
        img(dest,52)
    def code(s):p(escape(s).replace('\n','<br/>'),'code')
    def foot(canvas,doc):
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#D3DCE4'));canvas.line(48,45,A4[0]-48,45)
        canvas.setFont('CJK',8);canvas.setFillColor(colors.HexColor(GRAY));canvas.drawString(48,30,'COMP6704 · Group 9 · Lasso 项目中文说明');canvas.drawRightString(A4[0]-48,30,str(doc.page));canvas.restoreState()

    page(1,'项目逻辑与阅读顺序')
    p('Lasso 回归：<br/>经典优化算法的综述与实验比较','title')
    p('2026 年 10 月 7 日整理 · Convex Optimization · Group 9','small')
    p('核心问题：在同一个 Lasso 训练目标、同一初始化和同一最优性阈值下，ISTA、FISTA 与循环坐标下降分别需要多少计算？特征相关性与特征数量变化时，这个比较会怎样改变？')
    heading('从课程概念走到实验结果')
    table([['步骤','要回答的问题'],['凸建模','目标为什么是凸的？与范数约束、QP 有什么联系？'],['最优性','为什么系数会变成零？怎样判断算法已经足够接近解？'],['求解机制','完整向量更新、外推加速和逐坐标最小化有何成本差异？'],['实测证据','相同精度下谁更快？轮数、时间和预测误差分别说明什么？']], [90,W-90])
    heading('建议阅读顺序')
    p('先读本说明第 3–5 页，把模型、三种更新和实验协议连起来；再看第 6–9 页的实测图；最后用第 10–12 页准备结论、40 分钟展示和复现。英文报告是正式学术正文，包含 10 幅图、11 张表及 20 个参考条目。')
    heading('成员与署名')
    table([['姓名 / 报告署名','学号'],['蔡扬骁 / CAI Yangxiao','26023041R'],['薛鹏宇 / XUE Pengyu','26022951R'],['张珂嘉 / ZHANG Kejia','26049131R'],['周熙宇 / ZHOU Xiyu','26025265R']], [W*.65,W*.35])
    p('四位成员贡献相同，按姓氏的英文字母顺序署名。项目是一篇有实测比较的课程综述；讨论重点是已有方法的机制与适用条件。','small')

    page(2,'综述如何组织，文献如何使用')
    p('分类首先围绕“解怎样更新、一次更新需要什么、还维护哪些状态”。这些维度能解释实验现象，比按论文年份逐篇介绍更适合本项目。')
    table([['机制','代表文献','阅读重点'],['稀疏惩罚','Tibshirani (1996)','Lasso 模型与变量选择'],['近端向量更新','Daubechies et al. (2004)','阈值迭代'],['外推加速','Beck & Teboulle (2009)','FISTA 与目标误差界'],['逐坐标最小化','Friedman et al. (2010)','残差维护与路径计算'],['路径 / 曲率 / 分裂','Efron et al. (2004); Kim et al. (2007); Boyd et al. (2011)','LARS、内点法、ADMM'],['收敛与最优性','Tseng (2001); Parikh & Boyd (2014); Wright (2015)','假设、近端映射、坐标下降']], [110,200,W-310])
    heading('两条线分开讲')
    p('Ridge、Elastic Net 和 Adaptive Lasso 改变惩罚或权重，因此改变模型目标。ISTA、FISTA 和 CD 在这里求解同一个目标，因此主要比较优化成本。某个求解器先达到阈值，不意味着它训练出的模型有更强的统计预测能力。')
    heading('扩展文献保留到什么程度')
    p('Warm starts、restart 与 safe screening 用来解释更成熟的求解器还能减少哪些计算。本项目没有实现这些技术，也没有据此声称性能提升。LARS、内点法和 ADMM 提供更宽的求解背景；数学推导与实验仍集中在三种基础算法。')
    heading('引用核对与继续阅读')
    p('英文报告参考部分含 18 篇论文、Boyd–Vandenberghe (2004) 教材及 scikit-learn 官方文档。交付包保留 references.md、citation_audit.md 和文献核查记录，可定位每项论断的来源。这里沿用报告中已核对的引用，不追加未经核实的论文。')
    p('推荐先读 Tibshirani (1996)、Beck–Teboulle (2009) 与 Friedman et al. (2010)，再用 Parikh–Boyd (2014) 理解软阈值。Boyd–Vandenberghe 教材帮助连接凸性、Slater 条件和 KKT。完整题名、出版信息和原始链接见英文报告与引用核查文件。')

    page(3,'模型、凸性与稀疏性')
    eq(r'F(w)=g(w)+\lambda\|w\|_1,\qquad g(w)=\frac{\|Xw-y\|_2^2}{2n}','objective')
    p('X 是训练特征，y 是中心化后的训练响应，w 是待学习的系数。平方损失负责拟合，L1 惩罚限制系数总幅度。特征按训练集均值和标准差变换；预测时恢复未惩罚的截距。')
    heading('凸性与最优性')
    eq(r'\nabla^2 g(w)=X^\top X/n\succeq0,\qquad 0\in\nabla g(w^*)+\lambda\partial\|w^*\|_1','kkt')
    p('平方损失的 Hessian 半正定，L1 范数也凸，因此目标凸。λ&gt;0 时目标随系数幅度增大而趋于无穷，故存在最小值。X 满列秩是解唯一的充分条件；秩不足时不能仅据此判定解是否唯一。')
    p('如果某个最优系数为零，对应的损失梯度只需落在 [−λ, λ] 内；非零系数则要求梯度与惩罚的符号项抵消。这解释了 L1 为什么允许精确的零，而普通光滑惩罚通常只是缩小系数。')
    eq(r'\mathcal{S}_{\tau}(v)=\mathrm{sign}(v)\max(|v|-\tau,0)','soft')
    img(root/'output/figures/soft_threshold.png',145)
    p('软阈值把阈值区间内的输入直接压为零，也把区间外的幅度缩小。图来自模型解析表达式，是机制示意。','small')
    heading('与课堂上的约束形式和 QP 对接')
    p('同一惩罚解可对应约束问题 min g(w)，条件为 ||w||₁≤t，其中 t=||wλ||₁；λ 与 t 不必一一对应。引入辅助变量 u，令 −u≤w≤u，最小化 g(w)+λΣu，即得到凸二次规划。QP 的 KKT 条件可还原为上面的次梯度最优性条件。')

    page(4,'三种更新到底差在哪里')
    eq(r'w^{k+1}=\mathcal{S}_{\lambda/L}\left(w^k-\nabla g(w^k)/L\right),\quad L=\|X\|_2^2/n','ista')
    p('ISTA 先按平方损失的梯度移动整个系数向量，再做软阈值。FISTA 把梯度计算点换成由前两步构成的外推点，并维护一个加速状态。CD 固定其余变量，依次精确求解每个一维子问题，再维护当前残差。')
    table([['方法','一轮更新','额外状态','本项目实现'],['ISTA','完整向量','无','固定步长 1/L'],['FISTA','外推点上的向量','外推点、加速标量','标准版本；无 restart'],['CD','全部 d 个坐标','当前残差','循环扫描；无 screening']], [80,145,120,W-345])
    img(root/'output/figures/extended/trajectories.png',205)
    p('二维示例的等高线与路径：ISTA 沿谷底逐步移动；FISTA 可越过最优点再折回；CD 的路径由坐标方向的线段组成。三图展示前 25 次向量更新或完整扫描，最优点为 (1.7, −0.7)。CD 途中还画出每个坐标移动。','small')
    heading('理论怎样接到实验')
    p('在相应假设下，ISTA 和 FISTA 的目标误差上界分别是 O(1/k) 与 O(1/k²)。这是关于目标差距的保证。本项目按最优性残差停机，还测量实际时间，因此不能从这个界直接推出 FISTA 每次都最快。标准 FISTA 的目标或残差也可能起伏。')
    p('完整向量更新与一次 CD 扫描的稠密运算量均为 O(nd)，但执行方式和常数不同。一个 CD sweep 含 d 次标量更新；不能把“4 个 sweep”与“40 次向量更新”当作等成本操作。二维图用于解释路径，不提供时间或预测结论。')

    page(5,'实验协议：怎样公平比较')
    table([['项目','统一设置'],['主惩罚','λ=0.1 λmax；λmax=||X^T y/n||∞'],['初始点 / 停止','w=0；R≤10⁻⁶；最多 10,000 轮'],['预处理','仅训练集中心化 / 标准化'],['计时汇总','每个实例计时 5 次，取中位数'],['多实例汇总','3 个种子的中位时间，再算均值 ± 样本标准差'],['记录内容','时间、轮数、目标、残差、MSE、非零数']], [140,W-140])
    eq(r'G_L(w)=L\left[w-\mathcal{S}_{\lambda/L}\left(w-\nabla g(w)/L\right)\right]','mapping')
    eq(r'R(w)=\|G_L(w)\|_\infty/\max\{1,\|X^\top y/n\|_\infty\}','residual')
    p('近端梯度映射在最优点为零。R 用同一归一化尺度衡量三种算法的最优性残差。R≤10⁻⁶ 表示满足本项目的停止标准，不能解读为目标误差一定小于 10⁻⁶。')
    heading('实际运行的范围')
    table([['实验','实例 / 参数','实际拟合数'],['原始主比较','3 个 Synthetic + 1 个 Diabetes','60 次计时'],['原始惩罚比较','4 个实例 × 4 档 λ','16'],['相关性与维度','24 个实例 × 3 方法 × 5 次','360 次计时'],['扩展系数路径','2 个固定实例 × 34 档 λ','68']], [130,230,W-360])
    p('扩展实验固定一个数值计算线程，在导入数值库前设置，并保存检测到的线程信息。相同种子的相关性实验共用底层随机抽样、噪声和划分；维度实验使用嵌套的特征前缀，减少无关随机变化。')
    p('计时包含算法准备与每轮目标、残差检查；共享预处理和谱范数计算另行记录。新旧运行的线程与环境记录分别保留，绝对时间不混合汇总。全部实验输出保存配置、输入和源代码哈希，便于核对。')

    page(6,'原始基准：共同目标，不同成本')
    table([['数据','ISTA / ms','FISTA / ms','CD / ms'],['Synthetic','0.389 ± 0.013','0.519 ± 0.035','0.596 ± 0.010'],['Diabetes','1.419','1.437','0.530']], [105,(W-105)/3,(W-105)/3,(W-105)/3])
    img(root/'output/figures/timing_repetitions.png',225)
    p('各点为一次计时，黑线为同一实例的中位数。Synthetic 有三个实例，Diabetes 只有一个固定训练 / 测试划分。','small')
    heading('先讲一致性，再讲速度')
    p('所有原始运行均达到共同阈值。Synthetic 的最终目标约为 1.800±0.174；Diabetes 为 1812.178。三种算法在同一实例上得到的目标、系数与预测几乎一致，因此这里的主要差别是求解成本。')
    p('Synthetic 上 ISTA 最快；Diabetes 上 CD 最快。FISTA 在小规模实例上没有形成稳定时间优势。五次计时显示运行波动，不能被当成五个独立数据集，也不足以支持总体上的显著性结论。')
    heading('稀疏性与预测各说明什么')
    p('主参数下 Synthetic 平均测试 MSE 为 0.396±0.139，选择 5 个生成变量；Diabetes 测试 MSE 约 2966.94，保留 5 个变量。Synthetic 有已知真系数，可检查支持集；Diabetes 没有已知真支持集，不能把保留 5 个变量称为“正确恢复”。')
    p('实现检查包括正交设计的软阈值解析解及与 scikit-learn 参考解的比较：最大正交系数误差为 1.12×10⁻¹⁵，参考解相对目标差不超过 1.57×10⁻¹²。这些检查支持当前求解实现，不构成所有输入下的证明。','small')

    summary=json.loads((root/'results/2026-10-07-extended/summary.json').read_text())
    def result_table(study):
        vals=[s for s in summary['summary'] if s['study']==study]
        params=sorted(set(v['parameter'] for v in vals));rows=[['ρ' if study=='correlation' else 'd','ISTA / ms','FISTA / ms','CD / ms']]
        for t in params:
            row=[f'{t:g}']
            for method in ['ISTA','FISTA','CD']:
                x=next(v for v in vals if v['parameter']==t and v['method']==method)
                row.append(f"{x['time_ms_mean']:.3f} ± {x['time_ms_sd']:.3f}")
            rows.append(row)
        table(rows,[45,(W-45)/3,(W-45)/3,(W-45)/3])
    page(7,'相关性：什么时候加速更有用')
    p('600 个样本、60 个特征，10 个特征为一块；块内相关系数设为 0、0.5、0.9、0.99。每档 3 个种子，均使用同一惩罚比例与最优性阈值。')
    result_table('correlation')
    img(root/'output/figures/extended/correlation_comparison.png',225)
    p('前两图比较时间与轮数；右图展示 ρ=0.99、seed=10 的残差轨迹。误差棒为三个实例的样本标准差。','small')
    heading('从图里可以直接读出的结论')
    p('独立特征时 ISTA 的开销较小。ρ=0.9 时 CD 的平均时间略低于 FISTA；到 ρ=0.99，FISTA 的平均时间约 19.9 ms，低于 CD 的 62.5 ms 和 ISTA 的 154.6 ms。但 FISTA 的跨实例波动较大，不能把均值差写成每个实例上都成立的排序。')
    heading('机制解释与证据边界')
    p('完整训练 Gram 矩阵的平均条件数从约 4.1 增至 2492.8。相关性增大时，保守的固定步长可能使沿低曲率方向的推进变慢；FISTA 的外推在这个难例上减少了达到阈值所需的更新。图中的残差起伏也说明，加速不等于每步都单调。')
    p('条件数是诊断量。相关性变化还会改变 λmax、所选变量与优化路径，因此不能把全部时间变化归因于条件数。这个实验支持“算法优势会随问题结构改变”，没有验证一种方法在所有相关设计上占优。')

    page(8,'特征数量：为什么轮数少仍可能慢')
    p('1000 个样本，800 个用于训练；独立正态特征数从 50 增至 600。相同种子共用响应、噪声与数据划分，每档特征取同一个大矩阵的前缀。')
    result_table('scaling')
    img(root/'output/figures/extended/dimension_comparison.png',220)
    p('时间与完整轮数并列展示。CD 在四档维度上均约 4 个 sweep；一个 sweep 依次更新 d 个坐标。','small')
    heading('成本必须和轮数一起讲')
    p('在这组独立特征实验里，ISTA 始终有最短平均时间。d=600 时 ISTA、FISTA 和 CD 分别约 2.08、2.80 和 6.97 ms。CD 的扫描轮数保持不变，时间却随特征数量增长，因为一轮含有更多坐标子问题。')
    p('ISTA 的轮数从约 15 增至 43，FISTA 从约 21 增至 54。向量化的矩阵操作与 Python 内部的坐标循环执行方式不同，这与实测差别相符；本项目没有做独立的内核剖析，不能声称已经量化了循环开销的贡献。')
    heading('不要扩大到本实验没有覆盖的范围')
    p('最高维度为 600，仍小于训练样本数 800；这里没有 d&gt;n 的高维情形，也没有稀疏矩阵。生产级 CD 可采用编译实现、warm starts 或筛选，因此这些数字不代表对成熟软件库的全面排序。')

    page(9,'正则化路径：稀疏、收缩与拟合')
    p('用 CD 从零初始化分别求解 34 个预设 λ/λmax，范围为 0.01 到 1。展示原固定 Synthetic seed=0 与 Diabetes 划分；这组图没有使用 warm starts。')
    img(root/'output/figures/extended/coefficient_paths.png',300)
    p('上排：各系数随惩罚变化的路径。Synthetic 使用原始特征单位，彩线为 5 个真实活跃变量；Diabetes 使用标准化系数，彩线为主参数下选择的 5 个变量。下排：同一划分的训练与测试 MSE。','small')
    heading('三件事分别解释')
    p('第一，惩罚增强时整体趋向零模型；λ=λmax 时零系数满足最优性条件。第二，得到正确的非零位置仍可能存在幅度收缩：原始 Synthetic 基准的活跃系数平均绝对误差约 0.221。第三，更少变量不自动带来更小测试 MSE。')
    p('相关特征共同拟合时，单个系数的绝对值不必单调减少。Diabetes 的 s3 路径先向更负方向移动，再返回零，说明不能把“惩罚更强”解释为每个系数在每一步都缩小。')
    heading('怎样避免把展示图写成调参成绩')
    p('这些训练 / 测试曲线描述固定划分下的预设参数效果。没有据测试集选出最优参数后再声称无偏成绩；若后续要正式选择 λ，应在训练数据内部验证。某个划分上训练 MSE 高于测试 MSE，也不能据此推断普遍的泛化性质。')

    page(10,'最后该怎样评价三种算法')
    table([['方法','观察到的优势','主要代价 / 条件'],['ISTA','独立特征小问题开销较低','高相关难例更新多'],['FISTA','高相关难例平均耗时更少','外推与波动；并非总快'],['CD','Diabetes 快；扫描轮数少','每轮含 d 次更新；实现影响大']], [75,205,W-280])
    heading('可以用于报告结论的完整说法')
    p('三种方法求解同一个凸目标，在统一最优性阈值下得到近乎一致的拟合结果。谁更快取决于数据结构、停止规则与实现成本：独立特征的小规模实验偏向 ISTA，Diabetes 偏向 CD；最强相关性的扩展实验中，FISTA 有最低平均求解时间。')
    p('扩展的 360 次计时和 68 次路径拟合全部收敛，同一实例三种方法的最大相对目标差约 8.61×10⁻¹¹。这里的“收敛”按已保存的残差阈值判定，不等于数值上获得数学精确解。')
    heading('五个常见问答')
    table([['问题','回答要点'],['为什么选择 Lasso？','凸且非光滑；稀疏性与三种更新都可解析解释。'],['为什么不直接用梯度下降？','L1 在零处不可微；软阈值处理惩罚。'],['FISTA 有更好理论界，为什么还慢？','界针对目标误差；停机用 R，计时还含额外计算。'],['为什么需要真实和合成数据？','合成可知真系数；真实数据提供实际拟合情形。'],['为什么测试误差几乎相同？','目标、参数、数据都相同；优化精度足够后解接近。']], [185,W-185])
    heading('仍然没有回答的内容')
    p('计时来自同一台主机，三种子不足以建立广泛统计结论；Diabetes 只有一个划分。没有高维稀疏矩阵、大规模交叉验证或生产库的完整性能评测。报告应保留这些边界，避免把局部结果写成通用算法排名。')

    page(11,'40 分钟汇报与四人衔接')
    p('以下是可调整的讲解安排。四位成员各讲 10 分钟，顺序与署名一致；共同贡献不意味着只负责各自讲解的部分。正式幻灯片尚未制作，本包的英文 PDF 是完整项目报告。')
    table([['成员','分钟','内容 / 图'],['CAI Yangxiao','0–10','研究问题；综述分类；Lasso 模型与凸性'],['XUE Pengyu','10–20','软阈值；ISTA、FISTA、CD；二维轨迹'],['ZHANG Kejia','20–30','共同协议；原始基准；相关性图'],['ZHOU Xiyu','30–40','维度图；正则化路径；结论与局限']], [130,65,W-195])
    heading('每张图用三个句子讲清楚')
    p('先说固定了什么、改变了什么；再报一个读图得到的数值或趋势；最后解释机制并给出范围。例如：相关性图固定样本数、特征数和停止标准，ρ=0.99 时 FISTA 平均约 19.9 ms；外推在这个难例上有利，但实例间波动较大。')
    heading('四段之间的连接')
    p('第一段结束：模型是凸的，但零处不可微，所以接下来需要能处理 L1 的更新。第二段结束：三种方法成本不同，下一段在同一阈值下比较实际时间。第三段结束：相关性会改变优势，最后一段进一步看规模和惩罚如何改变计算及拟合。')
    heading('课程信息：已确认与待确认')
    p('最新版正式分组表确认 Group 9 主题为 Convex Optimization，展示日期为 2026 年 11 月 3 日（第 10 周）。项目占课程总评 55%，要求综述、算法实现、实验、优劣讨论及 40 分钟展示。报告提交截止、页数限制和详细评分表未从已读材料确认，不能把展示日期当成报告截止。')
    p('按最新分组表的问答规则，Group 9 需关注 Group 5、6、7、8 的展示并准备问题；日期分别为 11 月 24 日（5、6）、11 月 17 日（7）、11 月 3 日（8）。正式来源：<link href="https://canvas.polyu.edu.hk/courses/4470/modules/items/112438" color="#2563A6">Canvas 最新分组表</link>。课程相关讲义是背景资料，实验结果来自本地实际运行。','small')
    p('报告已说明生成式 AI 辅助用于文献整理、初稿和实验代码，并由组员核验数值与原始来源。引用核查文件保留已确认内容和访问限制。')

    page(12,'文件导航与复现')
    table([['交付目录','内容'],['01_Chinese_Guide','本说明；可编辑生成源'],['02_Report','最新版 17 页英文报告 PDF'],['03_Code_and_Results','代码、输入、两次正式实验、报告源和引用记录'],['04_Figures','展示图 PNG；矢量 SVG；原始基准图']], [150,W-150])
    heading('代码目录内的最短运行方式')
    p('进入 03_Code_and_Results，使用 Python 3.12 建立环境。所需版本固定在 requirements.txt；已保存的输入可直接读取，无需重新下载 Diabetes。')
    code('python3 -m venv .venv\n.venv/bin/python -m pip install -r requirements.txt')
    p('重跑原始比较与扩展比较时使用新的结果目录；脚本拒绝覆盖已有正式结果。绝对计时随主机变化，不能要求复现出完全相同的毫秒数。')
    code('.venv/bin/python scripts/run_experiments.py \\\n  --output results/reproduction-01\n.venv/bin/python scripts/run_extended_experiments.py \\\n  --output results/extended-reproduction-01')
    heading('只需要已有实验图时')
    code('.venv/bin/python scripts/refresh_extended_figures.py')
    p('这条命令只读 results/2026-10-07-extended，不重跑模型；更新 output/figures/extended 中四组 PNG / SVG。包内 04_Figures 是交付时的独立拷贝，重新生成后如需分享，请从 output 目录取新图。')
    heading('数字如何追到原始记录')
    p('原始基准在 results/2026-10-06：optimization_results.csv、timing_repeats.csv、regularization_results.csv、trace_*.csv 与系数文件。扩展记录在 results/2026-10-07-extended：相同类型汇总、path_results.csv、24 个实际输入、72 条残差轨迹及环境 / 配置 / 源码快照。')
    p('report.tex 是英文正文源；引用见 references.md 与 citation_audit.md。顶层 FILE_MANIFEST_SHA256.csv 记录交付文件的校验值。运行前报告快照是实验溯源文件；正式阅读请使用 02_Report 中的最新版。')
    p('本说明 PDF 的生成源保存在 01_Chinese_Guide/build_guide.py，属于可选文档工具，需要 ReportLab、Matplotlib 和包含中文字形的 TrueType 字体；实验复现仅需数值环境。说明中的所有数值来自已保存结果，没有因打包而重跑或改写原始实验。','small')

    doc=SimpleDocTemplate(str(output),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=48,bottomMargin=60,
                          title='COMP6704 Group 9 — Lasso 项目中文说明',author='CAI Yangxiao; XUE Pengyu; ZHANG Kejia; ZHOU Xiyu')
    doc.build(story,onFirstPage=foot,onLaterPages=foot)
    print(output)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--root',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    a.add_argument('--font',type=Path,default=Path('/Library/Fonts/Arial Unicode.ttf'));o=a.parse_args()
    o.output.parent.mkdir(parents=True,exist_ok=True);build(o.root,o.output,o.font)
