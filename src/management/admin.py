from django.contrib import admin

from .models import (
    ActivityLog,
    Allowance,
    Branch,
    Deduction,
    Department,
    Employee,
    JobGroup,
    JobGroupAllowance,
    JobGroupDeduction,
)


# Employee Admin
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id_number", "first_name", "last_name", "email")
    search_fields = ("id_number", "first_name", "last_name", "email")


admin.site.register(Employee, EmployeeAdmin)


# Inline admin for JobGroupAllowance
class JobGroupAllowanceInline(admin.TabularInline):
    model = JobGroupAllowance
    extra = 1  # Number of empty rows to show by default
    autocomplete_fields = ["allowance"]  # Helps with searching allowances
    fields = ["allowance", "calculation_type", "value"]


# Inline admin for JobGroupDeduction
class JobGroupDeductionInline(admin.TabularInline):
    model = JobGroupDeduction
    extra = 1
    autocomplete_fields = ["deduction"]
    fields = ["deduction", "calculation_type", "value"]


# Admin for JobGroup
@admin.register(JobGroup)
class JobGroupAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "base_salary",
        "calculate_total_allowances",
        "calculate_total_deductions",
        "calculate_net_salary",
    ]
    inlines = [JobGroupAllowanceInline, JobGroupDeductionInline]  # Add inlines
    search_fields = ["name"]
    ordering = ["name"]


# Admin for Allowance
@admin.register(Allowance)
class AllowanceAdmin(admin.ModelAdmin):
    list_display = ["name", "calculation_type", "default_value"]
    list_filter = ["calculation_type"]
    search_fields = ["name"]
    ordering = ["name"]


# Admin for Deduction
@admin.register(Deduction)
class DeductionAdmin(admin.ModelAdmin):
    list_display = ["name", "calculation_type", "default_value"]
    list_filter = ["calculation_type"]
    search_fields = ["name"]
    ordering = ["name"]


# Optional: Register JobGroupAllowance and JobGroupDeduction for management
@admin.register(JobGroupAllowance)
class JobGroupAllowanceAdmin(admin.ModelAdmin):
    list_display = ["job_group", "allowance", "value"]
    list_filter = ["job_group", "allowance"]
    search_fields = ["job_group__name", "allowance__name"]


@admin.register(JobGroupDeduction)
class JobGroupDeductionAdmin(admin.ModelAdmin):
    list_display = ["job_group", "deduction", "value"]
    list_filter = ["job_group", "deduction"]
    search_fields = ["job_group__name", "deduction__name"]


# Activity Log Admin
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "timestamp", "ip_address")
    search_fields = ("user__username", "action", "ip_address")
    list_filter = ("action",)


admin.site.register(ActivityLog, ActivityLogAdmin)


# Admin for Department
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


# Admin for Branch
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ["name", "location"]
    search_fields = ["name", "location"]
