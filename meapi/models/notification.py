from datetime import datetime
from typing import TYPE_CHECKING
from meapi.models.me_model import MeModel
from meapi.utils.exceptions import MeException
from meapi.utils.helpers import parse_date
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me


class Notification(MeModel):
    """
    Represents a Notification from the app.
        - Notification could be new comment, new profile watch, new deleted, contact birthday, suggestion, etc.
        - `For more information about Notification <https://me.app/notifications/>`_

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
        - CONTEXT -
        phone_number (``int`` *optional*):
            Phone number of the message context.
        name (``str`` *optional*):
            Name of the subject.
        uuid (``str`` *optional*):
            UUID of the message context.
        new_name (``str`` *optional*):
            New name of the message context.
        profile_picture (``str`` *optional*):
            Profile picture of the message context.
        tag (``str`` *optional*):
            Tag of the message context.
        profile_view_count (``int`` *optional*):
            Number of views of the profile watcher.

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
                 phone_number: int = None,
                 name: str = None,
                 uuid: str = None,
                 new_name: str = None,
                 notification_id: int = None,
                 profile_picture: str = None,
                 tag: str = None,
                 profile_view_count: int = None,
                 ):
        self.__client = _client
        self.id = id or notification_id
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
        # context:
        self.name = name
        self.uuid = uuid
        self.new_name = new_name
        self.phone_number = phone_number
        self.profile_picture = profile_picture
        self.tag = tag
        self.profile_view_count = profile_view_count
        self.__init_done = True

    def __setattr__(self, key, value):
        if getattr(self, '_Notification__init_done', None):
            if key != 'is_read':
                raise MeException("You can't change this attr!")
        return super().__setattr__(key, value)

    def __repr__(self):
        return f"<Notification category={self.category} id={self.id}>"

    def __str__(self):
        return str(self.id)

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
