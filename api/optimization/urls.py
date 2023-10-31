from django.urls import path
from api.optimization import views

urlpatterns = [
    path("parameter-optimization/", views.parameter_optimization),
    path("media-optimization/", views.media_optimization),
]
