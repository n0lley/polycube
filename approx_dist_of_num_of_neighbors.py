# todo: approximate (using Monte-Carlo method) and plot the distribution of number_of_neighbors as a function of the number_of_elements

import sys
from multiprocessing import Pool
import random
import numpy as np


from aggregate import AGGREGATE
import pyrosim

debug = False

def get_neighbor_counts(node_count):
    # generate aggregate
    aggregate = AGGREGATE(None, [None], node_count, no_sim=True)
    structure = aggregate.tree

    # remove the origin. Each node has 1 parent except the origin which has none.
    origin = structure.pop((0, 0, 0))

    # calculate neighbor counts
    neighbor_counts = [len(d) + 1 for d in
                       aggregate.tree.values()]  # each node has 1 parent with the exception of the origin which has 0 parents.
    # add the origin back in
    neighbor_counts.append(len(origin))

    # if in debug, assert truth values
    if debug:
        if node_count > 1:
            assert (min(neighbor_counts) > 0), "Error with generating polycube"
        else:
            assert (min(neighbor_counts) >= 0), "Error with generating polycube"
        assert (max(neighbor_counts) < 7), "Error with generating polycube"

    # calculate neighbor frequencies
    neighbor_frequencies = np.zeros(shape=6)
    for n in range(6):
        neighbor_frequencies[n] = neighbor_counts.count(n + 1)
    return neighbor_frequencies

def compute_work( node_count, iteration_number, ttl_iterations,seed_offset=0):
    """
    wrapper method for get_neighbor_counts which also sets the seed + keeps track of which iteration this is.
    :param node_count: number of nodes to include in our polynode
    :param iteration_number: which iteration we are running
    :param seed_offset: how to adjust the seed.
    :return: tuple of node_count, iteration_number, and the frequency of num neighbors
    """
    # TODO: Decide if this seeding is good or not.
    random.seed(seed_offset + iteration_number + node_count*ttl_iterations)
    ret = get_neighbor_counts(node_count)
    return (node_count, iteration_number, ret)


if __name__ == "__main__":
    assert len(sys.argv) >= 3, "Please run as python NAME.py <Number of nodes in polycube> <number of iterations for Monte-Carlo> <optional: starting seed>"
    ttl_iterations = int(sys.argv[2])
    ttl_node_count = int(sys.argv[1])
    if len(sys.argv) == 4:
        seed_offset = int(sys.argv[3])
    else:
        seed_offset = 0

    data = np.zeros(shape=(ttl_node_count, ttl_iterations, 6))

    # used for parallel computation
    process_count = None
    pool = Pool(processes=process_count)


    # compute the work
    for j in range(ttl_node_count):
        sys.stdout.write("%3d"%j)
        sys.stdout.flush()
        iterations_list = list(range(ttl_iterations))
        res = [pool.apply_async(compute_work, args=( j, iter_num, ttl_iterations, seed_offset)) for iter_num in iterations_list]
        for r in res:
            node_count, iter_num, ret = r.get()
            data[node_count, iter_num] = ret
        sys.stdout.write("\n")
        sys.stdout.flush()
    pool.close()
    pool.join()
    print(data)






