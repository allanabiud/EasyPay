from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DepartmentForm
from .models import (
    Allowance,
    Branch,
    Deduction,
    Department,
    Employee,
    JobGroup,
    JobGroupAllowance,
    JobGroupDeduction,
)


# Renders the admin dashboard
@login_required(login_url="/login_admin/")
def admin_dashboard(request):
    # Fetch number of employees, job groups, departments and branches
    employees = Employee.objects.all()
    job_groups = JobGroup.objects.all()
    departments = Department.objects.all()
    branches = Branch.objects.all()

    # Store the length of each list
    num_employees = len(employees)
    num_job_groups = len(job_groups)
    num_departments = len(departments)
    num_branches = len(branches)

    # Employee distribution by Job Group
    job_group_distribution = JobGroup.objects.annotate(
        employee_count=Count("employee")
    ).values("name", "employee_count")
    # Sort the job group distribution alphabetically
    job_group_distribution = sorted(
        job_group_distribution, key=lambda group: group["name"]
    )

    # Employee distribution by Branch
    branch_distribution = Branch.objects.annotate(
        employee_count=Count("employee")
    ).values("name", "employee_count")
    # Sort the branches alphabetically
    branch_distribution = sorted(branch_distribution, key=lambda branch: branch["name"])

    # Employee distribution by Department
    department_distribution = Department.objects.annotate(
        employee_count=Count("employee")
    ).values("name", "employee_count")
    # Sort the departments alphabetically
    department_distribution = sorted(
        department_distribution, key=lambda department: department["name"]
    )

    # Prepare data for the Salary Distribution Chart
    salary_group_data = [
        {"label": job_group.name, "value": float(job_group.calculate_net_salary())}
        for job_group in job_groups
    ]
    # Sort the data alphabetically by label (job group name)
    salary_group_data.sort(key=lambda x: x["label"])

    # Separate sorted labels and values
    salary_group_labels = [item["label"] for item in salary_group_data]
    salary_group_values = [item["value"] for item in salary_group_data]

    # Prepare labels and data for the charts
    job_group_labels = [job_group["name"] for job_group in job_group_distribution]
    job_group_counts = [
        job_group["employee_count"] for job_group in job_group_distribution
    ]
    branch_labels = [branch["name"] for branch in branch_distribution]
    branch_counts = [branch["employee_count"] for branch in branch_distribution]
    department_labels = [department["name"] for department in department_distribution]
    department_counts = [
        department["employee_count"] for department in department_distribution
    ]

    context = {
        "employees": employees,
        "job_groups": job_groups,
        "departments": departments,
        "branches": branches,
        "num_employees": num_employees,
        "num_job_groups": num_job_groups,
        "num_departments": num_departments,
        "num_branches": num_branches,
        "job_group_labels": job_group_labels,
        "job_group_counts": job_group_counts,
        "branch_labels": branch_labels,
        "branch_counts": branch_counts,
        "department_labels": department_labels,
        "department_counts": department_counts,
        "salary_group_labels": salary_group_labels,
        "salary_group_values": salary_group_values,
    }

    return render(request, "layouts/admin_dashboard.html", context)


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


# Admin Contact Page
def contact_admin(request):
    return render(request, "layouts/contact_admin.html")


# Admin Tables Page
def admin_tables(request):
    # Fetch data for tables and forms
    # Employees
    employees = Employee.objects.select_related(
        "job_group", "department", "branch"
    ).all()
    # Job Groups
    job_groups = JobGroup.objects.all()
    # Departments
    departments = Department.objects.all()
    # Branches
    branches = Branch.objects.all()
    # Users
    users = User.objects.all()
    # Allowances
    allowances = Allowance.objects.all()
    # Deductions
    deductions = Deduction.objects.all()
    # Job group allowances and deductions
    job_group_data = []
    for job_group in job_groups:
        # Fetch allowances and deductions associated with each job group
        job_group_id = job_group.id
        job_group_allowances = JobGroupAllowance.objects.filter(job_group=job_group)
        job_group_deductions = JobGroupDeduction.objects.filter(job_group=job_group)
        job_group_data.append(
            {
                "job_group_id": job_group_id,
                "job_group": job_group,
                "job_group_allowances": job_group_allowances,
                "job_group_deductions": job_group_deductions,
            }
        )
    # Forms
    department_form = DepartmentForm()

    context = {
        "employees": employees,
        "job_groups": job_groups,
        "job_group_data": job_group_data,
        "departments": departments,
        "branches": branches,
        "users": users,
        "allowances": allowances,
        "deductions": deductions,
        "department_form": department_form,
    }

    return render(request, "layouts/admin_tables.html", context)


# EMPLOYEES TABLE
# Add Employee
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


# Edit Employee
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


# Delete Employee
def delete_employee(request, id_number):
    employee = get_object_or_404(Employee, id_number=id_number)
    if request.method == "POST":
        employee.delete()
        messages.success(
            request,
            f"Employee '{employee.first_name} {employee.last_name}' deleted successfully!",
        )
        return redirect("admin_tables")
    return redirect("admin_tables")


# Delete All Employees
def delete_all_employees(request):
    if request.method == "POST":
        Employee.objects.all().delete()
        messages.success(request, "All employees deleted successfully!")
        return redirect("admin_tables")
    return redirect("admin_tables")


# ALLOWANCES TABLE
# Add Allowance
def add_allowance(request):
    if request.method == "POST":
        name = request.POST["name"]

        # Create and save the new allowance
        Allowance.objects.create(
            name=name,
        )
        messages.success(request, "Allowance added successfully!")
        return redirect("admin_tables")

    return redirect("admin_tables")


# Edit Allowance
def edit_allowance(request, id):
    allowance = get_object_or_404(Allowance, id=id)

    if request.method == "POST":
        allowance.name = request.POST["name"]
        allowance.save()

        messages.success(request, "Allowance updated successfully!")
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


# DEDUCTIONS TABLE
# Add Deduction
def add_deduction(request):
    if request.method == "POST":
        name = request.POST["name"]

        # Create and save the new deduction
        Deduction.objects.create(
            name=name,
        )

        messages.success(request, "Deduction added successfully!")
        return redirect("admin_tables")

    return redirect("admin_tables")


# Edit Deduction View
def edit_deduction(request, id):
    deduction = get_object_or_404(Deduction, id=id)

    if request.method == "POST":
        deduction.name = request.POST["name"]
        deduction.save()

        messages.success(request, "Deduction updated successfully!")
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


# DEPARTMENTS TABLE
# Add Department
def add_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()  # Saves the new department to the database
            messages.success(request, "Department added successfully!")
        else:
            messages.error(request, "Failed to add department. Please check the form.")
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


# BRANCHES TABLE
# Add Branch
def add_branch(request):
    if request.method == "POST":
        name = request.POST["name"]
        address = request.POST["address"]

        # Create and save the new branch
        Branch.objects.create(name=name, address=address)

        messages.success(request, "Branch added successfully!")
        return redirect("admin_tables")

    return redirect("admin_tables")


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


# Delete Branch View
def delete_branch(request, id):
    branch = get_object_or_404(Branch, id=id)

    if request.method == "POST":
        branch.delete()
        messages.success(request, f"Branch '{branch.name}' deleted successfully!")
        return redirect("admin_tables")

    return redirect("admin_tables")


# JOB GROUPS TABLE
# Add Job Group
def add_job_group(request):
    if request.method == "POST":
        name = request.POST["name"]
        base_salary = request.POST["base_salary"]

        # Create and save the new job group
        job_group = JobGroup.objects.create(name=name, base_salary=base_salary)

        # Parse the allowances and deductions from the request
        allowances = request.POST.getlist("allowances[]")
        deductions = request.POST.getlist("deductions[]")
        allowance_calculation_types = request.POST.getlist(
            "allowance_calculation_types[]"
        )
        allowance_values = request.POST.getlist("allowance_values[]")
        deduction_calculation_types = request.POST.getlist(
            "deduction_calculation_types[]"
        )
        deduction_values = request.POST.getlist("deduction_values[]")

        # Save the allowances
        for i in range(len(allowances)):
            allowance = Allowance.objects.get(id=allowances[i])
            value = allowance_values[i]
            calculation_type = allowance_calculation_types[i]
            # Create and save the new JobGroupAllowance
            JobGroupAllowance.objects.create(
                job_group=job_group,
                allowance=allowance,
                value=value,
                calculation_type=calculation_type,
            )

        # Save the deductions
        for i in range(len(deductions)):
            deduction = Deduction.objects.get(id=deductions[i])
            value = deduction_values[i]
            calculation_type = deduction_calculation_types[i]
            # Create and save the new JobGroupDeduction
            JobGroupDeduction.objects.create(
                job_group=job_group,
                deduction=deduction,
                value=value,
                calculation_type=calculation_type,
            )

        messages.success(request, "Job Group added successfully!")
        return redirect("admin_tables")

    return redirect("admin_tables")


# Edit Job Group
def edit_job_group(request, job_group_id):
    # Retrieve the job group by id
    job_group = get_object_or_404(JobGroup, id=job_group_id)

    if request.method == "POST":
        # Check if 'user' is part of the POST data and update accordingly
        name = request.POST["name"]
        base_salary = request.POST["base_salary"]

        # Update job group details
        job_group.name = name
        job_group.base_salary = base_salary
        job_group.save()

        # Parse the allowances and deductions from the request
        allowances = request.POST.getlist("allowances[]")
        deductions = request.POST.getlist("deductions[]")
        allowance_calculation_types = request.POST.getlist(
            "allowance_calculation_types[]"
        )
        deduction_calculation_types = request.POST.getlist(
            "deduction_calculation_types[]"
        )
        allowance_values = request.POST.getlist("allowance_values[]")
        deduction_values = request.POST.getlist("deduction_values[]")

        # Delete the existing job group allowances and deductions
        job_group.jobgroupallowance_set.all().delete()
        job_group.jobgroupdeduction_set.all().delete()

        # Save the allowances
        for i in range(len(allowances)):
            # Skip empty entries
            if not allowances[i] or allowance_values[i] == "":
                continue

            allowance = Allowance.objects.get(id=allowances[i])
            value = allowance_values[i]
            calculation_type = allowance_calculation_types[i]
            # Create and save the new JobGroupAllowance
            JobGroupAllowance.objects.create(
                job_group=job_group,
                allowance=allowance,
                value=value,
                calculation_type=calculation_type,
            )

        # Save the deductions
        for i in range(len(deductions)):
            # Skip empty entries
            if not deductions[i] or deduction_values[i] == "":
                continue

            deduction = Deduction.objects.get(id=int(deductions[i]))
            value = deduction_values[i]
            calculation_type = deduction_calculation_types[i]
            # Create and save the new JobGroupDeduction
            JobGroupDeduction.objects.create(
                job_group=job_group,
                deduction=deduction,
                value=value,
                calculation_type=calculation_type,
            )

        messages.success(request, "Job Group updated successfully!")
        return redirect("admin_tables")


# Add Allowance Row
def add_allowance_row(request):
    job_group_id = request.POST.get("job_group_id")  # Get the job group ID from HTMX
    allowances = Allowance.objects.all()  # Fetch allowances
    context = {"job_group_id": job_group_id, "allowances": allowances}
    return render(request, "partials/allowance_row.html", context)


# Delete Allowance Row
def delete_allowance_row(request):
    if request.method == "POST":
        return HttpResponse("")
    else:
        return HttpResponse(status=404)


# Add Deduction Row
def add_deduction_row(request):
    job_group_id = request.POST.get("job_group_id")  # Get the job group ID from HTMX
    deductions = Deduction.objects.all()  # Fetch deductions
    context = {"job_group_id": job_group_id, "deductions": deductions}
    return render(request, "partials/deduction_row.html", context)


# Delete Deduction Row
def delete_deduction_row(request):
    if request.method == "POST":
        return HttpResponse("")
    else:
        return HttpResponse(status=404)


# Delete Job Group
def delete_job_group(request, id):
    job_group = get_object_or_404(JobGroup, id=id)
    if request.method == "POST":
        job_group.delete()
        messages.success(
            request,
            f"Job Group '{job_group.name}' deleted successfully!",
        )
        return redirect("admin_tables")
    return redirect("admin_tables")


# Delete All Job Groups
def delete_all_job_groups(request):
    if request.method == "POST":
        JobGroup.objects.all().delete()
        messages.success(request, "All job groups deleted successfully!")
        return redirect("admin_tables")
    return redirect("admin_tables")
