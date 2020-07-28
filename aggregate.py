import numpy as np
import random
import math
import constants as c

from individual import INDIVIDUAL
global sequenceNumber
sequenceNumber = 0

def getSeqNumber():
    global sequenceNumber
    sequenceNumber += 1
    return sequenceNumber

class AGGREGATE(INDIVIDUAL):
    def __init__(self, numCubes=None):

        self.id = getSeqNumber()
        
        self.tree = {(0, 0, 0): []}
        self.positions = {}
        
        self.scores = []
        self.fitness = 0
        self.age = 0

        if numCubes == None:
            numCubes = np.random.choice(range(5, c.NUMCUBES))
        
        self.generate_random(numCubes=numCubes)

        if c.DEBUG:
            print("Tree built")

    def __str__(self):
        return "Fit: %.3f, Age: %d" % (self.fitness, self.age)

    def generate_random(self, numCubes=None):
        '''
        Takes numcubes as an integer argument for the size of the desired polycube
        Will randomly generate a polycube of desired size
        '''
        if numCubes is None:
            numCubes = np.random.choice(range(5, c.NUMCUBES))

        while numCubes > len(self.tree):
            
            self.add_cube()
        self.update_subtree_sizes()
    
    def increment_age(self):
        self.age += 1

    def mutate(self, *args, **kwargs):
        '''
        Choose between adding a new node or deleting a subtree. If adding, call add_cube.
        If deleting, find the length of the subtree, ensure the root of the subtree is not the polycube's root node, then delete every node in the subtree.
        '''
        self.id = getSeqNumber()
        mu = len(self.tree)/c.MAXCUBES
        # print(mu)
        
        if np.random.random() < mu and len(self.tree) > 5: #mu is mutation hyperparameter
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
            
            if c.DEBUG:
                print(self.tree)
                print("Removing subtree rooted at", nodeToDeleteCoordinates)
            
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

        #if child's coordinates are already occupied, or go outside the bounding box, do that again
        while child in self.tree.keys() or len(self.tree[parent]) >= 5:
            
            direction = np.random.choice([-1, 1])
            coord = np.random.choice([0, 1, 2])

            index = np.random.choice(len(keys))
            parent = keys[index]

            child = list(parent)
            child[coord] += direction
            child = tuple(child)

        #Point parent to child, add child to the structure
        self.tree[parent].append(child)
        self.tree[child] = []
        
        if c.DEBUG:
            print("Cube added at", child)
        
    def evaluate(self, sim, elmt, idNum=[0,0,0], debug=False):
        '''
        calls send_to_sim and
        calculate_displacement
        '''
        if debug:
            print(type(elmt))
        try:
            self.send_to_sim(sim, elmt)
            if debug:
                print(idNum, "sent to sim")
            sim.start(idNum=idNum)
            sim.wait_to_finish()
            if debug:
                print(idNum, "sim complete")
            fit = self.calculate_displacement(sim)
            return fit
        except Exception as e:
            print(idNum, e)
            if debug:
                print(e)
                raise e
            return -1
        
    def reset(self):
        '''
        reset fitness list
        '''
        
        self.scores = []

    def send_to_sim(self, sim, controller):
        '''
        Construct a body using the provided body tree. Call the controller's build function to add joints, neurons, and synapses.
        '''
        
        self.body = {}
        
        #establish what the lowest z-coordinate in the tree is so the robot can be shifted up accordingly
        lowest = 0
        for coord in self.tree:
            if coord[2] < lowest:
                lowest = coord[2]

        #Iterate over each index of the tree, call send_cube to build a block there. Store that cube mapped to its real-space coordinates (modified z)=
        i=0
        rgb = (0,0,0)
        for coord in self.tree:
            box, z = self.send_cube(sim, coord, lowest, rgb)
            newCoord = coord[:2] + (z,)
            self.body[newCoord] = box
            i += 1
        
        if c.DEBUG:
            print(self.body)
        
        #Send the aggregate's information to the controller for construction of the network.
        controller.build_controllers(sim, self.tree, self.body, lowest)
    
    
    def send_cube(self, sim, coord, lowest, rgb=(0,0,0)):
        '''
        Sends cube to the simulator at the specified coordinate, 
            with the specified controller's properties
        '''
        if rgb == (0,0,0):
            colors = np.random.random(size=3)
        else:
            colors = rgb
        
        x = format(coord[0]*c.SCALE, '.2f')
        y = format(coord[1]*c.SCALE, '.2f')
        z = format((coord[2] - lowest + .5)*c.SCALE, '.2f')
        
        box = sim.send_box( position = (x, y, z),
                 sides=(c.SCALE, c.SCALE, c.SCALE),
                 color=(colors[0], colors[1], colors[2]),
                 collision_group = "body")
        
        self.positions[coord] = [sim.send_position_x_sensor(body_id = box),
                                 sim.send_position_y_sensor(body_id = box)]
        
        return box, float(format(coord[2] - lowest + .5, '.2f'))

    
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
        if c.DEBUG:
            print("Pruning node", root)
        
        todel = []
        
        for child in self.tree[root]:
            todel.append(child)

        for child in todel:
            self.remove_subtree(child)

        for node in self.tree:
            if root in self.tree[node]:
                self.tree[node].remove(root)

        self.tree.pop(root)

    def calculate_displacement(self, sim):
        '''
        Get the displacement of the cube which displaced the least
        '''
        
        deltas = []
        
        if c.DEBUG:
            print(self.positions.keys())
        
        for coord in self.positions:
            p = self.positions[coord]
            sensorID = p[0]
            dx = sim.get_sensor_data(sensor_id = sensorID)
            dx = dx[-1]
            dx -= coord[0]
            dy = sim.get_sensor_data(sensor_id = p[1])[-1] - coord[1]
            d = dx**2 + dy**2
            deltas.append(d**0.5)
        
        return min(deltas)
