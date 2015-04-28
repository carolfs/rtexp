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

import sys, math

def avg(l):
    return sum(l) / float(len(l))

def stdev(l, avg):
    s = 0.0
    for i in l:
        s += (avg - i) ** 2
    return math.sqrt(s / (len(l) - 1))

def key(a):
    if a is None:
        return 2000
    else:
        return a

def median(l):
    if len(l) == 0:
        return None
    l.sort(key = key)
    if len(l) % 2 == 0:
        return avg((l[len(l) // 2 - 1], l[len(l) // 2]))
    else:
        return l[len(l) // 2]

import rtexp, ga, os, time
from rtexp import config

print("type,noise,g,variable,value")
for g in range(0, rtexp.GENERATIONS + 1, rtexp.SAVE):
    totals = [list() for i in range(8)]
    for run_number in range(rtexp.RUNS):
        t = [list() for i in range(8)]
        arquivo = rtexp.ARQUIVO % (run_number, g)
        if not os.path.exists(arquivo):
            break
        run = ga.Run.load(open(arquivo, 'rb'))
        for pop in run:
            for c in pop:
                #trials = rtexp.ChoiceRTTask()
                #trials.run(c, rtexp.make_network(c))
                t[0].append(c.fitness)
                if c.rt_valid is not None:
                    t[1].append(c.rt_valid)
                if c.rt_neutral is not None:
                    t[2].append(c.rt_neutral)
                if c.rt_invalid is not None:
                    t[3].append(c.rt_invalid)
                t[4].append(c.count[0]) # resp
                t[5].append(c.count[1]) # miss
                t[6].append(c.count[2]) # anticipated
                try: # wrong
                    t[7].append(c.count[3])
                except IndexError:
                    t[7].append(0)
                assert (c.count[0] + c.count[1]) == (rtexp.REPS * 2 * (rtexp.VALID + rtexp.INVALID + rtexp.NEUTRAL))
        for rt, gt in zip(t, totals):
            i = median(rt)
            if i is not None:
                gt.append(i)
    for var, total in zip(("Fitness", "Valid", "Neutral", "Invalid", "Responses", "Misses", "Anticipated", "Wrong"), totals):
        print(config['TYPE'], config['NOISE_SIGMA'], g, var, sep=',', end=',')
        if len(total) > 0:
            a = avg(total)
            print(a)
        else:
            print('')
    
    