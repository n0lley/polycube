
import numpy as np
import pickle
from copy import deepcopy
import os
import networkx as nx #for enumerating polycube trees
import enumeratePolycubes as ep
import math

from individual import INDIVIDUAL
    
def dominates(a, b):
    if a.fitness > b.fitness and a.age < b.age:
        fpi = math.ceil(len(a.scores)*.05)
        print(a.fitness, a.scores[0:fpi], "dominates", b.fitness, b.scores[0:fpi])
        return True
    else:
        return False
        
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
                self.p[i] = deepcopy(self.p[0])
                self.p[i].mutate()
                
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
            
    def hillclimber_selection(self, parent):
        """
        hill climber selection for genetic evolution
        :return: None
        """
        print("Parents:")
        parent.Print()
        print("_____________________________________________________")
        print("Children:")
        self.Print()
        for i in range(len(parent.p)):
            if parent.p[i].fitness > self.p[i].fitness:
                self.p[i] = deepcopy(parent.p[i])
                print(i, "failed to outperform its parent")
        print("New Pop:")
        self.Print()
          
    def tournament_selection(self):
        """
        tournament selection for genetic evolution
        :return: None
        """
        newpop = [None] * self.popSize
        
        #copy the best individual
        bestfit = 0
        bestindex = -1
        for i in range(len(self.p)):
            if self.p[i].fitness > bestfit:
                bestfit = self.p[i].fitness
                bestindex = i
        
        newpop[0] = deepcopy(self.p[bestindex])
        del self.p[bestindex]
        
        for i in range(1, len(self.p)):
            newpop[i] = self.p[i]
            newpop[i].mutate()
            
        newpop[-1] = self.p[0]
        newpop[-1].mutate()
        
        #replace current pop with new pop
        self.p = deepcopy(newpop)
        del newpop

        return a.id < b.id
        
    def afpo_selection(self):
        """
        AFPO for genetic evolution
        :return: None
        """
        # increment ages
        for i in range(len(self.p)):
            print(self.p[i].age, end='->')
            self.p[i].increment_age()
            print(self.p[i].age)

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
        self.p = deepcopy(dom_ind)

        # add new RANDOM individual
        self.p.append(self.ind())

        # expand the population
        initial_size = len(self.p)
        while len(self.p) < self.popSize:
            parent_index = np.random.randint(0, initial_size)
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
        
    def Print(self):
        
        for i in range(len(self.p)):
            self.p[i].scores.sort()
            print("[%d: %f]"%(i, self.p[i].fitness), self.p[i].scores)

class FIXEDAGGPOP(POPULATION):
    """
    Subclass created specifically to generate fixed populations of aggregates of specified size.
    """

    def __init__(self, ind, num_cubes=2):
        """
        Initialize the population, specify the number of cubes, enumerate polycubes of size num_cubes
        
        Parameters
        ----------
        ind : class
            in this case, should always be AGGREGATE().
            
        num_cubes : int
            number of cubes the robots in the aggregate population should be made of.
        
        """
        assert isinstance(ind(), INDIVIDUAL), print('ERROR: ind() must return an instance of the INDIVIDUAL class')
        assert hasattr(ind, 'evaluate'), print('ERROR: Object needs method .evaluate()')
        
        #establish variables
        self.ind = ind
        self.popSize = 0
        #print(self.num_cubes)
        
        #load structures, if not already created
        if os.path.exists("../%dcube.p"%num_cubes):
            print("population preloaded")
            f = open("../%dcube.p"%num_cubes, 'rb')
            self.morph_list = pickle.load(f)
            f.close()
            
        else:
            print("enumerating population")
            self.morph_list = ep.get_polycubes_of_size(num_cubes)
            f = open("../%dcube.p"%num_cubes, 'wb')
            pickle.dump(self.morph_list, f)
            f.close()
        
        #calculate popsize - one for each possible internal tree for each polycube.
        #TODO: eliminate rotationally equivalent trees
        #print(self.morph_list)
        for polycube in self.morph_list:
            A = ep.polycube_to_graph(polycube, num_cubes)
            G = nx.from_numpy_matrix(A)
            edges = ep.get_edge_list(G)
            trees = ep.brute_force_trees(num_cubes, edges)
            self.popSize += len(trees)
        
        print(self.popSize, format(num_cubes) + "-cube morphologies enumerated.")
        self.p = [None] * self.popSize
        
    def initialize(self):
        """
        generates a population of fixed aggregates size self.num_cubes
        :return: None
        """
        
        #fill the population with aggregate individuals
        #doesn't matter what they are, we're manually doing their trees
        for i in range(len(self.p)):
            self.p[i] = self.ind()
        
        popIndex = 0
        for i in range(len(self.morph_list)):
            #select a structure and enumerate its articulations
            polycube = self.morph_list[i]
            num_cubes = len(polycube)
            #print(polycube)
            A = ep.polycube_to_graph(polycube, num_cubes)
            #print(A)
            G = nx.from_numpy_matrix(A)
            edges = ep.get_edge_list(G)
            trees = ep.brute_force_trees(num_cubes, edges)

            #create morphology for each possible internal tree
            body_tree = {}
            for tree in trees:
                #fill the aggregate tree with its nodes
                for node in polycube:
                    body_tree[node] = []
                for edge in tree:
                    n0 = polycube[edge[0]]
                    n1 = polycube[edge[1]]
                    body_tree[n0].append(n1)
            
                #the next aggregate has this morphology now.
                self.p[popIndex].tree = body_tree
                popIndex += 1
