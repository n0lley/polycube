from copy import deepcopy
import numpy as np


class POPULATION:
    '''
    Handles evolutionary methods for the given object
    
    Attributes
    ----------
    ind     : class
        the individual type that composes the population
    n       : int
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
    '''
    
    def __init__(self, ind, n=10, unique=True):
        '''
        initializes the population of n objects
        '''

        assert hasattr(ind, 'mutate'), print('ERROR: Object needs method .mutate()')
        #assert hasattr(ind, 'evaluate'), print('ERROR: Object needs method .evaluate()')
        
        self.ind = ind
        self.n = n
        self.unique = unique
        
        self.p = {}
        self.fits = {}
        
    
    def initialize(self):
        '''
        generates the population
        '''        
        
        self.p[0] = self.ind()
        
        assert hasattr(self.p[0], 'fitness'), print('ERROR: Object needs field .fitness')
        
        for i in range(1, self.n):
            if self.unique:
                self.p[i] = self.ind()
            else:
                self.p[i] = self.p[0].mutate()
                
        
    def evaluate(self):
        '''
        evaluates each individual in the population
        '''
        
        for i in self.p:
            self.p[i].evaluate()
            self.fits[i] = self.p[i].fitness
            
    def reset(self):
        '''
        resets all fitness values
        '''
        
        for i in self.p:
            self.p[i].reset()
            self.p[i].fitness = 0
            
    def selection(self):
        '''
        standard GA selection with mutation
        '''
        
        newPop = {}
        
        #find best and copy over
        bestP = self.p[0]
        for i in self.p:
            if self.p[i].fitness > bestP.fitness:
                bestP = self.p[i] 
        
        newPop[0] = deepcopy(bestP)
        
        #random tournament to fill population
        for i in range(1, self.n):
            
            x, y = np.random.choice(self.n, size=2, replace=False)
            
            ind1 = self.p[x]
            ind2 = self.p[y]
            
            if ind1.fitness > ind2.fitness:
                newPop[i] = deepcopy(ind1)
            else:
                newPop[i] = deepcopy(ind2)
                
            newPop[i].mutate()
                
        self.p = deepcopy(newPop)
        
    
    
    
    
