from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='authentication/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('activate/<user_id>/<token>/', views.VerificationView.as_view(), name='activate'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('confirm_password_reset/<user_id>/<token>/', views.password_reset_view, name='confirm_password_reset'),
]
