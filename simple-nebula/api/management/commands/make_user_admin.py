from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from api.models import Membership

User = get_user_model()

class Command(BaseCommand):
    help = 'Promote a user to admin in all organizations they are a member of'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='The email of the user to promote')

    def handle(self, *args, **options):
        email = options['email']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise CommandError(f'User with email {email} does not exist')
        
        memberships = Membership.objects.filter(user=user)
        
        if not memberships.exists():
            self.stdout.write(self.style.WARNING(f'User {email} is not a member of any organizations'))
            return
        
        # Count the memberships
        total_count = memberships.count()
        already_admin_count = memberships.filter(role=Membership.Roles.ADMIN).count()
        updated_count = 0
        
        # Update all non-admin memberships to admin
        for membership in memberships:
            if membership.role != Membership.Roles.ADMIN:
                old_role = membership.get_role_display()
                membership.role = Membership.Roles.ADMIN
                membership.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated role from {old_role} to Admin in {membership.organization.name}'
                    )
                )
        
        # Summary message
        if updated_count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'User {email} is already an admin in all organizations ({already_admin_count})'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Made user {email} an admin in {updated_count} organizations. '
                    f'Already admin in {already_admin_count} organizations. '
                    f'Total organizations: {total_count}'
                )
            ) 