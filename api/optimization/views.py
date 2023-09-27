from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from .utils import estimate_parameters, generate_plot


@api_view(['POST'])
def optimization(request):

    # Get experimental data from response

    t_values = request.data.get('t')
    x_values = request.data.get('x')
    s_values = request.data.get('s')
    p_values = request.data.get('p')

    print('t_values', t_values)
    print('x_values', x_values)
    print('s_values', s_values)
    print('p_values', p_values)

    if any(val is None for val in [t_values, x_values, s_values, p_values]):
        return Response({'error': 'All inputs are required'}, status=status.HTTP_400_BAD_REQUEST)

    best_params = estimate_parameters(t_values, x_values, s_values, p_values)

    plot_filename = generate_plot(best_params,
                                  t_values, x_values, s_values, p_values)

    # Get the optimization URL and return it in the response
    optimization_url = request.build_absolute_uri(
        f'/media/optimization/{plot_filename}')

    response_data = {'optimization_url': optimization_url,
                     "best_params": best_params,
                     }
    return Response(response_data)
