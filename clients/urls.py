from django.contrib import admin
from django.urls import path
from . import views
from .views import chatbot_page,get_clients_for_company

app_name = 'clients'

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('register/', views.register_view, name="register"),
    path('logout/', views.logout_view, name="logout"),
    path('api/clients/<str:company_name>/', get_clients_for_company),
    path('chatbot/', chatbot_page, name='chatbot_page'),
]

