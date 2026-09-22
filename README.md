# VCTriPop
VCTriPop is a variation of VC-MAP-Elites that maintains three populations:
* Feasible (all constraints satisfied)
* Infeasible (static constraints not satisfied)
* Con Feasible (all static constraints satisfied; not all variable constraints satisfied)

To utilize memory, the infeasible population is permitted to grow until the feasible and constant constraint feasible populations fill their target memory allowance.

A full description of this algorithm is given in VCTriPop_Submission.pdf

# The QDA-VC Competition


Please first read through CompetitionDetails.pdf, which expains what is required for submission along information about the existing codebase. 

The easiest way to create a submission is to fork this repository, and modify main.py with your code. 

The test.py file in the main folder shows you how to run experiments in this environment. 




# Environment  
The information below describes the environment generally 


## Problem Spaces 

All problem spaces should be children classes of the ProblemSpaceInterface in the file at the base root level of this code base. The problem space should overwrite all existing functions in this parent class. The existing problems spaces are given in the problem spaces folder. 

### Creating a new problem space 
To create a new problem space add a new folder to the ProblemSpaces Folder, and create a class within it that implements that ProblemSpace class at the root of this repository. 

Override the following functions in this class: 

* generate_random_individual(self)

    This function returns a random individual in whatever representation you choose. 

* mutate(self, individual, mutation_rate) 

    This function should return a new individual that is mutated from the given individual. The mutation rate is a value between 0 and 1 that gives the degree of mutation. 

* cross_over(self, ind1, ind2)

    This function needs to take in two individuals and return two randomized combinations of the them 

* fitness(self, ind)

    This returns the quality of an individual as a maximization function 

* get_num_bins(self)

    Number of bins to place individuals in. This value is usually around 10 

* place_in_bin(self, ind)

    Given an individual return the bin index they would be placed in, given some behavioral metric 
    
* get_constant_constraints(self)

    Return a list of constraints all individuals must obey. This should stay the same every time it is called. The list of constraints should all be children of the Constraint class (in same file as ProblemSpace class), which has one function, Apply, which given an individual returns true if that condition is satisfied. 

* get_initial_variable_constraints(self)
  
    If there are any variable constraints that exist at the start of evolution, add them here. This can return an empty list. 
    
* is_constradictory(self, constraints)

    Given a list of static or variable constraints, return true if there is a contradiction between constraints. This does not have to check if an individual does exist that satisfies all constraints. 

* get_rand_constraint(self)

    Return a random variable constraint in this problem space. 

* get_ind_constraint(self, ind)

    Return a variable constraint that an individual satisfies. Can return a always true constraint if none would apply.  
    
## Existing problem spaces 

There are currently three implemented problem spaces in this repository. 

### Logic Grid Puzzles 
This is a problem space for generating logic grid puzzles. Individuals are represented at list of hints, which are mutated by randomly adding or removing hints and crossed over by randomly distributing hints between children. Fitness is determined by number of hints, with hint size being subtracted from 15 (to make it a maximization problem). Static constraints ensure that the puzzle is valid and solvable. Variable constraints force puzzles to contain a certain hint, although they can be reversed (e.g. the mushrooms are chopped vs the chopped ingredient is mushrooms). The problem space is initialized with a puzzle about making soup, but can be replaced with a different set up. 

### Lode Runner 
Taking from the PCG Benchmark, this problem space is about making levels from the game Lode Runner. Levels are presented as a arrays of number (each number representing a tile), mutated by interpolating between a individual and a randomized level, and cross-over interpolates between the two parents. Fitness is determined by how close tile distribution is to the original distribution in Lode Runner levels. Static constraints ensure playability, for example having only one player and being able to reach most of the level. Variable constraints can set minium and maximums of different components: the number of ropes, the number of ladders, and the number of enemies. 
    

### Traveling Thief Problem 
This problem space implements the traveling thief optimization problem, where a thief has to travel to all cities and collect items. They are rewarded for the total value of the items they took, but are penalized for travel time weighted by the proportional weight of the sack at each step.  Individuals are represented as two lists, the first giving the sequence of cities visited and the second determining which items are taken (encoded in binary). The items are mutated and cross-over like with bit strings. The city sequence is mutated by swapping pairs of cities, and cross-over by a middle section (determined by two random points) from one parents and replace the cities in the same order they appear in the second parent. The static constraint is that the total weight of the items cannot be more the sack capacity, and variable constraints determine that a specific item must be taken. 


## Algorithms 

Algorithms in this space seek to produce quality solutions, that span the diversity function, constrained by both the static and variable constraints. All algorithms must implement the GeneticAlgorithm interface provided at the root folder of this repository. Measures for all algorithms are automatically captured across evolution using the Measures class that is returned at the end of evolution. All existing algorithms are located in the Algorithms folder. 

### Measures 
The quality of algorithms are determined by a variety of measures. 

* QD-score: the sum of the fitness of the top performing individual from each bin (if an individual exists in that bin)
• Diversity: percentage of bins that have at least one individual
• Quality: the average fitness score of the top performing individual from each bin
• Δ-add: the average change in QD-score before a constraint is added and after a user interval is completed with the added constraint, normalized by the starting diversity
• Δ-remove: the average change in QD-score before a constraint is removed and after a user interval is completed with the removed constraint, normalized by the starting diversity

### Creating a new algorithm 
In a new subfolder of the algorithms folder, create a child class of VariableConstraintGA class. ONLY overwrite the following functions. 

* set_up(self)

    Use this function to conduct any set up required before starting evolution. 

*  run_one_generation(self, cons_changed)
  
  This functions preforms one generation of evolution. The value "cons_changed" will be true if the variable constraints (self.variable_constraints) have been changed since the last generation.  The problem space will be given in self.problem_space, the total number of  individuals you can add that generation is given in self.population_size, and the total number of individuals that can be saved at any given time is given in self.max_memory. This function should return a list of lists of size self.problem_space.get_num_bins() where each list contains only individuals that satisfies all static and variable constraints. Individuals should be placed in the bin returned by self.problem_space.place_in_bin(ind).  Each individual in a bin should be add as a tuple where the first value is the fitness (self.problem_space.fitness(ind)) and the second value is the individual itself. Individuals should also be sorted within each bin by fitness in descending order (so the the highest fitness is at index 0). 
    

The run function will run a full cycle of evolution, recording measures after each generations, and prompting the user (the procedural persona) to update constraints every interval. 


### Provided Algorithms 

#### Random Restarts. 
This algorithm maintains two populations. The infeasible population contains individuals that violate at least one static or variable constraint. Infeasible individuals are selected for reproduction based on how many constraints they violate. The feasible population satisfies all constraints and is organized into bins based on the diversity function. Each bin maintains the top 𝑁 (determined by the maximum memory capacity) individuals sorted by fitness. If there is no room left in a bin, an individual is only added if it is at least as good as the worst individual in the bin (and the worst individual is removed). Feasible individuals are selected by first randomly choosing a bin (of those with at least one individual in it), and then selected within a bin based on fitness. When the variable constraint list is changed, the population (both feasible and infeasible) is dumped and re-initialized with random individuals.

#### Shuffling. 
This algorithms maintains two populations, like in random restarts. However, when the variable constraint list is changed, the old population is not dumped. Instead the existing population is re-sorted into the infeasible population and feasible bins.


#### Filtering Algorithm. 
This algorithm similarly maintains two populations. However, an individual is placed in the infeasible population only if it violates the static constraints, and variable constraints are ignored. Any individual that violates a variable constraint is filtered out (but remains in the population) just before being returned.

#### Variable Constraint MAP-Elites (VC-MAP-Elites). 
This algorithm takes inspiration from the MAP-Elites algorithm and applies it to the landscape of variable constraints.

This algorithm keeps track of two populations: the static infeasible population, and the static feasible population. 

The static infeasible population contains individuals that violate one or more static constraints (𝑆). Individuals in the static infeasible population are stored in an array and are selected based on the number of static constraints they do satisfy. The static feasible population contains individuals that satisfy all static constraints (𝑆), but may violate one or more variable constraints (𝑉 ). This population is represented as a two dimensional grid. The x-axis stores individuals that vary based on the diversity function (𝐷). The y-axis, with height of ℎ (by default ℎ = 4), stores individuals based on the percentage of variable constraints they satisfy. The 0th row contains individuals that satisfy all variable constraints. The remaining ℎ − 1 rows are assigned intervals of percent of variable constraints satisfied — with larger row numbers having more variable constraint violations. When selecting an individual, the row is selected first, with probability inversely proportional to the row number (large row numbers are selected less often).

VC-MAP-Elites uses a dynamic memory system. The total memory capacity is first allocated between feasible and infeasible individuals (with a default 50% − 50% allocation). The feasible memory is spread between the 0th row of the static feasible grid, and the infeasible memory is spread between the static infeasible population
and the remaining ℎ −1 rows of the static feasible grid. Feasible individuals are placed in the grid until the memory capacity is exceeded, and the individual with the lowest fitness is removed (regardless of diversity bin). Similarly, infeasible individuals are added to the static infeasible or static feasible populations until the memory capacity is exceeded. If there are individuals in the static infeasible population, they are removed first in the order of individuals that violate the most constraints. When the static infeasible population is empty, individuals are removed from the static feasible grid with the individuals with lowest fitness being removed first.


## Personas 
The procedural personas act to simulate human users. 

### Adding a new persona 
To create a new persona add a file to the persona folder and create a child class of User. Overwrite the 'update_constraints(self, cur_constraints, feasible, recommendation = None)' function. This should return a modified list of variable constraint with either: one constraint from the original list (cur_constraints) removed, one constraint added, no changes made from cur_constraints. The feasible value will provide the post recent feasible population, divided into diversity bins and with each individual represented a tuple with the first value being fitness and the second being the individual itself. Recommendations are ignored in the current implementation. 

### Existing personas 
The current benchmark has 4 personas. 

* Exploratory Persona: this persona randomly adds or removes a constraint at each generation every cycle. This is
meant to simulate users or situations with no clear pattern.

• Strict Persona: this persona randomly adds a non-contradictory constraint at each cycle. If a non-contradictory constraint
cannot be found it does nothing. This is meant to test algorithms in the most difficult situations.

• Adaptable Persona: this persona adds a random constraint that is already satisfied in this current population. This is meant to simulate users who look for patterns or valuable individuals in the existing population, along with testing for how well the algorithms can exploit existing solutions.

• Cycle Persona: this algorithm adds a random constraint for the first two cycles, and then removes the first constraint added. It then switches between adding a new constraint and removing the oldest constraint (such that there are between 1 and 2 constraints). This provides a constantly changing environment, while still giving the algorithm 2-3 cycles to learn a constraint.

## Existing Data 
The experiments that were ran are located in the Tests folder, with the tests for each problem space being in the LodeRunner, LogicPuzzles, and TTP folders. Each folder has a results.txt file that gives a summary of the results, while the sub-folders provides the Measures object generated from each trial. Note that due to a bug in JsonPickle, the LodeRunner files were corrupted, and the generated levels cannot currently be recovered. However, the trial files store the main outcomes from each trial. The full_trial files contain the corrupted data, in case it can be recovered at a later time.  

This files were created using the RunExperiments-{problemspace}.py files, and analyzed using the results.py file and the graph.py file. 