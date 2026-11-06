"""Prespecified ADMM penalty sensitivity; existing result directories are never overwritten."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[name]='1'
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'scripts'))
import numpy as np
import scipy
from threadpoolctl import threadpool_limits,threadpool_info
from optimizers import solve
from run_experiments import load_data,write_csv

CONFIG=dict(rhos=[0.1,1.0,10.0],repeats=3,lambda_ratio=.1,tolerance=1e-6,
            max_rounds=10000,initialization='x=z=u=0',
            datasets=['synthetic_seed0','diabetes','corr_0.99_seed10','corr_0.99_seed11','corr_0.99_seed12'],
            stopping='same normalized proximal-gradient residual R(z) <= tolerance',
            timing='setup, factorization, iteration and monitoring included; shared spectral setup excluded')


def load_extended(path):
    with np.load(path) as arrays:
        rawX=arrays['X'];rawy=arrays['y'];train=arrays['train_indices'];test=arrays['test_indices']
    mean=rawX[train].mean(0);std=rawX[train].std(0,ddof=0)
    X=np.ascontiguousarray((rawX[train]-mean)/std)
    return dict(name=path.stem,X=X,y=np.ascontiguousarray(rawy[train]-rawy[train].mean()),
                L=float(np.linalg.norm(X,ord=2)**2/len(train)),
                lambda_max=float(np.max(np.abs(X.T@(rawy[train]-rawy[train].mean())/len(train)))))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default='results/2026-11-06-four-solvers/sensitivity')
    parser.add_argument('--extended-inputs',default='results/2026-11-06-four-solvers/extended/inputs')
    args=parser.parse_args();output=(ROOT/args.output).resolve();output.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((ROOT/'data/manifest.json').read_text())
    raw=[];rows=[];input_hashes={}
    with threadpool_limits(limits=1):
        data={name:load_data(name,manifest['datasets'][name]) for name in ['synthetic_seed0','diabetes']}
        for name in CONFIG['datasets'][2:]:
            path=(ROOT/args.extended_inputs/f'{name}.npz').resolve()
            data[name]=load_extended(path);input_hashes[name]=hashlib.sha256(path.read_bytes()).hexdigest()
        for name in ['synthetic_seed0','diabetes']:
            input_hashes[name]=manifest['datasets'][name]['sha256']
        for name,dataset in data.items():
            answers={rho:[] for rho in CONFIG['rhos']}
            for repeat in range(CONFIG['repeats']):
                order=CONFIG['rhos'][repeat:]+CONFIG['rhos'][:repeat]
                for rho in order:
                    answer=solve(dataset['X'],dataset['y'],CONFIG['lambda_ratio']*dataset['lambda_max'],dataset['L'],'ADMM',CONFIG['tolerance'],CONFIG['max_rounds'],admm_rho=rho)
                    answers[rho].append(answer)
                    raw.append(dict(dataset=name,rho=rho,repeat=repeat,time_seconds=answer['elapsed_seconds'],
                        setup_seconds=answer['setup_seconds'],iteration_seconds=answer['iteration_seconds'],
                        rounds=answer['rounds'],objective=answer['objective'],residual=answer['residual'],
                        primal_residual=answer['primal_residual'],dual_residual=answer['dual_residual'],converged=answer['converged']))
            for rho in CONFIG['rhos']:
                group=answers[rho];times=np.array([a['elapsed_seconds'] for a in group]);a=group[int(np.argsort(times)[len(times)//2])]
                record=next(x.copy() for x in raw if x['dataset']==name and x['rho']==rho);record.pop('repeat')
                record.update(time_seconds=float(np.median(times)),minimum_time_seconds=float(times.min()),maximum_time_seconds=float(times.max()),setup_seconds=a['setup_seconds'],iteration_seconds=a['iteration_seconds'])
                rows.append(record)
                write_csv(output/f'trace_{name}_rho{rho:g}.csv',[dict(zip(['round','seconds','objective','residual'],v)) for v in a['history']])
                write_csv(output/f'diagnostics_{name}_rho{rho:g}.csv',[dict(zip(['round','primal_l2','dual_l2'],v)) for v in a['diagnostic_history']])
                print(name,'rho',rho,'rounds',a['rounds'],'R',a['residual'],'converged',a['converged'],flush=True)
        write_csv(output/'sensitivity_repeats.csv',raw);write_csv(output/'sensitivity_results.csv',rows)
        source_paths=['src/optimizers.py','scripts/run_admm_sensitivity.py','requirements-admm.txt','experiment_plan_admm.md']
        source=output/'source';source.mkdir()
        for relative in source_paths:shutil.copy2(ROOT/relative,source/Path(relative).name)
        environment=dict(configuration=CONFIG,python=platform.python_version(),platform=platform.platform(),numpy=np.__version__,scipy=scipy.__version__,threadpools=threadpool_info(),input_sha256=input_hashes,source_sha256={relative:hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() for relative in source_paths},runs=len(raw),converged_runs=sum(r['converged'] for r in raw))
        (output/'configuration.json').write_text(json.dumps(CONFIG,indent=2)+'\n')
        (output/'environment.json').write_text(json.dumps(environment,indent=2)+'\n')
    print('Completed sensitivity:',len(raw),'timings;',sum(r['converged'] for r in raw),'converged',flush=True)


if __name__=='__main__':main()
