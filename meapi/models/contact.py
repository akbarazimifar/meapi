from datetime import datetime
from typing import Union
from meapi.helpers import parse_date
from meapi.models.common import _CommonMethodsForUserContactProfile
from meapi.models.me_model import MeModel
from meapi.models.user import User


class Contact(MeModel, _CommonMethodsForUserContactProfile):
    def __init__(self,
                 _meobj,
                 name: Union[str, None] = None,
                 id: Union[int, None] = None,
                 picture: Union[None, None] = None,
                 user: Union[dict, None] = None,
                 suggested_as_spam: Union[int, None] = None,
                 is_permanent: Union[bool, None] = None,
                 is_pending_name_change: Union[bool, None] = None,
                 user_type: Union[str, None] = None,
                 phone_number: Union[int, None] = None,
                 cached: Union[bool, None] = None,
                 is_shared_location: Union[bool, None] = None,
                 created_at: Union[str, None] = None,
                 modified_at: Union[str, None] = None,
                 in_contact_list: Union[bool, None] = None,
                 is_my_contact: Union[bool, None] = None
                 ):
        self.__meobj = _meobj
        self.name = name
        self.id = id
        self.picture = picture
        self.user: User = User.new_from_json_dict(user)
        self.suggested_as_spam = suggested_as_spam
        self.is_permanent = is_permanent
        self.is_pending_name_change = is_pending_name_change
        self.user_type = user_type
        self.phone_number = phone_number
        self.cached = cached
        self.is_shared_location = is_shared_location
        self.created_at: Union[datetime, None] = parse_date(created_at)
        self.modified_at: Union[datetime, None] = parse_date(modified_at)
        self.in_contact_list = in_contact_list or is_my_contact
        super().__init__()

    def __repr__(self):
        return f"<Contact name={self.name} phone={self.phone_number} id={self.id}>"

    def __str__(self):
        return self.name or "Not found"
