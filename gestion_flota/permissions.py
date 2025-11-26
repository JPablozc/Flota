from django.contrib.auth.models import Group

# Nombres de los grupos/roles que usaremos
ROLE_ADMIN = "Flota Admin"
ROLE_OPERADOR = "Flota Operador"
ROLE_LECTURA = "Flota Lectura"  # opcional, para marcar usuarios de solo lectura


def _in_group(user, group_name: str) -> bool:
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


def user_is_admin(user) -> bool:
    """
    Admin: superuser o miembro del grupo 'Flota Admin'.
    """
    return user.is_superuser or _in_group(user, ROLE_ADMIN)


def user_is_operador(user) -> bool:
    """
    Operador: Admin o miembro del grupo 'Flota Operador'.
    (Puede crear/editar, pero no borrar.)
    """
    return user_is_admin(user) or _in_group(user, ROLE_OPERADOR)


def user_is_lectura(user) -> bool:
    """
    Solo lectura: miembro del grupo 'Flota Lectura' o sin grupo de flota.
    """
    # Si es admin u operador, NO es solo lectura
    if user_is_operador(user):
        return False
    # Si está en el grupo de lectura o no tiene ninguno de flota, lo consideramos lectura
    if _in_group(user, ROLE_LECTURA):
        return True
    return True  # por defecto, si no tiene rol, lectura
