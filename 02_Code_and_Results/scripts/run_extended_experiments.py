"""Controlled, paired four-solver extensions with all timings measured on one host."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT/'.cache/matplotlib'))
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
sys.path.insert(0, str(ROOT/'src'))
sys.path.insert(0, str(ROOT/'scripts'))
import scipy
import sklearn
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from threadpoolctl import threadpool_limits, threadpool_info
from optimizers import solve, evaluate, soft_threshold
from run_experiments import load_data, write_csv, METHODS, COLORS

CONFIG = dict(seeds=[10,11,12], correlations=[0.,.5,.9,.99],
              correlation_samples=600, correlation_features=60, block_size=10,
              scaling_samples=1000, dimensions=[50,100,300,600],
              true_active_coefficients=[2.,-1.5,1.,-2.,1.5], noise_sd=.5,
              train_fraction=.8, lambda_ratio=.1, tolerance=1e-6,
              max_rounds=10000, timing_repeats=5, nonzero_threshold=1e-6,
              path_grid=sorted(set(np.geomspace(.01,1.,32).tolist()+[.1,.5])),
              threads_requested=1, methods=list(METHODS), admm_rho=1.0, objective='squared_loss/(2*n) + lambda*L1')


def prepare(name, rawX, rawy, order, output):
    train = order[:int(.8*len(rawy))]; test = order[int(.8*len(rawy)):]
    np.savez_compressed(output/'inputs'/f'{name}.npz', X=rawX, y=rawy,
                        train_indices=train, test_indices=test)
    mean=rawX[train].mean(0); std=rawX[train].std(0)
    X=np.ascontiguousarray((rawX[train]-mean)/std)
    Xt=np.ascontiguousarray((rawX[test]-mean)/std)
    ym=float(rawy[train].mean()); y=np.ascontiguousarray(rawy[train]-ym)
    start=perf_counter(); singular=np.linalg.svd(X,compute_uv=False)
    setup=perf_counter()-start
    return dict(name=name,X=X,y=y,Xtest=Xt,ytest=rawy[test],ymean=ym,std=std,
                L=float(singular[0]**2/len(y)),
                condition=float((singular[0]/singular[-1])**2),
                lambda_max=float(np.max(np.abs(X.T@y/len(y)))),
                spectral_seconds=setup)


def benchmark(data, study, parameter, seed, output, raw, rows):
    answers={m:[] for m in METHODS}; lam=.1*data['lambda_max']
    for repeat in range(5):
        for method in METHODS[repeat%len(METHODS):]+METHODS[:repeat%len(METHODS)]:
            a=solve(data['X'],data['y'],lam,data['L'],method,1e-6,10000)
            answers[method].append(a)
            raw.append(dict(study=study,parameter=parameter,seed=seed,method=method,
                repeat=repeat,seconds=a['elapsed_seconds'],setup_seconds=a['setup_seconds'],
                iteration_seconds=a['iteration_seconds'],rounds=a['rounds'],
                objective=a['objective'],residual=a['residual'],converged=a['converged']))
    for method in METHODS:
        group=answers[method]; times=np.array([a['elapsed_seconds'] for a in group])
        a=group[int(np.argsort(times)[len(times)//2])]
        rows.append(dict(study=study,parameter=parameter,seed=seed,method=method,
            time_ms=float(np.median(times)*1000),setup_ms=a['setup_seconds']*1000,
            iteration_ms=a['iteration_seconds']*1000,rounds=a['rounds'],
            objective=a['objective'],residual=a['residual'],converged=a['converged'],
            condition=data['condition'],spectral_ms=data['spectral_seconds']*1000,
            test_mse=float(np.mean((data['Xtest']@a['w']+data['ymean']-data['ytest'])**2)),
            nonzero=int(np.sum(np.abs(a['w'])>1e-6))))
        if method=='ADMM':
            write_csv(output/f"admm_diagnostics_{data['name']}.csv", [dict(zip(['round','primal_l2','dual_l2'],v)) for v in a['diagnostic_history']])
        np.savez(output/f"coefficients_{data['name']}_{method}.npz", standardized_w=a['w'])
        write_csv(output/f"trace_{data['name']}_{method}.csv",
                  [dict(zip(['round','seconds','objective','residual'],v)) for v in a['history']])
    spread=(max(a[0]['objective'] for a in answers.values())-
            min(a[0]['objective'] for a in answers.values()))
    scale=max(1.,abs(answers['CD'][0]['objective']))
    return spread/scale


def summarize(rows):
    out=[]
    for study, parameters in [('correlation',CONFIG['correlations']),('scaling',CONFIG['dimensions'])]:
        for parameter in parameters:
            for method in METHODS:
                selected=[r for r in rows if r['study']==study and r['parameter']==parameter and r['method']==method]
                record=dict(study=study,parameter=parameter,method=method)
                for field in ['time_ms','setup_ms','iteration_ms','rounds','condition','spectral_ms','test_mse','nonzero']:
                    vals=np.array([r[field] for r in selected]);record[field+'_mean']=float(vals.mean());record[field+'_sd']=float(vals.std(ddof=1))
                out.append(record)
    return out


def trajectory(output):
    """Historical three-solver teaching illustration, separate from four-solver timings."""
    illustration_methods = ('ISTA', 'FISTA', 'CD')
    Q=np.array([[1.,.9],[.9,1.]])
    X=np.sqrt(2)*np.linalg.cholesky(Q).T; y=X@np.array([2.,-1.])
    L=1.9; lam=.03; scale=max(1.,float(np.max(np.abs(X.T@y/2))))
    paths={}; checks={}
    for method in illustration_methods:
        w=np.zeros(2);z=w.copy();t=1.;residual=y.copy();p=[w.copy()]
        for k in range(10000):
            if evaluate(X,y,w,lam,L,scale)[1]<=1e-6:break
            if method=='CD':
                for j in range(2):
                    partial=residual+X[:,j]*w[j];rho=X[:,j]@partial/2
                    w[j]=np.sign(rho)*max(abs(rho)-lam,0.)/(X[:,j]@X[:,j]/2)
                    residual=partial-X[:,j]*w[j];p.append(w.copy())
            else:
                v=z if method=='FISTA' else w
                next_w=soft_threshold(v-X.T@(X@v-y)/(2*L),lam/L)
                if method=='FISTA':
                    nt=(1+np.sqrt(1+4*t*t))/2;z=next_w+(t-1)/nt*(next_w-w);t=nt
                w=next_w;p.append(w.copy())
        reference=solve(X,y,lam,L,method)
        error=float(np.max(np.abs(w-reference['w'])))
        if error>1e-10:raise RuntimeError('Trajectory differs from existing solver')
        checks[method]=error
        paths[method]=np.array(p[:51 if method=='CD' else 26]).tolist()
    optimum=solve(X,y,lam,L,'CD',tol=1e-12)['w']
    xx,yy=np.meshgrid(np.linspace(-.1,2.35,220),np.linspace(-1.35,.85,220))
    d=np.stack([xx-2,yy+1],axis=-1)
    zz=.5*np.einsum('...i,ij,...j->...',d,Q,d)+lam*(np.abs(xx)+np.abs(yy))
    delta=optimum-np.array([2.,-1.]);minimum=float(.5*delta@Q@delta+lam*np.abs(optimum).sum())
    fig,ax=plt.subplots(figsize=(7,4.5),layout='constrained')
    cs=ax.contour(xx,yy,zz,levels=minimum+np.array([.01,.03,.07,.15,.3,.6]),colors='#c1c7ce',linewidths=.8)
    contours=[]
    for segs in cs.allsegs:
        for points in segs:
            contours.append(points[::max(1,len(points)//90)].tolist())
    for method in illustration_methods:
        points=np.array(paths[method]);ax.plot(points[:,0],points[:,1],'.-',ms=3,lw=1.7,color=COLORS[method],label=method)
    ax.plot(0,0,'ko',ms=5,label='Start');ax.plot(*optimum,'k*',ms=13,label='Optimum')
    ax.set(xlabel=r'$w_1$',ylabel=r'$w_2$',title='First 25 vector updates / CD sweeps')
    ax.legend(ncol=3,fontsize=10);ax.grid(alpha=.15)
    for ext in ['png','svg']:fig.savefig(output/f'trajectories.{ext}',dpi=260)
    plt.close(fig)
    result=dict(paths=paths,contours=contours,optimum=optimum.tolist(),Q=Q.tolist(),lambda_value=lam,terminal_solver_difference=checks)
    (output/'trajectory_data.json').write_text(json.dumps(result,indent=2))
    return result


def plots(output,summary,paths,trace_root=None):
    trace_root = trace_root or output
    available_methods = tuple(m for m in METHODS if any(row['method']==m for row in summary))
    plt.rcParams.update({'font.size':12,'axes.titlesize':13,'axes.spines.top':False,
                         'axes.spines.right':False,'savefig.dpi':260})
    def save(fig,name):
        for ext in ['png','svg']:fig.savefig(output/f'{name}.{ext}')
        plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(14,4.3),layout='constrained')
    for method in available_methods:
        group=[r for r in summary if r['study']=='correlation' and r['method']==method]
        for ax,field in zip(axes[:2],['time_ms','rounds']):
            ax.errorbar(range(4),[r[field+'_mean'] for r in group],yerr=[r[field+'_sd'] for r in group],fmt='o-',color=COLORS[method],label=method,capsize=3)
        trace=np.genfromtxt(trace_root/f'trace_corr_0.99_seed10_{method}.csv',delimiter=',',names=True)
        axes[2].loglog(trace['round'][1:],trace['residual'][1:],color=COLORS[method],label=method,lw=1.8)
    for ax,title,ylabel in zip(axes[:2],['Time at common tolerance','Updates / complete CD sweeps'],['Solver time (ms)','Rounds']):
        ax.set(xticks=range(4),xticklabels=['0','.5','.9','.99'],xlabel=r'Within-block correlation $\rho$',ylabel=ylabel,title=title,yscale='log');ax.grid(alpha=.2)
    axes[0].legend(fontsize=10)
    axes[2].axhline(1e-6,color='#555',ls='--',lw=1)
    axes[2].set(xlabel='Updates / complete CD sweeps',ylabel='Normalized residual R',title=r'$\rho=0.99$, seed 10');axes[2].grid(alpha=.2)
    save(fig,'correlation_comparison')
    fig,axes=plt.subplots(1,2,figsize=(11,4.3),layout='constrained')
    for method in available_methods:
        group=[r for r in summary if r['study']=='scaling' and r['method']==method]
        for ax,field in zip(axes,['time_ms','rounds']):
            ax.errorbar(CONFIG['dimensions'],[r[field+'_mean'] for r in group],yerr=[r[field+'_sd'] for r in group],fmt='o-',capsize=3,color=COLORS[method],label=method)
    for ax,title,ylabel in zip(axes,['Solver time','Rounds to common tolerance'],['Solver time (ms)','Updates / complete CD sweeps']):
        ax.set(xlabel='Features d (800 training samples)',ylabel=ylabel,title=title,xscale='log',xticks=CONFIG['dimensions']);ax.set_xticklabels(CONFIG['dimensions']);ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator());ax.grid(alpha=.2)
    axes[0].set_yscale('log');axes[0].legend(fontsize=11);save(fig,'dimension_comparison')
    fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained')
    palettes=['#2563eb','#d97706','#15803d','#8b5cf6','#dc4870']
    for col,name in enumerate(['synthetic_seed0','diabetes']):
        record=paths[name];ratios=np.array(record['ratios']);coeffs=np.array(record['coefficients'])
        ax=axes[0,col]
        if col==0:
            ax.plot(ratios,coeffs[:,5:],color='#aab2bd',alpha=.3,lw=.8)
            for j in range(5):ax.plot(ratios,coeffs[:,j],color=palettes[j],lw=2,label=f'x{j}')
            ax.legend(ncol=3,fontsize=9,loc='upper center',bbox_to_anchor=(.5,-.27));ax.set_ylabel('Coefficient (original units)')
        else:
            active=np.flatnonzero(np.abs(coeffs[record['ratios'].index(.1)])>1e-6)
            inactive=[j for j in range(coeffs.shape[1]) if j not in active]
            ax.plot(ratios,coeffs[:,inactive],color='#aab2bd',alpha=.55,lw=1)
            for k,j in enumerate(active):ax.plot(ratios,coeffs[:,j],color=palettes[k],lw=2,label=record['features'][j])
            ax.legend(ncol=3,fontsize=9,loc='upper center',bbox_to_anchor=(.5,-.27));ax.set_ylabel('Coefficient (standardized units)')
        ax.set(title='Synthetic seed 0' if col==0 else 'Diabetes fixed split',xscale='log',xlabel=r'$\lambda/\lambda_{max}$');ax.axhline(0,color='#555',lw=.6);ax.grid(alpha=.2)
        ax=axes[1,col];ax.semilogx(ratios,record['train_mse'],lw=2,color='#2563eb',label='Training');ax.semilogx(ratios,record['test_mse'],lw=2,color='#d97706',label='Test');ax.set(xlabel=r'$\lambda/\lambda_{max}$',ylabel='MSE');ax.legend(fontsize=10);ax.grid(alpha=.2)
    save(fig,'coefficient_paths')


def render_saved_trajectory(data,output):
    available_methods = tuple(m for m in METHODS if m in data['paths'])
    fig,axes=plt.subplots(1,len(available_methods),figsize=(4.5*len(available_methods),4.4),layout='constrained',squeeze=False)
    axes=axes.ravel()
    optimum=np.array(data['optimum'])
    for ax,method in zip(axes,available_methods):
        for contour in data['contours']:
            v=np.array(contour);ax.plot(v[:,0],v[:,1],color='#c1c7ce',lw=.7)
        p=np.array(data['paths'][method]);ax.plot(p[:,0],p[:,1],'.-',color=COLORS[method],lw=2,ms=3)
        ax.plot(*p[-1],'s',color=COLORS[method],ms=7,label='After 25')
        ax.plot(0,0,'ko',ms=5,label='Start');ax.plot(*optimum,'k*',ms=12,label='Optimum')
        ax.set(xlim=(-.1,2.35),ylim=(-1.35,.85),xlabel=r'$w_1$',ylabel=r'$w_2$',title=method)
        ax.grid(alpha=.15)
    axes[0].legend(loc='upper right',fontsize=9)
    for ext in ['png','svg']:fig.savefig(output/f'trajectories.{ext}',dpi=260)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='results/2026-11-06-four-solvers/extended');args=parser.parse_args()
    output=(ROOT/args.output).resolve();output.mkdir(parents=True,exist_ok=False);(output/'inputs').mkdir()
    (output/'configuration.json').write_text(json.dumps(CONFIG,indent=2))
    for p in ['src/optimizers.py','scripts/run_experiments.py','scripts/run_extended_experiments.py','scripts/run_admm_sensitivity.py','experiment_plan_admm.md','requirements-admm.txt','report.tex']:
        shutil.copy2(ROOT/p,output/Path(p).name)
    raw=[];rows=[];spreads=[];data_records=[];paths={}
    with threadpool_limits(limits=1):
        for study in ['correlation','scaling']:
            for seed in CONFIG['seeds']:
                rng=np.random.default_rng(seed)
                if study=='correlation':
                    Z=rng.normal(size=(600,60)); common=rng.normal(size=(600,6));noise=rng.normal(scale=.5,size=600);order=rng.permutation(600)
                    for rho in CONFIG['correlations']:
                        X=np.sqrt(1-rho)*Z+np.sqrt(rho)*np.repeat(common,10,axis=1)
                        y=X[:,:5]@np.array(CONFIG['true_active_coefficients'])+noise
                        data=prepare(f'corr_{rho:g}_seed{seed}',X,y,order,output)
                        spreads.append(benchmark(data,study,rho,seed,output,raw,rows))
                        data_records.append(dict(name=data['name'],L=data['L'],condition=data['condition'],spectral_seconds=data['spectral_seconds']))
                        print(study,rho,seed,'max R',max(r['residual'] for r in rows[-len(METHODS):]),flush=True)
                else:
                    Xall=rng.normal(size=(1000,600));noise=rng.normal(scale=.5,size=1000);y=Xall[:,:5]@np.array(CONFIG['true_active_coefficients'])+noise;order=rng.permutation(1000)
                    for d in CONFIG['dimensions']:
                        data=prepare(f'dim_{d}_seed{seed}',Xall[:,:d],y,order,output)
                        spreads.append(benchmark(data,study,d,seed,output,raw,rows))
                        data_records.append(dict(name=data['name'],L=data['L'],condition=data['condition'],spectral_seconds=data['spectral_seconds']))
                        print(study,d,seed,'max R',max(r['residual'] for r in rows[-len(METHODS):]),flush=True)
        if not all(r['converged'] for r in raw):
            write_csv(output/'timing_repeats.csv',raw);write_csv(output/'optimization_results.csv',rows)
            raise RuntimeError('Some runs did not converge; do not rank their time as equal accuracy')
        if max(spreads)>1e-7:raise RuntimeError(f'Objective disagreement: {max(spreads)}')
        manifest=json.loads((ROOT/'data/manifest.json').read_text());path_rows=[]
        for name in ['synthetic_seed0','diabetes']:
            data=load_data(name,manifest['datasets'][name]);record=dict(ratios=CONFIG['path_grid'],coefficients=[],train_mse=[],test_mse=[],features=manifest['datasets'][name]['feature_columns'])
            for ratio in CONFIG['path_grid']:
                a=solve(data['X'],data['y'],ratio*data['lambda_max'],data['L'],'CD')
                if not a['converged']:raise RuntimeError('Path fit did not converge')
                coef=a['w']/data['std'] if name.startswith('synthetic') else a['w']
                train=float(np.mean((data['X']@a['w']-data['y'])**2));test=float(np.mean((data['Xtest']@a['w']+data['ymean']-data['ytest'])**2))
                record['coefficients'].append(coef.tolist());record['train_mse'].append(train);record['test_mse'].append(test)
                path_rows.append(dict(dataset=name,lambda_ratio=ratio,train_mse=train,test_mse=test,nonzero=int(np.sum(np.abs(a['w'])>1e-6)),residual=a['residual'],converged=a['converged']))
            paths[name]=record
        summary=summarize(rows);write_csv(output/'timing_repeats.csv',raw);write_csv(output/'optimization_results.csv',rows);write_csv(output/'aggregated_results.csv',summary);write_csv(output/'path_results.csv',path_rows)
        (output/'coefficient_path_data.json').write_text(json.dumps(paths,indent=2))
        (output/'summary.json').write_text(json.dumps(dict(summary=summary,validation=dict(all_converged=True,max_relative_objective_spread=max(spreads),timing_runs=len(raw),path_fits=len(path_rows))),indent=2))
        plots(output,summary,paths)
        # The separate two-dimensional teaching example remains in historical results;
        # it is not silently extended with a surrogate ADMM trajectory.
        env=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,sklearn=sklearn.__version__,matplotlib=matplotlib.__version__,platform=platform.platform(),threadpools=threadpool_info(),thread_environment={k:os.environ[k] for k in ['VECLIB_MAXIMUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']},datasets=data_records,source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['src/optimizers.py','scripts/run_experiments.py','scripts/run_extended_experiments.py','scripts/run_admm_sensitivity.py','experiment_plan_admm.md','requirements-admm.txt']},input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (output/'inputs').glob('*.npz')})
        (output/'environment.json').write_text(json.dumps(env,indent=2))
    print('Completed:',len(raw),'timings,',len(path_rows),'path fits; objective spread',max(spreads),flush=True)

if __name__=='__main__':main()
