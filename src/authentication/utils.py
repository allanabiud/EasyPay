import random
import string
from datetime import timedelta

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.timezone import now

from .models import OTP


def send_otp(employee):
    # Generate a 6-digit OTP
    otp = "".join(random.choices(string.digits, k=6))
    expiry = now() + timedelta(minutes=10)  # OTP expiry time (10 minutes)

    # Create or update OTP for the employee in a single atomic operation
    OTP.objects.update_or_create(
        employee=employee,  # Lookup parameter
        defaults={"otp": otp, "expiry": expiry},  # Fields to update
    )

    # Render the HTML email template
    email_context = {
        "first_name": employee.first_name,
        "otp": otp,
        "expiry_time": "10 minutes",
    }
    subject = "Your EasyPay Account Verification OTP Code"
    plain_message = f"Dear {employee.first_name} {employee.last_name},\n\nYour OTP code is {otp}. It will expire in 10 minutes."
    html_message = render_to_string("otp_email.html", email_context)

    # Send the email
    send_mail(
        subject=subject,
        message=plain_message,  # Fallback plain text
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[employee.email],
        html_message=html_message,  # HTML email content
    )


def verify_otp(employee, otp_input):
    # Verify OTP entered by the employee.
    try:
        otp_record = OTP.objects.get(employee=employee)
    except OTP.DoesNotExist:
        return "No OTP generated for this employee."

    if not otp_record.is_valid():
        return "OTP has expired."

    if otp_record.otp != otp_input:
        return "Invalid OTP."

    # OTP is valid, mark the employee as verified
    employee.verified = True
    employee.save()

    return "Employee successfully verified."


# A simple token generation
RESET_TOKEN_TIMEOUT = 600  # 10 minutes


def send_password_reset(request, user):
    # Generate a unique password reset token
    token = get_random_string(32)

    # Store token in cache or a more permanent storage (e.g., database or cache)
    cache.set(token, user.pk, timeout=RESET_TOKEN_TIMEOUT)

    # Create reset link
    current_site = get_current_site(request)  # Pass the request object here
    if not current_site:
        # If get_current_site fails, use the default domain from settings (e.g., localhost for development)
        domain = (
            settings.DEFAULT_DOMAIN
            if hasattr(settings, "DEFAULT_DOMAIN")
            else "localhost:8000"
        )
    else:
        domain = current_site.domain

    # Construct the reset link using the domain
    reset_link = f"http://{domain}/password-reset/{urlsafe_base64_encode(force_bytes(user.pk))}/{token}/"

    # Render the HTML email template
    email_context = {
        "first_name": user.first_name,
        "reset_link": reset_link,
    }
    subject = "Your EasyPay Password Reset Request"
    plain_message = f"Dear {user.first_name},\n\nWe received a request to reset your password. Click the link below to reset it:\n\n{reset_link}\n\nThis link will expire in 10 minutes."
    html_message = render_to_string("password_reset_email.html", email_context)

    # Send the password reset email
    send_mail(
        subject=subject,
        message=plain_message,  # Fallback plain text
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,  # HTML email content
    )
