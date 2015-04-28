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

# Simple Genetic Algorithm

import random, pickle

randobj = random.Random()

class Gene(float):
    MUTATION_RATE = 0.05
    def __new__(cls, min_value, max_value, mutation_step, value = None):
        if value == None:
            value = randobj.uniform(min_value, max_value)
        assert(value >= min_value and value <= max_value)
        x = super(Gene, cls).__new__(cls, value)
        x.__mutstep = mutation_step
        x.__maxv = max_value
        x.__minv = min_value
        return x
    def __getnewargs__(x):
        return (x.__minv, x.__maxv, x.__mutstep, float(x))
    def get_random(self):
        return type(self)(self.__minv, self.__maxv, self.__mutstep)
    def copy(self):
        if randobj.random() < self.MUTATION_RATE:
            # Mutate
            stepdn = - min([self.__mutstep, self - self.__minv])
            stepup = min([self.__mutstep, self.__maxv - self])
            x = self + randobj.uniform(stepdn, stepup)
            return self.__class__(self.__minv, self.__maxv, self.__mutstep, x)
        else:
            return self

class Chromosome:
    def __init__(self, list_genes, fitness = None):
        self.__genes = tuple(list_genes)
        self.fitness = fitness
    def __getitem__(self, key):
        return self.__genes[key]
    def get_random(self):
        return self.__class__([gene.get_random() for gene in self])
    def __lt__(self, other):
        return self.fitness < other.fitness
    def get_child(p1, p2):
        child = []
        for i, g in enumerate(p1):
            child.append(randobj.choice((g, p2[i])))
        return p1.__class__([gene.copy() for gene in child])
    def __len__(self):
        return len(self.__genes)
    def __str__(self):
        return str(self.__genes)

class Population:
    ELITE = True
    RANDOM_INDIVIDUALS = 0
    evaluate_fitness = None
    def __init__(self, list_individuals):
        self.age = 0
        self.__inds = list_individuals
        Population.evaluate_fitness(self)
        self.max_ind = max(self)
        self.no_improvement_age = 0
        self.__mean_fitness = float(sum([i.fitness for i in self])) / len(self)
        self.max_mean_fitness = self.__mean_fitness
    def __select(self):
        return max(randobj.choice(self), randobj.choice(self))
    def advance(self):
        new_inds = []
        if self.ELITE:
            new_inds.append(self.max_ind)
        for i in range(self.RANDOM_INDIVIDUALS):
            new_inds.append(self[0].get_random())
        for i in range(len(self) - len(new_inds)):
            p1, p2 = self.__select(), self.__select()
            new_inds.append(p1.get_child(p2))
        assert(len(new_inds) == len(self))
        self.__inds = new_inds
        Population.evaluate_fitness(self)
        self.max_ind = max(self)
        self.__mean_fitness = float(sum([i.fitness for i in self])) / len(self)
        if self.__mean_fitness <= self.max_mean_fitness:
            self.no_improvement_age += 1
        else:
            self.max_mean_fitness = self.__mean_fitness
        self.age += 1
    def __getitem__(self, key):
        return self.__inds[key]
    def __iter__(self):
        return iter(self.__inds)
    def __len__(self):
        return len(self.__inds)
    def __str__(self):
        return str(self.__inds)
    @classmethod
    def get_random(cls, n, genes):
        c = Chromosome(genes)
        return cls([c.get_random() for i in range(n)])
    def add_immigrant(self, im):
        i = self.__inds.index(self.max_ind)
        self.__inds[i] = im
        self.max_ind = max(self)
    def __lt__(self, other):
        return self.max_mean_fitness < other.max_mean_fitness

class Run(list):
    def __init__(self):
        self._g = 0
    @property
    def g(self):
        return self._g
    def iterate(self, n):
        for g in range(n):
            self.advance()
    def advance(self):
        self._g += 1
        for pop in self:
            pop.advance()
    def migrate(self):
        best = []
        for pop in self:
            best.append(pop.max_ind)
        randobj.shuffle(best)
        for i, pop in enumerate(self):
            pop.add_immigrant(best[i])
    def remove_stagnant(self, max_stagnation):
        max_pop = max(self)
        for i, pop in enumerate(self[:]):
            if pop is not max_pop and pop.no_improvement_age >= max_stagnation:
                print("Dropping population", i)
                self[i] = Population.get_random(len(pop), pop[0])
    def dump(self, fileobj):
        pickle.dump(randobj.getstate(), fileobj)
        pickle.dump(self, fileobj)
    @classmethod
    def load(cls, fileobj):
        randobj.setstate(pickle.load(fileobj))
        return pickle.load(fileobj)
    @staticmethod
    def seed(s):
        randobj.seed(s)
    @staticmethod
    def setstate(s):
        randobj.setstate(s)
