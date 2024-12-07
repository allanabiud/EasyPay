from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from management.models import Employee

from .utils import send_otp, verify_otp


def verify_employee(request):
    if request.method == "POST":
        id_number = request.POST.get("id_number")
        try:
            employee = Employee.objects.get(id_number=id_number)
            # Check if the employee is already verified
            if employee.verified:
                messages.info(request, "You have already verified. Please log in.")
                return redirect("login_employee")
            else:
                # Generate OTP
                send_otp(employee)  # Using the new send_otp function
                request.session["id_number"] = id_number  # Save ID number in session
                messages.success(
                    request, "A one-time code has been sent to your email."
                )
                return redirect("verify_code")  # Redirect to OTP verification form
        except Employee.DoesNotExist:
            messages.error(request, "ID Number not found. Contact an administrator.")
            return redirect("verify_employee")  # Redirect to verification form

    return render(request, "verify_employee.html")


def verify_code(request):
    id_number = request.session.get("id_number")  # Get the ID number from the session
    if not id_number:
        messages.error(request, "Employee not found. Please verify your ID.")
        return redirect("verify_employee")

    if request.method == "POST":
        otp_input = "".join(
            [
                request.POST.get("code1", ""),
                request.POST.get("code2", ""),
                request.POST.get("code3", ""),
                request.POST.get("code4", ""),
                request.POST.get("code5", ""),
                request.POST.get("code6", ""),
            ]
        )

        try:
            employee = Employee.objects.get(id_number=id_number)
            verification_result = verify_otp(
                employee, otp_input
            )  # Use the new OTP verification function

            if verification_result == "Employee successfully verified.":
                request.session["id_number"] = id_number  # Save ID for account creation
                messages.success(request, "Code verified successfully!")
                return redirect("create_account")
            else:
                messages.error(request, verification_result)
        except Employee.DoesNotExist:
            messages.error(request, "Employee not found. Please verify your ID.")

    return render(request, "verify_code.html", {"id_number": id_number})


def resend_otp(request, id_number):
    try:
        # Get the employee by ID number
        employee = Employee.objects.get(id_number=id_number)

        # Resend OTP
        send_otp(employee)  # Using the new send_otp function

        # Success message
        messages.success(request, "OTP has been resent successfully.")
    except Employee.DoesNotExist:
        # Handle case where employee is not found
        messages.error(request, "Employee not found.")

    # Redirect to verify_code with id_number as a query parameter
    return redirect(f"{reverse('verify_code')}?id_number={id_number}")
