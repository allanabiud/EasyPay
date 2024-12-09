from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .models import Allowance, Branch, Deduction, Department, Employee, JobGroup


# Renders the admin dashboard
@login_required(login_url="/login_admin/")
def admin_dashboard(request):
    return render(request, "layouts/admin_dashboard.html")


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

    return render(request, "layouts/login_admin.html", {"login_form": login_form})


# Admin Dashboard Logout
def logout_admin(request):
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect("login_admin")


def contact_admin(request):
    return render(request, "layouts/contact_admin.html")


def admin_tables(request):
    # Add Employee form dropdown data
    employees = Employee.objects.select_related(
        "job_group", "department", "branch"
    ).all()
    job_groups = JobGroup.objects.all()

    departments = Department.objects.all()
    branches = Branch.objects.all()
    users = User.objects.all()

    # Fetch Allowance data
    allowances = Allowance.objects.all()
    # Get the deductions
    deductions = Deduction.objects.all()

    context = {
        "employees": employees,
        "job_groups": job_groups,
        "departments": departments,
        "branches": branches,
        "users": users,
        "allowances": allowances,
        "deductions": deductions,
    }

    return render(request, "layouts/admin_tables.html", context)


def add_employee(request):
    if request.method == "POST":
        id_number = request.POST["id_number"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        job_group_id = request.POST["job_group"]
        department_id = request.POST["department"]
        branch_id = request.POST["branch"]
        verified = request.POST.get("verified", "False") == "True"
        user_id = request.POST.get("user")

        try:
            job_group = JobGroup.objects.get(id=job_group_id)
            department = Department.objects.get(id=department_id)
            branch = Branch.objects.get(id=branch_id)
            user = User.objects.get(id=user_id) if user_id else None

            Employee.objects.create(
                id_number=id_number,
                first_name=first_name,
                last_name=last_name,
                email=email,
                job_group=job_group,
                department=department,
                branch=branch,
                verified=verified,
                user=user,
            )
            messages.success(request, "Employee added successfully!")
        except Exception as e:
            messages.error(request, f"Error adding employee: {e}")

        return redirect("admin_tables")

    return redirect("admin_tables")


def edit_employee(request, id_number):
    # Retrieve the employee
    employee = get_object_or_404(Employee, id_number=id_number)
    print(employee.user)  # Should display the linked user or None

    if request.method == "POST":
        # Check if 'user' is part of the POST data and update accordingly
        user_id = request.POST.get("user")  # Get user ID from POST data (if it exists)

        # Update employee details
        employee.id_number = request.POST.get("id_number")
        employee.first_name = request.POST["first_name"]
        employee.last_name = request.POST["last_name"]
        employee.email = request.POST["email"]
        employee.job_group_id = request.POST["job_group"]
        employee.department_id = request.POST["department"]
        employee.branch_id = request.POST["branch"]

        # Only update 'user' if it's present in the POST data
        if user_id:
            employee.user_id = user_id

        # Save the updated employee
        employee.save()

        # Success message
        messages.success(request, "Employee updated successfully!")
        return redirect("admin_tables")

    # GET: Render modal pre-filled with employee details
    users = User.objects.all()  # All users (filter if needed)
    job_groups = JobGroup.objects.all()
    departments = Department.objects.all()
    branches = Branch.objects.all()

    return render(
        request,
        "layouts/admin_tables.html",
        {
            "employee": employee,
            "users": users,
            "job_groups": job_groups,
            "departments": departments,
            "branches": branches,
        },
    )


# Add Allowance
def add_allowance(request):
    if request.method == "POST":
        name = request.POST["name"]
        calculation_type = request.POST["calculation_type"]
        default_value = request.POST["default_value"]

        # Create and save the new allowance
        Allowance.objects.create(
            name=name,
            calculation_type=calculation_type,
            default_value=default_value,
        )
        messages.success(request, "Allowance added successfully!")
        return redirect("admin_tables")

    return redirect("admin_tables")


# Add Deduction
def add_deduction(request):
    if request.method == "POST":
        name = request.POST["name"]
        calculation_type = request.POST["calculation_type"]
        default_value = request.POST["default_value"]

        # Create and save the new deduction
        Deduction.objects.create(
            name=name,
            calculation_type=calculation_type,
            default_value=default_value,
        )

        messages.success(request, "Deduction added successfully!")
        return redirect("admin_tables")

    return redirect("admin_tables")


# Add Department
def add_department(request):
    if request.method == "POST":
        name = request.POST["name"]

        # Create and save the new department
        Department.objects.create(name=name)

        messages.success(request, "Department added successfully!")
        return redirect("admin_tables")

    return redirect("admin_tables")


# Add Branch
def add_branch(request):
    if request.method == "POST":
        name = request.POST["name"]
        location = request.POST["location"]

        # Create and save the new branch
        Branch.objects.create(name=name, location=location)

        messages.success(request, "Branch added successfully!")
        return redirect("admin_tables")

    return redirect("admin_tables")


# Edit Department
def edit_department(request, id):
    # Retrieve the department by id
    department = get_object_or_404(Department, id=id)

    if request.method == "POST":
        # Update the department's name from the form data
        department.name = request.POST["name"]
        department.save()

        # Show success message and redirect to the admin tables page
        messages.success(request, "Department updated successfully!")
        return redirect("admin_tables")

    # GET request: Render modal pre-filled with department details
    return render(
        request,
        "layouts/admin_tables.html",
        {
            "department": department,
        },
    )


# Edit Branch
def edit_branch(request, id):
    branch = get_object_or_404(Branch, id=id)

    if request.method == "POST":
        branch.name = request.POST["name"]
        branch.address = request.POST["address"]
        branch.save()

        messages.success(request, "Branch updated successfully!")
        return redirect("admin_tables")

    # GET request: Render modal pre-filled with branch details
    return render(
        request,
        "layouts/admin_tables.html",
        {
            "branch": branch,
        },
    )


# Edit Allowance
def edit_allowance(request, id):
    allowance = get_object_or_404(Allowance, id=id)

    if request.method == "POST":
        allowance.name = request.POST["name"]
        allowance.calculation_type = request.POST["calculation_type"]
        allowance.default_value = request.POST["default_value"]
        allowance.save()

        messages.success(request, "Allowance updated successfully!")
        return redirect("admin_tables")

    return redirect("admin_tables")


# Edit Deduction View
def edit_deduction(request, id):
    deduction = get_object_or_404(Deduction, id=id)

    if request.method == "POST":
        deduction.name = request.POST["name"]
        deduction.calculation_type = request.POST["calculation_type"]
        deduction.default_value = request.POST["default_value"]
        deduction.save()

        messages.success(request, "Deduction updated successfully!")
        return redirect("admin_tables")

    return redirect("admin_tables")


# Delete Branch View
def delete_branch(request, id):
    branch = get_object_or_404(Branch, id=id)

    if request.method == "POST":
        branch.delete()
        messages.success(request, f"Branch '{branch.name}' deleted successfully!")
        return redirect("admin_tables")

    return redirect("admin_tables")


# Delete Department View
def delete_department(request, id):
    department = get_object_or_404(Department, id=id)

    if request.method == "POST":
        department.delete()
        messages.success(
            request, f"Department '{department.name}' deleted successfully!"
        )
        return redirect("admin_tables")

    return redirect("admin_tables")


# Delete Allowance View
def delete_allowance(request, id):
    allowance = get_object_or_404(Allowance, id=id)

    if request.method == "POST":
        allowance.delete()
        messages.success(request, f"Allowance '{allowance.name}' deleted successfully!")
        return redirect("admin_tables")

    return redirect("admin_tables")


# Delete Deduction View
def delete_deduction(request, id):
    deduction = get_object_or_404(Deduction, id=id)

    if request.method == "POST":
        deduction.delete()
        messages.success(request, f"Deduction '{deduction.name}' deleted successfully!")
        return redirect("admin_tables")

    return redirect("admin_tables")
