from django.contrib import admin
from django.urls import path
from . import views
from .views import upload_view

app_name = 'posts'

urlpatterns = [
    path('posts_list/', views.posts_list_view, name="list"),
    path('posts_create/', views.posts_create_view, name="create"),
    path('<slug:slug>/', views.posts_view, name="view"), 
    path('upload/', upload_view, name='upload'),  
    
         
]
