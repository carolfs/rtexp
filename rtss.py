#Copyright 2014, 2015 Carolina Feher da Silva
#
#This file is part of rtexp.
#
#rtexp is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#rtexp is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with rtexp.  If not, see <http://www.gnu.org/licenses/>.

import ga, configparser, os

###
# Fonte: http://stackoverflow.com/questions/15033511/compute-a-confidence-interval-from-sample-data
import numpy as np
import scipy as sp
import scipy.stats

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return m, m-h, m+h

###

if __name__ == '__main__':
    print('cond', 'exptype', 'cuetype', 'mean', 'ciinf', 'cisup', sep=",")
    for expn in range(3, 9):
        config = configparser.ConfigParser()
        config.read('exp%d.cfg' % expn)
        config = config['EXP']
        g = int(config['GENERATIONS'])
        ARQUIVO = os.path.join(config['DIR'], 'r%03d-g%03d')
        vrt, nrt, irt = [], [], []
        for run_number in range(int(config['RUNS'])):
            arquivo = ARQUIVO % (run_number, g)
            assert os.path.exists(arquivo)
            with open(arquivo, 'rb') as f:
                run = ga.Run.load(f)
            for pop in run:
                for ind in pop:
                    if ind.rt_valid is not None:
                        vrt.append(ind.rt_valid)
                    if ind.rt_neutral is not None:
                        nrt.append(ind.rt_neutral)
                    if ind.rt_invalid is not None:
                        irt.append(ind.rt_invalid)
        for cue_type, data in (('Valid', vrt), ('Neutral', nrt), ('Invalid', irt)):
            mean, ciinf, cisup = mean_confidence_interval(data)
            print('cond%d' % ((expn + 1) // 2), 'SRT' if config['TYPE'] == 'Simple' else 'CRT', cue_type, mean, ciinf, cisup, sep=",")