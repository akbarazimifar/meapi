from typing import Union, Tuple, List, TYPE_CHECKING
from meapi.api.raw.notifications import *
from meapi.models.notification import Notification

if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me

notification_categories = {
    'names': ['JOINED_ME', 'CONTACT_ADD', 'UPDATED_CONTACT', 'DELETED_CONTACT', 'NEW_NAME_REQUEST',
              'NEW_NAME_REQUEST_APPROVED'],
    'system': ['NAME_SUGGESTION_UPDATED', 'SPAM_SUGGESTION_APPROVED', 'TURN_ON_MUTUAL', 'NONE'],
    'comments': ['NEW_COMMENT', 'PUBLISHED_COMMENT', 'TURN_ON_COMMENTS'],
    'who_watch': ['WEEKLY_VISITS'],
    'birthday': ['BIRTHDAY'],
    'location': ['TURN_ON_LOCATION', 'SHARE_LOCATION'],
    'who_deleted': ['WEEKLY_DELETED']
}


class NotificationsMethods:
    """
    This class is not intended to create an instance's but only to be inherited by ``Me``.
    The separation is for order purposes only.
    """

    def __init__(self: 'Me'):
        raise TypeError(
            "Notifications class is not intended to create an instance's but only to be inherited by Me class."
        )

    def unread_notifications_count(self: 'Me') -> int:
        """
        Get count of unread notifications.

        :return: count of unread notifications.
        :rtype: ``int``
        """
        return unread_notifications_count_raw(client=self)['count']

    def get_notifications(self: 'Me',
                          page: int = 1,
                          limit: int = 20,
                          names_filter: bool = False,
                          system_filter: bool = False,
                          comments_filter: bool = False,
                          who_watch_filter: bool = False,
                          who_deleted_filter: bool = False,
                          birthday_filter: bool = False,
                          location_filter: bool = False
                          ) -> List[Notification]:
        """
        Get app notifications: new names, birthdays, comments, watches, deletes, location shares and system notifications.

        :param page: :py:func:`get_notifications`.``count`` / ``page_size``. *Default:* ``1``.
        :type page: ``int``
        :param limit: Limit of notifications in each page. *Default:* ``20``.
        :type limit: ``int``
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
        :return: List of :py:obj:`~meapi.models.notification.Notification` objects.
        :rtype: List[:py:obj:`~meapi.models.notification.Notification`]
        """
        args = locals()
        filters = []
        for fil, val in args.items():
            if val and fil.endswith('filter'):
                filters = [*filters, *notification_categories[fil.replace("_filter", "")]]
        results = get_notifications_raw(client=self, page_number=page, results_limit=limit, categories=filters)
        return [Notification.new_from_dict(notification, _client=self) for notification in results['results']]

    def read_notification(self: 'Me', notification_id: Union[int, str, Notification]) -> bool:
        """
        Mark notification as read.

        :param notification_id: Notification id from :py:func:`get_notifications` or :py:obj:`~meapi.models.notification.Notification` object.
        :type notification_id: ``int`` | ``str`` | :py:obj:`~meapi.models.notification.Notification`
        :return: Is read success.
        :rtype: ``bool``
        """
        if isinstance(notification_id, Notification):
            notification_id = notification_id.id
        return read_notification_raw(client=self, notification_id=int(notification_id))['is_read']
