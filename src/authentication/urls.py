from django.urls import path

from .views import resend_otp, verify_code, verify_employee

urlpatterns = [
    path("verify/", verify_employee, name="verify_employee"),
    path("verify-code/", verify_code, name="verify_code"),
    path("resend-otp/<str:id_number>/", resend_otp, name="resend_otp"),
]
