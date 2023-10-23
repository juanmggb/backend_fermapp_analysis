import numpy as np
from scipy.integrate import odeint
from geneticalgorithm import geneticalgorithm as ga
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from django.conf import settings
import os
import uuid


def monod_model(y, t, mu, Y, Yp, Ks):
    X, S, P = y
    # X, S = y
    dXdt = mu * X * S / (Ks + S)
    dSdt = -Y * dXdt
    dPdt = Yp * dXdt
    return [dXdt, dSdt, dPdt]


# Numerical integration of the ODE system


def integrate_odes(params, t_values, x0, s0, p0):
    mu, Y, Yp, Ks = params
    initial_conditions = [x0, s0, p0]
    solution = odeint(monod_model, initial_conditions, t_values, args=(mu, Y, Yp, Ks))
    return solution[:, 0], solution[:, 1], solution[:, 2]  # Extract x, s and p


# Mean squared error (MSE) for fitness evaluation


def mse(params, t_values, x_values, s_values, p_values):
    x_estimated, s_estimated, p_estimated = integrate_odes(
        params, t_values, x_values[0], s_values[0], p_values[0]
    )
    error = (
        np.sum((x_estimated - x_values) ** 2)
        + np.sum((s_estimated - s_values) ** 2)
        + np.sum((p_estimated - p_values) ** 2)
    ) / len(s_values)
    return error


def estimate_parameters(t_values, x_values, s_values, p_values):
    # Genetic Algorithm parameters
    algorithm_param = {
        "max_num_iteration": 100,
        "population_size": 100,
        "mutation_probability": 0.1,
        "elit_ratio": 0.01,
        "crossover_probability": 0.5,
        "parents_portion": 0.3,
        "crossover_type": "uniform",
        "max_iteration_without_improv": None,
    }

    # Parameter bounds for mu, k, and Y
    varbound = np.array([[0, 3], [0, 1], [0, 20], [0, 20]])

    # Run genetic algorithm
    model = ga(
        function=lambda params: mse(params, t_values, x_values, s_values, p_values),
        dimension=4,
        variable_type="real",
        variable_boundaries=varbound,
        algorithm_parameters=algorithm_param,
    )
    model.run()

    # Get best parameters
    best_params = model.best_variable
    return best_params


def generate_plot(best_params, t_values, x_values, s_values, p_values):
    # Delete any existing images in the optimization directory
    optimization_dir = os.path.join(settings.BASE_DIR, "media", "optimization")
    for filename in os.listdir(optimization_dir):
        if filename.endswith(".html"):
            os.remove(os.path.join(optimization_dir, filename))

    x_estimated, s_estimated, p_estimated = integrate_odes(
        best_params, t_values, x_values[0], s_values[0], p_values[0]
    )

    # Create a plot with all the variables
    fig = go.Figure()

    # Add experimental data and optimized model for X
    fig.add_trace(
        go.Scatter(x=t_values, y=x_values, mode="markers", marker=dict(color="red"))
    )
    fig.add_trace(
        go.Scatter(x=t_values, y=x_estimated, mode="lines", line=dict(color="red"))
    )

    # Add experimental data and optimized model for S
    fig.add_trace(
        go.Scatter(x=t_values, y=s_values, mode="markers", marker=dict(color="blue"))
    )
    fig.add_trace(
        go.Scatter(x=t_values, y=s_estimated, mode="lines", line=dict(color="blue"))
    )

    # Add experimental data and optimized model for P
    fig.add_trace(
        go.Scatter(x=t_values, y=p_values, mode="markers", marker=dict(color="green"))
    )
    fig.add_trace(
        go.Scatter(x=t_values, y=p_estimated, mode="lines", line=dict(color="green"))
    )

    # Update x-axis label
    fig.update_xaxes(title_text="Time")

    # Update y-axis label
    fig.update_yaxes(title_text="Concentration")

    # Update layout
    fig.update_layout(
        title="Experimental Data and Optimized Monod Model",
        showlegend=False,
        height=450,  # Set the height in pixels
        # width=800,   # Set the width in pixels
        # Set margin and padding to 0 on all sides
        margin=dict(l=0, r=0, b=0, pad=0),
    )

    # Generate a random string for the plot filename
    plot_filename = str(uuid.uuid4()) + ".html"

    # Save the plot with the random filename
    plot_path = os.path.join(settings.BASE_DIR, "media", "optimization", plot_filename)
    fig.write_html(plot_path)

    return plot_filename
