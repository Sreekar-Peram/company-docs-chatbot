from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 




def home(request):
    """ 
     1) if not registered then we will have a button that will redirect to registration
     2) if registered and logged in then we will move on to clients redirect --> posts_list

    """
    return render(request, 'home.html')
