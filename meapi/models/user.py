from typing import Union
from meapi.models.common import _CommonMethodsForUserContactProfile
from meapi.models.me_model import MeModel


class User(MeModel, _CommonMethodsForUserContactProfile):
    def __init__(self,
                 _meobj,
                 email: Union[str, None] = None,
                 profile_picture: Union[str, None] = None,
                 first_name: Union[str, None] = None,
                 last_name: Union[str, None] = None,
                 gender: Union[str, None] = None,
                 uuid: Union[str, None] = None,
                 is_verified: Union[bool, None] = None,
                 phone_number: Union[int, None] = None,
                 slogan: Union[str, None] = None,
                 is_premium: Union[bool, None] = None,
                 verify_subscription: Union[bool, None] = None,
                 id: Union[int, None] = None,
                 comment_count: Union[int, None] = None,
                 location_enabled: Union[bool, None] = None,
                 distance: Union[float, None] = None
                 ):
        self.__meobj = _meobj
        self.email = email
        self.profile_picture = profile_picture
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.uuid = uuid
        self.is_verified = is_verified
        self.phone_number = phone_number
        self.slogan = slogan
        self.is_premium = is_premium
        self.verify_subscription = verify_subscription
        self.id = id
        self.comment_count = comment_count
        self.location_enabled = location_enabled
        self.distance = distance
        super().__init__()

    @property
    def name(self):
        return str(self.first_name or '' + ((' ' if self.first_name else '') + self.last_name or ''))

    def __repr__(self):
        return f"<User name={self.first_name} {self.last_name or ''}>"

    def __str__(self):
        return self.uuid