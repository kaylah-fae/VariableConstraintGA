

from ProblemSpaceInterface import ProblemSpace
import threading
import sys
import math 
import json
import pickle 

class MyTimeoutError(Exception):
    # exception for our timeouts
    pass
def timeout_func(func, args=(), kwargs={}, timeout=30, default=None):
    """This function will spawn a thread and run the given function
    using the args, kwargs and return the given default value if the
    timeout is exceeded.
    http://stackoverflow.com/questions/492519/timeout-on-a-python-function-call
    """
    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = default
            self.exc_info = (None, None, None)
        def run(self):
            self.result = func(*args, **kwargs)
            # try:
            #     self.result = func(*args, **kwargs)
            # except Exception as err:
            #     self.exc_info = sys.exc_info()
        def suicide(self):
            raise MyTimeoutError(
                "{0} timeout (taking more than {1} sec)".format(func.__name__, timeout)
            )
    it = InterruptableThread()
    it.start()
    it.join(timeout)
    if it.exc_info[0] is not None:
        a, b, c = it.exc_info
        raise Exception(a, b, c)  # communicate that to caller
    if it.is_alive():
        it.suicide()
        raise RuntimeError
    else:
        return it.result

class Measures:
    """
    Capture values throughout 
    the evolution process 
    """
    def __init__(self):
        self.populations = []
        self.diversity = [] 
        self.constraint_size = [] 
        self.adaptability_div = [] 
        self.robustness_div = [] 
        self.advisability_div = [] 

        self.adaptability_qd = [] 
        self.robustness_qd = [] 
        self.advisability_qd = [] 
        self.quality = [] 
        self.qd_score = [] 
        self.gen_is_valid = [] 
    
    def add_adaptability(self, old_pop, new_pop):
        old_fitnesses = [element[0][0] for element in old_pop if len(element) > 0]
        new_fitnesses = [element[0][0] for element in new_pop if len(element) > 0]
        old_num_bins = len([bi for bi in old_pop if len(bi) > 0])
        old_div = old_num_bins / len(old_pop)


        old_qd = sum(old_fitnesses)
        new_qd = sum(new_fitnesses)

        new_num_bins = len([bi for bi in new_pop if len(bi) > 0])
        new_div = new_num_bins / len(new_pop)

        div_score = (new_div - old_div) / old_div if old_div != 0 else 0 
        qd_score = (new_qd - old_qd) / old_qd if old_qd != 0 else 0 

        self.adaptability_div.append(float(div_score))
        self.adaptability_qd.append(float(qd_score)) 
    
    def add_robustness(self, old_pop, new_pop):
        old_fitnesses = [element[0][0] for element in old_pop if len(element) > 0]
        new_fitnesses = [element[0][0] for element in new_pop if len(element) > 0]
        old_num_bins = len([bi for bi in old_pop if len(bi) > 0])
        old_div = old_num_bins / len(old_pop)


        old_qd = sum(old_fitnesses)
        new_qd = sum(new_fitnesses)

        new_num_bins = len([bi for bi in new_pop if len(bi) > 0])
        new_div = new_num_bins / len(new_pop)

        div_score = (new_div - old_div) / old_div if old_div != 0 else 0 
        qd_score = (new_qd - old_qd) / old_qd if old_qd != 0 else 0 

        self.robustness_div.append(float(div_score))
        self.robustness_qd.append(float(qd_score))

    
    def add_gen(self, population, constraint_size, made_change, valid_gen):
        self.populations.append(population)
        self.gen_is_valid.append(valid_gen)
        

        fitnesses = [element[0][0] for element in population if len(element) > 0]

        self.qd_score.append(float(sum(fitnesses))) 
        #qd_score = sum(fitnesses)

        if len(fitnesses) > 0:
            self.quality.append(float(sum(fitnesses) / len(fitnesses)))
        else:
            self.quality.append(-1)
        num_bins = len([bi for bi in population if len(bi) > 0])
        new_div = num_bins / len(population)
        
        self.diversity.append(float(new_div))
        self.constraint_size.append(float(constraint_size)) 


class User:
    """
    This is an interface for a procedural 
    persona that reacts to evolution over arbitrary 
    problem spaces 
    """
    def __init__(self, problem_space: ProblemSpace):
        self.problem_space = problem_space
    
    def update_constraints(self, cur_constraints, feasible):
        return [], False 

class VariableConstraintGA:
    """
    Interface for a variable constraint 
    genetic algorithm 
    """
    def __init__(self, problem_space: ProblemSpace, number_generations, population_size, max_memory, cross_over_rate, mutation_rate, user, update_interval):
        self.problem_space = problem_space
        self.number_generations = number_generations 
        self.population_size = population_size 
        self.max_memory = max_memory 
        self.cross_over_rate = cross_over_rate
        self.mutation_rate = mutation_rate
        self.user = user 
        self.made_change = False 
        self.followed_rec = False 
        self.update_interval = update_interval 
    
    def dummy_pop(self):
        pop = [] 
        for i in range(self.problem_space.get_num_bins()):
            pop.append([])
        return pop 
    
    def reset(self):
        """
        Reset environment for next run 

        Should NOT be over-written 
        """
        self.variable_constraints = self.problem_space.get_initial_variable_constraints()
        self.measure_history = Measures()

    def set_up(self):
        """
        Run at the start of each run 

        Can be over-written by child 
        """
        pass 
    
    def record_gen(self, population,  new_constraints, made_change, valid_gen):
        """
        Record outcomes from a single generation 

        Should NOT be over-written 
        """
        self.measure_history.add_gen(population, len(new_constraints),made_change, valid_gen)

    def run_one_generation(self, made_change): 
        """
        Complete a single generation of the algorithm

        Returns the population of valid (by both constant and variable constraints)
        individuals that are shorted in bins. Each individual should be stored as a tuple
        with the first value being the fitness and the second being the object 

        EX: [[(fit1, obj1)], [], [(fit2, obj2), (fit3, obj3)], .... ] 
        
        NEEDS to be over-written 
        """
        return [] * self.problem_space.get_num_bins() 

    def is_valid(self, ind):
        for con in self.variable_constraints + self.problem_space.get_constant_constraints():
            if not con.apply(ind):
                return False 
        return True 

    def is_pop_valid(self, pop):
        for bin in pop:
            for fit, ind in bin:
                if not self.is_valid(ind):
                    return False 
                if abs(fit - self.problem_space.fitness(ind)) > 0.000000001: 
                    return False 
        return True 

    def get_avg_qd_score(self):
        qd_scores = self.measure_history.qd_score 

        return sum(qd_scores) / len(qd_scores)

    def save_measure_history(self, filename, folder = ""):
        json_dict = {"qd-scores": self.measure_history.qd_score, "valid_gens": self.measure_history.gen_is_valid, "delta_add_qd": self.measure_history.adaptability_qd, "delta_remove_qd": self.measure_history.robustness_qd}

        json_str = json.dumps(json_dict)
        json_file = open(folder +  filename + ".json", "w")
        json_file.write(json_str)
        json_file.close()

        pickle_file = open(folder +  filename + ".pickle", "wb")
        pickle.dump(self.measure_history, pickle_file)
        pickle_file.close()

    
    def run(self):
        """
        Run the full evolution cycle 

        Should NOT be over-written 
        """
        self.reset()
        self.set_up()
        constraints_add_this_cycle = False 
        constraints_removed = False 
        old_pop = [[]]
        
        for gen in range(self.number_generations):
            valid_gen = True 
            #population = self.run_one_generation(self.made_change)
            try:
                population = timeout_func(self.run_one_generation, kwargs={"made_change":self.made_change}, timeout=30)
            except MyTimeoutError as ex:
                valid_gen = False 
                population = self.dummy_pop()
            
            if not self.is_pop_valid(population):
                valid_gen = False 
                population = self.dummy_pop()

            # if interval is met, ask user to update 
            if gen % self.update_interval == 0:
                # end of old cycle 
                if constraints_add_this_cycle:
                    self.measure_history.add_adaptability(old_pop, population)
                elif constraints_removed:
                    self.measure_history.add_robustness(old_pop, population)

                variable_constraints , made_change = self.user.update_constraints(self.variable_constraints[:], population)

                # beginning of new cycle 
                old_pop = population 
                constraints_add_this_cycle = len(self.variable_constraints) < len(variable_constraints)
                constraints_removed = len(self.variable_constraints) > len(variable_constraints)
            else:
                made_change = False 
            self.record_gen(population, self.variable_constraints, self.made_change, valid_gen)
            self.made_change = made_change
            self.variable_constraints = variable_constraints
        
        return population