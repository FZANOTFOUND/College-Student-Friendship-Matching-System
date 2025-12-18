PERMISSION = {
    "user": 0,
    "admin": 1
}


def get_permission(role):
    if isinstance(role, int):
        return max(0, role)
    if isinstance(role, str):
        role = role.lower()
        return PERMISSION.get(role, 0)
    return 0
