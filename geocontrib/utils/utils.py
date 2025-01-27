from django.db.models import Q

def apply_permissions_to_queryset(user, queryset):
    """
    Applique les permissions au queryset en fonction du rôle de l'utilisateur et des statuts autorisés.
    """
    permissions = {
        'Administrateur projet': ['draft', 'pending', 'published', 'archived'],
        'Modérateur': ['draft', 'pending', 'published'],
        'Super Contributeur': ['draft', 'pending', 'published'],
        'Contributeur': ['draft', 'pending', 'published'],
    }

    if user.is_superuser:
        return queryset

    user_status = getattr(user, 'status', None)
    allowed_statuses = permissions.get(user_status, [])

    if user_status == 'Contributeur':
        queryset = queryset.filter(
            Q(creator__first_name=user.first_name) &
            Q(creator__last_name=user.last_name) &
            Q(status__in=allowed_statuses)
        )
    elif user_status in permissions:
        queryset = queryset.filter(
            Q(project__admins=user) |
            Q(project__moderators=user) |
            Q(status__in=allowed_statuses)
        )
    else:
        queryset = queryset.none()

    return queryset
