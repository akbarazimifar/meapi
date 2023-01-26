from datetime import datetime
from typing import TYPE_CHECKING
from meapi.models.me_model import MeModel
from meapi.utils.exceptions import FrozenInstance
from meapi.utils.helpers import parse_date
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me


class Notification(MeModel):
    """
    Represents a Notification from the app.
        - Notification could be new comment, new profile watch, new deleted, contact birthday, suggestion, etc.
        - `For more information about Notification <https://me.app/notifications/>`_

    Examples:

        >>> my_notifications = me.get_notifications()
        >>> notification = my_notifications[0][0]
        >>> notification.category
        'UPDATED_CONTACT'
        >>> notification.name
        'Mike Hannigan'
        >>> notification.new_name
        'Princess Consuela Banana-Hammock'
        >>> me.publish_comment(uuid=notification.uuid,your_comment="Hi *** bag!")
        <Comment id=678 status=waiting msg=Hi *** bag! author=Phoebe Buffay>


    Parameters:
        id (``int``):
            The id of the notification.
        created_at (`datetime``):
            Date of creation.
        modified_at (`datetime``):
            Date of last modification.
        is_read (``bool``):
            Whether the notification is read.
        sender (``str``):
            UUID of the sender of the notification.
        status (``str``):
            Status of the notification.
        delivery_method (``str``):
            Delivery method of the notification. Most likely ``push``.
        distribution_date (``datetime``):
            Date of distribution.
        category (``str``):
            Category of the notification.
        message_lang (``str``):
            Language of the notification, ``en``, ``he`` etc.
        message_subject (``str`` *optional*):
            Subject of the notification.
        message_body (``str`` *optional*):
            Body of the notification.
        context (``dict`` *optional*):
            The context of the notification: name, uuid, new_name, tag, profile_picture and more.

    Methods:

    .. automethod:: read
    """
    def __init__(self,
                 _client: 'Me',
                 id: int,
                 created_at: str,
                 modified_at: str,
                 is_read: bool,
                 sender: str,
                 status: str,
                 delivery_method: str,
                 distribution_date: str,
                 message_subject: str,
                 message_category: str,
                 message_body: str,
                 message_lang: str,
                 category: str,
                 context: dict = None
                 ):
        self.__client = _client
        self.id = id
        self.created_at: datetime = parse_date(created_at)
        self.modified_at: datetime = parse_date(modified_at)
        self.is_read = is_read
        self.sender = sender
        self.status = status
        self.delivery_method = delivery_method
        self.distribution_date: datetime = parse_date(distribution_date)
        self.message_subject = message_subject
        self.category = message_category or category
        self.message_body = message_body
        self.message_lang = message_lang
        self.context = context
        self.__init_done = True

    def __setattr__(self, key, value):
        if getattr(self, '_Notification__init_done', None):
            if key != 'is_read':
                raise FrozenInstance(self, key)
        return super().__setattr__(key, value)

    def read(self) -> bool:
        """
        Mark the notification as read.
            - The same as :py:func:`~meapi.Me.read_notification`.

        Returns:
            ``bool``: Whether the notification was marked as read.
        """
        if self.is_read:
            return True
        return self.__client.read_notification(self.id)
