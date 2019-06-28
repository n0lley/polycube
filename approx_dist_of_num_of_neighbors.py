# todo: approximate (using Monte-Carlo method) and plot the distribution of number_of_neighbors as a function of the number_of_elements

import queue
import random
import sys
from multiprocessing import Pool

import numpy as np

from aggregate import AGGREGATE

debug = True
BLOCK = 1
AIR = 2


class Air(object):
    AIR_UNKOWN = 1
    AIR_EXTERNAL = 2
    AIR_INTERNAL = 3

    def __init__(self, position):
        self.position = position  # a tuple of (x,y,z)
        self.type = Air.AIR_UNKOWN


class Block(object):
    def __init__(self, position, connections):
        self.position = position  # a tuple of (x,y,z)
        self.connections = connections  # a list of tuples of (x,y,z) positions of neighboring cubes
        self.connection_count = len(self.connections)


def get_aggregate(node_cnt):
    return AGGREGATE(None, [None], node_cnt, no_sim=True).tree


def compute_interior_nodes(node_cnt):
    # get the structure
    structure = get_aggregate(node_cnt)

    # find bounding box
    x_max_node = None
    x_min, x_max = 0, 0
    y_min, y_max = 0, 0
    z_min, z_max = 0, 0

    for x, y, z in structure:
        # print(x,y,z)
        if x < x_min:
            x_min = x
        elif x >= x_max:
            x_max = x
            x_max_node = (x, y, z)

        if y < y_min:
            y_min = y
        elif y > y_max:
            y_max = y

        if z < z_min:
            z_min = z
        elif z > z_max:
            z_max = z
    # print(x_min, x_max)
    # print(y_min, y_max)
    # print(z_min, z_max)

    # calc size of matrix
    x_size = x_max - x_min + 3
    y_size = y_max - y_min + 3
    z_size = z_max - z_min + 3

    # compute offsets
    x_offset = -1 * x_min + 1
    y_offset = -1 * y_min + 1
    z_offset = -1 * z_min + 1

    # reserve matrix
    matrix = np.zeros(shape=(x_size, y_size, z_size), dtype=object)

    node_queue_1 = queue.Queue()  # queue of Block Objects
    node_queue_2 = queue.Queue()  # queue of Block Objects

    air_queue = queue.Queue()  # queue of Air Objects

    to_evaluate_queue = queue.Queue()  # queue of tuples of coordinates

    # Add connection to parent node for each node. Runs in O(36n)=O(n) time
    for node in structure:
        for child in structure[node]:  # max of 6 children
            if node not in structure[child]:  # list so traverse; max of 6 connections.
                structure[child].append(node)

    # fill in the matrix with nodes & fill queues with nodes
    for x, y, z in structure:
        node = (x + x_offset, y + y_offset, z + z_offset)
        # print(node)
        tmp = Block(node, structure[(x,y,z)])
        matrix[node] = (BLOCK, tmp)
        node_queue_1.put(node)  # used to construct neighboring air search space
        node_queue_2.put(tmp)  # used to determine interior nodes
    # print(matrix)

    # Add air nodes to matrix + fill air_queue
    while not node_queue_1.empty():
        node = node_queue_1.get()
        x, y, z = node

        # add neighboring cells to air queue if they are empty and valid cells.
        # x neighbors
        for i in range(-1, 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    if x + i < 0 or x + i >= x_size:
                        continue
                    if y + j < 0 or y + j >= y_size:
                        continue
                    if z + k < 0 or z + k >= z_size:
                        continue
                    if matrix[x + i, y + j, z + k] != 0:
                        continue
                    # create new Air Object + add to queue and matrix
                    tmp_air = Air((x + i, y + j, z + k))
                    air_queue.put(tmp_air)
                    matrix[(x + i, y + j, z + k)] = (AIR, tmp_air)


    # determine which node is guarenteed to be an exterior node. Start here
    x, y, z = x_max_node
    node = (x + x_offset+1, y + y_offset, z + z_offset)
    # print("shape", matrix.shape)
    # print(x_max_node)
    # print("Priming: %s to be AIR_EXTERNAL"%str(node))
    tmp_air = matrix[node]
    tmp_air[1].type = Air.AIR_EXTERNAL
    to_evaluate_queue.put(tmp_air[1])

    continue_looping = not to_evaluate_queue.empty()
    # flood local air to determine which cells are external air
    while continue_looping:
        curr_cell = to_evaluate_queue.get()
        # print("evaluating: %s" %str(curr_cell.position))
        x, y, z = curr_cell.position

        # x neighbors
        for i in [-1, 1]:
            if x + i < 0 or x + i >= x_size:
                # print("out of scope")
                continue
            cell = matrix[x + i, y, z]
            if cell == 0 or cell[0] == BLOCK or cell[1].type == Air.AIR_EXTERNAL:
                # print(cell)
                # print("not unknown air.")
                continue
            cell[1].type = Air.AIR_EXTERNAL
            to_evaluate_queue.put(cell[1])

        # y neighbors
        for i in [-1, 1]:
            if y + i < 0 or y + i >= y_size:
                # print("out of scope")
                continue
            cell = matrix[x, y + i, z]
            if cell == 0 or cell[0] == BLOCK or cell[1].type == Air.AIR_EXTERNAL:
                # print(cell)
                # print("not unknown air.")
                continue

            cell[1].type = Air.AIR_EXTERNAL
            to_evaluate_queue.put(cell[1])

        # z neighbors
        for i in [-1, 1]:
            if z + i < 0 or z + i >= z_size:
                # print("out of scope")
                continue
            cell = matrix[x, y, z + i]
            if cell == 0 or cell[0] == BLOCK or cell[1].type == Air.AIR_EXTERNAL:
                # print(cell)
                # print("not unknown air.")
                continue
            cell[1].type = Air.AIR_EXTERNAL

            to_evaluate_queue.put(cell[1])
        continue_looping = not to_evaluate_queue.empty()

    node_neighbor_cnt_queue = queue.Queue()

    while not node_queue_2.empty():
        curr_cell = node_queue_2.get()
        # print("Considering:", curr_cell.position)
        x, y, z = curr_cell.position

        # x neighbors
        for i in [-1, 1]:
            if x + i < 0 or x + i >= x_size:
                continue
            cell = matrix[x + i, y, z]
            if debug:
                assert cell != 1, "Invalid cell type."
            if cell[0] == AIR and cell[1].type != Air.AIR_EXTERNAL:
                # print(cell[1].position, cell[1].type)
                curr_cell.connection_count += 1

        # y neighbors
        for i in [-1, 1]:
            if y + i < 0 or y + i >= y_size:
                continue
            cell = matrix[x, y + i, z]
            if debug:
                assert cell != 1, "Invalid cell type."
            if cell[0] == AIR and cell[1].type != Air.AIR_EXTERNAL:
                # print(cell[1].position, cell[1].type)
                curr_cell.connection_count += 1

        # z neighbors
        for i in [-1, 1]:
            if z + i < 0 or z + i >= x_size:
                continue
            cell = matrix[x, y, z + i]
            if debug:
                assert cell != 1, "Invalid cell type."
            if cell[0] == AIR and cell[1].type != Air.AIR_EXTERNAL:
                # print(cell[1].position, cell[1].type)
                curr_cell.connection_count += 1

        node_neighbor_cnt_queue.put(curr_cell.connection_count)

    neighbor_frequencies = np.zeros(shape=6)
    while not node_neighbor_cnt_queue.empty():
        neighbor_cnt = node_neighbor_cnt_queue.get()
        if neighbor_cnt == 0:
            continue
        neighbor_frequencies[neighbor_cnt - 1] += 1

    return neighbor_frequencies


def get_neighbor_counts(node_cnt):
    # generate aggregate
    structure = get_aggregate(node_cnt)

    # remove the origin. Each node has 1 parent except the origin which has none.
    origin = structure.pop((0, 0, 0))

    # calculate neighbor counts
    # each node has 1 parent with the exception of the origin which has 0 parents.
    neighbor_counts = [len(d) + 1 for d in
                       structure.values()]
    # add the origin back in
    neighbor_counts.append(len(origin))

    # if in debug, assert truth values
    if debug:
        if node_cnt > 1:
            assert (min(neighbor_counts) > 0), "Error with generating polycube"
        else:
            assert (min(neighbor_counts) >= 0), "Error with generating polycube"
        assert (max(neighbor_counts) < 7), "Error with generating polycube"

    # calculate neighbor frequencies
    neighbor_frequencies = np.zeros(shape=6)
    # print(neighbor_counts)
    for n in neighbor_counts:
        if n == 0:
            continue
        neighbor_frequencies[n - 1] += 1
    return neighbor_frequencies


def compute_work(node_cnt, iteration_number, ttl_iteration_cnt, seed_offset=0):
    """
    wrapper method for get_neighbor_counts which also sets the seed + keeps track of which iteration this is.
    :param node_cnt: number of nodes to include in our polynode
    :param iteration_number: which iteration we are running
    :param ttl_iteration_cnt: total number of iterations we plan to run. Needed for seeding calculations
    :param seed_offset: how to adjust the seed.
    :return: tuple of node_cnt, iteration_number, and the frequency of num neighbors
    """
    # TODO: Decide if this seeding is good or not.
    random.seed(seed_offset + iteration_number + node_cnt * ttl_iteration_cnt)
    neighbor_frequencies = compute_interior_nodes(node_cnt)
    neighbor_frequencies /= node_cnt
    return node_cnt, iteration_number, neighbor_frequencies


if __name__ == "__main__":
    # compute_interior_nodes(10)
    # exit(0)
    assert len(
        sys.argv) >= 3, "Please run as python NAME.py <Number of nodes in polycube>" \
                        "<number of iterations for Monte-Carlo> <optional: starting seed>"
    num_iterations = int(sys.argv[2])
    ttl_node_count = int(sys.argv[1])

    # num_iterations = 1
    # ttl_node_count = 4
    if len(sys.argv) == 4:
        global_seed_offset = int(sys.argv[3])
    else:
        global_seed_offset = 0

    np.set_printoptions(suppress=True, formatter={'float_kind': lambda x: '%5.2f' % x})

    data = np.zeros(shape=(num_iterations, 6))

    # used for parallel computation
    process_count = 12
    pool = Pool(processes=process_count)

    # compute the work
    iterations_list = range(num_iterations)
    res = [pool.apply_async(compute_work, args=(ttl_node_count, iter_num, num_iterations, global_seed_offset)) for iter_num in iterations_list]
    for n, r in enumerate(res):
        node_count, iter_num, ret = r.get()
        data[iter_num] = ret
        if n%1000 == 0:
            sys.stdout.write("/n%d/n"%(n//1000))
            sys.stdout.flush()
    pool.close()
    pool.join()
    
    import pickle
    with open("%d_cubes_%d_iterations.p"%(ttl_node_count, num_iterations), "wb") as f:
        pickle.dump(data, f)
