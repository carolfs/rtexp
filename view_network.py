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

def n2rgb(n):
    if n >= 0:
        r = 255
        g = round((3 - n) / 3 * 255)
        b = round((3 - n) / 3 * 255)
    else:
        r = round((3 + n) / 3 * 255)
        g = round((3 + n) / 3 * 255)
        b = 255
    return "#{:02X}{:02X}{:02X}".format(r, g, b)

import rtexp, ga, os, time

input_neurons = ["left_target", "left_cue", "neutral_cue", "right_cue", "right_target"]
hidden_neurons = ['hidden_%d' % (i + 1) for i in range(rtexp.HIDDEN_NEURONS)]
if rtexp.config['TYPE'] == 'Simple':
    output_neurons = ['output']
else:
    output_neurons = ['left_output', 'right_output']
neurons = input_neurons + hidden_neurons + output_neurons
labels = [s.replace("_", "\\n") for s in neurons]
print("digraph {")
print('    ordering=out;')
print('    { rank = same; ' + ';'.join(input_neurons) + ';}')
if len(hidden_neurons) > 0:
    print('    { rank = same; ' + ';'.join(hidden_neurons) + ';}')
print('    { rank = same; ' + ';'.join(output_neurons) + ';}')
#for pe, po in zip(input_neurons[:-1], input_neurons[1:]):
#    print('    %s -> %s [style="invis",weight=10' % (pe, po), end='')
#    print('];')

g = rtexp.GENERATIONS
weights = [[] for i in range(rtexp.NEURONS + rtexp.NEURONS ** 2)]
for run_number in range(rtexp.RUNS):
    arquivo = rtexp.ARQUIVO % (run_number, g)
    if not os.path.exists(arquivo):
        break
    run = ga.Run.load(open(arquivo, 'rb'))
    max_ind = None
    max_fitness = 0
    for pop in run:
        for c in pop:
            if c.fitness > max_fitness:
                max_ind = c
                max_fitness = c.fitness
    for l, gene in zip(weights, max_ind):
        l.append(gene)
# Bias
for n, l, w in zip(neurons, labels, weights[0:rtexp.NEURONS]):
    v = avg(w)
    print("    %s [label=\"%s\",style=filled,color=\"%s\",shape=circle,width=.75, height=.5,fixedsize=true];" % (n, l, n2rgb(v)))
i = rtexp.NEURONS
for npre in neurons:
    for npost in neurons:
        v = avg(weights[i])
        print("    %s -> %s [color=\"%s\"" % (npre, npost, n2rgb(v)), end="")
        if neurons.index(npre) > neurons.index(npost):
            print(',constraint = false')
        print('];')
        i += 1
print("}")
    
    
