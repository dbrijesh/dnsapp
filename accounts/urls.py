from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('logout/complete/', views.logout_complete, name='logout_complete'),
    path('profile/', views.profile_view, name='profile'),
    path('auth/callback', views.auth_callback, name='auth_callback'),
]
