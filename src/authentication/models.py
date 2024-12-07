from django.db import models
from django.utils import timezone

from management.models import Employee


class OTP(models.Model):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name="otp"
    )
    otp = models.CharField(max_length=6)
    expiry = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() < self.expiry

    def __str__(self):
        return f"OTP for {self.employee.first_name} {self.employee.last_name}"
