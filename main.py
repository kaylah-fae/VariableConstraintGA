from math import floor
import random
import numpy.random as npr

from GeneticAlgorithmInterface import VariableConstraintGA 

def roulette_selection(population):
    small = min([c[0] for c in population]) # make all the fitnesses positive 
    if small < 0:
        add = -small 
    else:
        add = 0 
    m = sum([c[0] + add for c in population])
    if m == 0:
        selection_probs = [1 / len(population) for _ in population]
    else:
        selection_probs = [(c[0] + add) / m for c in population]
    return population[npr.choice(len(population), p=selection_probs)]

def decide(rate):
    return random.random() < rate

class YouAlgorithm(VariableConstraintGA):

    # self.population_size # the max number of individuals you can generate per generation 
    # self.max_memory # the max number of individuals you can store at any time (always > than pop size)
    # self.mutation_rate # the rate of mutation to give mutation function 
    # self.cross_over_rate # the ratio of time you should preform the cross over function 
    # self.variable_constraints # the current list of variable constraints 

    # ind1 = self.problem_space.generate_random_individual() # randomly generate a new individual 
    # ind2 = self.problem_space.generate_random_individual() 

    # fit = self.problem_space.fitness(ind1) # quality value of individual 
    # ind3 = self.problem_space.mutate(ind1, self.mutation_rate) # perform mutation 
    # child1, child2 = self.problem_space.cross_over(ind1, ind2) # perform cross over 
    # self.problem_space.get_num_bins() # number of diversity bins in problem space 
    # self.problem_space.place_in_bin(ind1) # get the index of bin ind should be placed in 
    
    # # you can check if individuals satisfy a constant through the apply function 
    # cons[0].apply(ind1) # returns true if constraint is satisfied 
    

    def set_up(self): 
        """
        Insert all your set up code here 

        You can generation an initial population 
        of individuals. However you may only 
        generate self.population_size in this method, and 
        can only store up to self.max_memory individuals  
        in total   
        
        We provide the useful functions 
        and values available for you to use here 
        """

        
        self.constant_constraints = self.problem_space.get_constant_constraints() # list of static constraints 
        self.max_feasible_rate = 0.5
        self.max_con_feasible_rate = 0.3

        self.select_feasible_weight = 2
        self.select_con_feasible_weight = 1
        self.var_constraint_weight = 0.5

        self._calc_max_nums()

        self.feasibles = []
        self.con_feasibles = []
        self.infeasibles = [] 

        self.num_feasible = 0 
        self.num_con_feasible = 0
        self.num_infeasible = 0  
        
        for _ in range(self.problem_space.get_num_bins()):
            self.feasibles.append([])
            self.con_feasibles.append([])
        
        # generate initial population 
        for _ in range(self.population_size):
            ind = self.problem_space.generate_random_individual()
            self.place_in_bin(ind)

    def run_one_generation(self, made_change): 
        """
        Complete a single generation of the algorithm

        Returns the population of valid (by both constant and variable constraints)
        individuals that are shorted in bins. Each individual should be stored as a tuple
        with the first value being the fitness and the second being the object 

        EX: [[(fit1, obj1)], [], [(fit2, obj2), (fit3, obj3)], .... ] 
        
        """
        # if the constraints have been change, reshuffle population 
        if made_change:
            self.re_shuffle()

        for _ in range(floor(self.population_size / 2)):
            # select 
            child1 = self._select()[1]
            child2 = self._select()[1]

            # cross over 
            if decide(self.cross_over_rate):
                child1, child2 = self.problem_space.cross_over(child1, child2)
            
            # mutate 
            child1 = self.problem_space.mutate(child1, self.mutation_rate)
            child2 = self.problem_space.mutate(child2, self.mutation_rate)

            # update population 
            self.place_in_bin(child1)
            self.place_in_bin(child2)
        
        return self.feasibles

    def _calc_max_nums(self):
        self.max_num_feasible = floor(self.max_memory * self.max_feasible)
        self.max_num_con_feasible = floor(self.max_memory * self.max_con_feasible_rate)
    
        self.max_feasible_inds_per_bin = floor(self.max_num_feasible / self.problem_space.get_num_bins()) 
        self.max_con_feasible_inds_per_bin = floor(self.max_num_con_feasible / self.problem_space.get_num_bins())

    def place_in_bin(self, ind):
        con_violated = self._con_constraints_violated(ind)
        var_violated = self._var_constraints_violated(ind)
                    
        if con_violated == 0:
            b = self.problem_space.place_in_bin(ind)  
            bins = self.con_feasibles
            max_inds_per_bin = self.max_con_feasible_inds_per_bin

            if var_violated == 0:
                # Belongs in the feasible population
                bins = self.feasibles
                max_inds_per_bin = self.max_feasible_inds_per_bin
                self.num_feasible += 1
            else:
                # Belongs in the con feasible population
                self.num_con_feasible += 1

            constraints_sat = 1 - (var_violated/len(self.variable_constraints))
            fitness = constraints_sat * self.var_constraint_weight + self.problem_space.fitness(ind) * 1 - self.var_constraint_weight
            bins[b].append((fitness, ind))
            self._sort_pop(bins[b])
            while len(bins[b]) > max_inds_per_bin:
                bins[b].pop(-1)
                if var_violated == 0:
                    self.num_feasible -= 1
                else:
                    self.num_con_feasible -= 1

        else:
            # Belongs in the infeasible population
            constraints_sat = 1 - (con_violated/len(self.constant_constraints))
            self.infeasibles.append((constraints_sat, ind))
            self._sort_pop(self.infeasibles)
            self.num_infeasible += 1
            while self._total_pop() > self.max_memory:
                self.infeasibles.pop(-1)

    def _constraints_violated(self, ind, constraints):
        constraints_violated = 0 
        for con in constraints:
            if not con.apply(ind):
                constraints_violated += 1
        return constraints_violated

    def _con_constraints_violated(self, ind):
        return self._constraints_violated(ind, self.constant_constraints)

    def _var_constraints_violated(self, ind):
        return self._constraints_violated(ind, self.variable_constraints)

    def _sort_pop(self, pop):
        pop.sort(key=lambda i: i[0], reverse=True)

    def _total_pop(self):
        return self.num_feasible + self.num_con_feasible + self.num_infeasible

    def _select_bin(self, bins):
        # randomly select a bin with children 
        bi = random.choice(range(len(bins)))
        while len(bins[bi]) == 0:
            bi = random.choice(range(len(bins))) 
        
        # select from bin using roulette selection 
        return roulette_selection(bins[bi])

    def _select(self):
        # select from feasible 
        if decide((self.num_feasible * self.select_feasible_weight) / self._total_pop()):
            return self._select_bin(self.feasibles)
        # select from con feasible
        elif decide((self.num_con_feasible * self.select_con_feasible_weight) / self.num_con_feasible + self.num_infeasible):
            return self._select_bin(self.con_feasibles)
        # select from infeasible 
        else:
            return roulette_selection(self.infeasible_pop)