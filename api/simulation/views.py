from api.utilis.numerical_methods import perform_simulation
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import matplotlib
import numpy as np

matplotlib.use("Agg")


# Define the view that handles the simulation request


@api_view(["POST"])
def simulation(request):
    # Get the inputs from the request
    model = request.data.get("model")
    mu = request.data.get("mu")
    Y = request.data.get("Y")
    Yp = request.data.get("Yp")
    Ks = request.data.get("Ks")
    Ki = request.data.get("Ki")
    X0 = request.data.get("X0")
    S0 = request.data.get("S0")
    P0 = request.data.get("P0")
    step_size = request.data.get("step_size")
    tf = request.data.get("tf")

    # Check that all inputs are provided
    if any(val is None for val in [mu, Y, Yp, Ks, Ki, X0, S0, P0, step_size, tf]):
        return Response(
            {"error": "All inputs are required"}, status=status.HTTP_400_BAD_REQUEST
        )

    # try:
    # Convert the inputs to floats
    mu = float(mu)
    Y = float(Y)
    Yp = float(Yp)
    Ks = float(Ks)
    Ki = float(Ki)
    X0 = float(X0)
    S0 = float(S0)
    P0 = float(P0)
    step_size = float(step_size)
    tf = float(tf)

    # Perform simulation

    # Create an array of time points with the specified step size
    t_eval = np.arange(0, tf + step_size, step_size)
    sol = perform_simulation(model, [X0, S0, P0], t_eval, (mu, Y, Yp, Ks, Ki))

    # Serialize the simulation results
    time_data = sol.t.tolist()
    x_data = sol.y[0].tolist()
    s_data = sol.y[1].tolist()
    p_data = sol.y[2].tolist()

    response_data = {"time": time_data, "x": x_data, "s": s_data, "p": p_data}

    return Response(response_data)

    # In a try-except block, the as keyword is used to assign the caught exception to a variable.
    # except (ValueError, TypeError) as e:
    #     # Return an error response if there's a problem with the inputs
    #     return Response(
    #         {"error": "Invalid input values"}, status=status.HTTP_400_BAD_REQUEST
    #     )

    # except Exception as e:
    #     # Return a generic error response for any other exceptions
    #     return Response(
    #         {"error": "An error occurred during the simulation"},
    #         status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #     )
