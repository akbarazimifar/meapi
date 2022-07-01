from typing import Union
from meapi.models.me_model import MeModel
from meapi.utils.exceptions import MeException
from meapi.utils.helpers import parse_date


class Notification(MeModel):
    """

    - `For more information about Notification <https://me.app/notifications/>`_
    """
    def __init__(self,
                 _client,
                 id: Union[int, None] = None,
                 created_at: Union[str, None] = None,
                 modified_at: Union[str, None] = None,
                 is_read: Union[bool, None] = None,
                 sender: Union[str, None] = None,
                 status: Union[str, None] = None,
                 delivery_method: Union[str, None] = None,
                 distribution_date: Union[str, None] = None,
                 message_subject: Union[str, None] = None,
                 message_category: Union[str, None] = None,
                 message_body: Union[str, None] = None,
                 message_lang: Union[str, None] = None,
                 context: Union[dict, None] = None,
                 ):
        self.__client = _client
        self.id = id
        self.created_at = parse_date(created_at)
        self.modified_at = parse_date(modified_at)
        self.is_read = is_read
        self.sender = sender
        self.status = status
        self.delivery_method = delivery_method
        self.distribution_date = parse_date(distribution_date)
        self.message_subject = message_subject
        self.message_category = message_category
        self.message_body = message_body
        self.message_lang = message_lang
        self.context = NotificationContext.new_from_json_dict(context, notification_id=self.id)

        self.__init_done = True

    def __setattr__(self, key, value):
        if getattr(self, '_Notification__init_done', None):
            if key != 'is_read':
                raise MeException("You can't change this attr!")
        return super().__setattr__(key, value)

    def __repr__(self):
        return f"<Notification category={self.message_category} id={self.id}>"

    def __str__(self):
        return str(self.id)

    def read(self) -> bool:
        if self.is_read:
            raise MeException("This notifications already mark as read!")
        if self.__client.read_notification(self.id):
            self.is_read = True
            return True
        return False


class NotificationContext(MeModel):
    def __init__(self,
                 name: Union[str, None] = None,
                 uuid: Union[str, None] = None,
                 category: Union[str, None] = None,
                 new_name: Union[str, None] = None,
                 phone_number: Union[int, None] = None,
                 notification_id: Union[int, None] = None,
                 profile_picture: Union[str, None] = None,
                 tag: Union[str, None] = None
                 ):
        self.name = name
        self.uuid = uuid
        self.category = category
        self.new_name = new_name
        self.phone_number = phone_number
        self.notification_id = notification_id
        self.profile_picture = profile_picture
        self.tag = tag
        super().__init__()
