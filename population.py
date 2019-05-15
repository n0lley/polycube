


class POPULATION:
    '''
    POPULATION class that handles evolutionary methods
        for the given object
    '''
    
    def __init__(self, n, object):
        '''
        initializes the population of n objects
        '''

        assert hasattr(object, 'mutate'), print('Object needs method .mutate()')
        assert hasattr(object, 'evaluate'), print('Object needs method .evaluate()')
        assert hasattr(object, 'fitness'), print('Object needs field .fitness')
        
        self.p = {}
        
    def evaluate(self):
        '''
        evaluates each individual in the population
        '''
        
        pass
    
    