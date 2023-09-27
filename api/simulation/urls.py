from django.urls import path
from api.simulation.views import simulation

urlpatterns = [
    path('simulation/', simulation),
]
