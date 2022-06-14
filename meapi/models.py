import inspect
import json
from abc import ABCMeta
from datetime import datetime
from typing import Union, Any, List


def parse_datetime(datetime_str: str) -> Union[datetime, None]:
    return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S%z') if datetime_str else datetime_str


def get_object(cls, data: Union[dict, Any]):
    if not data:
        return None
    if isinstance(data, dict):
        cls_attrs = cls._init_parameters.keys()
        for key in data.copy():
            if key not in cls_attrs:
                del data[key]
        return cls(**data)
    return cls(data)


class _ParameterReader(ABCMeta):
    """Internal class to get class init parameters"""

    def __init__(cls, *args, **kwargs):
        parameters = inspect.signature(cls.__init__).parameters
        parameters = {key: value for key, value in parameters.items() if key not in ['self', 'args', 'kwargs']}
        try:
            cls._init_parameters = cls.__bases__[0]._init_parameters.copy()
            cls._init_parameters.update(parameters)
        except AttributeError:
            cls._init_parameters = parameters

        super().__init__(*args, **kwargs)


class MeModel(metaclass=_ParameterReader):
    """ Base class from which all Me models will inherit. """

    # def __init__(self, _index=0):
    #     self._index = _index

    def __str__(self):
        """ Returns a string representation of MeModel. By default
        this is the same as as_json_string(). """
        return self.as_json_string()

    def __eq__(self, other):
        return other and self.as_dict() == other.as_dict()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        if hasattr(self, 'id'):
            return hash(self.id)
        else:
            raise TypeError('unhashable type: {} (no id attribute)'.format(type(self)))

    def as_json_string(self, ensure_ascii=True):
        return json.dumps(self.as_dict(), ensure_ascii=ensure_ascii, sort_keys=True)

    def as_dict(self):
        data = {}
        for (key, value) in self.__dict__.items():
            if isinstance(getattr(self, key, None), (list, tuple, set)):
                data[key] = list()
                for subobj in getattr(self, key, None):
                    if getattr(subobj, 'as_dict', None):
                        data[key].append(subobj.as_dict())
                    else:
                        data[key].append(subobj)

            elif getattr(getattr(self, key, None), 'as_dict', None):
                data[key] = getattr(self, key).as_dict()

            elif isinstance(value, datetime):
                data[key] = str(getattr(self, key, None))

            elif getattr(self, key, None):
                data[key] = getattr(self, key, None)

        return data

    @classmethod
    def new_from_json_dict(cls, data: dict, **kwargs):
        json_data = data.copy()
        if kwargs:
            for key, val in kwargs.items():
                json_data[key] = val

        c = cls(**json_data)
        c._json = data
        return c


class Profile(MeModel):
    def __init__(self, comments_blocked: bool, is_he_blocked_me: bool, is_permanent: bool, is_shared_location: bool,
                 last_comment: None, mutual_contacts_available: bool, mutual_contacts: List[dict], share_location: bool,
                 social: dict, carrier: str, comments_enabled: bool, country_code: str, date_of_birth: datetime,
                 device_type: str, distance: None, email: str, facebook_url: str, first_name: str, gdpr_consent: bool,
                 gender: str, google_url: None, is_premium: bool, is_verified: bool, last_name: str,
                 location_enabled: bool, location_name: str, login_type: str, me_in_contacts: bool, phone_number: int,
                 phone_prefix: int, profile_picture: str, slogan: str, user_type: str, uuid: str,
                 verify_subscription: bool, who_deleted_enabled: bool, who_watched_enabled: bool,
                 ) -> None:
        super().__init__()
        self.comments_blocked = comments_blocked
        self.is_he_blocked_me = is_he_blocked_me
        self.is_permanent = is_permanent
        self.is_shared_location = is_shared_location
        self.last_comment = last_comment
        self.mutual_contacts_available = mutual_contacts_available
        self.mutual_contacts: List[MutualContact] = [get_object(MutualContact, mutual_contact) for mutual_contact in
                                                     mutual_contacts]
        self.share_location = share_location
        self.social: Socials = get_object(Socials, social)
        self.carrier = carrier
        self.comments_enabled = comments_enabled
        self.country_code = country_code
        self.date_of_birth = date_of_birth
        self.device_type = device_type
        self.distance = distance
        self.email = email
        self.facebook_url = facebook_url
        self.first_name = first_name
        self.gdpr_consent = gdpr_consent
        self.gender = gender
        self.google_url = google_url
        self.is_premium = is_premium
        self.is_verified = is_verified
        self.last_name = last_name
        self.location_enabled = location_enabled
        self.location_name = location_name
        self.login_type = login_type
        self.me_in_contacts = me_in_contacts
        self.phone_number = phone_number
        self.phone_prefix = phone_prefix
        self.profile_picture = profile_picture
        self.slogan = slogan
        self.user_type = user_type
        self.uuid = uuid
        self.verify_subscription = verify_subscription
        self.who_deleted_enabled = who_deleted_enabled
        self.who_watched_enabled = who_watched_enabled


class Socials(MeModel):
    def __init__(self, facebook: dict, fakebook: dict, instagram: dict, linkedin: dict, pinterest: dict, spotify: dict,
                 tiktok: dict, twitter: dict) -> None:
        self.facebook: Social = get_object(Social, facebook)
        self.fakebook: Social = get_object(Social, fakebook)
        self.instagram: Social = get_object(Social, instagram)
        self.linkedin: Social = get_object(Social, linkedin)
        self.pinterest: Social = get_object(Social, pinterest)
        self.spotify: Social = get_object(Social, spotify)
        self.tiktok: Social = get_object(Social, tiktok)
        self.twitter: Social = get_object(Social, twitter)


class Social(MeModel):
    def __init__(self, posts: List[dict], profile_id: str, is_active: bool, is_hidden: bool) -> None:
        self.posts: List[Post] = [get_object(Post, post) for post in posts]
        self.profile_id = profile_id
        self.is_active = is_active
        self.is_hidden = is_hidden


class Post(MeModel):
    def __init__(self, posted_at, photo: str, text_first: str, text_second: str, author: str, redirect_id: str,
                 owner: str) -> None:
        self.posted_at: Union[datetime, None] = parse_datetime(posted_at) if posted_at else posted_at
        self.photo = photo
        self.text_first = text_first
        self.text_second = text_second
        self.author = author
        self.redirect_id = redirect_id
        self.owner = owner


class MutualContact(MeModel):
    def __init__(self, phone_number: int, name: str, referenced_user: dict, date_of_birth: datetime) -> None:
        self.phone_number = phone_number
        self.name = name
        self.referenced_user: User = get_object(User, referenced_user)
        self.date_of_birth = date_of_birth


class User(MeModel):
    def __init__(self, email: str, profile_picture: str, first_name: str, last_name: str, gender: str, uuid: str,
                 is_verified: bool, phone_number: int, slogan: str, is_premium: bool, verify_subscription: bool,
                 id: int, comment_count: int, location_enabled: bool, distance: None) -> None:
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


class Contact(MeModel):
    def __init__(self, name: str, picture: None, user: dict, suggested_as_spam: int, is_permanent: bool,
                 is_pending_name_change: bool, user_type: str, phone_number: int, cached: bool, is_my_contact: bool,
                 is_shared_location: bool) -> None:
        self.name = name
        self.picture = picture
        self.user: User = get_object(User, user)
        self.suggested_as_spam = suggested_as_spam
        self.is_permanent = is_permanent
        self.is_pending_name_change = is_pending_name_change
        self.user_type = user_type
        self.phone_number = phone_number
        self.cached = cached
        self.is_my_contact = is_my_contact
        self.is_shared_location = is_shared_location
