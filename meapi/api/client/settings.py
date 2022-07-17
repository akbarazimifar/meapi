from typing import Tuple
from meapi.utils.exceptions import MeException
from meapi.models import settings
from meapi.api.raw.settings import *
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me


class Settings:
    """
    This class is not intended to create an instance's but only to be inherited by ``Me``.
    The separation is for order purposes only.
    """
    def __init__(self: 'Me'):
        raise MeException("Settings class is not intended to create an instance's but only to be inherited by Me class.")

    def get_settings(self: 'Me') -> settings.Settings:
        """
        Get current settings.

        :return: :py:class:`meapi.models.settings.Settings` object.
        :rtype: :py:class:`meapi.models.settings.Settings`
        """
        return settings.Settings.new_from_dict(get_settings_raw(self), _client=self)

    def change_settings(self: 'Me',
                        mutual_contacts_available: bool = None,
                        who_watched_enabled: bool = None,
                        who_deleted_enabled: bool = None,
                        comments_enabled: bool = None,
                        location_enabled: bool = None,
                        language: str = None,
                        who_deleted_notification_enabled: bool = None,
                        who_watched_notification_enabled: bool = None,
                        distance_notification_enabled: bool = None,
                        system_notification_enabled: bool = None,
                        birthday_notification_enabled: bool = None,
                        comments_notification_enabled: bool = None,
                        names_notification_enabled: bool = None,
                        notifications_enabled: bool = None,
                        ) -> Tuple[bool, settings.Settings]:
        """
        Change social, app and notification settings.

        :param mutual_contacts_available: Show common contacts between users. *Default:* ``None``.
        :type mutual_contacts_available: ``bool``
        :param who_watched_enabled: Users will be notified that you have viewed their profile. *Default:* ``None``.
            - They will only be able to get information about you if they are premium users (``is_premium`` = True in :py:func:`get_profile`) or, by using this libary....
            - This setting must be True if you want to use :py:func:`who_watched` method.
        :type who_watched_enabled: ``bool``
        :param who_deleted_enabled: Users will be notified that you have deleted them from your contact book. *Default:* ``None``.
            - They will only be able to get information about you if they are premium users (``is_premium`` = True in :py:func:`get_profile`) or, by using this libary....
            - This setting must be True if you want to use :py:func:`who_deleted` method.
        :type who_deleted_enabled: ``bool``
        :param comments_enabled: Allow users to publish comment (:py:func:`publish_comment`) in your profile. *Default:* ``None``.
            - Comments will not be posted until you approve them with :py:func:`approve_comment`.
        :type comments_enabled: ``bool``
        :param location_enabled: Allow shared locations. *Default:* ``None``.
        :type location_enabled: ``bool``
        :param language: lang code: ``iw``, ``en``, etc. (For notifications text). *Default:* ``None``.
        :type language: ``str``
        :param who_deleted_notification_enabled: *Default:* ``None``.
        :type who_deleted_notification_enabled: ``bool``
        :param who_watched_notification_enabled: *Default:* ``None``.
        :type who_watched_notification_enabled: ``bool``
        :param distance_notification_enabled: *Default:* ``None``.
        :type distance_notification_enabled: ``bool``
        :param system_notification_enabled: *Default:* ``None``.
        :type system_notification_enabled: ``bool``
        :param birthday_notification_enabled: *Default:* ``None``.
        :type birthday_notification_enabled: ``bool``
        :param comments_notification_enabled: *Default:* ``None``.
        :type comments_notification_enabled: ``bool``
        :param names_notification_enabled: *Default:* ``None``.
        :type names_notification_enabled: ``bool``
        :param notifications_enabled: *Default:* ``None``.
        :type notifications_enabled: ``bool``
        :return: Tuple: is success, :py:class:`meapi.models.settings.Settings` object.
        :rtype: Tuple[``bool``, :py:class:`meapi.models.settings.Settings`]
        """
        args = locals()
        del args['self']
        body = {setting: value for setting, value in args.items() if value is not None}
        if not body:
            raise MeException("You need to change at least one setting!")
        results = change_settings_raw(self, **body)
        success = True
        for key, value in body.items():
            if results[key] != value:
                success = False
        return success, settings.Settings.new_from_dict(results, _client=self)
