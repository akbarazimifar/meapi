from typing import TYPE_CHECKING
from meapi.utils.exceptions import MeException, FrozenInstance
from meapi.models.me_model import MeModel
from meapi.utils.helpers import parse_date
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me


class Settings(MeModel):
    """
    Manage your social, notification and app settings.
        - You can edit your settings by simply assigning a new value to the attribute.
        - Modifiable attributes are marked with ``modifiable``.
        - For more information about the modifiable attributes, see :py:func:`~meapi.Me.change_settings`.

    Example:
        >>> # Take control of your privacy:
        >>> my_settings = me.get_settings()
        >>> my_settings.who_watched_enabled = False
        >>> my_settings.who_deleted_enabled = False
        >>> my_settings.mutual_contacts_available = False
        >>> my_settings.comments_enabled = False
        >>> my_settings.location_enabled = False

    Parameters:
        who_deleted_enabled (``bool`` *modifiable*):
            If ``True``, other users can see if you deleted them from your contact book
                - The users can see it only if they ``is_premium`` users, or by using ``meapi`` ;)
                - Must be enabled in order to use :py:func:`~meapi.Me.who_deleted`.

        who_watched_enabled (``bool`` *modifiable*):
            If ``True``, other users can see if you watch their profile.
                - The users can see it only if they ``is_premium`` users, or by using ``meapi`` ;)
                - Must be enabled in order to use :py:func:`~meapi.Me.who_watched`.

        comments_enabled (``bool`` *modifiable*):
            Allow other users to :py:func:`~meapi.Me.publish_comment` on your profile.
                - You always need to :py:func:`~meapi.Me.approve_comment` before they are published.
                - You can block spesfic users from commenting on your profile with :py:func:`~meapi.Me.block_comments`.

        location_enabled (``bool`` *modifiable*):
            Allow other users ask to see your location.

        mutual_contacts_available (``bool`` *modifiable*):
            If ``True``, other users can see your mutual contacts.
                - See :py:func:`~meapi.Me.friendship` for more information.

        notifications_enabled (``bool`` *modifiable*):
            Get notify on new messages.
                - See :py:func:`~meapi.Me.get_notifications` for more information.

        who_deleted_notification_enabled (``bool`` *modifiable*):
            Get notify on who deleted you from your contact book.
                - You will only receive notifications if ``who_deleted_enabled`` is ``True``.

        who_watched_notification_enabled (``bool`` *modifiable*):
            Get notify on who watched your profile.
                - You will only receive notifications if ``who_watched_enabled`` is ``True``.

        comments_notification_enabled (``bool`` *modifiable*):
            Get notify on new comments, likes etc.
                - You will only receive notifications if ``comments_enabled`` is ``True``.

        birthday_notification_enabled (``bool`` *modifiable*):
            Get notify on contact birthday.

        distance_notification_enabled (``bool`` *modifiable*):
            Get notify on contacts distance.

        names_notification_enabled (``bool`` *modifiable*):
            Get notify when someone saved you in is contacts book, new joined contacts to Me, new rename approve and more.

        system_notification_enabled (``bool`` *modifiable*):
            Get notify on system messages: spam reports, mutual requests and more.

        contact_suspended (``bool``):
            If `True`, the contact is suspended.

        language (``str`` *modifiable*):
            Language of the notifications.

        last_backup_at (:py:obj:`~datetime.datetime` *optional*):
            Last backup time.

        last_restore_at (:py:obj:`~datetime.datetime` *optional*):
            Last restore time.

        spammers_count (``int``):
            Number of spammers.
    """
    def __init__(self,
                 _client: 'Me',
                 birthday_notification_enabled: bool = None,
                 comments_enabled: bool = None,
                 comments_notification_enabled: bool = None,
                 contact_suspended: bool = None,
                 distance_notification_enabled: bool = None,
                 language: str = None,
                 last_backup_at: str = None,
                 last_restore_at: str = None,
                 location_enabled: bool = None,
                 mutual_contacts_available: bool = None,
                 names_notification_enabled: bool = None,
                 notifications_enabled: bool = None,
                 spammers_count: int = None,
                 system_notification_enabled: bool = None,
                 who_deleted_enabled: bool = None,
                 who_deleted_notification_enabled: bool = None,
                 who_watched_enabled: bool = None,
                 who_watched_notification_enabled: bool = None,
                 caller_id_type: int = None
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
        self.caller_id_type = caller_id_type
        self.__client = _client
        self.__init_done = True

    def __setattr__(self, key, value):
        if getattr(self, '_Settings__init_done', None):
            if key in ('spammers_count', 'last_backup_at', 'last_restore_at', 'contact_suspended'):
                raise FrozenInstance(self, key, f"You can't change this setting {key}!")
            is_success, new = self.__client.change_settings(**{key: value})
            if is_success and getattr(new, key, None) != value:
                raise MeException(f"{key} not updated!")
        return super().__setattr__(key, value)
