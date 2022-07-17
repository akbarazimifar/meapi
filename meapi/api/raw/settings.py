from typing import TYPE_CHECKING
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me


def get_settings_raw(client: 'Me') -> dict:
    """
    Get current settings.

    :return: Dict with settings.
    :rtype: ``dict``

    Example::

        {
            "birthday_notification_enabled": True,
            "comments_enabled": True,
            "comments_notification_enabled": True,
            "contact_suspended": False,
            "distance_notification_enabled": True,
            "language": "iw",
            "last_backup_at": None,
            "last_restore_at": None,
            "location_enabled": True,
            "mutual_contacts_available": True,
            "names_notification_enabled": True,
            "notifications_enabled": True,
            "spammers_count": 24615,
            "system_notification_enabled": True,
            "who_deleted_enabled": True,
            "who_deleted_notification_enabled": True,
            "who_watched_enabled": True,
            "who_watched_notification_enabled": True,
        }
    """
    return client._make_request('get', '/main/settings/')


def change_settings_raw(client: 'Me', **kwargs) -> dict:
    """
    Change current settings.

    :param kwargs: Dict with new settings.
    :return: Dict with settings.
    :rtype: ``dict``

    Example::

        {
            "birthday_notification_enabled": True,
            "comments_enabled": True,
            "comments_notification_enabled": True,
            "contact_suspended": False,
            "distance_notification_enabled": True,
            "language": "iw",
            "last_backup_at": None,
            "last_restore_at": None,
            "location_enabled": True,
            "mutual_contacts_available": True,
            "names_notification_enabled": True,
            "notifications_enabled": True,
            "system_notification_enabled": True,
            "who_deleted_enabled": True,
            "who_deleted_notification_enabled": True,
            "who_watched_enabled": True,
            "who_watched_notification_enabled": True,
        }
    """
    return client._make_request('patch', '/main/settings/', kwargs)
