import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
import uuid
from django.conf import settings
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Define kinetic model


def monod_model(t, y, mu, Y, Yp, Ks):
    X, S, P = y

    dXdt = mu * X * S / (Ks + S)
    dSdt = - Y * dXdt
    dPdt = Yp * dXdt
    return [dXdt, dSdt, dPdt]


# Function to perform the simulation
def perform_simulation(X0, S0, P0, tf, step_size, mu, Y, Yp, Ks):

    # Define the initial conditions and the time span
    y0 = [X0, S0, P0]
    t_span = [0, tf]

    # Create an array of time points with the specified step size
    t_eval = np.arange(t_span[0], t_span[1] + step_size, step_size)

    # Solve the differential equations
    sol = solve_ivp(monod_model, t_span, y0,
                    args=(mu, Y, Yp, Ks), t_eval=t_eval)

    return sol


def generate_plot(sol):

    # Delete any existing images in the simulation directory
    simulation_dir = os.path.join(settings.BASE_DIR, 'media', 'simulation')
    for filename in os.listdir(simulation_dir):
        if filename.endswith('.html'):
            os.remove(os.path.join(simulation_dir, filename))
    # Create a subplot with 3 rows and shared x-axis
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        subplot_titles=("Biomass", "Substrate", "Product"), vertical_spacing=0.05)

    # Add the traces for Biomass, Substrate, and Product
    fig.add_trace(go.Scatter(
        x=sol.t, y=sol.y[0], mode='lines', name='Biomass'), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=sol.t, y=sol.y[1], mode='lines', name='Substrate'), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=sol.t, y=sol.y[2], mode='lines', name='Product'), row=3, col=1)

    # Update x-axis labels
    fig.update_xaxes(title_text="Time", row=3, col=1)

    # Update y-axis labels
    fig.update_yaxes(title_text="Concentration", row=1, col=1)
    fig.update_yaxes(title_text="Concentration", row=2, col=1)
    fig.update_yaxes(title_text="Concentration", row=3, col=1)

    # Update layout
    fig.update_layout(
        title='Concentration vs Time',
        height=1200,  # Set the height in pixels
        showlegend=False,
        # width=800,   # Set the width in pixels
        # legend=dict(
        #     x=0.5,
        #     y=-0.15,
        #     xanchor='center',
        #     yanchor='top',
        #     orientation='h'
        # )
        margin=dict(l=0, r=0, b=0, pad=0)
    )

    # Generate a random string for the plot filename
    plot_filename = str(uuid.uuid4()) + '.html'

    # Save the plot with the random filename
    plot_path = os.path.join(settings.BASE_DIR, 'media',
                             'simulation', plot_filename)
    fig.write_html(plot_path)

    return plot_filename
