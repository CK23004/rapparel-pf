from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Create default groups and permissions'

    def handle(self, *args, **kwargs):
        admin_group, created = Group.objects.get_or_create(name='Admin')
        manager_group, created = Group.objects.get_or_create(name='Manager')
        staff_group, created = Group.objects.get_or_create(name='Staff')

        # Assign permissions to groups
        # Example: admin_group.permissions.add(Permission.objects.get(codename='add_user'))

#use the below command to run the above script
#python manage.py create_groups
