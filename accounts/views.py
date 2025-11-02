from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import AdminRegistrationForm, CustomLoginForm

def landing_page(request):
    return render(request, 'accounts/landing.html')

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.user_type == 'admin':
                return redirect('admin_dashboard')
            return redirect('patient_dashboard')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def admin_register(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'admin'
            user.save()
            messages.success(request, 'Account created!')
            return redirect('login')
    else:
        form = AdminRegistrationForm()
    return render(request, 'accounts/admin_register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('landing')

