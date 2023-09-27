from django.urls import path
from . import views

# CURRENT TOKEN
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('', views.user_list, name='user-list'),
    path('register/', views.register_user, name='register-user'),
    path('update-user/', views.update_user, name='update-user'),
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
