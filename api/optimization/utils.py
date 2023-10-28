import numpy as np
from geneticalgorithm import geneticalgorithm as ga
import plotly.graph_objs as go
from django.conf import settings
import os
import uuid
from api.utilis.numerical_methods import perform_simulation, algorithm_param


def mse(params, model, t_eval, x_values, s_values, p_values):
    sol = perform_simulation(
        model, [x_values[0], s_values[0], p_values[0]], t_eval, params
    )

    x_estimated, s_estimated, p_estimated = sol.y[0, :], sol.y[1, :], sol.y[2, :]

    error = (
        np.sum((x_estimated - x_values) ** 2)
        + np.sum((s_estimated - s_values) ** 2)
        + np.sum((p_estimated - p_values) ** 2)
    ) / len(s_values)
    return error


def estimate_parameters(model, t_eval, x_values, s_values, p_values):
    # Run genetic algorithm

    # Parameter bounds for mu, k, and Yx and Yp
    varbound = (
        np.array([[0, 3], [0, 1], [0, 20], [0, 400]])
        if (model == "monod")
        else np.array([[0, 3], [0, 1], [0, 20], [0, 400], [0, 1]])
    )

    model = ga(
        function=lambda params: mse(
            params, model, t_eval, x_values, s_values, p_values
        ),
        dimension=4 if (model == "monod") else 5,
        variable_type="real",
        variable_boundaries=varbound,
        algorithm_parameters={**algorithm_param, "n_jobs": -1},  # Use all CPU cores
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

    mu, Yx, Yp, Ks = best_params
    sol = perform_simulation(
        x_values[0], s_values[0], p_values[0], t_values, mu, Yx, Yp, Ks
    )

    x_estimated, s_estimated, p_estimated = sol.y[0, :], sol.y[1, :], sol.y[2, :]

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
