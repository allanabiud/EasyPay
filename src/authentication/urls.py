from django.urls import path

from .views import (
    request_password_reset,
    resend_otp,
    reset_password_form,
    verify_code,
    verify_employee,
)

urlpatterns = [
    path("verify/", verify_employee, name="verify_employee"),
    path("verify-code/", verify_code, name="verify_code"),
    path("resend-otp/<str:id_number>/", resend_otp, name="resend_otp"),
    path("password-reset/", request_password_reset, name="request_password_reset"),
    path(
        "password-reset/<uidb64>/<token>/",
        reset_password_form,
        name="reset_password_form",
    ),
]
