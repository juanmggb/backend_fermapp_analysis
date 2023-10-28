import numpy as np
from scipy.integrate import solve_ivp

from api.utilis.mathematical_models import monod_model, inhibition_model


# Genetic Algorithm parameters
algorithm_param = {
    "max_num_iteration": 50,
    "population_size": 50,
    "mutation_probability": 0.1,
    "elit_ratio": 0.01,
    "crossover_probability": 0.8,
    "parents_portion": 0.3,
    "crossover_type": "one_point",  # or "two_point", "uniform", "one_point"
    "max_iteration_without_improv": None,
}


# Function to perform the simulation
def perform_simulation(model, y0, t_eval, params):
    # Define the time span
    t_span = [0, t_eval[-1]]

    # Solve the differential equations
    mu, Yx, Yp, Ks, Ki = params

    if model == "monod":
        sol = solve_ivp(monod_model, t_span, y0, args=(mu, Yx, Yp, Ks), t_eval=t_eval)
    elif model == "inhibition":
        sol = solve_ivp(
            inhibition_model, t_span, y0, args=(mu, Yx, Yp, Ks, Ki), t_eval=t_eval
        )
    else:
        raise ValueError("Model must be either Monod or inhibition")
    return sol
