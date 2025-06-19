from django.shortcuts import render, redirect 
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from django.contrib.auth import login, logout
from.models import Company,Client
from django.http import JsonResponse

# Create your views here.
def register_view(request):
    if request.method == "POST": 
        form = UserCreationForm(request.POST) 
        if form.is_valid(): 
            login(request, form.save())
            return redirect("posts:create")
    else:
        form = UserCreationForm()
    return render(request, "clients/register.html", { "form": form })

def login_view(request): 
    if request.method == "POST": 
        form = AuthenticationForm(data=request.POST)
        if form.is_valid(): 
            login(request, form.get_user())
            return redirect("posts:create")
    else: 
        form = AuthenticationForm()
    return render(request, "clients/login.html", { "form": form })

def logout_view(request):
    if request.method == "POST": 
        logout(request) 
        return redirect("clients:login")
 # Optional if you're making GET requests
def get_clients_for_company(request, company_name):
    try:
        company = Company.objects.get(name=company_name)
        clients = list(Client.objects.filter(company=company).values_list('name', flat=True))
        return JsonResponse({'clients': clients})
    except Company.DoesNotExist:
        return JsonResponse({'error': 'Company not found'}, status=404)
def chatbot_page(request):
   #  Automatically get company from ?company=Headrun
    company_name = request.GET.get("company", "")
    
    # TEMP: Choose a default client manually for testing
    if company_name == "Headrun":
        client_name = "Client1 Headrun"
    elif company_name == "Tech_Service":
        client_name = "Client1_TechService"
    else:
        client_name = ""

    return render(request, "index.html", {
        "company_name": company_name,
        "client_name": client_name,
    })