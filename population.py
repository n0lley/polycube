# import numpy as np

import random
from copy import deepcopy

from individual import INDIVIDUAL

class POPULATION:
    """
    Handles evolutionary methods for the given object
    
    Attributes
    ----------
    ind     : class
        the individual type that composes the population
    popSize       : int
        the population size
    unique  : bool
        defines how the initial population is created
    p       : dict
        holds the individuals in the population
    fits    : dict
        holds each individual's fitness values
    
    Methods
    -------
    initialize()
        generates the initial, random population
    evaluate()
        evaluates each individual
    """
    
    def __init__(self, ind, pop_size=10, unique=True):
        """
        initializes the population of popSize objects
        :param ind: function which returns an instance of the INDIVIDUAL class.
        :param pop_size: target number of individuals in the class
        :param unique: Should we seed the initial population with unique individuals or mutants of a single one.
        """
        assert isinstance(ind(), INDIVIDUAL), print('ERROR: ind() must return an instance of the INDIVIDUAL class')
        # assert hasattr(ind, 'evaluate'), print('ERROR: Object needs method .evaluate()')
        
        self.ind = ind
        self.popSize = pop_size
        self.unique = unique

        self.p = [None] * self.popSize
        self.fits = {}
        
    def initialize(self):
        """
        generates the population
        :return: None
        """
        self.p[0] = self.ind()
        
        assert hasattr(self.p[0], 'fitness'), print('ERROR: Object needs field .fitness')
        
        for i in range(1, self.popSize):
            if self.unique:
                self.p[i] = self.ind()
            else:
                self.p[i] = self.p[0].mutate()

    def evaluate(self):
        """
        evaluates each individual in the population
        :return: None
        """
        for i in range(len(self.p)):
            self.p[i].evaluate()
            self.fits[i] = self.p[i].fitness
            
    def reset(self):
        """
        resets all fitness values
        :return: None
        """
        for i in range(len(self.p)):
            self.p[i].reset()
            self.p[i].fitness = 0
            
    def selection(self):
        """
        AFPO for genetic evolution
        :return: None
        """
        # increment ages
        for i in range(len(self.p)):
            self.p[i].increment_age()

        # contract the population to non-dominated individuals
        dom_ind = []
        for s in range(len(self.p)):
            dominated = False
            for t in range(len(self.p)):
                if dominates(self.p[t], self.p[s]):
                    dominated = True
                    break
            if not dominated:
                dom_ind.append(self.p[s])
        self.p = dom_ind

        # add new RANDOM student
        self.p.append(self.ind())

        # expand the population
        initial_size = len(self.p)
        while len(self.p) < self.popSize:
            parent_index = random.randrange(0, initial_size)
            new_indv = deepcopy(self.p[parent_index])
            new_indv.mutate()
            self.p.append(new_indv)

    def getNonDominated(self):

        dom_ind = []
        for s in range(len(self.p)):
            dominated = False
            for t in range(len(self.p)):
                if dominates(self.p[t], self.p[s]):
                    dominated = True
                    break
            if not dominated:
                dom_ind.append(self.p[s])
        return sorted(dom_ind, key=lambda x: x.age)

def dominates(a, b):
    if a.fitness < b.fitness or a.age > b.age:
        return False

    if a.fitness > b.fitness or a.age < b.age:
        return True

    return a.id < b.id
