#!/usr/bin/env python3

import os
from runner import RunnerData, SlurmRunner, TerminalRunner
from runner.utils import submit
from ase import Atoms, db
from ase.io import read, write
import numpy as np
import copy
from matplotlib import pyplot as plt
import time


forms = []
for i in os.listdir('data'):
    if i.endswith('LOCPOT'):
        forms.append('.'.join(i.split('.')[:-1]))
forms.sort()

for i, ff in enumerate(forms, start=1):
    with open(f'data/{ff}.LOCPOT', 'r') as fio:
        print(i, ff, float([fio.readline() for _ in range(5)][-1].split()[-1]))

fdb = db.connect('database.db')
if 'database.db' not in os.listdir():
    fdb.metadata = {'default_columns': ['id', 'user', 'formula', 'status']}

# runner
"""
# Runner for slurm workflow manager
pre_runner_data = RunnerData()
pre_runner_data.append_tasks('shell', 'module load anaconda')
pre_runner_data.append_tasks('shell', 'module load gcc')
runner = SlurmRunner('PPM',
                     pre_runner_data=pre_runner_data,
                     cycle_time=900,
                     max_jobs=50)
runner.to_database()
"""


# Runner for terminal
runner = TerminalRunner("PPM",
                        cycle_time=900,
                        max_jobs=1
                       )
runner.to_database()


params = {'ChargeCuUp': -0.0669933,
          'ChargeCuDown': -0.0627402,
          'Ccharge': 0.212718,
          'Ocharge': -0.11767,
          'Cklat': 0.0925,
          'Oklat': 0.0908,
          'CuUpshift': 2.2422001068,
          'rC0': 1.85,
          'rO0': 1.15,
          'rOx': 0,
          'rOy': 0,
          'sigma': 0.71,
          'Ckrad': 20,
          'Okrad': 20,
          'Amp': 7,
          'z_top_layer': 8.5,           # Z to remove atoms so only top layer atoms are added to input_plot.xyz and used for Pauli fitting in OpenCL branch
          'scan_xy_buffer': 2           # xy buffer in A to extend the scanning
         }

runner_data = RunnerData('get_ppm_data')
runner_data.scheduler_options = {'-n': 1,
                                 '--time': '0-00:30:00',
                                 '--mem-per-cpu': 12000}
# runner_data.parents = [1]
runner_data.add_file('get_data.py')
runner_data.add_file('gen_params.py')
runner_data.append_tasks('python', 'gen_params.py', copy.deepcopy(params))
runner_data.append_tasks('shell', 'chmod +x prepare.sh')
runner_data.append_tasks('shell', 'chmod +x run_PPM.sh')
runner_data.append_tasks('shell', './prepare.sh')
runner_data.append_tasks('shell', './run_PPM.sh')
runner_data.append_tasks('python', 'get_data.py')
runner_data.append_tasks('shell', 'if [ -d PPM-complex_tip ]; then rm -rf PPM-complex_tip; fi')
runner_data.append_tasks('shell', 'if [ -d PPM-OpenCL ]; then rm -rf PPM-OpenCL; fi')
runner_data.keep_run = True

for ff in forms:
    if fdb.count(label=ff) == 0:
        atoms = read(f'data/{ff}.POSCAR', format='vasp')
        # id_ = fdb.write(atoms, status='submit', runner='slurm:PPM', label=ff)
        id_ = fdb.write(atoms, status='submit', runner='terminal:PPM', label=ff)
        runner_data.to_db('database.db', id_)

