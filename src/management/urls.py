from django.urls import path

from . import views as management_views

urlpatterns = [
    path("login_admin/", management_views.login_admin, name="login_admin"),
    path("logout_admin/", management_views.logout_admin, name="logout_admin"),
    path("admin_dashboard/", management_views.admin_dashboard, name="admin_dashboard"),
    path("contact-admin/", management_views.contact_admin, name="contact_admin"),
]
