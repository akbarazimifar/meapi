import inspect
import json
from abc import ABCMeta
from datetime import datetime
from typing import Union, List


def parse_date(date_str: str, date_only=False) -> Union[datetime, datetime.date, None]:
    if not date_str:
        return date_str
    date = datetime.strptime(str(date_str), '%Y-%m-%d' + ('' if date_only else 'T%H:%M:%S%z'))
    return date.date() if date_only else date


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
    def __str__(self):
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
        if not data or data is None:
            return None
        cls_attrs = cls._init_parameters.keys()
        json_data = data.copy()
        if kwargs:
            for key, val in kwargs.items():
                json_data[key] = val
        for key in json_data.copy():
            if key not in cls_attrs:
                del json_data[key]
        c = cls(**json_data)
        c._json = data
        return c


class Profile(MeModel):
    def __init__(self,
                 comments_blocked: Union[bool, None] = None,
                 is_he_blocked_me: Union[bool, None] = None,
                 is_permanent: Union[bool, None] = None,
                 is_shared_location: Union[bool, None] = None,
                 last_comment: Union[None, None] = None,
                 mutual_contacts_available: Union[bool, None] = None,
                 mutual_contacts: Union[List[dict], None] = None,
                 share_location: Union[bool, None] = None,
                 social: Union[dict, None] = None,
                 carrier: Union[str, None] = None,
                 comments_enabled: Union[bool, None] = None,
                 country_code: Union[str, None] = None,
                 date_of_birth: Union[str, None] = None,
                 device_type: Union[str, None] = None,
                 distance: Union[None, None] = None,
                 email: Union[str, None] = None,
                 facebook_url: Union[str, None] = None,
                 first_name: Union[str, None] = None,
                 gdpr_consent: Union[bool, None] = None,
                 gender: Union[str, None] = None,
                 google_url: Union[None, None] = None,
                 is_premium: Union[bool, None] = None,
                 is_verified: Union[bool, None] = None,
                 last_name: Union[str, None] = None,
                 location_enabled: Union[bool, None] = None,
                 location_name: Union[str, None] = None,
                 login_type: Union[str, None] = None,
                 me_in_contacts: Union[bool, None] = None,
                 phone_number: Union[int, None] = None,
                 phone_prefix: Union[int, None] = None,
                 profile_picture: Union[str, None] = None,
                 slogan: Union[str, None] = None,
                 user_type: Union[str, None] = None,
                 uuid: Union[str, None] = None,
                 verify_subscription: Union[bool, None] = None,
                 who_deleted_enabled: Union[bool, None] = None,
                 who_watched_enabled: Union[bool, None] = None,
                 in_contact_list: Union[bool, None] = None,
                 ):
        self.comments_blocked = comments_blocked
        self.is_he_blocked_me = is_he_blocked_me
        self.is_permanent = is_permanent
        self.is_shared_location = is_shared_location
        self.last_comment = last_comment
        self.mutual_contacts_available = mutual_contacts_available
        self.mutual_contacts: List[MutualContact] = [MutualContact.new_from_json_dict(mutual_contact) for mutual_contact in
                                                     mutual_contacts] if mutual_contacts_available else mutual_contacts
        self.share_location = share_location
        self.social: Socials = Socials.new_from_json_dict(social)
        self.carrier = carrier
        self.comments_enabled = comments_enabled
        self.country_code = country_code
        self.date_of_birth: Union[datetime.date, None] = parse_date(date_of_birth, date_only=True)
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
        self.in_contact_list = in_contact_list
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
    def __init__(self=None,
                 facebook: Union[dict, None] = None,
                 fakebook: Union[dict, None] = None,
                 instagram: Union[dict, None] = None,
                 linkedin: Union[dict, None] = None,
                 pinterest: Union[dict, None] = None,
                 spotify: Union[dict, None] = None,
                 tiktok: Union[dict, None] = None,
                 twitter: Union[dict, None] = None
                 ):
        self.facebook: Social = Social.new_from_json_dict(facebook)
        self.fakebook: Social = Social.new_from_json_dict(fakebook)
        self.instagram: Social = Social.new_from_json_dict(instagram)
        self.linkedin: Social = Social.new_from_json_dict(linkedin)
        self.pinterest: Social = Social.new_from_json_dict(pinterest)
        self.spotify: Social = Social.new_from_json_dict(spotify)
        self.tiktok: Social = Social.new_from_json_dict(tiktok)
        self.twitter: Social = Social.new_from_json_dict(twitter)


class Social(MeModel):
    def __init__(self,
                 posts: Union[List[dict], None] = None,
                 profile_id: Union[str, None] = None,
                 is_active: Union[bool, None] = None,
                 is_hidden: Union[bool, None] = None
                 ):
        self.posts: Union[List[Post], None] = [Post.new_from_json_dict(post) for post in posts] if posts else posts
        self.profile_id = profile_id
        self.is_active = is_active
        self.is_hidden = is_hidden


class Post(MeModel):
    def __init__(self,
                 posted_at: Union[str, None] = None,
                 photo: Union[str, None] = None,
                 text_first: Union[str, None] = None,
                 text_second: Union[str, None] = None,
                 author: Union[str, None] = None,
                 redirect_id: Union[str, None] = None,
                 owner: Union[str, None] = None
                 ):
        self.posted_at: Union[datetime, None] = parse_date(posted_at) if posted_at else posted_at
        self.photo = photo
        self.text_first = text_first
        self.text_second = text_second
        self.author = author
        self.redirect_id = redirect_id
        self.owner = owner


class MutualContact(MeModel):
    def __init__(self,
                 phone_number: Union[int, None] = None,
                 name: Union[str, None] = None,
                 referenced_user: Union[dict, None] = None,
                 date_of_birth: Union[str, None] = None
                 ):
        self.phone_number = phone_number
        self.name = name
        self.referenced_user: User = User.new_from_json_dict(referenced_user)
        self.date_of_birth = date_of_birth


class User(MeModel):
    def __init__(self,
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
                 distance: Union[None, None] = None
                 ):
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
    def __init__(self,
                 name: Union[str, None] = None,
                 picture: Union[None, None] = None,
                 user: Union[dict, None] = None,
                 suggested_as_spam: Union[int, None] = None,
                 is_permanent: Union[bool, None] = None,
                 is_pending_name_change: Union[bool, None] = None,
                 user_type: Union[str, None] = None,
                 phone_number: Union[int, None] = None,
                 cached: Union[bool, None] = None,
                 is_shared_location: Union[bool, None] = None,
                 ):
        self.name = name
        self.picture = picture
        self.user: User = User.new_from_json_dict(user)
        self.suggested_as_spam = suggested_as_spam
        self.is_permanent = is_permanent
        self.is_pending_name_change = is_pending_name_change
        self.user_type = user_type
        self.phone_number = phone_number
        self.cached = cached
        self.is_shared_location = is_shared_location


class BlockedNumber(MeModel):
    def __int__(self,
                block_contact: Union[bool, None] = None,
                me_full_block: Union[bool, None] = None,
                phone_number: Union[int, None] = None):
        self.block_contact = block_contact
        self.me_full_block = me_full_block
        self.phone_number = phone_number