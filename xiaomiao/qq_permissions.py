from collections.abc import Iterable


def has_manage_permission(
    user_id: int | str,
    *,
    manage_users: Iterable[int | str],
    super_users: Iterable[int | str],
    root_users: Iterable[int | str],
) -> bool:
    user = str(user_id)
    return (
        user in _normalize_ids(manage_users)
        or user in _normalize_ids(super_users)
        or user in _normalize_ids(root_users)
    )


def has_super_permission(
    user_id: int | str,
    *,
    super_users: Iterable[int | str],
    root_users: Iterable[int | str],
) -> bool:
    user = str(user_id)
    return user in _normalize_ids(super_users) or user in _normalize_ids(root_users)


def _normalize_ids(user_ids: Iterable[int | str]) -> set[str]:
    return {str(user_id).strip() for user_id in user_ids if str(user_id).strip()}
