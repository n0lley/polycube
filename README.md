
# Polycubes
Polycubes is an implementation of Pyrosim that simulates polycube-based modular robots. The master branch is a starting point containing an algorithm for creating the polycube robots and simulating them with basic distributed controllers, then coevolving them. Each subsequent branch from master contains a step of abstraction away from the initial algorithm and controller, with the goal of eventually achieving a controller that can generate a desired behavior in any given polycube structure.

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
