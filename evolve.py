from coevolve import COEVOLVE
from population import POPULATION
from aggregate import AGGREGATE
from element import ELEMENT
from element import TouchSensorUniversalHingeJointElement
from element import TouchAndLightSensorYAxisHingeJointElement
from element import TouchAndLightSensorXAxisHingeJointElement

elementTypes = [TouchSensorUniversalHingeJointElement,
                TouchAndLightSensorYAxisHingeJointElement,
                TouchAndLightSensorXAxisHingeJointElement]

N = 15
GENS = 100

aggregates = POPULATION(AGGREGATE, n=N, unique=True)
elements = POPULATION(ELEMENT, n=N, unique=True)

aggregates.initialize()
elements.initialize()

for i in range(N):
    elements.p[i] = elementTypes[i%3]()
    
coevolve = COEVOLVE(aggregates, elements)

coevolve.exhaustive()

coevolve.print_fitness(0)

for g in range(1, GENS+1):
    
    #selection and mutation
    coevolve.selection()
    
    #resets all fitness values
    coevolve.reset()
    
    #evaluation
    coevolve.exhaustive()
    
    #report fitness values
    coevolve.print_fitness(g)
    
    
    
    
    

    










