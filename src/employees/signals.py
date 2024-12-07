from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def add_user_to_employee_group(sender, instance, created, **kwargs):
    # Automatically adds new users to the Employees group
    if created:  # Only for new users
        employee_group, _ = Group.objects.get_or_create(name="Employees")
        instance.groups.add(employee_group)
