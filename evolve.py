from coevolve import COEVOLVE
from population import POPULATION
from aggregate import AGGREGATE
from element import ELEMENT

aggregates = POPULATION(AGGREGATE, n=15, unique=True)
elements = POPULATION(ELEMENT, n=15, unique=True)