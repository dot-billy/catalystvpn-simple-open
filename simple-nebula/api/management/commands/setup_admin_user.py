from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from api.models import User, Organization, Membership
import uuid

class Command(BaseCommand):
    help = 'Set up a user as admin, creating organizations if needed'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='The email of the user to set up')
        parser.add_argument('--create-org', action='store_true', help='Create a default organization if none exists')
        parser.add_argument('--org-name', type=str, help='Name for the organization to create', default='Default Organization')
        parser.add_argument('--create-user', action='store_true', help='Create the user if they don\'t exist')
        parser.add_argument('--password', type=str, help='Password for the new user if created')
        parser.add_argument('--full-name', type=str, help='Full name for the new user if created')

    def handle(self, *args, **options):
        email = options['email']
        create_org = options['create_org']
        org_name = options['org_name']
        create_user = options['create_user']
        password = options['password']
        full_name = options['full_name'] or "Admin User"
        
        # Get or create user
        try:
            user = User.objects.get(email=email)
            self.stdout.write(f"Found existing user: {user.email}")
        except User.DoesNotExist:
            if create_user and password:
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    full_name=full_name
                )
                self.stdout.write(self.style.SUCCESS(f"Created new user: {user.email}"))
            else:
                raise CommandError(f"User {email} does not exist. Use --create-user and --password to create them.")
        
        # Get all organizations
        orgs = Organization.objects.all()
        
        # Create a default organization if requested and none exist
        if orgs.count() == 0 and create_org:
            slug = slugify(org_name)
            org = Organization.objects.create(
                name=org_name,
                slug=slug,
                description=f"Default organization for {user.email}"
            )
            self.stdout.write(self.style.SUCCESS(f"Created new organization: {org.name} ({org.slug})"))
            orgs = Organization.objects.all()  # Refresh the queryset
        
        if orgs.count() == 0:
            self.stdout.write(self.style.WARNING("No organizations exist. Use --create-org to create one."))
            return
            
        # Track counters
        added_to_orgs = 0
        already_in_orgs = 0
        already_admin_in_orgs = 0
        promoted_in_orgs = 0
        
        # For each organization, make sure the user is a member and an admin
        for org in orgs:
            # Check if user is already a member
            membership = Membership.objects.filter(user=user, organization=org).first()
            
            if membership:
                already_in_orgs += 1
                # Check if already admin
                if membership.role == Membership.Roles.ADMIN:
                    already_admin_in_orgs += 1
                    self.stdout.write(f"User is already admin in: {org.name} ({org.slug})")
                else:
                    # Promote to admin
                    old_role = membership.get_role_display()
                    membership.role = Membership.Roles.ADMIN
                    membership.save()
                    promoted_in_orgs += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"Promoted user from {old_role} to Admin in: {org.name} ({org.slug})"
                    ))
            else:
                # Add user to organization as admin
                Membership.objects.create(
                    user=user,
                    organization=org,
                    role=Membership.Roles.ADMIN
                )
                added_to_orgs += 1
                self.stdout.write(self.style.SUCCESS(
                    f"Added user as Admin to: {org.name} ({org.slug})"
                ))
        
        # Print summary
        self.stdout.write("\nSummary:")
        self.stdout.write(f"- Total organizations: {orgs.count()}")
        if added_to_orgs > 0:
            self.stdout.write(self.style.SUCCESS(f"- Added to {added_to_orgs} organizations"))
        if promoted_in_orgs > 0:
            self.stdout.write(self.style.SUCCESS(f"- Promoted to admin in {promoted_in_orgs} organizations"))
        if already_admin_in_orgs > 0:
            self.stdout.write(f"- Already admin in {already_admin_in_orgs} organizations")
        self.stdout.write(self.style.SUCCESS(f"User {email} is now an admin in all {orgs.count()} organizations")) 