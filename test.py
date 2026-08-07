

from GeneticAlgorithmInterface import VariableConstraintGA
from Algorithms.VCMapElites import VariableConstraintMapElites
from Algorithms.Filtering import Filtering
from Algorithms.Shuffling import Shuffling
from Algorithms.RandomRestarts import RandomRestarts 
from Personas.Exploratory import ExploratoryUser
from Personas.DoNothing import DoNothing 
from Personas.Strict import StrictUser 
from Personas.Adaptive import AdaptiveUser
from Personas.TwoForwardOneBack import TwoForOneBackUser
from ProblemSpaces.LodeRunner.LodeRunnerProblemSpace import LodRunnerProblemSpace
from ProblemSpaces.LogicPuzzles.LogicPuzzleSpace import LogicPuzzleSpace 
from ProblemSpaces.TravelingThief.TTP_ProblemSpace import TTPProblemSpace

""""
Run a single experiment and save the results 
Uncomment out sections of the code to test different problem spaces,users or algorithms 
"""


number_generation = 150 
population_size = 100 
max_memory = 500 


problem_space = LodeRunnerProblemSpace()
cross_over = 0.5 
mutation = 0.05



"""problem_space = LogicPuzzleSpace()
cross_over = 0.7 
mutation = 0.5""" 


"""problem_space = TTPProblemSpace()
cross_over = 0.5 
mutation = 0.1""" 

user = ExploratoryUser(problem_space)
#user = AdaptiveUser(problem_space)
#user = TwoForOneBackUser(problem_space)
#user = StrictUser(problem_space)


algorithm = Shuffling(problem_space, number_generations=number_generation, population_size=population_size, max_memory=max_memory, cross_over_rate=cross_over, mutation_rate=mutation,user=user, update_interval=50)

#algorithm = Filtering(problem_space, number_generations=number_generation, population_size=population_size, max_memory=max_memory, cross_over_rate=cross_over, mutation_rate=mutation,user=user, update_interval=50)
#algorithm = RandomRestarts(problem_space, number_generations=number_generation, population_size=population_size, max_memory=max_memory, cross_over_rate=cross_over, mutation_rate=mutation,user=user, update_interval=50)
#algorithm = VariableConstraintMapElites(problem_space, number_generations=number_generation, population_size=population_size, max_memory=max_memory, cross_over_rate=cross_over, mutation_rate=mutation,user=user, update_interval=50)


algorithm.run()

print("Average QD score: {}".format(algorithm.get_avg_qd_score()))
algorithm.save_measure_history("test_data")