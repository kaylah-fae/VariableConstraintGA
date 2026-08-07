from ProblemSpaceInterface import ProblemSpace, Constraint 
import random 

# Feasibility constraints 

class PlayerConstraint(Constraint):
    def __init__(self, env):
        self.env = env

    def apply(self, ind):
        info = ind.get_info()

        return info["player"] == 1 

def new_player_class(value): 
    class PlayerConstraint2(Constraint):
        def __init__(self, env):
            self.env = env

        def apply(self, ind):
            info = ind.get_info()

            return info["player"] <  value
    
    return PlayerConstraint2 
    

class ExplorationConstraint(Constraint):
    def __init__(self, env):
        self.env = env

    def apply(self, ind):
        info = ind.get_info()
        exp = ((info["exploration"] > 0).astype(int)).sum()
        goal = 0.2  * info["width"] * info["height"]
        
        return exp >= goal 

def new_explor_con(value):
    class ExplorationConstraint(Constraint):
        def __init__(self, env):
            self.env = env

        def apply(self, ind):
            info = ind.get_info()
            exp = ((info["exploration"] > 0).astype(int)).sum()
            goal = value  * info["width"] * info["height"]
            
            return exp >= goal 
    return ExplorationConstraint


class CollectedGoldConstraint(Constraint):
    def __init__(self, env):
        self.env = env

    def apply(self, ind):
        info = ind.get_info()
        
        return info["collected_gold"] == info["gold"]
    
def new_gold_class(value):
    class CollectedGoldConstraint(Constraint):
        def __init__(self, env):
            self.env = env

        def apply(self, ind):
            info = ind.get_info()
            
            return info["collected_gold"] >= value * info["gold"]
    return CollectedGoldConstraint 

class SurfaceConstraint(Constraint): 
    def __init__(self, env):
        self.env = env

    def apply(self, ind):
        info = ind.get_info()

        if info["tiles"] == 0:
            return True

        used_tiles = info["used_tiles"] / info["tiles"]
        
        return used_tiles >= 0.75

def new_surf_con(value):
    class SurfaceConstraint(Constraint): 
        def __init__(self, env):
            self.env = env

        def apply(self, ind):
            info = ind.get_info()

            if info["tiles"] == 0:
                return True

            used_tiles = info["used_tiles"] / info["tiles"]
            
            return used_tiles >= value
    return SurfaceConstraint

player_constraints = [new_player_class(v) for v in [2,3,5,10,20,30,40]]
explor_cons = [new_explor_con(v) for v in [0.01, 0.05, 0.1, 0.15]]
gold_cons = [new_gold_class(v) for v in [ 0.3, 0.5, 0.8, 0.7, 0.9]]
tile_conts = [new_surf_con(v) for v in [0.2, 0.4, 0.5, 0.7]]
STATIC_CONS = [PlayerConstraint, ExplorationConstraint, SurfaceConstraint] + player_constraints + explor_cons + gold_cons + tile_conts

# Variable Constraints 
class VariableConstraint(Constraint): 
    def __init__(self,env, type, value, min=True):
        self.env = env
        self.type = type
        self.value = value 
        self.min = min 

    def apply(self, ind):
        info = ind.get_info()

        value = info[self.type]

        if self.min:
            return value >= self.value
        else:
            return value <= self.value 
        

def is_contradictory(constraints):
    var_const = [con for con in constraints if isinstance(con, VariableConstraint)]
    for con in var_const:
        same_type = [con2 for con2 in var_const if con2.type == con.type]

        con_dir = [con3 for con3 in same_type if con3.min == con.min]

        if len(con_dir) > 0:
            return True 

        values = [con3.value for con3 in same_type]
        if con.min:
            if min(values) < con.value:
                return True 
        else:
            if max(values) > con.value:
                return True 
    
    return False 
            
var_con_dict = {"gold":(0, 50), "rope":(0, 140), "ladder":(0,140)}

def get_random_constraint(env):
    t = random.choice(list(var_con_dict.keys()))
    value = random.randint(var_con_dict[t][0], var_con_dict[t][1])
    is_m = random.choice([True, False])

    return VariableConstraint(env, t, value, is_m)

def get_random_in(env, ind):
    info = ind.get_info()

    t = random.choice(list(var_con_dict.keys()))
    value = random.randint(var_con_dict[t][0], var_con_dict[t][1]) 

    is_m = value < info[t]

    return VariableConstraint(env, t, value, is_m)