import sys
import os 
from pathlib import Path
import math 
from copy import deepcopy
import numpy as np 
 


sys.path.append(str(Path.cwd().parent.parent)) 
sys.path.append(str(Path.cwd().parent)) 
sys.path.append(str(Path.cwd())) 
from ProblemSpaceInterface import ProblemSpace, Constraint
try: 
    from pcg_benchmark.spaces import contentSwap 
    import pcg_benchmark  
    from contraints import STATIC_CONS, get_random_constraint, get_random_in, is_contradictory
except: 
    from ProblemSpaces.LodeRunner.pcg_benchmark.spaces import contentSwap
    from ProblemSpaces.LodeRunner.contraints import STATIC_CONS, get_random_constraint, get_random_in, is_contradictory
    from  ProblemSpaces.LodeRunner import pcg_benchmark

def get_range_reward(value, min_value, plat_low, plat_high = None, max_value = None):
    if max_value == None:
        max_value = plat_high
    if plat_high == None:
        plat_high = plat_low
        max_value = plat_low
    if value >= plat_low and value <= plat_high:
        return 1.0
    if value <= min_value or value >= max_value:
        return 0.0
    if value < plat_low:
        return np.clip((value - min_value) / (plat_low - min_value + 0.00000001), 0.0, 1.0)
    if value > plat_high:
        return np.clip((max_value - value) / (max_value - plat_high + 0.00000001), 0.0, 1.0)

def fitness(info):
        decoration = 0

        decoration = 0.9 * (info["walking"] + info["hanging"] + info["climbing"]) + 0.1 * info["falling"]
        decoration = get_range_reward(decoration, 0, 0.75, 1)
        decoration += get_range_reward(info["islands"], 0, 0, 0.1 * info["width"] * info["height"],  info["width"] * info["height"] / 2)
        decoration /= 2

        return decoration 

class LodeRunnerInd:
    def __init__(self, env, grid):
        self.grid = grid 
        self.env = env 
        self.info = None 
    def get_info(self):
        if self.info is None:
            self.info = self.env.info(self.grid)
        
        return self.info


class LodRunnerProblemSpace(ProblemSpace): 
    """
    To add a problem space to this benchmark, 
    create a class that inherits this class as a 
    parent 

    You will need to over-write all methods 
    in this class 
    """
    def __init__(self): 
        self.env = pcg_benchmark.make("loderunner-v0") 

    def generate_random_individual(self):
        '''
        Return a random in individual in the problem space 
        for initialization 
        '''
        return LodeRunnerInd(self.env, self.env.content_space.sample() ) 

    def mutate(self, individual, mutation_rate):
        '''
        Take in an individual and return a mutation

        Amount of mutation can vary between 0 and 1 from mutation rate 
        e.g. each bit has a X% chance of flipping 

        Should NOT modify starting individual 
        '''
   
        child = contentSwap(individual.grid, self.env.content_space.sample(), mutation_rate, -1)
 
        return LodeRunnerInd(self.env, child ) 

    def cross_over(self, ind1, ind2):
        """
        Take in two individuals and return a random combination of the two

        Should NOT modify the starting individuals  

        """
        child1 = LodeRunnerInd(self.env, contentSwap(ind1.grid, ind2.grid, 0.5, -1)) 
        child2 = LodeRunnerInd(self.env, contentSwap(ind1.grid, ind2.grid, 0.5, -1)) 
 
        return child1, child2 
    
    def fitness(self, ind): 
        """
        returns how close the percentage of items matches 
        with the percentages of the original games 
        """
        return fitness(ind.get_info()) 
    
    def get_num_bins(self):
        """
        Return the number of bins of the diversity measure 
        """
        return 10 
    
    def place_in_bin(self, ind):
        """
        Return an index between 0 and 9
        based on how many enemies are in the level with
        each bin having a range of 2
        (e.g bin 0: 0-1, bin 1: 2-3, ... bin 9: 18+)
        """
        num_enemies = ind.get_info()["enemy"]
        bi = min(math.floor(num_enemies / 2), 9) 
        return bi 

    def get_constant_constraints(self):
        """
        Return a list of constraints that 
        all individuals must obey

        These constraints should be ATOMIC rather then general 
        """
        static = [] 
        for con in STATIC_CONS:
            static.append(con(self.env))

        return static
    
    def get_initial_variable_constraints(self):
        """
        Return a list of initial variable constraints 
        """
        return [] 
    

    def is_contradictory(self, constraints):
        """
        Given a list of constraints 
        return true if they are inherently 
        contradictory 

        This does NOT need to ensure 
        that an individual could exist with 
        all listed constraints 
        """
        return is_contradictory(constraints)  
    
    def get_rand_constraint(self):
        """
        Return a random variable constraint from the 
        problem space 
        """
        return get_random_constraint(self.env)
    
    def get_ind_constraint(self, ind):
        """
        Given an individual, return a random 
        constraint that is is obeys 
        """
        return get_random_in(self.env, ind)
    

    