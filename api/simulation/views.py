from django.http import HttpResponse
from .utils import generate_plot, perform_simulation
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import matplotlib

matplotlib.use("Agg")


# Define the view that handles the simulation request


@api_view(["POST"])
def simulation(request):
    # Get the inputs from the request
    mu = request.data.get("mu")
    Y = request.data.get("Y")
    Yp = request.data.get("Yp")
    Ks = request.data.get("Ks")
    X0 = request.data.get("X0")
    S0 = request.data.get("S0")
    P0 = request.data.get("P0")
    step_size = request.data.get("step_size")
    tf = request.data.get("tf")

    # Check that all inputs are provided
    if any(val is None for val in [mu, Y, Yp, Ks, X0, S0, P0, step_size, tf]):
        return Response(
            {"error": "All inputs are required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Convert the inputs to floats
        mu = float(mu)
        Y = float(Y)
        Yp = float(Yp)
        Ks = float(Ks)
        X0 = float(X0)
        S0 = float(S0)
        P0 = float(P0)
        step_size = float(step_size)
        tf = float(tf)

        # Perform simulation
        sol = perform_simulation(X0, S0, P0, tf, step_size, mu, Y, Yp, Ks)

        # Generate the plot and save it to a file
        plot_filename = generate_plot(sol)

        # Get the simulation URL and return it in the response
        simulation_url = request.build_absolute_uri(
            f"/media/simulation/{plot_filename}"
        )

        response_data = {
            "simulation_url": simulation_url,
        }
        return Response(response_data)

    # In a try-except block, the as keyword is used to assign the caught exception to a variable.
    except (ValueError, TypeError) as e:
        # Return an error response if there's a problem with the inputs
        return Response(
            {"error": "Invalid input values"}, status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        # Return a generic error response for any other exceptions
        return Response(
            {"error": "An error occurred during the simulation"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
