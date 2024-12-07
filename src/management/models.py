from django.contrib.auth.models import User
from django.db import models


class JobGroup(models.Model):
    name = models.CharField(max_length=100)
    base_salary = models.DecimalField(max_digits=11, decimal_places=2, default=0)

    def calculate_total_allowances(self):
        """Calculate the total allowances for this job group."""
        total = 0
        for allowance in self.allowances.all():
            if allowance.calculation_type == "percentage":
                total += (allowance.value / 100) * self.base_salary
            else:  # Fixed amount
                total += allowance.value
        return total

    def calculate_total_deductions(self):
        """Calculate the total deductions for this job group."""
        total = 0
        for deduction in self.deductions.all():
            if deduction.calculation_type == "percentage":
                total += (deduction.value / 100) * self.base_salary
            else:  # Fixed amount
                total += deduction.value
        return total

    def calculate_net_salary(self):
        """Calculate the net salary after applying allowances and deductions."""
        net_salary = (
            self.base_salary
            + self.calculate_total_allowances()
            - self.calculate_total_deductions()
        )

        return net_salary

    def __str__(self):
        return self.name


class Allowance(models.Model):
    CALCULATION_TYPES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]

    name = models.CharField(max_length=100)
    job_groups = models.ManyToManyField(JobGroup, related_name="allowances")
    calculation_type = models.CharField(max_length=15, choices=CALCULATION_TYPES)
    value = models.DecimalField(max_digits=11, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} ({self.calculation_type}: {self.value})"


class Deduction(models.Model):
    CALCULATION_TYPES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]

    name = models.CharField(max_length=100)
    job_groups = models.ManyToManyField(JobGroup, related_name="deductions")
    calculation_type = models.CharField(max_length=15, choices=CALCULATION_TYPES)
    value = models.DecimalField(max_digits=11, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} ({self.calculation_type}: {self.value})"


class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Branch(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Employee(models.Model):
    id_number = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    job_group = models.ForeignKey(JobGroup, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)

    def calculate_total_allowances(self):
        return sum(
            allowance.calculated_amount(self.job_group.base_salary)
            for allowance in self.job_group.allowances.all()
        )

    def calculate_total_deductions(self):
        return sum(
            deduction.calculated_amount(self.job_group.base_salary)
            for deduction in self.job_group.deductions.all()
        )

    def net_salary(self):
        return (
            self.job_group.base_salary
            + self.calculate_total_allowances()
            - self.calculate_total_deductions()
        )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.id_number})"


class ActivityLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="activity_logs",
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # To log IPs

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"
