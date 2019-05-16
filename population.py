


class POPULATION:
    '''
    POPULATION class that handles evolutionary methods
        for the given object
    '''
    
    def __init__(self, object, n=10, unique=True):
        '''
        initializes the population of n objects
        
        object: (class) individual class to be evolved
        n: (int) population size
        unique: (bool) if True, initializes n independent individuals
                       if False, generates random mutants of 1 individual
        '''

        assert hasattr(object, 'mutate'), print('ERROR: Object needs method .mutate()')
        assert hasattr(object, 'evaluate'), print('ERROR: Object needs method .evaluate()')
        assert hasattr(object, 'generate_random'), print('ERROR: Object needs method .generate_random()')
        
        self.ind = object
        self.popSize = n
        self.unique = unique
        
        self.p = {}
        self.fits = {}
        
        self.initialize()
        
    
    def initialize(self):
        '''
        generates the population
        '''        
        
        self.p[0] = self.ind()
        
        assert hasattr(self.p[0], 'fitness'), print('ERROR: Object needs field .fitness')
        
        for i in range(1, self.popSize):
            if self.unique:
                self.p[i] = self.ind()
            else:
                self.p[i] = self.p[0].mutate()
                
            
        
       
    
        
        
    def evaluate(self):
        '''
        evaluates each individual in the population
        '''
        
        pass
    
    