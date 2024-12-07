from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render


# Renders the admin dashboard
@login_required(login_url="/login_admin/")
def admin_dashboard(request):
    return render(request, "admin_dashboard.html")


# Admin Dashboard Login
def login_admin(request):
    if request.method == "POST":
        login_form = AuthenticationForm(request=request, data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get("username")
            password = login_form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if the user belongs to the "Administrators" group
                if user.groups.filter(name="Administrators").exists():
                    login(request, user)
                    messages.success(request, "Login successful!")
                    return redirect("admin_dashboard")  # Redirect to admin dashboard
                else:
                    messages.error(
                        request, "You do not have permission to access this page."
                    )
                    return redirect("login_admin")  # Redirect back to login page

            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid form data.")

    elif request.method == "GET":
        login_form = AuthenticationForm()

    return render(request, "login_admin.html", {"login_form": login_form})


# Admin Dashboard Logout
def logout_admin(request):
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect("login_admin")


def contact_admin(request):
    return render(request, "contact_admin.html")
