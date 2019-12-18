
# Polycubes
Polycubes is an implementation of Pyrosim that simulates polycube-based modular robots and distributed neural controllers.

The Small_Polycubes branch exhaustively simulates elements with fixed populations of polycube structures of sizes 2 through 5. Each structure is distinct from every other structure in the population in terms of reflection and rotation about the z axis. Individuals from the controller population are simulated with every individual from the morphology population, then given a fitness determined by the average of all their performances.

Evolution can be started by running evolve.py and specifying the random seed, polycube size, and run name in that order. The size of the element population, the number of generations of evolution, and the size of a cube may all be modified in constants.py

# Experimental Design

The initial stage of Small_Polycubes is intended to be the simplest possible controllers, a one-weight genome that determines the phase offset of a module's two motors. Our experimental cycle is then as follows:

We evaluate a population of 50 controllers under our current algorithm against fixed aggregate populations. Should the controllers prove capable of producing displacement in all polycubes in the population, then they are considered robust. Should they fail to do so, we make one of the following changes:

  Increase controller complexity - change input function, add to genome, add more inputs
  Modify evolutionary algorithm
  Modify the encoding of the controller - from a direct encoding to indirect

The order in which these changes are made will be determined by the results from testing.
And then repeat our cycle.
  
# Getting started 
* Please install both of the dependencies below. Instructions are on their github repository pages
* Please run python evolve.py <Seed> to evolve some robots

# Dependencies
##  pyrosim: A python robot simulator. 

Pyrosim enables the creation of robots with arbitrary body plans
and neural controllers, and the optimization of them in arbitrary simulated
environments. Visit the [Documentation](https://mec-lab.github.io/pyrosim) for more detailed information.

[![DOI](https://zenodo.org/badge/168368037.svg)](https://zenodo.org/badge/latestdoi/168368037)

Cite : [BibTex](./pyrosim-bibtex.bib)

For more information about pyrosim, please view the main repository at [https://www.github.com/mec-lab/pyrosim](https://www.github.com/mec-lab/pyrosim)

## ParallelPy

ParallelPy allows for parallel execution of independent code across multiple computers.
It's primary purpose is to parallelize the physics simulations needed to preform evolutionary robotics experiments across a compute cluster.

For more information about ParllelPy, please view the main repository at [https://www.github.com/davidmatthews1uvm/parallelpy](https://www.github.com/davidmatthews1uvm/parallelpy)  
