import numpy as np


class COEVOLVE:
    '''
    handles co-evolutionary methods for AGGREGATE and ELEMENT classes
        
    Attributes
    ----------
    aggrs    : POPULATION instance
        Population of aggregate objects
    elmts    : POPULATION instance
        Population of element objects
        
    Methods
    -------
    exhaustive()
        Evaluates with every combination of aggregate and element
    random_subset(p=0.5, q=0.5)
        Evaluates every combination within given subsets, with size
        determined by the given proportions
    '''
    
    def __init__(self, aggrs, elmts):
        '''
        initializes the two populations 
        '''
        
        self.aggrs = aggrs
        self.elmts = elmts
        
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
                
    def random_subset(self, p=0.5, q=0.5):
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
        
        
        
        
        
        
        
        
        
        
        
                
                