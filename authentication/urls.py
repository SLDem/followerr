from django.urls import path, include
from django.contrib.auth import views as auth_views
from django_email_verification import urls as mail_urls

from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('email/', include(mail_urls)),
]
