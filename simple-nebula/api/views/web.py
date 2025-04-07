from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from ..models import Organization, Network, SecurityGroup

def login_view(request):
    """Handle login requests and render the login page."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'api/login.html', {'error': 'Invalid email or password.'})
    
    return render(request, 'api/login.html')

@login_required
def dashboard_view(request):
    """Render the dashboard page for authenticated users."""
    # Get counts for display
    user = request.user
    user_orgs = Organization.objects.filter(membership__user=user)
    
    context = {
        'user': user,
        'organizations_count': user_orgs.count(),
        'networks_count': Network.objects.filter(organization__in=user_orgs).count(),
        'security_groups_count': SecurityGroup.objects.filter(organization__in=user_orgs).count(),
    }
    
    return render(request, 'api/dashboard.html', context)

@login_required
def logout_view(request):
    """Handle logout requests."""
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    
    # If not a POST request, redirect to dashboard
    return redirect('dashboard') 