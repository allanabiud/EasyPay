from django.urls import path

from .views import (
    account_settings,
    create_account,
    employee_dashboard,
    generate_breakdown_pdf,
    login_employee,
    logout_employee,
    salary_breakdown,
)

urlpatterns = [
    path("create-account/", create_account, name="create_account"),
    path("logout_employee/", logout_employee, name="logout_employee"),
    path("employee-dashboard/", employee_dashboard, name="employee_dashboard"),
    path("login-employee/", login_employee, name="login_employee"),
    path("salary-breakdown/", salary_breakdown, name="salary_breakdown"),
    path("salary-breakdown/pdf/", generate_breakdown_pdf, name="generate_salary_pdf"),
    path("account/settings/", account_settings, name="account_settings"),
]
