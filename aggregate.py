import numpy as np
import random
import math
import constants as c

class AGGREGATE:
    def __init__(self, numCubes=None):
        
        self.tree = {}
        self.tree[(0,0,0)] = []
        self.body = {}
        self.positions = {}
        
        self.scores = []
        self.fitness = 0

        if numCubes == None:
            numCubes = np.random.choice(range(1, c.NUMCUBES))
        
        self.generate_random(numCubes)
        self.update_subtree_sizes()
        print("Tree built")

    def generate_random(self, numCubes):
        '''
        Takes numcubes as an integer argument for the size of the desired polycube
        Will randomly generate a polycube of desired size
        '''

        while numCubes > len(self.tree):
            
            self.add_cube()
    
    
    def mutate(self):
        '''
        Choose between adding a new node or deleting a subtree. If adding, call add_cube.
        If deleting, find the length of the subtree, ensure the root of the subtree is not the polycube's root node, then delete every node in the subtree.
        '''
        
        if np.random.random() < c.MU: #mu is mutation hyperparameter
            N = len(self.tree)
            cList = [] #list of coordinates
            pList = np.zeros(N) #list of probabilities
            for v, (node, children) in enumerate(self.tree.items()):
                k = self.subtreeLength[node]
                probDelete = (N-k)/N 
                cList.append(node)
                pList[v] = probDelete
            pList /= np.sum(pList)
            i = np.random.choice(range(N), p=pList)
            nodeToDeleteCoordinates = cList[i]
            #TODO: delete subtree rooted at node chosen
            self.remove_subtree(nodeToDeleteCoordinates)
            
        else:
            
            self.add_cube()

        self.update_subtree_sizes()
        
    def add_cube(self):
        '''
        adds a cube to the tree
        '''
        #np.random.seed(0)

        #select whether to move + or -
        direction = np.random.choice([-1, 1])

        #coordinate to move in: 0->x, 1->y, 2->z
        coord = np.random.choice([0, 1, 2])

        #pick a random cube from the structure
        keys = list(self.tree.keys())
        index = np.random.choice(len(keys))
        parent = keys[index]

        #convert parent to a list, change the selected coordinate, and convert back to tuple
        child = list(parent)
        child[coord] += direction
        child = tuple(child)

        #if child's coordinates are already occupied, do that again
        while child in self.tree.keys():

            index = np.random.choice(len(keys))
            parent = keys[index]

            child = list(parent)
            child[coord] += direction
            child = tuple(child)

        #Point parent to child, add child to the structure
        self.tree[parent].append(child)
        self.tree[child] = []
        
        print("Cube added at", child)
        
    def evaluate(self, sim, elmt):
        '''
        calls send_to_sim and
            calculate_displacement
        '''
        self.send_to_sim(sim, elmt)
        sim.start()
        sim.wait_to_finish()
        return self.calculate_displacement(sim)
        
    def reset(self):
        '''
        reset fitness list
        '''
        
        self.scores = []
    
    def send_to_sim(self, sim, element):
        '''
        Construct a body using the provided body tree. Call the element's build function to add joints, neurons, and synapses.
        '''
        
        #establish what the lowest z-coordinate in the tree is so the robot can be shifted up accordingly
        lowest = 0
        for coord in self.tree:
            if coord[2] < lowest:
                lowest = coord[2]

        if len(self.body) == 0:
            #Iterate over each index of the tree, call send_cube to build a block there. Store that cube mapped to its real-space coordinates (modified z)
            for coord in self.tree:
                box, z = self.send_cube(sim, coord, lowest)
                newCoord = coord[:2] + (z,)
                self.body[newCoord] = box
    
        else:
            for coord in self.tree:
                self.send_cube(sim, coord, lowest)
        #Using the element's specifications, build the joints, neurons, and synapses
        for parent in self.tree:
            #modify parent coordinates to match real-space
            rparent = parent[:2] + (parent[2] - lowest + .5,)
            for child in self.tree[parent]:
                #modify child coordinates to match real-space
                rchild = child[:2]+ (child[2] - lowest + .5,)
                element.send_element(sim, self.body[rchild], self.body[rparent], [rchild, rparent])
    
    
    def send_cube(self, sim, coord, lowest):
        '''
        Sends cube to the simulator at the specified coordinate, 
            with the specified element's properties
        '''
        
        colors = np.random.random(size=3)
        
        box = sim.send_box(position=(coord[0]*c.SCALE, coord[1]*c.SCALE, (coord[2] - lowest + .5)*c.SCALE),
                 sides=(c.SCALE, c.SCALE, c.SCALE),
                 color=(colors[0], colors[1], colors[2]))
        
        self.positions[coord] = [sim.send_position_x_sensor(body_id = box),
                                 sim.send_position_y_sensor(body_id = box),
                                 sim.send_position_z_sensor(body_id = box)]
        
        return box, coord[2] - lowest + .5

    
    def check_connections(self):
        '''
        prints distance matrix
        if '1' is in each row/column, the tree is valid
        '''
        
        cubes = list(self.tree.keys())
        N = len(cubes)
        dMatrix = np.zeros((N, N), dtype='int')
        
        for i in range(N):
            for j in range(N):
                x1, y1, z1 = cubes[i]
                x2, y2, z2 = cubes[j]
                dist = (x1-x2) + (y1-y2) + (z1-z2)
                dMatrix[i, j] = dist
        
        dMatrix = np.abs(dMatrix)
        cond = True
        for i in range(N):
            cond = cond and np.isin(1, dMatrix[i])
        
        print('Valid Tree:', cond)
        
    def update_subtree_sizes(self):
        '''
        Creates a dict mapping each node in tree with the size of its subtree. Leaves have a value of 1.
        '''
        
        self.subtreeLength = {}
        #print(self.tree)
        self.get_subtree_length((0,0,0))
        #print(self.subtreeLength)

    def get_subtree_length(self, coord):
        '''
        Returns the length of the subtree located at the specified node by recursively summing the sizes of its children's subtrees
        '''
        if self.tree[coord] == []:
            self.subtreeLength[coord] = 1
            return 1

        else:
            sum = 1
            for child in self.tree[coord]:
                sum += self.get_subtree_length(child)
            self.subtreeLength[coord] = sum
            return self.subtreeLength[coord]

    def remove_subtree(self, root):
        '''
        Remove the specified node (root) and the subtree it is the root of. Also remove reference to the root from its parent
            '''
        print("Pruning node", root)
        
        todel = []
        
        for child in self.tree[root]:
            todel.append(child)

        for child in todel:
            self.remove_subtree(child)

        for node in self.tree:
            if root in self.tree[node]:
                self.tree[node].remove(root)
    
        self.positions.pop(root)
        self.tree.pop(root)

    def calculate_displacement(self, sim):
        '''
        Get the average displacement using the positional sensors of each node
        '''
        delta = 0
        
        for coord in self.positions:
            p = self.positions[coord]
            dx = sim.get_sensor_data(sensor_id = p[0])[-1] - coord[0]
            dy = sim.get_sensor_data(sensor_id = p[1])[-1] - coord[1]
            dz = sim.get_sensor_data(sensor_id = p[2])[-1] - coord[2]
            d = dx**2 + dy**2 + dz**2
            delta += d**0.5

        return delta/len(self.positions)
