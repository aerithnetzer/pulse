from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User

class Command(BaseCommand):
    help = 'Create custom roles'

    def handle(self, *args, **options):
        new_group, created = Group.objects.get_or_create(name='editor')
        user = User.objects.get(username='aerith')
        user.groups.add(new_group)
        self.stdout.write(self.style.SUCCESS('Successfully created role'))