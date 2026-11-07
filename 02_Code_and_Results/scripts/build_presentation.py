"""Build the editable four-solver PowerPoint and synchronized bilingual notes.

Uses the group's original PolyU presentation background and saved numerical
results. It never reruns an optimizer. Source content: presentation/slide_content.json.
"""
from pathlib import Path
import csv
import hashlib
import json
from statistics import mean, stdev

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from PIL import Image, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent/'04_Presentation'
ASSETS = ROOT/'output/figures/presentation_four_solvers'
BRAND = ROOT/'presentation/brand'
RESULTS = ROOT/'results/2026-11-06-four-solvers'
W,H = 13.333333,7.5
MAROON='A63547'; DARKRED='741426'; INK='222936'; MUTED='616975'
PALE='F6EFF1'; GRAY='F4F6F8'; LINE='DFE3E8'; WHITE='FFFFFF'
COLORS={'ISTA':'2563A6','FISTA':'CF7A26','CD':'258365','ADMM':'805AB1'}
FONT='Arial'
USED=set()


def rgb(value):return RGBColor.from_string(value)
def rect(slide,x,y,w,h,fill=WHITE,line=None,rounded=False):
    sh=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    sh.fill.solid();sh.fill.fore_color.rgb=rgb(fill)
    if line:sh.line.color.rgb=rgb(line);sh.line.width=Pt(.6)
    else:sh.line.fill.background()
    if rounded:
        try:sh.adjustments[0]=.12
        except Exception:pass
    return sh

def text(slide,x,y,w,h,value,size=20,color=INK,bold=False,align=PP_ALIGN.LEFT,font=FONT):
    sh=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=sh.text_frame;tf.clear();tf.word_wrap=True
    tf.margin_left=Inches(.025);tf.margin_right=Inches(.025);tf.margin_top=Inches(.015);tf.margin_bottom=0
    for i,line in enumerate(str(value).split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.alignment=align
        p.space_before=Pt(0);p.space_after=Pt(5);p.line_spacing=1.05
        r=p.add_run();r.text=line;r.font.name=font;r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=rgb(color)
    return sh

def linked(slide,x,y,w,h,value,url,size=12,color=MAROON):
    sh=text(slide,x,y,w,h,value,size,color)
    for p in sh.text_frame.paragraphs:
        for r in p.runs:r.hyperlink.address=url
    return sh

def picture(slide,name,x,y,maxw,maxh):
    p=ASSETS/(name+'.png');assert p.exists(),p
    USED.add(p)
    im=Image.open(p);rw,rh=im.size;scale=min(maxw/rw,maxh/rh)
    w,h=rw*scale,rh*scale
    return slide.shapes.add_picture(str(p),Inches(x+(maxw-w)/2),Inches(y+(maxh-h)/2),width=Inches(w),height=Inches(h))

def card(slide,x,y,w,h,title,body,color=MAROON,title_size=20,body_size=20):
    rect(slide,x,y,w,h,GRAY,LINE,True)
    rect(slide,x,y,.055,h,color)
    text(slide,x+.18,y+.16,w-.34,.6,title,title_size,color,True)
    text(slide,x+.18,y+.9,w-.34,h-1.03,body,body_size)

def bullets(slide,x,y,w,items,size=21,gap=.85,color=INK):
    for i,t in enumerate(items):
        text(slide,x,y+i*gap,.23,.36,'•',size,MAROON,True)
        text(slide,x+.29,y+i*gap,w-.29,gap-.08,t,size,color)

def table(slide,x,y,width,headers,rows,widths=None,rowh=.57,fontsize=18):
    tab=slide.shapes.add_table(len(rows)+1,len(headers),Inches(x),Inches(y),Inches(width),Inches(rowh*(len(rows)+1))).table
    if widths:
        for col,frac in zip(tab.columns,widths):col.width=Inches(width*frac)
    for i,row in enumerate([headers]+rows):
        for j,value in enumerate(row):
            c=tab.cell(i,j);c.fill.solid();c.fill.fore_color.rgb=rgb(MAROON if i==0 else WHITE if i%2==0 else GRAY)
            c.margin_left=Inches(.12);c.margin_right=Inches(.08);c.margin_top=Inches(.06);c.margin_bottom=Inches(.02)
            c.vertical_anchor=MSO_ANCHOR.MIDDLE
            tf=c.text_frame;tf.clear();tf.word_wrap=True
            p=tf.paragraphs[0];p.space_after=Pt(0)
            r=p.add_run();r.text=str(value);r.font.name=FONT;r.font.size=Pt(fontsize-1 if i==0 else fontsize);r.font.bold=i==0;r.font.color.rgb=rgb(WHITE if i==0 else INK)
    return tab

def base(prs,item):
    s=prs.slides.add_slide(prs.slide_layouts[6])
    if item['id'] in [1,3,10,20,31]:
        return s
    s.shapes.add_picture(str(BRAND/'original_3_2.png'),0,0,width=Inches(W),height=Inches(H))
    text(s,.45,.12,11.9,.43,item['title'],26,WHITE,True)
    # Replace the baked legacy footer so speaker/part labels remain accurate.
    rect(s,0,7.1,W,.4,DARKRED)
    text(s,.45,7.17,3.7,.24,item['speaker']+'  '+item.get('student_id',''),10,WHITE)
    text(s,4.2,7.17,6.9,.24,item['part'],10,WHITE,align=PP_ALIGN.CENTER)
    text(s,11.8,7.17,1.0,.24,f"{item['id']:02d} / 34",10,WHITE,align=PP_ALIGN.RIGHT)
    return s

def headline(slide,value):text(slide,.62,.87,12.06,.72,value,23,INK,True)
def takeaway(slide,value):
    rect(slide,.6,6.41,12.13,.48,PALE)
    size=16.0
    font_path=Path('C:/Windows/Fonts/arialbd.ttf')
    if not font_path.exists():font_path=Path('/mnt/c/Windows/Fonts/arialbd.ttf')
    if font_path.exists():
        while size>13.5:
            metric=ImageFont.truetype(str(font_path),round(size*10))
            if metric.getlength(value)<=11.74*72*10:break
            size-=.25
    text(slide,.78,6.49,11.79,.30,value,size,MAROON,True)
def source(slide,value):text(slide,.65,6.93,12.0,.16,value,8.1,MUTED)

def timefmt(seconds):return f'{seconds//60:02d}:{seconds%60:02d}'
def records(name):
    with (RESULTS/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def pm(v,d=3):return f'{mean(v):.{d}f} ± {stdev(v):.{d}f}' if len(v)>1 else f'{v[0]:.{d}f}'


def main():
    OUT.mkdir(exist_ok=True)
    content=json.loads((ROOT/'presentation/slide_content.json').read_text(encoding='utf-8'))
    items=content['slides'] if isinstance(content,dict) else content
    assert [a['id'] for a in items]==list(range(1,35))
    assert sum(int(a['seconds']) for a in items if a['id']<=30)==1800
    roles=json.loads((ROOT/'presentation/team_roles.json').read_text(encoding='utf-8'))
    mainrows=records('main/optimization_results.csv');extrows=records('extended/optimization_results.csv')
    prs=Presentation();prs.slide_width=Inches(W);prs.slide_height=Inches(H)
    prs.core_properties.title='Classical Optimization Algorithms for Lasso Regression'
    prs.core_properties.subject='COMP6704 Group 9 — Four-solver comparison'
    prs.core_properties.author='COMP6704 Group 9'
    prs.core_properties.last_modified_by='ZHANG Kejia'
    prs.core_properties.keywords='Lasso; ISTA; FISTA; cyclic CD; ADMM; Group 9'
    prs.core_properties.comments='Presentation design: ZHANG Kejia. Intro: ZHANG; Part I: CAI; Part II: XUE; Part III: ZHOU. Team-confirmed contributions.'
    timing=[];notes=[];elapsed=0
    for item in items:
        i=item['id']
        s=base(prs,item)
        if i in [1,3,10,20,31]:
            # Keep the original university-branded cover and section-dividers.
            s.shapes.add_picture(str(BRAND/'original_1_2.png'),0,0,width=Inches(W),height=Inches(H))
            if i==1:
                text(s,.8,1.27,9.4,2.03,'Classical Optimization\nAlgorithms for Lasso Regression',34,WHITE,True)
                text(s,.83,3.55,10.8,.56,'Four solvers · One objective · A common accuracy target',22,WHITE)
                for j,m in enumerate(roles['members']):
                    text(s,.82+j*3.10,5.16,3.03,.5,m['name'],17,WHITE,True)
                    text(s,.82+j*3.10,5.65,3.03,.4,m['student_id'],15,WHITE)
                text(s,.83,6.74,9.8,.26,'Opening: ZHANG Kejia  |  30-minute presentation + 10-minute Q&A',12,MUTED)
                linked(s,.83,7.06,9.8,.22,'github.com/Caiyangxiao/COMP6704-Group9-Project',roles['repository'],10.5)
            elif i==31:
                text(s,.8,1.5,8.5,1.2,'Discussion',43,WHITE,True)
                text(s,.82,2.75,9.8,.62,'10-minute Q&A · All four members',25,WHITE)
                text(s,.82,3.73,10.8,1.75,'CAI — formulation and ADMM\nXUE — acceleration and comparison protocol\nZHANG — cyclic CD and reproducibility\nZHOU — ISTA and empirical findings',19,WHITE)
                linked(s,.83,6.85,10.4,.27,'Code, data and reproducibility: github.com/Caiyangxiao/COMP6704-Group9-Project',roles['repository'],11)
            else:
                names={3:('PART I','Background and formulation'),10:('PART II','Algorithms and experimental design'),20:('PART III','Results and conclusions')}
                a,b=names[i];text(s,.82,1.65,8.6,.7,a,25,WHITE,True)
                text(s,.8,2.58,9.4,1.8,b,36,WHITE,True)
                text(s,.82,5.1,8.7,.5,item['speaker'],24,WHITE,True)
                text(s,.82,5.68,8.7,.4,'Student ID: '+item['student_id'],17,WHITE)
            # Hero backgrounds cover the ordinary slide footer intentionally.
        elif i==2:
            headline(s,'Four implementations answer one shared optimization question.')
            cols=[('I  Background','CAI Yangxiao','Formulation, convexity\nand sparse optimality'),('II  Algorithms','XUE Pengyu','ISTA, FISTA, cyclic CD, ADMM\nand a common protocol'),('III  Results','ZHOU Xiyu','Accuracy, runtime, sensitivity\nand conditional conclusions')]
            for j,(a,b,c) in enumerate(cols):
                x=.65+j*4.15;card(s,x,1.9,4.0,3.6,a,b+'\n\n'+c,body_size=21)
            takeaway(s,'Introduction and work overview: ZHANG Kejia  |  Experimental design and evaluation: all four members')
            source(s,'Group 9 four-solver report, Sections 1–6; member contributions confirmed by the group.')
        elif i==4:
            headline(s,'Sparse regression makes optimization and feature selection visible.')
            picture(s,'truth_support',.65,1.75,8.1,4.2)
            card(s,9.02,1.88,3.65,1.7,'50 candidate features','5 generating variables',body_size=21)
            card(s,9.02,3.83,3.65,1.9,'Convex + nonsmooth','A tractable model with\nalgorithmic choices',body_size=20)
            takeaway(s,'Known generating coefficients give a direct check of support recovery and shrinkage.')
            source(s,'Report Sections 1 and 4.1; saved synthetic-generation specification. Bars show the generating coefficients.')
        elif i==5:
            headline(s,'Every solver minimizes the same normalized Lasso objective.')
            rect(s,.7,1.7,11.95,1.5,GRAY,LINE,True);picture(s,'eq_objective',1.0,1.9,11.35,1.1)
            card(s,.7,3.53,5.77,2.22,'Squared training loss','Fits centered responses\nX: n × d,  w: d coefficients',body_size=21)
            card(s,6.72,3.53,5.93,2.22,'L1 penalty λ‖w‖₁','Encourages sparse coefficients\nλ controls regularization',body_size=21)
            takeaway(s,'Center and scale using training statistics; restore an unpenalized intercept for prediction.')
            source(s,'Report Section 2.1, Eq. (1); Tibshirani (1996).')
        elif i==6:
            headline(s,'Changing the penalty changes the estimator.')
            table(s,.7,1.78,11.95,['Model','Penalty','Main distinction'],[
                ['Ridge','α‖w‖₂² / 2','Usually dense coefficients'],['Lasso','λ‖w‖₁','Exact zeros through thresholding'],['Elastic net','λ‖w‖₁ + α‖w‖₂² / 2','Sparsity and correlated-variable grouping'],['Adaptive Lasso','λ Σⱼ ωⱼ|wⱼ|','Fixed weighted thresholds']],widths=[.19,.34,.47],rowh=.71,fontsize=20)
            takeaway(s,'The benchmark fixes unweighted Lasso and compares how four algorithms solve it.')
            source(s,'Report Section 1.2 and Table 1; Hoerl & Kennard (1970), Tibshirani (1996), Zou & Hastie (2005), Zou (2006).')
        elif i==7:
            headline(s,'Convexity supports global optimization; subgradients permit zeros.')
            rect(s,.7,1.69,11.95,1.2,GRAY,LINE,True);picture(s,'eq_kkt',1.0,1.85,11.35,.85)
            card(s,.7,3.19,5.78,2.6,'Convex objective','∇²g(w) = XᵀX / n ⪰ 0\nλ‖w‖₁ is convex\nEvery local minimum is global.',body_size=21)
            card(s,6.73,3.19,5.92,2.6,'Coordinate optimality','w*ⱼ ≠ 0:  ∇ⱼg = −λ sign(w*ⱼ)\nw*ⱼ = 0:  |∇ⱼg| ≤ λ\n∂|0| = [−1, 1]',body_size=20)
            takeaway(s,'Coefficient uniqueness requires additional structure; optimality and true-support recovery are separate checks.')
            source(s,'Report Section 2.2; Boyd & Vandenberghe (2004), Tibshirani (2013).')
        elif i==8:
            headline(s,'Soft thresholding sets small inputs to zero and shrinks larger ones.')
            picture(s,'soft_threshold',.68,1.9,7.6,4.12)
            picture(s,'eq_soft',8.45,1.85,4.15,1.6)
            table(s,8.6,3.75,3.85,['Input','τ = 0.5'],[['1.2','0.7'],['−0.8','−0.3'],['0.2','0']],widths=[.5,.5],rowh=.47,fontsize=19)
            takeaway(s,'The same proximal operation appears in ISTA, FISTA, coordinate descent and ADMM.')
            source(s,'Report Section 2.3, Eq. (5); Parikh & Boyd (2014).')
        elif i==9:
            headline(s,'Fix the model, then compare update mechanisms and computation.')
            owners={'ISTA':'ZHOU Xiyu','FISTA':'XUE Pengyu','CD':'ZHANG Kejia','ADMM':'CAI Yangxiao'}
            mechanism={'ISTA':'Gradient step\n+ threshold','FISTA':'Extrapolation\n+ threshold','CD':'Exact scalar\nminimization','ADMM':'Linear solve\n+ split updates'}
            for j,m in enumerate(['ISTA','FISTA','CD','ADMM']):card(s,.65+j*3.13,1.9,2.98,3.88,m,mechanism[m]+'\n\nImplemented by\n'+owners[m],COLORS[m],body_size=19)
            takeaway(s,'Same data, preprocessing, λ and final stationarity target across all four implementations.')
            source(s,'Report Sections 3.1–3.4 and confirmed author contributions; classical methods, no new algorithm claimed.')
        elif i==11:
            headline(s,'ISTA takes a fitting step, then applies the L1 proximal map.')
            rect(s,.7,1.7,11.95,1.55,GRAY,LINE,True);picture(s,'eq_ista',1.0,1.93,11.35,1.05)
            for j,(a,b) in enumerate([('1  Current iterate','wᵏ'),('2  Gradient step','η = 1/L'),('3  Threshold','τ = ηλ')]):card(s,.7+j*4.1,3.58,3.85,2.15,a,b,COLORS['ISTA'],body_size=25)
            takeaway(s,'O(nd) dense work per monitored round; a nonincreasing objective with a valid step size.')
            source(s,'Report Section 3.1; Daubechies et al. (2004), Beck & Teboulle (2009). Implementation: ZHOU Xiyu.')
        elif i==12:
            headline(s,'FISTA adds momentum through an extrapolated evaluation point.')
            rect(s,.7,1.73,7.8,4.1,GRAY,LINE,True);picture(s,'eq_fista',.96,1.95,7.28,3.58)
            card(s,8.8,1.73,3.85,4.1,'Acceleration','O(k⁻²) objective-error bound\n\nStandard FISTA can oscillate.\n\nNo restart is used here.',COLORS['FISTA'],body_size=21)
            takeaway(s,'A stronger objective-error guarantee does not determine elapsed time to the common residual threshold.')
            source(s,'Report Section 3.1; Beck & Teboulle (2009). Implementation: XUE Pengyu.')
        elif i==13:
            headline(s,'Cyclic CD solves one coefficient exactly using the latest residual.')
            rect(s,.7,1.7,11.95,1.65,GRAY,LINE,True);picture(s,'eq_cd',1.0,1.88,11.35,1.25)
            card(s,.7,3.65,5.78,2.16,'Residual reuse','r⁽ʲ⁾ = r + xⱼwⱼ\nUpdate wⱼ, then r = r⁽ʲ⁾ − xⱼwⱼ',COLORS['CD'],body_size=21)
            card(s,6.73,3.65,5.92,2.16,'One complete sweep','Visit j = 1, …, d\nO(n) per coordinate; O(nd) per sweep',COLORS['CD'],body_size=21)
            takeaway(s,'A small sweep count can still contain many sequential scalar updates.')
            source(s,'Report Section 3.2; Friedman et al. (2010), Wu & Lange (2008). Implementation: ZHANG Kejia.')
        elif i==14:
            headline(s,'ADMM separates squared loss and the L1 penalty through x = z.')
            rect(s,.7,1.7,11.95,2.82,GRAY,LINE,True);picture(s,'eq_admm',1.0,1.9,11.35,2.42)
            text(s,.9,4.91,11.55,.8,'β > 0 is the algorithmic penalty.  λ controls the Lasso model.',22,MAROON,True)
            text(s,.9,5.63,11.55,.45,'Initialize x, z, u at zero.  Return w = z.  Main benchmark: β = 1.',21)
            takeaway(s,'The matrix, threshold and objective all use the same 1/(2n) loss normalization.')
            source(s,'Report Section 3.3, Eqs. (14)–(16); Boyd et al. (2011). Implementation: CAI Yangxiao.')
        elif i==15:
            headline(s,'ADMM reuses a factorization within each cold solve.')
            card(s,.7,1.9,5.78,3.82,'Prepare once','Form XᵀX/n + βI\nCache a Cholesky factor\nInclude this cost in total time.\n\nDense preparation: O(nd² + d³)',COLORS['ADMM'],body_size=21)
            card(s,6.73,1.9,5.92,3.82,'Repeat the split updates','Triangular solve, threshold, dual step\nMonitor the same F(z) and R(z)\n\nPer monitored round: O(nd + d²)\nExtra matrix storage: O(d²)',COLORS['ADMM'],body_size=20)
            takeaway(s,'No factorization is shared across timing repetitions, instances or penalty settings.')
            source(s,'Report Sections 3.3–3.4; current dense Cholesky implementation and common monitoring protocol.')
        elif i==16:
            headline(s,'Rounds expose update counts; elapsed time includes their different costs.')
            table(s,.7,1.75,11.95,['Method','Core operation','Objective','Monitored work'],[
                ['ISTA','Vector thresholding','Monotone','O(nd)'],['FISTA','Extrapolation + threshold','May oscillate','O(nd)'],['Cyclic CD','d exact scalar updates','Monotone','O(nd) / sweep'],['ADMM','Cached solve + split updates','May oscillate','O(nd + d²)']],widths=[.17,.39,.22,.22],rowh=.7,fontsize=19)
            takeaway(s,'All comparisons use the same returned-vector stationarity measure and cold total time.')
            source(s,'Report Section 3.4 and Table 2; no universal cyclic-CD or ADMM rate is assigned.')
        elif i==17:
            headline(s,'Saved inputs and paired designs isolate the effects we vary.')
            table(s,.7,1.72,11.95,['Study','Samples / features','Instances and control'],[
                ['Synthetic','300 / 50; train 240','Seeds 0–2; 5 active variables'],['Diabetes','442 / 10; train 353','One saved split; true support unknown'],['Correlation','600 / 60; train 480','ρ = 0, 0.5, 0.9, 0.99; paired seeds 10–12'],['Dimension','1,000 / 50–600; train 800','d = 50, 100, 300, 600; paired prefixes']],widths=[.2,.35,.45],rowh=.75,fontsize=18.5)
            takeaway(s,'Train-only preprocessing and fixed splits are shared by every solver on each problem.')
            source(s,'Report Section 4.1; CSV hashes, controlled NPZ inputs and split indices are retained.')
        elif i==18:
            headline(s,'Stop at the same stationarity accuracy on the returned coefficients.')
            rect(s,.7,1.68,11.95,2.15,GRAY,LINE,True);picture(s,'eq_residual',1.0,1.9,11.35,1.72)
            bullets(s,.85,4.15,11.7,['R(w) ≤ 10⁻⁶; maximum 10,000 complete rounds.','Five interleaved timings; report each instance’s median.','Total includes preparation and monitoring; shared spectral setup is recorded separately.'],20.5,.64)
            takeaway(s,'R = 0 is KKT stationarity. A small R is not an objective-error upper bound.')
            source(s,'Report Section 4.2, Eqs. (18)–(19). ADMM uses w = z; primal/dual split residuals are extra diagnostics.')
        elif i==19:
            headline(s,'Validate the normalization, then preserve the evidence needed to rerun it.')
            card(s,.7,1.9,5.78,3.9,'6 correctness tests passed','Orthogonal closed form\nNormalized ADMM first update\nIndependent reference across β\nZero threshold and rank-deficient design',body_size=20)
            card(s,6.73,1.9,5.92,3.9,'560 primary + 45 sensitivity runs','All reached R ≤ 10⁻⁶\nRaw timings, coefficients and traces\nFixed inputs, configs and source hashes\n11 figure groups from saved data',body_size=20)
            takeaway(s,'All four methods were rerun on one host; historical timings are preserved separately.')
            source(s,'Report Section 4.3; tests/test_optimizers.py and results/2026-11-06-four-solvers/.')
        elif i==21:
            headline(s,'Converged solvers give nearly identical fitted results.')
            rows=[]
            for m in ['ISTA','FISTA','CD','ADMM']:
                syn=[float(r['test_mse']) for r in mainrows if r['method']==m and r['dataset'].startswith('synthetic')]
                dia=next(r for r in mainrows if r['method']==m and r['dataset']=='diabetes')
                rows.append([m,pm(syn),f"{float(dia['test_mse']):.3f}",'5 on every main input'])
            table(s,.7,1.88,11.95,['Solver','Synthetic test MSE','Diabetes test MSE','Nonzero coefficients'],rows,widths=[.16,.28,.27,.29],rowh=.72,fontsize=20)
            text(s,.88,5.77,11.55,.38,'Maximum main within-problem relative objective spread: 3.17 × 10⁻¹²',20,MAROON,True)
            takeaway(s,'Tiny test-error differences at fixed λ provide no evidence of optimizer predictive superiority.')
            source(s,'Report Section 5.2, Table 4; synthetic values are means ± sample SD across three instances.')
        elif i==22:
            headline(s,'ISTA is fastest on the synthetic inputs; ADMM is fastest on Diabetes here.')
            picture(s,'main_runtime',.7,1.74,11.95,4.37)
            takeaway(s,'Time includes ADMM preparation. The conclusion concerns these implementations and this host.')
            source(s,'Report Section 5.1, Table 3; 5 timings per instance. Synthetic: means ± sample SD of three instance medians.')
        elif i==23:
            headline(s,'The common residual shows when each solver reaches the accuracy target.')
            picture(s,'stationarity',.7,1.72,11.95,4.25)
            takeaway(s,'FISTA’s accelerated objective bound does not guarantee earlier residual stopping on each problem.')
            source(s,'Report Section 5.1; median-time histories. A CD round is a complete sweep; ADMM includes all split updates.')
        elif i==24:
            headline(s,'Strong correlation changes the ranking and exposes instance variation.')
            picture(s,'correlation_time',.65,1.79,7.75,4.25)
            seed_rows=[]
            for seed in [10,11,12]:
                rr=[r for r in extrows if r['study']=='correlation' and float(r['parameter'])==.99 and int(r['seed'])==seed]
                f=next(r for r in rr if r['method']=='FISTA');a=next(r for r in rr if r['method']=='ADMM')
                seed_rows.append([str(seed),f"{float(f['time_ms']):.2f}",f"{float(a['time_ms']):.2f}"])
            text(s,8.67,1.84,4.0,.65,'At ρ = 0.99: time (ms)',20,MAROON,True)
            table(s,8.67,2.55,3.98,['Seed','FISTA','ADMM'],seed_rows,widths=[.24,.38,.38],rowh=.57,fontsize=18)
            text(s,8.69,5.02,3.92,.87,'ADMM has the lower mean;\nFISTA wins on 2 of 3 seeds.',20,INK,True)
            takeaway(s,'At ρ = 0.99: ADMM 17.457 ± 1.401 ms; FISTA 24.041 ± 23.123 ms.')
            source(s,'Report Section 5.4, Table 6; paired seeds 10–12. Error bars show sample SD across three instance medians.')
        elif i==25:
            headline(s,'ADMM’s cold preparation becomes material as the feature count grows.')
            picture(s,'dimension_time',.65,1.76,8.0,4.36)
            card(s,8.92,1.85,3.72,3.95,'At d = 600','ADMM total: 17.413 ms\nPreparation: 8.251 ms\n\n47% of the total\n\nISTA total: 10.582 ms',COLORS['ADMM'],body_size=20)
            takeaway(s,'CD still uses 4 sweeps, but each sweep visits more coordinates; round count alone misses the cost.')
            source(s,'Report Section 5.5 and Table 7; means over three representative median-time runs, 800 training samples.')
        elif i==26:
            headline(s,'ADMM’s best algorithmic penalty depends on the input.')
            picture(s,'admm_beta',.7,1.78,11.95,4.22)
            takeaway(s,'Model λ is fixed. The main comparison keeps predeclared β = 1 regardless of sensitivity outcomes.')
            source(s,'Report Section 5.6, Table 8; β = 0.1, 1, 10. Three timings per setting; 45 runs in this separate study.')
        elif i==27:
            headline(s,'Exact support recovery still leaves shrinkage error in the retained coefficients.')
            picture(s,'coefficient_analysis',.7,1.77,11.95,4.23)
            takeaway(s,'Synthetic support is known; Diabetes coefficients describe associations on one saved split.')
            source(s,'Report Section 5.3; CD represents a converged solution. Synthetic coefficients are restored to original units.')
        elif i==28:
            headline(s,'A smaller selected model need not have the smallest prediction error.')
            picture(s,'regularization',.7,1.76,11.95,4.3)
            takeaway(s,'At λ/λmax = 0.1, the synthetic fits recover 5 variables but have higher average test MSE than at 0.01.')
            source(s,'Report Section 5.3 and Table 5; CD, means across three synthetic instances. Test scores are not used for tuning.')
        elif i==29:
            headline(s,'The useful solver choice depends on design, implementation and accuracy.')
            for j,(a,b,m) in enumerate([('Independent features','ISTA has the lowest\nmean time in our tests.','ISTA'),('Positive correlation','ADMM has the lowest mean;\nFISTA varies by instance.','ADMM'),('Diabetes, one split','ADMM has the lowest\nrecorded cold median.','ADMM')]):card(s,.65+j*4.15,1.9,4.0,2.9,a,b,COLORS[m],body_size=21)
            text(s,.87,5.2,11.6,.86,'Scope: small dense designs · 3 synthetic instances · 1 real-data split\nPython/native-kernel and monitoring costs remain part of the comparison.',19,MUTED)
            takeaway(s,'Model λ changes sparsity and shrinkage; algorithmic β changes ADMM’s computation.')
            source(s,'Report Section 6; conclusions are conditional on the recorded datasets, preprocessing, implementations and stopping rule.')
        elif i==30:
            headline(s,'Four implementations, shared writing and shared experimental evaluation.')
            rr=[]
            for m in roles['members']:
                speaking={'CAI Yangxiao':'Part I','XUE Pengyu':'Part II','ZHANG Kejia':'Opening + PPT design','ZHOU Xiyu':'Part III'}[m['name']]
                rr.append([m['name'],m['student_id'],m['algorithm'],speaking])
            table(s,.7,1.82,11.95,['Member','Student ID','Implementation','Presentation role'],rr,widths=[.23,.19,.23,.35],rowh=.66,fontsize=18)
            text(s,.85,5.35,11.6,.77,'Report writing and revision: all four members\nExperimental design and evaluation: all four members',21,MAROON,True)
            takeaway(s,'Presentation design and opening overview: ZHANG Kejia. All four members join the Q&A.')
            source(s,'Member responsibilities supplied and confirmed by Group 9; report Author contributions section.')
        elif i==32:
            headline(s,'ADMM’s split diagnostics explain progress; common R(z) controls stopping.')
            picture(s,'admm_diagnostics',.7,1.75,11.95,4.3)
            takeaway(s,'Primal: ‖x − z‖₂. Dual: β‖zᵏ⁺¹ − zᵏ‖₂. These raw norms have a different scale from R(z).')
            source(s,'Backup; saved ADMM diagnostics and common residual on correlation 0.99, seed 10. No extra stopping criterion is imposed.')
        elif i==33:
            headline(s,'The full repetitions retain outliers and overlapping timing ranges.')
            picture(s,'timing_repetitions',.7,1.64,11.95,4.53)
            takeaway(s,'Five fixed-data repetitions support descriptive timing comparisons; no significance test is claimed.')
            source(s,'Backup; main/timing_repeats.csv. Sample variation across data instances is a separate source of uncertainty.')
        elif i==34:
            headline(s,'Selected primary references and the reproducible project repository.')
            refs=[
                ('Tibshirani (1996)','Regression shrinkage and selection via the lasso.'),
                ('Daubechies et al. (2004)','Iterative thresholding for linear inverse problems.'),
                ('Beck & Teboulle (2009)','FISTA for linear inverse problems.'),
                ('Friedman et al. (2010)','Coordinate descent regularization paths.'),
                ('Wu & Lange (2008)','Coordinate descent for lasso-penalized regression.'),
                ('Boyd et al. (2011)','ADMM for distributed optimization and learning.'),
                ('Parikh & Boyd (2014)','Proximal algorithms.'),
                ('Efron et al. (2004)','Least angle regression; Diabetes context.'),
                ('Tseng (2001)','Block coordinate descent convergence.'),
                ('Tibshirani (2013)','The lasso problem and uniqueness.')]
            for j,(a,b) in enumerate(refs):
                col=j//5;row=j%5;x=.8+col*6.3;y=1.76+row*.79
                text(s,x,y,5.9,.31,a,16,MAROON,True);text(s,x,y+.33,5.9,.42,b,15,INK)
            linked(s,.83,6.29,11.8,.5,'github.com/Caiyangxiao/COMP6704-Group9-Project',roles['repository'],17)
            source(s,'Backup; full bibliographic details and links appear in the report’s References. All empirical figures use Group 9 saved results.')
        else:raise RuntimeError(i)
        sec=int(item['seconds'])
        start=elapsed
        if i<=30:elapsed+=sec
        note_header=(f"SLIDE {i:02d} | {item['title']}\nSpeaker: {item['speaker']} {item.get('student_id','')}\n"
                     +(f"Suggested time: {sec} seconds | {timefmt(start)}–{timefmt(elapsed)} | Main presentation: 30:00\n" if i<=30 else 'Q&A / backup: outside the 30-minute main presentation.\n')
                     +'English and Chinese are alternative scripts; present in one language.\n')
        en=item.get('english_notes','');zh=item.get('chinese_notes','')
        cues=item.get('visual_cues',[]);cues='\n'.join(cues) if isinstance(cues,list) else str(cues)
        references=item.get('source_refs',[]);references='; '.join(references) if isinstance(references,list) else str(references)
        note=note_header+'\nENGLISH SCRIPT\n'+en+'\n\n中文讲解稿\n'+zh+'\n\nVISUAL / DELIVERY CUES（不朗读）\n'+cues+'\n\nSOURCES\n'+references
        s.notes_slide.notes_text_frame.text=note
        notes.append(note)
        timing.append({'slide':i,'title':item['title'],'speaker':item['speaker'],'student_id':item.get('student_id',''),'main_seconds':sec if i<=30 else 0,'start':timefmt(start) if i<=30 else '', 'end':timefmt(elapsed) if i<=30 else '', 'category':'main' if i<=30 else 'Q&A' if i==31 else 'backup'})
    assert elapsed==1800
    # Any invisible objects outside the 16:9 slide indicate a layout defect.
    for idx,s in enumerate(prs.slides,1):
        for shape in s.shapes:
            assert shape.left>=-500 and shape.top>=-500,(idx,shape.name)
            assert shape.left+shape.width<=prs.slide_width+2000,(idx,shape.name,'right')
            assert shape.top+shape.height<=prs.slide_height+2000,(idx,shape.name,'bottom')
    target=OUT/'COMP6704_Group9_Lasso_Presentation.pptx';prs.save(target)
    (OUT/'Speaker_Notes_Bilingual.txt').write_text(('\n\n'+'='*80+'\n\n').join(notes),encoding='utf-8-sig')
    with (OUT/'Presentation_Timing.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(timing[0]));writer.writeheader();writer.writerows(timing)
    manifest={'slide_count':len(prs.slides),'main_slide_count':30,'main_presentation_seconds':1800,'qa_seconds':600,'backup_slide_count':3,'team_roles':roles,'source_content_sha256':hashlib.sha256((ROOT/'presentation/slide_content.json').read_bytes()).hexdigest(),'presentation_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'used_assets':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(USED)}}
    (OUT/'presentation_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Built {target}: 34 slides, 30:00 main presentation, 10:00 Q&A, 3 backup slides.')


if __name__=='__main__':main()
