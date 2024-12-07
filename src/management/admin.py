from django.contrib import admin

from .models import (
    ActivityLog,
    Allowance,
    Branch,
    Deduction,
    Department,
    Employee,
    JobGroup,
)


# Employee Admin
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id_number", "first_name", "last_name", "email")
    search_fields = ("id_number", "first_name", "last_name", "email")


admin.site.register(Employee, EmployeeAdmin)


# Job Group Admin
class JobGroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "base_salary",
        "total_allowances",
        "total_deductions",
        "net_salary",
    )

    def total_allowances(self, obj):
        """Calculate and return total allowances for the job group."""
        return obj.calculate_total_allowances()

    def total_deductions(self, obj):
        """Calculate and return total deductions for the job group."""
        return obj.calculate_total_deductions()

    def net_salary(self, obj):
        """Calculate and return the net salary after allowances and deductions."""
        return obj.calculate_net_salary()

    total_allowances.admin_order_field = (
        "base_salary"  # Optional: allows sorting by total allowances
    )
    total_deductions.admin_order_field = (
        "base_salary"  # Optional: allows sorting by total deductions
    )
    net_salary.admin_order_field = (
        "base_salary"  # Optional: allows sorting by net salary
    )

    total_allowances.short_description = "Total Allowances"
    total_deductions.short_description = "Total Deductions"
    net_salary.short_description = "Net Salary"


admin.site.register(JobGroup, JobGroupAdmin)

# Department Admin
admin.site.register(Department)

# Branch Admin
admin.site.register(Branch)


# Allowance Admin
class AllowanceAdmin(admin.ModelAdmin):
    list_display = ("name", "display_job_groups", "calculation_type", "value")
    search_fields = ("name",)
    list_filter = ("job_groups",)

    def display_job_groups(self, obj):
        """Display the names of job groups associated with the allowance."""
        return ", ".join([job_group.name for job_group in obj.job_groups.all()])

    display_job_groups.short_description = "Job Groups"


admin.site.register(Allowance, AllowanceAdmin)


# Deduction Admin
class DeductionAdmin(admin.ModelAdmin):
    list_display = ("name", "display_job_groups", "calculation_type", "value")
    search_fields = ("name",)
    list_filter = ("job_groups",)

    def display_job_groups(self, obj):
        """Display the names of job groups associated with the deduction."""
        return ", ".join([job_group.name for job_group in obj.job_groups.all()])

    display_job_groups.short_description = "Job Groups"


admin.site.register(Deduction, DeductionAdmin)


# Activity Log Admin
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "timestamp", "ip_address")
    search_fields = ("user__username", "action", "ip_address")
    list_filter = ("action",)


admin.site.register(ActivityLog, ActivityLogAdmin)
