from django.db import migrations


def create_initial_rbac_data(apps, schema_editor):
    """
    Creates the initial data required for the RBAC system to function:
    1. Foundational Actions (create, read, update, delete).
    2. Default and Admin Roles.
    3. (Optional but recommended) Foundational Resources.
    4. Assigns all existing permissions to the Admin role.
    """
    # Get models from the versioned app registry
    Role = apps.get_model("rbac", "Role")
    Resource = apps.get_model("rbac", "Resource")
    Action = apps.get_model("rbac", "Action")
    Permission = apps.get_model("rbac", "Permission")
    RolePermission = apps.get_model("rbac", "RolePermission")

    # --- 1. Create Foundational Actions ---
    actions_to_create = [
        {"code": "create", "description": "Allows creating a new item."},
        {"code": "read", "description": "Allows viewing items."},
        {"code": "update", "description": "Allows editing an existing item."},
        {"code": "delete", "description": "Allows deleting an item."},
    ]
    for action_data in actions_to_create:
        Action.objects.get_or_create(code=action_data["code"], defaults=action_data)

    # --- 2. (Optional) Create Foundational Resources ---
    # It's often useful to create the main resources your app will have.
    resources_to_create = [
        {"code": "projects", "description": "Company projects and tasks."},
        {"code": "invoices", "description": "Customer billing and invoices."},
        {"code": "users", "description": "System user accounts."},
    ]
    for resource_data in resources_to_create:
        Resource.objects.get_or_create(
            code=resource_data["code"], defaults=resource_data
        )

    # --- 3. Auto-create all possible Permissions from existing Actions & Resources ---
    all_actions = Action.objects.all()
    all_resources = Resource.objects.all()
    for resource in all_resources:
        for action in all_actions:
            Permission.objects.get_or_create(resource=resource, action=action)

    # --- 4. Create Default and Admin Roles ---
    Role.objects.get_or_create(
        name="Default",
        defaults={
            "description": "Default permissions for new users."
            " This role is assigned automatically."
        },
    )

    admin_role, created = Role.objects.get_or_create(
        name="Admin",
        defaults={
            "description": "Provides full access to the system for administrators."
        },
    )

    # --- 5. Assign ALL Permissions to the Admin Role ---
    # This makes the 'Admin' role a true super-role within your RBAC system.
    if created or not admin_role.role_perms.exists():
        all_permissions = Permission.objects.all()
        for perm in all_permissions:
            RolePermission.objects.get_or_create(role=admin_role, permission=perm)


class Migration(migrations.Migration):
    dependencies = [
        ("rbac", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_initial_rbac_data),
    ]
