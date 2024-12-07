import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from weasyprint import HTML

from management.models import ActivityLog, Allowance, Deduction, Employee
from management.utils import get_client_ip, log_activity


# Render Employee Dashboard
@login_required(login_url="login_employee")
def employee_dashboard(request):
    employee = Employee.objects.get(user=request.user)
    job_group = employee.job_group
    base_salary = job_group.base_salary
    net_salary = job_group.calculate_net_salary()
    net_salary = round(net_salary, 2)

    # Get allowances and deductions for the job group
    allowances = Allowance.objects.filter(job_groups=job_group)
    deductions = Deduction.objects.filter(job_groups=job_group)
    # Get the user's activity logs
    recent_logs = ActivityLog.objects.filter(user=request.user).order_by("-timestamp")[
        :5
    ]  # Fetch last 5 logs

    # Chart Data for Allowances
    allowance_data = {
        "labels": [allowance.name for allowance in allowances],
        "values": [],
    }
    for allowance in allowances:
        if allowance.calculation_type == "percentage":
            # Calculate allowance amount based on percentage
            allowance_amount = (allowance.value / 100) * base_salary
        else:
            allowance_amount = allowance.value
        allowance_data["values"].append(float(allowance_amount))

    # Chart Data for Deductions
    deduction_data = {
        "labels": [deduction.name for deduction in deductions],
        "values": [],
    }
    for deduction in deductions:
        if deduction.calculation_type == "percentage":
            # Calculate deduction amount based on percentage
            deduction_amount = (deduction.value / 100) * base_salary
        else:
            deduction_amount = deduction.value
        deduction_data["values"].append(float(deduction_amount))

    total_allowance = sum(allowance_data["values"])  # Calculate total allowance
    total_deduction = sum(deduction_data["values"])  # Calculate total deduction

    context = {
        "employee": employee,
        "email": employee.email,
        "department": employee.department,
        "job_group": employee.job_group,
        "branch": employee.branch,
        "net_salary": net_salary,
        "allowance_data": json.dumps(allowance_data),
        "deduction_data": json.dumps(deduction_data),
        "total_allowance": total_allowance,
        "total_deduction": total_deduction,
        "recent_logs": recent_logs,
    }
    return render(request, "employee_dashboard.html", context)


# Employee Dashboard Login
def login_employee(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            # Find the employee associated with this username
            employee = Employee.objects.get(user__username=username)

            # Check if the employee is verified
            if not employee.verified:
                messages.info(
                    request, "You are in the system. Please verify your account first."
                )
                return redirect("verify_employee")

            # Authenticate and log in the user
            user = authenticate(request, username=username, password=password)
            if user:
                # Check if the user is part of the "Employees" group
                if not user.groups.filter(name="Employees").exists():
                    messages.error(
                        request, "You do not have permission to access this page."
                    )
                    log_activity(
                        user=user,
                        action="Unauthorized Login Attempt",
                        ip_address=get_client_ip(request),
                    )
                    return redirect("login_employee")

                login(request, user)
                # Log successful login
                log_activity(
                    user=user,
                    action="Successful Login",
                    ip_address=get_client_ip(request),
                )
                messages.success(request, "Login successful!")
                return redirect("employee_dashboard")
            else:
                messages.error(request, "Invalid username or password.")
                return redirect("login_employee")
        except Employee.DoesNotExist:
            messages.error(request, "No account found for this username.")
            return redirect("login_employee")

    return render(request, "login_employee.html")


# Employee Dashboard Logout
def logout_employee(request):
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect("login_employee")


# Employee Create Account
@login_required(login_url="verify_employee")
def create_account(request):
    if request.method == "POST":
        id_number = request.session.get("id_number")
        username = request.POST.get("username")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        try:
            employee = Employee.objects.get(id_number=id_number)

            if password != password_confirm:
                messages.error(request, "Passwords do not match.")
                return render(request, "create_account.html")

            # Create the user and link to employee
            user = User.objects.create_user(username=username, password=password)
            user.first_name = employee.first_name
            user.last_name = employee.last_name
            user.email = employee.email
            user.save()
            # Link employee to user
            employee.user = user  # Set the employee's user field
            employee.save()

            messages.success(request, "Account created successfully.")
            messages.info(request, "Login into your account.")
            return redirect("login_employee")

        except Employee.DoesNotExist:
            messages.error(
                request,
                "Employee with the provided ID number does not exist. Contact an admin.",
            )
            return redirect("verify_employee")

    return render(request, "create_account.html")


# Employee Salary Breakdown
@login_required(login_url="login_employee")
def salary_breakdown(request):
    # Get the employee associated with the user
    employee = get_object_or_404(Employee, user=request.user)
    # Get the job group associated with the employee
    job_group = employee.job_group
    base_salary = job_group.base_salary
    # Calculate total allowances
    total_allowances = Decimal(0)
    allowances = []
    for allowance in job_group.allowances.all():
        if allowance.calculation_type == "percentage":
            allowance_amount = (allowance.value / 100) * base_salary
        else:  # Fixed amount
            allowance_amount = allowance.value
        total_allowances += allowance_amount
        allowances.append(
            {
                "name": allowance.name,
                "calculation_type": allowance.calculation_type,
                "value": allowance.value,
                "amount": allowance_amount,
            }
        )

    # Calculate total deductions
    total_deductions = Decimal(0)
    deductions = []
    for deduction in job_group.deductions.all():
        if deduction.calculation_type == "percentage":
            deduction_amount = (deduction.value / 100) * base_salary
        else:  # Fixed amount
            deduction_amount = deduction.value
        total_deductions += deduction_amount
        deductions.append(
            {
                "name": deduction.name,
                "calculation_type": deduction.calculation_type,
                "value": deduction.value,
                "amount": deduction_amount,
            }
        )

    # Calculate net salary
    net_salary = job_group.calculate_net_salary()
    net_salary = round(net_salary, 2)

    context = {
        "employee": employee,
        "job_group": job_group,
        "base_salary": base_salary,
        "allowances": allowances,
        "total_allowances": total_allowances,
        "deductions": deductions,
        "total_deductions": total_deductions,
        "net_salary": net_salary,
    }

    return render(request, "salary_breakdown.html", context)


# Generate PDF of Salary Breakdown
@login_required(login_url="login_employee")
def generate_breakdown_pdf(request):
    # Get the employee and associated details
    employee = get_object_or_404(Employee, user=request.user)
    job_group = employee.job_group
    base_salary = job_group.base_salary

    # Calculate allowances
    total_allowances = Decimal(0)
    allowances = []
    for allowance in job_group.allowances.all():
        if allowance.calculation_type == "percentage":
            allowance_amount = (allowance.value / 100) * base_salary
        else:  # Fixed amount
            allowance_amount = allowance.value
        total_allowances += allowance_amount
        allowances.append(
            {
                "name": allowance.name,
                "calculation_type": allowance.calculation_type,
                "value": allowance.value,
                "amount": allowance_amount,
            }
        )

    # Calculate deductions
    total_deductions = Decimal(0)
    deductions = []
    for deduction in job_group.deductions.all():
        if deduction.calculation_type == "percentage":
            amount = (deduction.value / 100) * base_salary
        else:  # Fixed amount
            amount = deduction.value
        total_deductions += amount
        deductions.append(
            {
                "name": deduction.name,
                "calculation_type": deduction.calculation_type,
                "value": deduction.value,
                "amount": amount,
            }
        )

    # Calculate net salary
    net_salary = job_group.calculate_net_salary()

    # Render the PDF template
    context = {
        "employee": employee,
        "job_group": job_group,
        "base_salary": base_salary,
        "allowances": allowances,
        "total_allowances": total_allowances,
        "deductions": deductions,
        "total_deductions": total_deductions,
        "net_salary": net_salary,
    }
    html_string = render_to_string("salary_breakdown_pdf.html", context)

    # Generate the PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Salary_Breakdown_{employee.id_number}.pdf"'
    )
    HTML(string=html_string).write_pdf(response)

    # Log PDF generation
    log_activity(
        user=request.user,
        action="Generated Salary Breakdown PDF",
        ip_address=get_client_ip(request),
    )
    return response


# Employee Account Settings
@login_required(login_url="login_employee")
def account_settings(request):
    # Get the employee and associated details
    employee = get_object_or_404(Employee, user=request.user)
    job_group = employee.job_group

    context = {
        "employee": employee,
        "job_group": job_group,
    }

    if request.method == "POST":
        # Get the old password, new password, and password confirmation
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        username = request.POST.get("username")

        # Create the user object
        user = request.user
        ip_address = get_client_ip(request)

        # Handle username update
        if username and username != user.username:
            old_username = user.username
            user.username = username
            log_activity(
                user=user,
                action=f"Changed username from '{old_username}' to '{username}'",
                ip_address=ip_address,
            )

        # Handle password update if provided
        if old_password or new_password or confirm_password:
            if not old_password:
                messages.error(request, "Please provide your old password.")
                return redirect("account_settings")

            # Authenticate old password
            if not authenticate(username=user.username, password=old_password):
                messages.error(request, "The old password is incorrect.")
                return redirect("account_settings")

            if new_password != confirm_password:
                messages.error(
                    request, "The new password and confirmation do not match."
                )
                return redirect("account_settings")

            user.set_password(new_password)
            # Log password change
            log_activity(
                user=user,
                action="Changed account password",
                ip_address=ip_address,
            )
            # Keep the user logged in after changing the password
            update_session_auth_hash(request, user)

        # Save updates
        user.save()
        messages.success(request, "Your account information has been updated.")
        return redirect("account_settings")

    return render(request, "account_settings.html", context)
