"""Embed frozen experiment coordinates in the existing standalone LaTeX source."""
from pathlib import Path
import json
import shutil
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'results/2026-10-07-extended'
summary=json.loads((DATA/'summary.json').read_text())
rows=summary['summary']
paths=json.loads((DATA/'coefficient_path_data.json').read_text())
trajectory=json.loads((DATA/'trajectory_data.json').read_text())
METHODS=['ISTA','FISTA','CD'];colors=['lassoblue','lassoorange','lassogreen']
seriescolors=['lassoblue','lassoorange','lassogreen','lassopurple','lassopink']

def coords(x,y):return ' '.join(f'({float(a):.8g},{float(b):.8g})' for a,b in zip(x,y))
def plot(x,y,style,sd=None):
    if sd is None:return '\\addplot['+style+'] coordinates {'+coords(x,y)+'};\n'
    points=' '.join(f'({float(a):.8g},{float(b):.8g}) +- (0,{float(c):.8g})' for a,b,c in zip(x,y,sd))
    return '\\addplot['+style+',error bars/.cd,y dir=both,y explicit] coordinates {'+points+'};\n'
def find(study,param,method):return next(r for r in rows if r['study']==study and r['parameter']==param and r['method']==method)
def figure(body,caption,label):
    return '\n\\begin{center}\\begin{minipage}{\\linewidth}\\captionsetup{type=figure}\\centering\\begin{tikzpicture}\n'+body+'\\end{tikzpicture}\n\\caption{'+caption+'}\\label{'+label+'}\\end{minipage}\\end{center}\n'

block=r'''
% BEGIN EXTENDED EXPERIMENTS
\subsection{Controlled correlation and dimension studies}\label{sec:extended}
The original benchmark is small and mostly well conditioned. To test whether its ordering persists, we vary within-block feature correlation and then feature count. The correlation study uses 600 observations and 60 features in blocks of ten. For feature $j$ in block $b$, independent standard-normal draws give
\begin{equation}
 x_j=\sqrt{\rho}\,z_b+\sqrt{1-\rho}\,z_j,
 \qquad \rho\in\{0,0.5,0.9,0.99\}.
 \label{eq:block-correlation}
\end{equation}
The first five coefficients are $(2,-1.5,1,-2,1.5)$, and noise has standard deviation 0.5. Seeds 10--12 share underlying random draws, noise, and a 480/120 split across correlation levels. The dimension study uses independent features, 1,000 observations, an 800/200 split, and $d\in\{50,100,300,600\}$. Within each seed, smaller designs use prefixes of the same 600-column matrix and the same response vector.

Both studies retain zero initialization, $\lambda=0.1\lambda_{\max}$, $R\leq10^{-6}$, and the 10,000-round limit. Each instance has five interleaved timings; reported means and sample standard deviations describe three instance medians. Solver time includes monitoring but excludes the shared spectral calculation. Thread settings are requested before importing the numerical libraries. These timings form a separate run and are not pooled with the original benchmark.

All 360 timed solves converge. The largest relative objective spread between solvers on the same problem is $8.61\times10^{-11}$. This check supports comparison at the stated stationarity tolerance; it does not make $R$ an objective-error bound. Actual inputs, splits, code snapshots, settings, and complete traces are retained with the new results.

\begin{center}\begin{minipage}{\linewidth}\captionsetup{type=table}\centering\small
\caption{Correlation study: condition number and solver time (ms).}\label{tab:correlation}
\begin{tabular*}{\linewidth}{@{\extracolsep{\fill}}@{}lrrrr@{}}\toprule
$\rho$ & $\kappa$ & ISTA & FISTA & Cyclic CD\\\midrule
'''
for rho in [0,.5,.9,.99]:
    r=[find('correlation',rho,m) for m in METHODS]
    cells=[f'${v["time_ms_mean"]:.3f}\\,{{\\pm}}\\,{v["time_ms_sd"]:.3f}$' for v in r]
    winner=int(np.argmin([v['time_ms_mean'] for v in r]));cells[winner]='\\textbf{'+cells[winner]+'}'
    block+=f'{rho:g} & ${r[0]["condition_mean"]:.1f}$ & '+' & '.join(cells)+r'\\'+'\n'
block+=r'''\bottomrule\end{tabular*}\par\vspace{3pt}{\scriptsize $\mu\pm s$: three instance medians; $\kappa$: mean full-Gram condition number.}\end{minipage}\end{center}

At $\rho=0$, ISTA takes $0.360\pm0.010$ ms. At $\rho=0.99$, its mean time rises to 154.599 ms, while FISTA takes $19.862\pm18.153$ ms and CD takes $62.507\pm8.707$ ms. Acceleration has a measured advantage in this highly correlated setting, although the three FISTA instances vary widely. At $\rho=0.5$, the ISTA and CD means are close; the measurements do not establish a precise ranking between them.

The mean condition number $\kappa(X^\top X/n)$ grows from 4.1 to 2492.8. Greater correlation creates weak-curvature directions, which can slow fixed-step progress. The selected support and penalty scale also change, so this full-design condition number is a diagnostic rather than a complete prediction of solver time. The recorded $\rho=0.99$ trace shows FISTA reaching the threshold sooner despite residual oscillations; smooth progress and fast stopping are different properties.
'''
corr=r'''\begin{groupplot}[group style={group size=2 by 2,horizontal sep=1.6cm,vertical sep=1.8cm},width=.43\linewidth,height=4.1cm,grid=major]
'''
for field,title,ylabel in [('time_ms','Time at common tolerance','Time (ms)'),('rounds','Rounds to tolerance','Updates / CD sweeps')]:
    corr+=r'\nextgroupplot[title={'+title+r'},ymode=log,xtick={0,1,2,3},xticklabels={0,0.5,0.9,0.99},xlabel={Correlation $\rho$},ylabel={'+ylabel+'}]\n'
    for m,c in zip(METHODS,colors):
        group=[find('correlation',rho,m) for rho in [0,.5,.9,.99]]
        corr+=plot(range(4),[r[field+'_mean'] for r in group],c+',thick,mark=*',[r[field+'_sd'] for r in group])
        if field=='time_ms':corr+=r'\addlegendentry{'+m+'}\n'
corr+=r'''\nextgroupplot[title={$\rho=0.99$, seed 10},xmode=log,ymode=log,xlabel={Updates / CD sweeps},ylabel={Residual $R$},legend style={at={(.02,.98)},anchor=north west}]
'''
for m,c in zip(METHODS,colors):
    trace=np.genfromtxt(DATA/f'trace_corr_0.99_seed10_{m}.csv',delimiter=',',names=True)[1:]
    idx=np.arange(len(trace)) if len(trace)<600 else np.unique(np.r_[np.arange(10),np.geomspace(10,len(trace)-1,260).astype(int),len(trace)-1])
    corr+=plot(trace['round'][idx],trace['residual'][idx],c+',thick')
corr+=r'''\addplot[black!60,dashed] coordinates {(1,0.000001) (10000,0.000001)};
\nextgroupplot[title={Full-design curvature},ymode=log,xtick={0,1,2,3},xticklabels={0,0.5,0.9,0.99},xlabel={Correlation $\rho$},ylabel={$\kappa(X^\top X/n)$}]
'''
corr+=plot(range(4),[find('correlation',rho,'ISTA')['condition_mean'] for rho in [0,.5,.9,.99]],'black!65,thick,mark=*')
corr+=r'\end{groupplot}'+'\n'
block+=figure(corr,r'Correlation, solver cost, and curvature. Error bars: sample SD across three instance medians. The residual panel uses seed 10; dashed line: $R=10^{-6}$. Long traces are sampled for display.', 'fig:correlation')

block+=r'''
\subsection{Feature count and work per round}
Figure~\ref{fig:dimension} fixes the sample count while increasing the feature count. CD uses four complete sweeps for all twelve instances, but its mean time rises from 0.651 ms at $d=50$ to 6.972 ms at $d=600$. A sweep updates every coordinate, so a constant sweep count still entails more scalar updates. Python-loop and matrix-vector costs remain part of these implementations rather than isolated causes in a profiling study.

ISTA is fastest at every tested width: its mean time increases from 0.341 to 2.078 ms, while its mean round count increases from 15.0 to 43.3. FISTA takes 0.498 to 2.795 ms and more rounds under this residual rule. The width study therefore preserves the ordering of the original independent-feature experiment, whereas strong correlation changes it. This comparison does not cover sparse matrices, $d>n$, or compiled coordinate-descent implementations.
'''
scale=r'''\begin{groupplot}[group style={group size=2 by 1,horizontal sep=1.6cm},width=.43\linewidth,height=4.5cm,xmode=log,xtick={50,100,300,600},xticklabels={50,100,300,600},minor tick num=0,xlabel={Features $d$},grid=major]
'''
for field,title,ylabel in [('time_ms','Solver time','Time (ms)'),('rounds','Rounds to tolerance','Updates / CD sweeps')]:
    scale+=r'\nextgroupplot[title={'+title+'},ylabel={'+ylabel+'}'+(',ymode=log' if field=='time_ms' else '')+']\n'
    for m,c in zip(METHODS,colors):
        group=[find('scaling',d,m) for d in [50,100,300,600]]
        scale+=plot([50,100,300,600],[r[field+'_mean'] for r in group],c+',thick,mark=*',[r[field+'_sd'] for r in group])
        if field=='time_ms':scale+=r'\addlegendentry{'+m+'}\n'
scale+=r'\end{groupplot}'+'\n'
block+=figure(scale,r'Feature-count study with 800 training observations. Means and sample SD across three instance medians; five timings per instance. Shared spectral setup is excluded.', 'fig:dimension')

block+=r'''
\subsection{Coefficient paths and fitting error}
The original four-penalty study is extended to 34 pre-specified values between $0.01\lambda_{\max}$ and $\lambda_{\max}$ on synthetic seed 0 and the fixed Diabetes split. CD starts from zero for each fit and reaches the same tolerance. Figure~\ref{fig:paths} records the coefficients as well as training and test MSE, without selecting a penalty from test scores.

The synthetic paths show retained coefficients approaching zero as the penalty strengthens; weaker penalties also admit small coefficients on inactive variables. On Diabetes, the five highlighted paths are the predictors selected at the main ratio 0.1, not a known true support. Their magnitudes need not all shrink monotonically: s3 first moves farther below zero before returning toward zero. Unlike the orthogonal formula, correlated predictors are fitted jointly, and the penalty changes their allocation of the shared signal.

Large penalties increase fitting error sharply on both fixed splits. Training MSE can exceed test MSE on a particular split; these curves are neither uncertainty estimates nor a generalization bound. A validation procedure would be needed to select a penalty for prediction. The paths explain how the model changes, while the timing studies compare how different algorithms solve a fixed model.
'''
pathfig=r'''\begin{groupplot}[group style={group size=2 by 2,horizontal sep=1.7cm,vertical sep=2.5cm},width=.42\linewidth,height=4.1cm,xmode=log,xlabel={$\lambda/\lambda_{\max}$},grid=major]
'''
for name,title,ylabel in [('synthetic_seed0','Synthetic seed 0','Original coefficients'),('diabetes','Diabetes fixed split','Standardized coefficients')]:
    data=paths[name];ratios=data['ratios'];coefs=np.array(data['coefficients'])
    pathfig+=r'\nextgroupplot[title={'+title+'},ylabel={'+ylabel+r'},legend style={at={(.5,-.32)},anchor=north,legend columns=3,font=\tiny}]'+'\n'
    active=list(range(5)) if name.startswith('synthetic') else list(np.flatnonzero(np.abs(coefs[ratios.index(.1)])>1e-6))
    for j in range(coefs.shape[1]):
        if j not in active:pathfig+=plot(ratios,coefs[:,j],'black!25,thin,forget plot')
    for k,j in enumerate(active):
        pathfig+=plot(ratios,coefs[:,j],seriescolors[k]+',thick')
        pathfig+=r'\addlegendentry{'+data['features'][j]+'}\n'
for name in ['synthetic_seed0','diabetes']:
    data=paths[name];pathfig+=r'\nextgroupplot[ylabel={MSE},legend style={at={(.02,.98)},anchor=north west}]'+'\n'
    for field,c,label in [('train_mse','lassoblue','Training'),('test_mse','lassoorange','Test')]:
        pathfig+=plot(data['ratios'],data[field],c+',thick')+r'\addlegendentry{'+label+'}\n'
pathfig+=r'\end{groupplot}'+'\n'
block+=figure(pathfig,r'Coefficient and error paths over 34 penalties (CD, cold starts). Colored: true active coefficients in the synthetic case; predictors selected at ratio 0.1 in Diabetes. Gray: remaining coefficients. Each column uses its own response scale.', 'fig:paths')

block+=r'''
\subsection{A two-dimensional view of the updates}
A small quadratic example makes the update mechanisms visible without a timing claim. Set $a=(2,-1)^\top$, $Q=\left(\begin{smallmatrix}1&0.9\\0.9&1\end{smallmatrix}\right)$, and $F_{\mathrm{toy}}(w)=\tfrac12(w-a)^\top Q(w-a)+0.03\|w\|_1$. All solvers start at zero, and the unique minimizer is $(1.7,-0.7)^\top$.

Figure~\ref{fig:trajectory} shows the first 25 vector updates or complete CD sweeps. ISTA advances slowly along the elongated contours; FISTA reaches the optimum's neighborhood and crosses it; CD moves along one coordinate at a time. One CD sweep contains two scalar moves, so the panels illustrate geometry rather than equal-cost speed. The traced implementations' terminal coefficients match the existing solvers exactly on this example.
'''
trajfig=r'''\begin{groupplot}[group style={group size=3 by 1,horizontal sep=1.0cm},width=.28\linewidth,height=4.4cm,xmin=-.1,xmax=2.35,ymin=-1.35,ymax=.85,xtick={0,1,2},ytick={-1,0},xlabel={$w_1$},ylabel={$w_2$},grid=major]
'''
for m,c in zip(METHODS,colors):
    trajfig+=r'\nextgroupplot[title={'+m+'}]\n'
    for points in trajectory['contours']:
        points=np.array(points)
        if np.linalg.norm(points[0]-points[-1])<.07:points=np.vstack([points,points[0]])
        trajfig+=plot(points[:,0],points[:,1],'black!22,thin')
    points=np.array(trajectory['paths'][m]);trajfig+=plot(points[:,0],points[:,1],c+',thick,mark=*,mark size=.7pt')
    trajfig+=plot([points[-1,0]],[points[-1,1]],c+',only marks,mark=square*,mark size=2pt')
    trajfig+=plot([0],[0],'black,only marks,mark=*,mark size=1.7pt')
    trajfig+=plot([trajectory['optimum'][0]],[trajectory['optimum'][1]],'black,only marks,mark=star,mark size=3pt')
trajfig+=r'\end{groupplot}'+'\n'
block+=figure(trajfig,r'First 25 vector updates / CD sweeps on the same two-dimensional Lasso objective. Gray: contours; dot: start; star: minimizer; colored square: final displayed iterate. Each CD sweep includes two scalar steps.', 'fig:trajectory')
block+='\n% END EXTENDED EXPERIMENTS\n'

p=ROOT/'report.tex';text=p.read_text();archive=ROOT/'output/archive/revision-08';archive.mkdir(exist_ok=True)
if not (archive/'report-before-expanded-experiments.tex').exists():shutil.copy2(p,archive/'report-before-expanded-experiments.tex')
if '% BEGIN EXTENDED EXPERIMENTS' in text:
    start=text.index('% BEGIN EXTENDED EXPERIMENTS');end=text.index('% END EXTENDED EXPERIMENTS')+len('% END EXTENDED EXPERIMENTS');text=text[:start]+text[end:]
text=text.replace('\\definecolor{lassogreen}{HTML}{258365}', '\\definecolor{lassogreen}{HTML}{258365}\n\\definecolor{lassopurple}{HTML}{805AB1}\n\\definecolor{lassopink}{HTML}{C34A76}') if '\\definecolor{lassopurple}' not in text else text
text=text.replace('All experiments read the saved inputs and fixed splits in Table~\\ref{tab:data}.','The original benchmark reads the saved inputs and fixed splits in Table~\\ref{tab:data}; controlled extensions are specified separately in Section~\\ref{sec:extended}.')
text=text.replace('All 60 timing runs','All 60 original timing runs')
text=text.replace('ISTA is fastest on the synthetic instances; coordinate descent is fastest on Diabetes.', 'ISTA is fastest on the original synthetic instances; coordinate descent is fastest on Diabetes. Controlled correlation and dimension studies test whether this ordering persists.')
text=text.replace("FISTA's stronger worst-case objective bound does not yield a measured time advantage under this stopping rule.", "FISTA has no time advantage on the original benchmark but is faster on average at within-block correlation 0.99.")
text=text.replace('ISTA was fastest on the three synthetic instances, and CD was fastest on the fixed Diabetes split.', 'ISTA was fastest on the three original synthetic instances, and CD was fastest on the fixed Diabetes split.')
text=text.replace('The experiment does not cover all feature correlations, high-dimensional regimes, or production solvers.', 'The extensions cover four block-correlation levels and feature counts up to 600, but not all covariance structures, underdetermined designs, or production solvers.')
needle='\\section{Limitations and Conclusions}';text=text.replace(needle,block+'\n'+needle)
needle='The extensions cover four block-correlation levels'
if 'Strong correlation changes the relative performance of the proximal methods' not in text:
    text=text.replace(needle,'Strong correlation changes the relative performance of the proximal methods: FISTA is faster on average at $\\rho=0.99$, with large variation across instances. Increasing feature count in independent designs preserves ISTA\'s advantage. CD uses few sweeps, but their growing coordinate cost prevents sweep count alone from predicting time.\n\n'+needle)
p.write_text(text)
print('Embedded four figures and one table in the existing source; no external figure files required.')
