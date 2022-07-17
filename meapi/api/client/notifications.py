from typing import Union, Tuple
from meapi.api.raw.notifications import *
from meapi.models.notification import Notification
from meapi.utils.exceptions import MeException
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me

notification_categories = {
    'names': ['JOINED_ME', 'CONTACT_ADD', 'UPDATED_CONTACT', 'DELETED_CONTACT', 'NEW_NAME_REQUEST', 'NEW_NAME_REQUEST_APPROVED'],
    'system': ['NAME_SUGGESTION_UPDATED', 'SPAM_SUGGESTION_APPROVED', 'TURN_ON_MUTUAL', 'NONE'],
    'comments': ['NEW_COMMENT', 'PUBLISHED_COMMENT', 'TURN_ON_COMMENTS'],
    'who_watch': ['WEEKLY_VISITS'],
    'birthday': ['BIRTHDAY'],
    'location': ['TURN_ON_LOCATION', 'SHARE_LOCATION'],
    'who_deleted': ['WEEKLY_DELETED']
}


class Notifications:
    """
    This class is not intended to create an instance's but only to be inherited by ``Me``.
    The separation is for order purposes only.
    """
    def __init__(self: 'Me'):
        raise MeException("Notifications class is not intended to create an instance's but only to be inherited by Me class.")

    def unread_notifications_count(self: 'Me') -> int:
        """
        Get count of unread notifications.

        :return: count of unread notifications.
        :rtype: ``int``
        """
        return unread_notifications_count_raw(self)['count']

    def get_notifications(self: 'Me',
                          page_number: int = 1,
                          results_limit: int = 20,
                          names_filter: bool = False,
                          system_filter: bool = False,
                          comments_filter: bool = False,
                          who_watch_filter: bool = False,
                          who_deleted_filter: bool = False,
                          birthday_filter: bool = False,
                          location_filter: bool = False
                          ) -> Tuple[int, List[Notification]]:
        """
        Get app notifications: new names, birthdays, comments, watches, deletes, location shares and system notifications.

        :param page_number: :py:func:`get_notifications`.``count`` / ``page_size``. *Default:* ``1``.
        :type page_number: int
        :param results_limit: Limit of notifications in each page. *Default:* ``20``.
        :type results_limit: ``int``
        :param names_filter: New names, deletes, joined, renames, rename requests. *Default:* ``False``.
        :type names_filter: ``bool``
        :param system_filter: System notifications: spam reports, your name requests, suggestions to turn on mutual contacts. *Default:* ``False``.
        :type system_filter: ``bool``
        :param comments_filter: Comments notifications: new comments, published comments and suggestions to turn on comments (See :py:func:`get_comments`). *Default:* ``False``.
        :type comments_filter: ``bool``
        :param who_watch_filter: Who watched your profile (See :py:func:`who_watched`). *Default:* ``False``.
        :type who_watch_filter: ``bool``
        :param who_deleted_filter: Who deleted you from his contacts (See :py:func:`who_deleted`). *Default:* ``False``.
        :type who_deleted_filter: ``bool``
        :param birthday_filter: Contacts birthdays. *Default:* ``False``.
        :type birthday_filter: ``bool``
        :param location_filter: Shared locations: suggestions to turn on location, locations that shared with you. *Default:* ``False``.
        :type location_filter: ``bool``
        :return: Tuple of count of notifications and list of :py:obj:`~meapi.models.notification.Notification` objects.
        :rtype: Tuple[``int``, List[:py:obj:`~meapi.models.notification.Notification`]]
        """
        args = locals()
        filters = []
        for fil, val in args.items():
            if val and fil.endswith('filter'):
                filters = [*filters, *notification_categories[fil.replace("_filter", "")]]
        results = get_notifications_raw(self, page_number, results_limit, filters)

        return results['count'], [Notification.new_from_dict(notification, _client=self,
                                                             **notification.pop('context')) for notification in results['results']]

    def read_notification(self: 'Me', notification_id: Union[int, str]) -> bool:
        """
        Mark notification as read.

        :param notification_id: Notification id from :py:func:`get_notifications`.
        :type notification_id: ``int`` | ``str``
        :return: Is read success.
        :rtype: bool
        """
        return read_notification_raw(self, int(notification_id))['is_read']
