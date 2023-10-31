import numpy as np
from scipy.integrate import solve_ivp

from api.utilis.mathematical_models import monod_model, inhibition_model


# Function to perform the simulation
def perform_simulation(model, y0, t_eval, params):
    # Define the time span
    t_span = [0, t_eval[-1]]

    # Solve the differential equations

    if model == "monod":
        mu, Yx, Yp, Ks = params
        sol = solve_ivp(monod_model, t_span, y0, args=(mu, Yx, Yp, Ks), t_eval=t_eval)
    elif model == "inhibition":
        mu, Yx, Yp, Ks, Ki = params
        sol = solve_ivp(
            inhibition_model, t_span, y0, args=(mu, Yx, Yp, Ks, Ki), t_eval=t_eval
        )
    else:
        raise ValueError("Model must be either Monod or inhibition")
    return sol
