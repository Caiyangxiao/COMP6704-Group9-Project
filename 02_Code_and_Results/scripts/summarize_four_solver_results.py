"""Summarize frozen four-solver records; no solver is rerun."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
METHODS=('ISTA','FISTA','CD','ADMM')


def read(path):
    with path.open(newline='') as stream:return list(csv.DictReader(stream))


def descriptive(records,field):
    values=np.array([float(row[field]) for row in records])
    return dict(mean=float(values.mean()),sd=float(values.std(ddof=1)) if len(values)>1 else None)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--results',default='results/2026-11-06-four-solvers');args=parser.parse_args()
    output=(ROOT/args.results).resolve()
    main_rows=read(output/'main/optimization_results.csv')
    extension_rows=read(output/'extended/optimization_results.csv')
    sensitivity=read(output/'sensitivity/sensitivity_results.csv')
    raw=read(output/'main/timing_repeats.csv')+read(output/'extended/timing_repeats.csv')
    result={'main':{},'sensitivity':{},'counts':{'primary_timing_runs':len(raw),'primary_converged':sum(row['converged']=='True' for row in raw)}}
    for population in ['synthetic','diabetes']:
        result['main'][population]={}
        for method in METHODS:
            selected=[row for row in main_rows if row['dataset'].startswith(population) and row['method']==method]
            result['main'][population][method]={field:descriptive(selected,field) for field in ['time_seconds','setup_seconds','iteration_seconds','rounds','objective','residual','test_mse','nonzero']}
    for population in ['synthetic_seed0','diabetes','corr_0.99']:
        result['sensitivity'][population]={}
        for rho in [.1,1.,10.]:
            selected=[row for row in sensitivity if row['dataset'].startswith(population) and float(row['rho'])==rho]
            result['sensitivity'][population][str(rho)]={field:descriptive(selected,field) for field in ['time_seconds','rounds','residual','primal_residual','dual_residual']}
    spreads=[]
    for records,key in [(main_rows,lambda r:r['dataset']),(extension_rows,lambda r:(r['study'],r['parameter'],r['seed']))]:
        for group in {key(r) for r in records}:
            objectives=np.array([float(r['objective']) for r in records if key(r)==group])
            spreads.append(float((objectives.max()-objectives.min())/max(1.,abs(objectives.min()))))
    result['max_relative_objective_spread']=max(spreads)
    result['validation']=json.loads((output/'main/validation.json').read_text())
    result['controlled']=json.loads((output/'extended/summary.json').read_text())
    result['sensitivity_timing_runs']=len(read(output/'sensitivity/sensitivity_repeats.csv'))
    result['actual_environment']=json.loads((output/'main/run_config.json').read_text())
    # Confirm paired generator data agree with the historical saved actual arrays.
    consistency=[]
    historical=ROOT/'results/2026-10-07-extended/inputs'
    for path in sorted((output/'extended/inputs').glob('*.npz')):
        with np.load(path) as new,np.load(historical/path.name) as old:
            match=all(np.array_equal(new[key],old[key]) for key in new.files)
            within_roundoff=all(np.allclose(new[key],old[key],rtol=0,atol=1e-14) for key in new.files)
            fields={key:float(np.max(np.abs(new[key]-old[key]))) for key in new.files}
        consistency.append({'dataset':path.stem,'arrays_bitwise_identical_to_historical_inputs':match,'arrays_match_to_1e-14_absolute':within_roundoff,'max_abs_difference_by_field':fields})
    result['controlled_input_consistency']=consistency
    result['current_source_hashes']={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in [ROOT/'src/optimizers.py',ROOT/'scripts/run_experiments.py',ROOT/'scripts/run_extended_experiments.py',ROOT/'scripts/run_admm_sensitivity.py']}
    (output/'analysis_summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Primary:',result['counts'],'Sensitivity:',result['sensitivity_timing_runs'],'maxrelativeobjective',max(spreads))
    print('Controlled inputs bitwise match:',sum(x['arrays_bitwise_identical_to_historical_inputs'] for x in consistency),'/',len(consistency),'within1e-14:',sum(x['arrays_match_to_1e-14_absolute'] for x in consistency))
    print(json.dumps(result['main'],indent=2))


if __name__=='__main__':main()
