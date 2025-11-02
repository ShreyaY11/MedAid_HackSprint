from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/admin/', views.admin_register, name='admin_register'),
    path('logout/', views.logout_view, name='logout'),
]
