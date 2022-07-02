from typing import Union
from meapi.utils.exceptions import MeException
from meapi.models.me_model import MeModel
from meapi.utils.helpers import parse_date


class Settings(MeModel):
    """
    Manage your social, notification and app settings.
        - You can edit your settings by simply assigning a new value to the attribute.

    Example:
        .. code-block:: python

            # Enable who_watched just to check who watched -
            # - your profile you and then disable it back.
            my_settings = me.get_settings()
            my_settings.who_watched_enabled = True
            for watcher in me.who_watched():
                print(watcher.user.name)
            my_settings.who_watched_enabled = False

    Parameters:
        who_deleted_enabled (``bool``):
            If `True`, other users can see if you deleted them from your contact book.
                - Must be enabled in order to use :py:func:`~meapi.Me.who_deleted`.

        who_watched_enabled (``bool``):
            If `True`, other users can see if you watch their profile.
                - Must be enabled in order to use :py:func:`~meapi.Me.who_watched`.

        comments_enabled (``bool``):
            Allow other users to publish comments on your profile (You always need to approve them before they are published).

        location_enabled (``bool``):
            Allow other users ask to see your location.

        mutual_contacts_available (``bool``):
            If `True`, other users can see your mutual contacts.

        notifications_enabled (``bool``):
            Get notify on new messages.

        who_deleted_notification_enabled (``bool``):
            Get notify on who deleted you from your contact book.

        who_watched_notification_enabled (``bool``):
            Get notify on who watched your profile.

        comments_notification_enabled (``bool``):
            Get notify on new comments, likes etc.

        birthday_notification_enabled (``bool``):
            Get notify on contact birthday.

        distance_notification_enabled (``bool``):
            Get notify on contacts distance.

        names_notification_enabled (``bool``):
            Get notify when someone saved you in is contacts book, new joined contacts to Me, new rename approve and more.

        system_notification_enabled (``bool``):
            Get notify on system messages: spam reports, mutual requests and more.

        contact_suspended (``bool``):
            If `True`, the contact is suspended.

        language (str):
            Language of the notifications.

        last_backup_at (:py:obj:`~datetime.datetime` *optional*):
            Last backup time.

        last_restore_at (:py:obj:`~datetime.datetime` *optional*):
            Last restore time.

        spammers_count (``int``):
            Number of spammers.
    """
    def __init__(self,
                 _client,
                 birthday_notification_enabled: Union[bool, None] = None,
                 comments_enabled: Union[bool, None] = None,
                 comments_notification_enabled: Union[bool, None] = None,
                 contact_suspended: Union[bool, None] = None,
                 distance_notification_enabled: Union[bool, None] = None,
                 language: Union[str, None] = None,
                 last_backup_at: Union[str, None] = None,
                 last_restore_at: Union[str, None] = None,
                 location_enabled: Union[bool, None] = None,
                 mutual_contacts_available: Union[bool, None] = None,
                 names_notification_enabled: Union[bool, None] = None,
                 notifications_enabled: Union[bool, None] = None,
                 spammers_count: Union[int, None] = None,
                 system_notification_enabled: Union[bool, None] = None,
                 who_deleted_enabled: Union[bool, None] = None,
                 who_deleted_notification_enabled: Union[bool, None] = None,
                 who_watched_enabled: Union[bool, None] = None,
                 who_watched_notification_enabled: Union[bool, None] = None,
                 ):
        self.birthday_notification_enabled = birthday_notification_enabled
        self.comments_enabled = comments_enabled
        self.comments_notification_enabled = comments_notification_enabled
        self.contact_suspended = contact_suspended
        self.distance_notification_enabled = distance_notification_enabled
        self.language = language
        self.last_backup_at = parse_date(last_backup_at)
        self.last_restore_at = parse_date(last_restore_at)
        self.location_enabled = location_enabled
        self.mutual_contacts_available = mutual_contacts_available
        self.names_notification_enabled = names_notification_enabled
        self.notifications_enabled = notifications_enabled
        self.spammers_count = spammers_count
        self.system_notification_enabled = system_notification_enabled
        self.who_deleted_enabled = who_deleted_enabled
        self.who_deleted_notification_enabled = who_deleted_notification_enabled
        self.who_watched_enabled = who_watched_enabled
        self.who_watched_notification_enabled = who_watched_notification_enabled
        self.__client = _client
        self.__init_done = True

    def __repr__(self):
        return f"<Settings lang={self.language}>"

    def __setattr__(self, key, value):
        if getattr(self, '_Settings__init_done', None):
            if key not in ['spammers_count', 'last_backup_at', 'last_restore_at', 'contact_suspended']:
                if key == 'language':
                    if isinstance(value, str) and len(value) == 2 and value.isalpha():
                        pass
                if not isinstance(value, bool):
                    raise MeException(f"{str(key)} value must be a bool type!")
            else:
                raise MeException("You can't change this setting!")
            res = self.__client.change_settings(**{key: value})
            if res[0] and getattr(res[1], key, None) != value:
                raise MeException(f"{key} not updated!")
        return super().__setattr__(key, value)
