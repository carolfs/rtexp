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

from scipy import integrate
from numpy import inf
import math, sys, random, bayesian_rt
from bayesian_rt import S, trial, mean_stder
    
def simple_task(REPS):
    rtv = []
    rtn = []
    rti = []
    anticipated = [0, 0, 0]
    correct = [0, 0, 0]
    for tn in range(REPS):
        ta = random.randint(1, bayesian_rt.tmax)
        Seq = [S(i + 1, 'L', ta, s, sigma) for i in range(bayesian_rt.tmax)]
        for i, (rtl, pista) in enumerate(((rtv, r), (rtn, 0.5), (rti, (1 - r)))):
            for t, (pAe, pAd) in zip(range(1, bayesian_rt.tmax + 1), trial(Seq, pista, ta, s, sigma)):
                if (pAe + pAd) >= acmin:
                    rt = t
                    if rt >= ta:
                        rtl.append(rt - ta)
                        correct[i] += 1
                    else:
                        anticipated[i] += 1
                    break
    for i in range(3):
        assert (correct[i] + anticipated[i]) == REPS
        print(correct[i] / REPS, anticipated[i] / REPS, sep='\t')
    return rtv, rtn, rti

def choice_task(REPS):
    rtv = []
    rtn = []
    rti = []
    wrong = [0, 0, 0]
    anticipated = [0, 0, 0]
    missed = [0, 0, 0]
    correct = [0, 0, 0]
    for tn in range(REPS):
        ta = random.randint(1, bayesian_rt.tmax)
        Seq = [S(i + 1, 'L', ta, s, sigma) for i in range(bayesian_rt.tmax * 10)]
        for i, (rtl, pista) in enumerate(((rtv, r), (rtn, 0.5), (rti, (1 - r)))):
            for t, (pAe, pAd) in zip(range(1, bayesian_rt.tmax * 10 + 1), trial(Seq, pista, ta, s, sigma)):
                if pAe >= acmin:
                    rt = t
                    if rt < ta:
                        anticipated[i] += 1
                    elif pAd >= acmin:
                        if random.random() < 0.5:
                            rtl.append(rt - ta)
                            correct[i] += 1
                        else:
                            wrong[i] += 1
                    else:
                        rtl.append(rt - ta)
                        correct[i] += 1
                    break
                elif pAd >= acmin:
                    rt = t
                    if rt < ta:
                        anticipated[i] += 1
                    else:
                        wrong[i] += 1
                    break
            else:
              missed[i] += 1
    for i in range(3):
        assert (correct[i] + wrong[i] + anticipated[i] + missed[i]) == REPS
        errors = wrong[i] + anticipated[i] + missed[i]
        print(correct[i] / REPS, errors / REPS, wrong[i] / REPS, anticipated[i] / REPS, missed[i] / REPS, sep='\t')
    return rtv, rtn, rti

if __name__ == '__main__':
    try:
        # Parameters
        s = float(sys.argv[1]) # Target stimulus intensity
        assert s > 0
        sigma = float(sys.argv[2]) # Noise intensity
        assert sigma > 0
        bayesian_rt.tmax = int(sys.argv[3]) # Maximum time the target can appear
        assert bayesian_rt.tmax > 0
        # Probability that the target will appear on the left (given by the cue)
        r = float(sys.argv[4])
        assert 0.5 < r and r <= 1
        acmin = float(sys.argv[5]) # Minimum accuracy
        assert 0 <= acmin and acmin <= 1
        exp_type = sys.argv[6] # Experiment type
        assert exp_type == 'SRT' or exp_type == 'CRT'
        try:
            REPS = int(sys.argv[7]) # Number of trials
        except Exception:
            REPS = 1000
        assert REPS > 0
    except:
        print("This script expects six required parameters and one optional parameter:")
        print("  1. s: stimulus intensity, s > 0")
        print("  2. sigma: noise intensity, sigma > 0")
        print("  3. tmax: maximum time the target can appear")
        print("  4. r: probability that the target will appear "\
              "on the left, given by a valid cue (0.5 < r <= 1)")
        print("  5. acmin: minimum accuracy (0 <= acmin <= 1)")
        print("  6. exp_type: experiment type (SRT or CRT)")
        print("  7. REPS: number of trials (REPS > 0)")
        sys.exit(0)
  
    if exp_type == 'SRT':
        rtv, rtn, rti = simple_task(REPS)
    else:
        rtv, rtn, rti = choice_task(REPS)
    print(mean_stder(rtv))
    print(mean_stder(rtn))
    print(mean_stder(rti))