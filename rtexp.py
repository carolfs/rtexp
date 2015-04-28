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

import random, math, sys, os, ifnn, time, ga, configparser

# Read experiment configuration
config = configparser.ConfigParser()
config.read(sys.argv[1])
config = config['EXP']

EXT_STIMULI = float(config['EXT_STIMULI'])
CUE_STIMULI = float(config.get('CUE_STIMULI', EXT_STIMULI))
TAU = float(config.get('TAU', 10))
COST_FACTOR = float(config['COST_FACTOR'])
MIN_GENE = float(config['MIN_GENE'])
MAX_GENE = float(config['MAX_GENE'])
MUTATION_STEP = float(config['MUTATION_STEP'])
GENERATIONS = int(config['GENERATIONS'])
SAVE = int(config['SAVE'])
if GENERATIONS % SAVE != 0:
    sys.stderr.write('Bad number of generations.\n')
    sys.exit(-1)
RUNS = int(config['RUNS'])
NUM_POPS = int(config['NUM_POPS'])
NUM_INDS = int(config['NUM_INDS'])
MIGRAR = int(config['MIGRAR'])
MAX_STAGNATION = int(config['MAX_STAGNATION'])
NOISE = int(config['NOISE'])
NOISE_SIGMA = float(config['NOISE_SIGMA'])
DIR = config['DIR']
FILENAME = os.path.join(DIR, 'r%03d-g%03d')

def advance_nn(self, nn, s):
    return nn.advance(s)

def advance_nn_with_noise(self, nn, s):
    noise = [random.gauss(0, NOISE_SIGMA) for i in range(nn.num_neurons())]
    return nn.advance_with_noise(s, noise)

class Task:
    # Time parameters
    PRE_TIME = 50
    MIN_CUE_TIME = 100
    MAX_CUE_TIME = None
    MAX_RT = 1000
    
    advance = advance_nn_with_noise if NOISE else advance_nn
    
    @classmethod
    def define_trials(cls, valid, neutral, invalid, catch, reps):
        cls.trials = (
            ('L', 'V'),
            ('R', 'V'),
        ) * valid * reps + (
            ('L', 'I'),
            ('R', 'I'),
        ) * invalid * reps + (
            ('L', 'N'),
            ('R', 'N'),
        ) * neutral * reps + (
            ('C', 'V'),
        ) * round(catch * valid * 2 * reps) + (
            ('C', 'I'),
        ) * round(catch * invalid * 2 * reps) + (
            ('C', 'N'),
        ) * round(catch * neutral * 2 * reps)
    
    def run(self, c, nn):
        results = []
        for params in self.trials:
            nn.reset()
            s = [0] * nn.num_input_neurons()
            for i in range(self.PRE_TIME):
                output = self.advance(nn, s)
            side, vcue = params
            if vcue == 'N':
                cue = [0, CUE_STIMULI, 0]
            elif side == 'L' and vcue == 'V' or side == 'R' and vcue == 'I':
                cue = [CUE_STIMULI, 0, 0]
            else:
                cue = [0, 0, CUE_STIMULI]
            t = -random.randint(self.MIN_CUE_TIME, self.MAX_CUE_TIME)
            rt = None
            s[1:4] = cue
            while t <= self.MAX_RT:
                if t == 0:
                    if side == 'L':
                        s[0] = EXT_STIMULI
                    elif side == 'R':
                        s[4] = EXT_STIMULI
                    else:
                        assert side == 'C'
                assert len(s) == nn.num_input_neurons()
                output = self.advance(nn, s)
                result = self.got_result(output, side)
                if result is not None:
                    result['params'] = params
                    result['rt'] = t
                    results.append(result)
                    break
                else:
                    t += 1
            else:
                result = {}
                result['params'] = params
                result['rt'] = None
                results.append(result)
        self.set_fitness(c, results)
    @staticmethod
    def get_fitness(rt):
        return 1000 * math.exp(-0.01 * rt)
    @staticmethod
    def print_stats(c):
        # Printing statistics
        
        print("%10d" % c.fitness, end='\t')
        if c.rt_valid is not None:
            print("% 7.2f" % c.rt_valid, end='\t')
        else:
            print("-------", end='\t')
        if c.rt_neutral is not None:
            print("% 7.2f" % c.rt_neutral, end='\t')
        else:
            print("-------", end='\t')
        if c.rt_invalid is not None:
            print("% 7.2f" % c.rt_invalid, end='\t')
        else:
            print("-------", end='\t')
        print('\t'.join(['%3d' for i in c.count]) % c.count, end='\t')
        print()

class SimpleRTTask(Task):
    def got_result(self, output, side):
        if output[0]:
            return {}
        else:
            return None
    
    def set_fitness(self, c, results):
        c.fitness = 0
        anticipated = 0
        resp = 0
        miss = 0
        catch = 0
        rt_valid = []
        rt_invalid = []
        rt_neutral = []
        for r in results:
            side, vcue = r['params']
            if r['rt'] is not None:
                resp += 1
                if side == 'C': # responded in a catch trial
                    pass
                elif r['rt'] <= 0: # anticipated
                    anticipated += 1
                else:
                    c.fitness += self.get_fitness(r['rt'])
                    if vcue == 'V':
                        rt_valid.append(r['rt'])
                    elif vcue == 'I':
                        rt_invalid.append(r['rt'])
                    else:
                        assert vcue == 'N'
                        rt_neutral.append(r['rt'])
            else:
                if side == 'C':
                    c.fitness += 1000
                    catch += 1
                else:
                    miss += 1
        c.rt_valid = median(rt_valid)
        c.rt_invalid = median(rt_invalid)
        c.rt_neutral = median(rt_neutral)
        c.count = (resp, miss, anticipated, catch)

class ChoiceRTTask(Task):
    def got_result(self, output, side):
        if output[0] and output[1]:
            return {'correct': False}
        elif output[0]:
            return {'correct': (side == 'L')}
        elif output[1]:
            return {'correct': (side == 'R')}
        else:
            return None
    
    def set_fitness(self, c, results):
        c.fitness = 0
        anticipated = 0
        resp = 0
        miss = 0
        wrong = 0
        catch = 0
        rt_valid = []
        rt_invalid = []
        rt_neutral = []
        for r in results:
            side, vcue = r['params']
            if r['rt'] is not None:
                resp += 1
                if side == 'C': # responded in a catch trial
                    pass
                elif r['rt'] <= 0: # anticipated
                    anticipated += 1
                elif r['correct']:
                    c.fitness += self.get_fitness(r['rt'])
                    if vcue == 'V':
                        rt_valid.append(r['rt'])
                    elif vcue == 'I':
                        rt_invalid.append(r['rt'])
                    else:
                        assert vcue == 'N'
                        rt_neutral.append(r['rt'])
                else:
                    wrong += 1
            else:
                if side == 'C':
                    c.fitness += 1000
                    catch += 1
                else:
                    miss += 1
        c.rt_valid = median(rt_valid)
        c.rt_invalid = median(rt_invalid)
        c.rt_neutral = median(rt_neutral)
        c.count = (resp, miss, anticipated, wrong, catch)

def avg(l):
    try:
        return sum(l) / float(len(l))
    except:
        return None

def median(l):
    if len(l) == 0:
        return None
    l.sort()
    if len(l) % 2 == 0:
        return avg((l[len(l) // 2 - 1], l[len(l) // 2]))
    else:
        return l[len(l) // 2]

def simplert_fitness_function(pop):
    #print('   fitness\tvalidRT\tinvldRT\tneutrRT\tres\tmis\tant\tcat')
    for c in pop:
        trials = SimpleRTTask()
        trials.run(c, make_network(c))
    #print()

def choicert_fitness_function(pop):
    #print('   fitness\tvalidRT\tneutrRT\tinvldRT\tres\tmis\tant\twro\tcat')
    for c in pop:
        trials = ChoiceRTTask()
        trials.run(c, make_network(c))
    #print()
    
if config['TYPE'] == 'Simple':
    ga.Population.evaluate_fitness = simplert_fitness_function
    #print('Simple RT task selected.')
    OUTPUT_NEURONS = 1
else:
    ga.Population.evaluate_fitness = choicert_fitness_function
    #print('Choice RT task selected.')
    OUTPUT_NEURONS = 2
ga.Run.MAX_STAGNATION = MAX_STAGNATION

INPUT_NEURONS = 5
HIDDEN_NEURONS = int(config['HIDDEN_NEURONS'])
NEURONS = INPUT_NEURONS + HIDDEN_NEURONS + OUTPUT_NEURONS

VALID = int(config['VALID'])
INVALID = int(config['INVALID'])
NEUTRAL = int(config['NEUTRAL'])
CATCH = float(config.get('CATCH', 0))
REPS = int(config['REPS'])
Task.MAX_CUE_TIME = int(config.get('MAX_CUE_TIME', 200))

# For the simple GA

def get_list_genes():
    list_genes = []
    for i in range(NEURONS):
        list_genes.append(ga.Gene(MIN_GENE, MAX_GENE, MUTATION_STEP)) # bias
    for i in range(NEURONS * NEURONS): # synapses
        list_genes.append(ga.Gene(MIN_GENE, MAX_GENE, MUTATION_STEP))
    return list_genes

def make_network(c):
    return ifnn.Network(INPUT_NEURONS, OUTPUT_NEURONS, HIDDEN_NEURONS, c, TAU)
            
def friendly_time(t):
    s = []
    if t > 86400:
        s.append('%d day(s)' % (t // 86400))
        t = t % 86400
    if t > 3600:
        s.append('%d hour(s)' % (t // 3600))
        t = t % 3600
    if t > 60:
        s.append('%d minute(s)' % (t // 60))
        t = t % 60
    s.append('%d seconds(s)' % int(t))
    return ' '.join(s)
    
def sub_pop(run, i):
    newpop = ga.Population.get_random(NUM_INDS, get_list_genes())
    run[i] = newpop

Task.define_trials(VALID, NEUTRAL, INVALID, CATCH, REPS)

if __name__ == '__main__':
    if not os.path.exists(DIR):
        os.mkdir(DIR)
    for run_number in range(RUNS):
        print("Run", run_number + 1)
        arquivo = FILENAME % (run_number, 0)
        if os.path.exists(arquivo):
            with open(arquivo, 'rb') as f:
                run = ga.Run.load(f)
        else:
            run = ga.Run()
            for i in range(NUM_POPS):
                pop = ga.Population.get_random(NUM_INDS, get_list_genes())
                run.append(pop)
            with open(arquivo, 'wb') as f:
                run.dump(f)
        print("Generation 0")
        while run.g < GENERATIONS:
            new_g = run.g + SAVE
            arquivo = FILENAME % (run_number, new_g)
            if os.path.exists(arquivo):
                with open(arquivo, 'rb') as f:
                    run = ga.Run.load(f)
            else:
                run.iterate(SAVE)
                assert run.g == new_g
                if MIGRAR and run.g % MIGRAR == 0:
                    run.migrate()
                with open(arquivo, 'wb') as f:
                    run.dump(f)
            print("Generation %d" % (run.g))