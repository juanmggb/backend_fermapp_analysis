from django.urls import path
from api.optimization import views

urlpatterns = [
    path('optimization/', views.optimization)
]
