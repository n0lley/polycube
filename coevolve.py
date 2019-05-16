

class COEVOLVE:
    '''
    COEVOLVE class that handles co-evolutionary methods
        for AGGREGATE and ELEMENT classes
    '''
    
    def __init__(self, pop1, pop2):
        '''
        initializes the two populations 
        '''
        
        self.aggrs = pop1
        self.elmts = pop2
        
    def exhaustive(self):
        
        for i in self.elmts.p:
            elmt = self.elmts.p[i]
            for j in self.aggrs.p:
                aggr = self.aggrs.p[j]
                
                aggr.build_with(elmt)