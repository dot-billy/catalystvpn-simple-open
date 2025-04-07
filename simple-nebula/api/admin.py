from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Organization, Membership, CertificateAuthority,
    Certificate, SecurityGroup, Node, Lighthouse, APIKey, Network
)


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('organization', 'role', 'created_at')
    can_delete = True
    verbose_name = "Organization Membership"
    verbose_name_plural = "Organization Memberships"


class OrganizationMembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('user', 'role', 'created_at')
    can_delete = True
    verbose_name = "Member"
    verbose_name_plural = "Members"


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'full_name', 'organization_roles', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined', 'memberships__role')
    search_fields = ('email', 'full_name', 'memberships__organization__name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2'),
        }),
    )
    inlines = [MembershipInline]
    
    def organization_roles(self, obj):
        """Display all organizations and roles for this user."""
        memberships = obj.memberships.select_related('organization').all()
        if not memberships:
            return "No organizations"
        return ", ".join([f"{m.organization.name}: {m.get_role_display()}" for m in memberships])
    
    organization_roles.short_description = "Organization Roles"


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'member_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'slug', 'description')
    ordering = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrganizationMembershipInline]
    
    def member_count(self, obj):
        return obj.memberships.count()
    
    member_count.short_description = "Members"


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_name', 'organization_name', 'role', 'created_at', 'updated_at')
    list_filter = ('role', 'organization__name', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__full_name', 'organization__name', 'organization__slug')
    ordering = ('-updated_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('role',)
    
    def user_email(self, obj):
        return obj.user.email
    
    def user_name(self, obj):
        return obj.user.full_name
    
    def organization_name(self, obj):
        return obj.organization.name
    
    user_email.short_description = "Email"
    user_email.admin_order_field = 'user__email'
    user_name.short_description = "Name"
    user_name.admin_order_field = 'user__full_name'
    organization_name.short_description = "Organization"
    organization_name.admin_order_field = 'organization__name'


@admin.register(CertificateAuthority)
class CertificateAuthorityAdmin(admin.ModelAdmin):
    list_display = ('organization', 'expires_at', 'revoked', 'created_at')
    list_filter = ('revoked', 'created_at', 'expires_at')
    search_fields = ('organization__name',)
    ordering = ('-created_at',)
    readonly_fields = ('ca_cert', 'ca_key', 'created_at')
    fieldsets = (
        (None, {'fields': ('organization', 'expires_at', 'revoked')}),
        ('Certificate Details', {'fields': ('ca_cert', 'ca_key'), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('ca', 'cert_type', 'nebula_ip', 'expires_at', 'revoked', 'created_at')
    list_filter = ('cert_type', 'revoked', 'created_at', 'expires_at')
    search_fields = ('ca__organization__name', 'nebula_ip')
    ordering = ('-created_at',)
    readonly_fields = ('cert', 'key', 'created_at')
    fieldsets = (
        (None, {'fields': ('ca', 'cert_type', 'nebula_ip', 'expires_at', 'revoked')}),
        ('Certificate Details', {'fields': ('cert', 'key'), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )


@admin.register(SecurityGroup)
class SecurityGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'organization__name', 'description')
    ordering = ('name',)


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'cidr', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('name', 'organization__name', 'cidr')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'hostname', 'organization', 'nebula_ip', 'network', 'last_check_in')
    list_filter = ('created_at', 'last_check_in')
    search_fields = ('name', 'hostname', 'organization__name', 'nebula_ip')
    ordering = ('name',)
    filter_horizontal = ('security_groups',)
    readonly_fields = ('created_at', 'updated_at', 'last_check_in', 'config')
    fieldsets = (
        (None, {'fields': ('name', 'hostname', 'organization', 'network', 'nebula_ip')}),
        ('Security', {'fields': ('security_groups', 'certificate')}),
        ('Status', {'fields': ('last_check_in',)}),
        ('Configuration', {'fields': ('config',), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Lighthouse)
class LighthouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'hostname', 'organization', 'nebula_ip', 'public_ip', 'is_active', 'last_check_in')
    list_filter = ('is_active', 'created_at', 'last_check_in')
    search_fields = ('name', 'hostname', 'organization__name', 'nebula_ip', 'public_ip')
    ordering = ('name',)
    filter_horizontal = ('security_groups',)
    readonly_fields = ('created_at', 'updated_at', 'last_check_in')
    fieldsets = (
        (None, {'fields': ('name', 'hostname', 'organization', 'network', 'nebula_ip', 'public_ip')}),
        ('Security', {'fields': ('security_groups', 'certificate')}),
        ('Status', {'fields': ('last_check_in', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('id', 'entity_type', 'created_at', 'last_used', 'is_active')
    list_filter = ('entity_type', 'is_active', 'created_at', 'last_used')
    search_fields = ('id', 'node__name', 'lighthouse__name')
    ordering = ('-created_at',)
    readonly_fields = ('key_hash', 'created_at', 'last_used')
    fieldsets = (
        (None, {'fields': ('entity_type', 'node', 'lighthouse', 'is_active')}),
        ('Key Details', {'fields': ('key_hash',), 'classes': ('collapse',)}),
        ('Usage', {'fields': ('last_used',), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
