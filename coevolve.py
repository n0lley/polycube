import numpy as np


class COEVOLVE:
    '''
    COEVOLVE class that handles co-evolutionary methods
        for AGGREGATE and ELEMENT classes
        
    To be used with population class in ./population.py
    '''
    
    def __init__(self, pop1, pop2):
        '''
        initializes the two populations 
        '''
        
        self.aggrs = pop1
        self.elmts = pop2
        
    def exhaustive(self):
        '''
        Evaluates every single aggregate composed with 
            every single element 
        '''

        for i in self.elmts.p:
            elmt = self.elmts.p[i]
            for j in self.aggrs.p:
                aggr = self.aggrs.p[j]
                aggr.send_to_sim(sim, elmt)
                
    def random_subset(self, p, q):
        '''
        Selects subsets of proportion p from aggregate 
            and proportion q from elements for evaluation
        '''
        
        assert 0 <= p <= 1, print('First input needs to be a valid proportion')
        assert 0 <= q <= 1, print('Second input needs to be a valid proportion')
        
        n1 = self.aggrs.popSize
        n2 = self.elmts.popSize
        
        aggrSub = np.random.choice(n1, size=int(np.ceil(p*n1)))
        elmtSub = np.random.choice(n2, size=int(np.ceil(q*n2)))
        
        for i in elmtSub:
            elmt = self.elmts.p[i]
            for j in aggrSub:
                aggr = self.aggrs.p[j]
                aggr.send_to_sim(sim, elmt)
        
        
        
        
        
        
        
        
        
        
        
                
                