import numpy as np
from geneticalgorithm import geneticalgorithm as ga
from api.utilis.numerical_methods import perform_simulation


def get_ordered_params(params, fixed_params):
    dimension = len(params)
    # This array will be used to perform the simulation. It is important order the kinetic parameters for the simulation
    ordered_params = np.zeros(dimension + len(fixed_params))
    d = 0

    for i in range(len(ordered_params)):
        # If the position i corresponds to a fixed parameter add that value to ordered_params
        if fixed_params.get(i) is not None:
            ordered_params[i] = fixed_params[i]
        # If the position i corresponds to a optimization parameter add that value to ordered_parms
        else:
            ordered_params[i] = params[d]
            d += 1
    return ordered_params


def mse(params, kinetic_model, t_eval, x_values, s_values, p_values, fixed_params):
    # Get ordered params
    ordered_params = get_ordered_params(params, fixed_params)

    # Perform simulation
    sol = perform_simulation(
        kinetic_model,
        [x_values[0], s_values[0], p_values[0]],
        t_eval,
        ordered_params,  # always pass the same ordered kinetic parameters mu, Yx, Yp, Ks (and Ki when model is inhibition model)
    )

    # Extract simulation results
    x_estimated, s_estimated, p_estimated = sol.y[0, :], sol.y[1, :], sol.y[2, :]

    # Calculate mean squared error
    error = (
        np.sum((x_estimated - x_values) ** 2)
        + np.sum((s_estimated - s_values) ** 2)
        + np.sum((p_estimated - p_values) ** 2)
    ) / len(s_values)

    return error


def estimate_parameters(kinetic_data, t_eval, x_values, s_values, p_values, GA_params):
    # Initialize necessary variables
    dimension = 0
    varbound = []
    fixed_params = {}
    opt_params = {}
    index = 0

    # Extract kinetic model and parameters
    kinetic_model = kinetic_data.pop("model")
    kinetic_params = kinetic_data

    # Genetic Algorithm parameters
    algorithm_param = {
        "max_num_iteration": GA_params.get("max_num_iteration", 50),
        "population_size": GA_params.get("population_size", 50),
        "mutation_probability": GA_params.get("mutation_probability", 0.1),
        "elit_ratio": GA_params.get("elit_ratio", 0.01),
        "crossover_probability": GA_params.get("crossover_probability", 0.8),
        "parents_portion": 0.3,
        "crossover_type": GA_params.get(
            "parents_portion", "one_point"
        ),  # or "two_point", "uniform", "one_point"
        "max_iteration_without_improv": GA_params.get(
            "max_iteration_without_improv", None
        ),
    }

    # Identify which parameters need to be optimized and which are fixed
    for kinetic_param, value in kinetic_params.items():
        if value["optimize"]:
            # Establish search range
            varbound.append([value["min"], value["max"]])
            # Add one dimenssion to the optimization problem
            dimension += 1

            # Store kinetic param with an empty value
            opt_params[kinetic_param] = None
        else:
            # Establish the value and position of the fixed parameter
            fixed_params[index] = value["fixed"]

        # Increase index
        index += 1

    # Convert varbound to numpy array
    varbound = np.array(varbound)

    # Run the genetic algorithm
    model = ga(
        function=lambda params: mse(
            params,
            kinetic_model,
            t_eval,
            x_values,
            s_values,
            p_values,
            fixed_params,
        ),
        dimension=dimension,
        variable_type="real",
        variable_boundaries=varbound,
        algorithm_parameters={
            **algorithm_param,
            "n_jobs": -1,
        },  # Use all available CPU cores
    )
    model.run()

    # Retrieve the best parameters from the optimization
    best_params = model.best_variable
    error = model.best_function

    index = 0
    for key, value in opt_params.items():
        opt_params[key] = best_params[index]
        index += 1

    return fixed_params, best_params, error, opt_params
