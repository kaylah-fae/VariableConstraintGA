import json

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
from ProblemSpaces.LodeRunner.LodeRunnerProblemSpace import LodeRunnerProblemSpace
from ProblemSpaces.LogicPuzzles.LogicPuzzleSpace import LogicPuzzleSpace 
from ProblemSpaces.TravelingThief.TTP_ProblemSpace import TTPProblemSpace
from main import VCTriPop

""""
Run a single experiment and save the results 
Uncomment out sections of the code to test different problem spaces,users or algorithms 
"""

def test(Algorithm, problem_space_params, User, gen_params):
    problem_space, space_params = problem_space_params
    user = User(problem_space)
    algorithm = Algorithm(problem_space, number_generations=gen_params["number_generations"], population_size=gen_params["population_size"], max_memory=gen_params["max_memory"], cross_over_rate=space_params["cross_over"], mutation_rate=space_params["mutation"],user=user, update_interval=50)

    algorithm.run()
    # algorithm.save_measure_history("test_data")
    return algorithm.get_avg_qd_score()

def compare_results(min, max):
    best = {}
    for i in range(min, max):
        results = None
        with open(f"test_results_{i}.json", "r") as f:
            results = json.load(f)
        for pspace, pspace_results in results.items():
            if pspace not in best:
                best[pspace] = {}
            for persona, persona_results in pspace_results.items():
                if persona not in best[pspace]:
                    best[pspace][persona] = {}
                for alg, alg_result in persona_results.items():
                    if alg not in best[pspace][persona]:
                        best[pspace][persona][alg] = (-1, -1)
                    if alg_result > best[pspace][persona][alg][1]:
                        best[pspace][persona][alg] = (i, alg_result)
    with open(f"test_results_compare.json", "w") as f:
        json.dump(best, f)
        

if __name__ == "__main__":
    gen_params = {
        "number_generations": 150,
        "population_size": 100, 
        "max_memory": 500,
    }

    problem_space_paramss = [
        ("LodeRunner", (LodeRunnerProblemSpace(), {
            "cross_over": 0.5,
            "mutation": 0.05,
        })),
        ("TravelingSalesman", (TTPProblemSpace(), {
            "cross_over": 0.5,
            "mutation": 0.1,
        })),
        ("LogicPuzzles", (LogicPuzzleSpace(), {
            "cross_over": 0.7,
            "mutation": 0.5,
        }))
    ]
    Users = [
        ("Exploratory", ExploratoryUser), 
        ("Adaptive", AdaptiveUser), 
        ("TwoForOneBack", TwoForOneBackUser), 
        ("Strict", StrictUser)
    ]
    Algorithms = [
        # ("Shuffling", Shuffling), 
        # ("Filtering", Filtering), 
        # ("RandomRestarts", RandomRestarts), 
        # ("VariableConstraintMapElites", VariableConstraintMapElites), 
        ("VCTriPop", VCTriPop)
    ]

    results = {}
    for (pspace_name, problem_space_params) in problem_space_paramss:
        for (u_name, User) in Users:
            for (alg_name, Algorithm) in Algorithms:
                print(f"Running test for {pspace_name}:{u_name}:{alg_name}")
                qd_score = test(Algorithm, problem_space_params, User, gen_params)
                print(f"QD Score: {qd_score}")
                if pspace_name not in results:
                    results[pspace_name] = {}
                if u_name not in results[pspace_name]:
                    results[pspace_name][u_name] = {}
                results[pspace_name][u_name][alg_name] = qd_score

    with open(f"test_results_16.json", "w") as f:
        json.dump(results, f)

    # compare_results(1, 16)
    