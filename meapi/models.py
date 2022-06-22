import inspect
import json
from abc import ABCMeta
from datetime import datetime, date
from typing import Union, List
from meapi.exceptions import MeException
from meapi.helpers import validate_profile_details, get_vcard
import meapi.me as me_base

IGNORED_KEYS = []


def parse_date(date_str: str, date_only=False) -> Union[datetime, date, None]:
    if date_str is None:
        return date_str
    date_obj = datetime.strptime(str(date_str), '%Y-%m-%d' + ('' if date_only else 'T%H:%M:%S%z'))
    return date_obj.date() if date_only else date_obj


class _CommonMethodsForUserContactProfile:
    """
    Common methods for user, profile and contact
    """
    def block(self, block_contact=True, me_full_block=True) -> bool:
        if getattr(self, f'_{self.__class__.__name__}__my_profile', None):
            raise MeException("you can't block yourself!")
        return getattr(self, f'_{self.__class__.__name__}__meobj').block_profile(phone_number=self.phone_number, block_contact=block_contact, me_full_block=me_full_block)

    def unblock(self, unblock_contact=True, me_full_unblock=True) -> bool:
        if getattr(self, f'_{self.__class__.__name__}__my_profile', None):
            raise MeException("you can't unblock yourself!")
        return getattr(self, f'_{self.__class__.__name__}__meobj').unblock_profile(phone_number=self.phone_number, unblock_contact=unblock_contact, me_full_unblock=me_full_unblock)

    def get_vcard(self, prefix_name: str = "", profile_picture: bool = True, **kwargs) -> str:
        return get_vcard(self.__dict__, prefix_name, profile_picture, **kwargs)


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
    def __init__(self):
        self.__init_done = True

    def __str__(self) -> str:
        return self.as_json_string()

    def __eq__(self, other) -> bool:
        return other and self.as_dict() == other.as_dict()

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        if hasattr(self, 'id'):
            return hash(self.id)
        else:
            raise TypeError('unhashable type: {} (no id attribute)'.format(type(self)))

    def __setattr__(self, key, value):
        """
        Prevent attr changes after the init in protected data classes
        """
        if getattr(self, '_MeModel__init_done', None):
            raise MeException(f"You cannot change the protected attr '{key}' of '{self.__class__.__name__}'!")
        return super().__setattr__(key, value)

    def as_json_string(self, ensure_ascii=True) -> str:
        """
        Return class data in json format
        """
        return json.dumps(self.as_dict(), ensure_ascii=ensure_ascii, sort_keys=True)

    def as_dict(self) -> dict:
        """
        Return class data as dict
        """
        data = {}
        for (key, value) in self.__dict__.items():
            if str(key).startswith("_"):
                continue
            elif isinstance(getattr(self, key, None), (list, tuple, set)):
                data[key] = list()
                for subobj in getattr(self, key, None):
                    if getattr(subobj, 'as_dict', None):
                        data[key].append(subobj.as_dict())
                    else:
                        data[key].append(subobj)

            elif getattr(getattr(self, key, None), 'as_dict', None):
                data[key] = getattr(self, key).as_dict()

            elif isinstance(value, (date, datetime)):
                data[key] = str(getattr(self, key, None))

            elif getattr(self, key, None):
                data[key] = getattr(self, key, None)
        return data

    @classmethod
    def new_from_json_dict(cls, data: dict, _meobj=None, **kwargs):
        """
        Create new instance from json_dict
        """
        if not data or data is None:
            return None
        cls_attrs = cls._init_parameters.keys()
        if '_meobj' in cls_attrs:
            if not isinstance(_meobj, me_base.Me):
                raise MeException(f"When creating instance of {cls.__name__} you must provide instance of Me in order to perform calls to Me api!")
            data['_meobj'] = _meobj
        json_data = data.copy()
        if kwargs:
            for key, val in kwargs.items():
                json_data[key] = val
        for key in json_data.copy():
            if key not in cls_attrs:
                if key not in IGNORED_KEYS and not key.startswith('_'):
                    print(f"- The key '{key}' with the value of '{json_data[key]}' just skipped. "
                          f"Try to update meapi to the latest version (pip3 install -U meapi) "
                          f"If it's still skipping, open issue in github: <https://github.com/david-lev/meapi/issues>")
                del json_data[key]
        c = cls(**json_data)
        return c


class Profile(MeModel, _CommonMethodsForUserContactProfile):
    def __init__(self,
                 _meobj,
                 comments_blocked: Union[bool, None] = None,
                 is_he_blocked_me: Union[bool, None] = None,
                 is_permanent: Union[bool, None] = None,
                 is_shared_location: Union[bool, None] = None,
                 last_comment: Union[dict, None] = None,
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
                 location_longitude: Union[float, None] = None,
                 location_latitude: Union[float, None] = None,
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
                 my_profile: bool = False
                 ):
        self.__meobj = _meobj
        self.comments_blocked = comments_blocked
        self.is_he_blocked_me = is_he_blocked_me
        self.is_permanent = is_permanent
        self.is_shared_location = is_shared_location
        self.last_comment = Comment.new_from_json_dict(last_comment, _meobj=_meobj)
        self.mutual_contacts_available = mutual_contacts_available
        self.mutual_contacts: List[MutualContact] = [MutualContact.new_from_json_dict(mutual_contact) for mutual_contact in
                                                     mutual_contacts] if mutual_contacts_available else mutual_contacts
        self.share_location = share_location
        self.social: Socials = Socials.new_from_json_dict(social, _meobj=_meobj) if social else social
        self.carrier = carrier
        self.comments_enabled = comments_enabled
        self.country_code = country_code
        self.date_of_birth: Union[date, None] = parse_date(date_of_birth, date_only=True)
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
        self.location_longitude = location_longitude
        self.location_latitude = location_latitude
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
        self.__my_profile = my_profile

    def __setattr__(self, key, value):
        if getattr(self, '_Profile__my_profile', None) is not None:
            if self.__my_profile:
                value = validate_profile_details(key, value)
                if self.__meobj.update_profile_info(**{key: value})[key] == value:
                    return super().__setattr__(key, value)
            else:
                raise MeException("You cannot update profile if it's not yours!")
        super().__setattr__(key, value)

    def __repr__(self):
        return f"<Profile name={self.first_name} {self.last_name or ''} uuid={self.uuid}>"

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}"


class User(MeModel, _CommonMethodsForUserContactProfile):
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
        super().__init__()

    def __repr__(self):
        return f"User name={self.first_name} {self.last_name or ''}>"

    def __str__(self):
        return self.uuid


class Contact(MeModel, _CommonMethodsForUserContactProfile):
    def __init__(self,
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


class Socials(MeModel):
    def __init__(self=None,
                 facebook: Union[dict, None] = None,
                 fakebook: Union[dict, None] = None,
                 instagram: Union[dict, None] = None,
                 linkedin: Union[dict, None] = None,
                 pinterest: Union[dict, None] = None,
                 spotify: Union[dict, None] = None,
                 tiktok: Union[dict, None] = None,
                 twitter: Union[dict, None] = None,
                 _my_socials: bool = False
                 ):
        self.facebook: Social = Social.new_from_json_dict(facebook) if facebook['is_active'] else None
        self.fakebook: Social = Social.new_from_json_dict(fakebook) if fakebook['is_active'] else None
        self.instagram: Social = Social.new_from_json_dict(instagram) if instagram['is_active'] else None
        self.linkedin: Social = Social.new_from_json_dict(linkedin) if linkedin['is_active'] else None
        self.pinterest: Social = Social.new_from_json_dict(pinterest) if pinterest['is_active'] else None
        self.spotify: Social = Social.new_from_json_dict(spotify) if spotify['is_active'] else None
        self.tiktok: Social = Social.new_from_json_dict(tiktok) if tiktok['is_active'] else None
        self.twitter: Social = Social.new_from_json_dict(twitter) if twitter['is_active'] else None
        self.__my_socials = _my_socials
        super().__init__()


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
        super().__init__()

    def __repr__(self):
        return f"<Social profile_id={self.profile_id} is_active={self.is_active}>"

    def __str__(self):
        return str(self.profile_id)


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
        super().__init__()

    def __repr__(self):
        return f"<Post text={self.text_first} id={self.redirect_id}>"

    def __str__(self):
        return str(self.text_first)


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
        super().__init__()

    def __repr__(self):
        return f"<MutualContact name={self.name} phone={self.phone_number}>"

    def __str__(self):
        return self.name


class BlockedNumber(MeModel):
    def __init__(self,
                block_contact: Union[bool, None] = None,
                me_full_block: Union[bool, None] = None,
                phone_number: Union[int, None] = None
                ):
        self.block_contact = block_contact
        self.me_full_block = me_full_block
        self.phone_number = phone_number
        super().__init__()

    def __repr__(self):
        return f"<BlockedNumber phone={self.phone_number}>"

    def __str__(self):
        return str(self.phone_number)


class Friendship(MeModel):
    def __init__(self,
                 calls_duration: Union[None, None] = None,
                 he_called: Union[int, None] = None,
                 he_named: Union[str, None] = None,
                 he_watched: Union[int, None] = None,
                 his_comment: Union[None, None] = None,
                 i_called: Union[int, None] = None,
                 i_named: Union[str, None] = None,
                 i_watched: Union[int, None] = None,
                 is_premium: Union[bool, None] = None,
                 mutual_friends_count: Union[int, None] = None,
                 my_comment: Union[str, None] = None
                 ):
        self.calls_duration = calls_duration
        self.he_called = he_called
        self.he_named = he_named
        self.he_watched = he_watched
        self.his_comment = his_comment
        self.i_called = i_called
        self.i_named = i_named
        self.i_watched = i_watched
        self.is_premium = is_premium
        self.mutual_friends_count = mutual_friends_count
        self.my_comment = my_comment
        super().__init__()

    def __repr__(self):
        return f"<Friendship of={self.i_named} and={self.he_named}>"

    def __str__(self):
        return self.i_named


class Deleter(MeModel):
    def __init__(self,
                 created_at: Union[str, None] = None,
                 user: Union[dict, None] = None
                 ):
        self.created_at = parse_date(created_at)
        self.user = User.new_from_json_dict(user)
        super().__init__()

    def __repr__(self):
        return f"<Deleter name={self.user.first_name} {self.user.last_name or ''}>"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name or ''}"


class Watcher(MeModel):
    def __init__(self, last_view: Union[str, None] = None,
                 user: Union[dict, None] = None,
                 count: Union[int, None] = None,
                 is_search: Union[bool, None] = None) -> None:
        self.last_view: datetime = parse_date(last_view)
        self.user: User = User.new_from_json_dict(user)
        self.count = count
        self.is_search = is_search
        super().__init__()

    def __repr__(self):
        return f"<Watcher name={self.user.first_name} {self.user.last_name or ''} count={self.count}>"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name or ''}"


class Comment(MeModel):
    def __init__(self,
                 _meobj,
                 like_count: Union[int, None] = None,
                 status: Union[str, None] = None,
                 message: Union[str, None] = None,
                 author: Union[dict, None] = None,
                 is_liked: Union[bool, None] = None,
                 id: Union[int, None] = None,
                 comments_blocked: Union[bool, None] = None,
                 created_at: Union[str, None] = None,
                 comment_likes: Union[dict, None] = None,
                 my_comment: bool = False
                 ):
        self.like_count = like_count
        self.status = status
        self.message = message
        self.author = User.new_from_json_dict(author)
        self.is_liked = is_liked
        self.id = id
        self.comments_blocked = comments_blocked
        self.created_at = parse_date(created_at)
        self.comment_likes = [User.new_from_json_dict(user['author']) for user in
                              comment_likes] if comment_likes else None
        self.__meobj = _meobj
        self.__my_comment = my_comment
        self.__init_done = True

    def __setattr__(self, key, value):
        if getattr(self, '_Comment__init_done', None):
            if key not in ['message', 'status', 'like_count', 'comment_likes']:
                raise MeException("You can't change this attr!")
        return super().__setattr__(key, value)

    def __repr__(self):
        return f"<Comment id={self.id} status={self.status} msg={self.message}>"

    def __str__(self):
        return self.message

    def approve(self) -> bool:
        if self.__my_comment:
            raise MeException("You can only approve others comments!")
        if self.id:
            if self.__meobj.approve_comment(self.id):
                self.status = 'approved'
                return True
        return False

    def like(self) -> bool:
        if self.id:
            if self.__meobj.like_comment(self.id):
                self.like_count += 1
                return True
        return False

    def delete(self):
        if self.__my_comment:
            raise MeException("You can delete others comments!")
        if self.id:
            if self.__meobj.delete_comment(self.id):
                self.status = 'ignored'
                return True
        return False


class Group(MeModel):
    def __init__(self,
                 _meobj,
                 name: Union[str, None] = None,
                 count: Union[int, None] = None,
                 last_contact_at: Union[str, None] = None,
                 contacts: Union[List[dict], None] = None,
                 contact_ids: Union[List[int], None] = None,
                 status: str = "active"
                 ):
        self.name = name
        self.count = count
        self.last_contact_at: Union[datetime, None] = parse_date(last_contact_at)
        self.contacts = [Contact.new_from_json_dict(contact) for contact in contacts] if contacts else contacts
        self.contact_ids = contact_ids
        self.status = status
        self.__meobj = _meobj
        self.__init_done = True

    def __setattr__(self, key, value):
        if getattr(self, '_Group__init_done', None):
            if key != 'status':
                raise MeException("You can't change this attr!")
        return super().__setattr__(key, value)

    def __repr__(self):
        return f"<Group name={self.name} count={self.count}>"

    def __str__(self):
        return self.name

    def delete(self) -> bool:
        if self.status != 'active':
            raise MeException(f"The name '{self.name}' is already hidden!")
        if self.__meobj.delete_name(self.contact_ids):
            self.status = 'hidden'
            return True
        return False

    def restore(self) -> bool:
        if self.status != 'hidden':
            raise MeException(f"The name '{self.name}' is already activated!")
        if self.__meobj.restore_name(self.contact_ids):
            self.status = 'active'
            return True
        return False

    def ask_to_rename(self, new_name) -> bool:
        if self.status != 'active':
            raise MeException("You can't ask to rename if the name is hidden. restore and then ask again!")
        if self.__meobj.ask_group_rename(self.contact_ids, new_name):
            return True
        return False


class Settings(MeModel):
    def __init__(self,
                 birthday_notification_enabled: Union[bool, None] = None,
                 comments_enabled: Union[bool, None] = None,
                 comments_notification_enabled: Union[bool, None] = None,
                 contact_suspended: Union[bool, None] = None,
                 distance_notification_enabled: Union[bool, None] = None,
                 language: Union[str, None] = None,
                 last_backup_at: Union[None, None] = None,
                 last_restore_at: Union[None, None] = None,
                 location_enabled: Union[bool, None] = None,
                 mutual_contacts_available: Union[bool, None] = None,
                 names_notification_enabled: Union[bool, None] = None,
                 notifications_enabled: Union[bool, None] = None,
                 spammers_count: Union[int, None] = None,
                 system_notification_enabled: Union[bool, None] = None,
                 who_deleted_enabled: Union[bool, None] = None,
                 who_deleted_notification_enabled: Union[bool, None] = None,
                 who_watched_enabled: Union[bool, None] = None,
                 who_watched_notification_enabled: Union[bool, None] = None,
                 _meobj=None
                 ):
        self.birthday_notification_enabled = birthday_notification_enabled
        self.comments_enabled = comments_enabled
        self.comments_notification_enabled = comments_notification_enabled
        self.contact_suspended = contact_suspended
        self.distance_notification_enabled = distance_notification_enabled
        self.language = language
        self.last_backup_at = last_backup_at
        self.last_restore_at = last_restore_at
        self.location_enabled = location_enabled
        self.mutual_contacts_available = mutual_contacts_available
        self.names_notification_enabled = names_notification_enabled
        self.notifications_enabled = notifications_enabled
        self.spammers_count = spammers_count
        self.system_notification_enabled = system_notification_enabled
        self.who_deleted_enabled = who_deleted_enabled
        self.who_deleted_notification_enabled = who_deleted_notification_enabled
        self.who_watched_enabled = who_watched_enabled
        self.who_watched_notification_enabled = who_watched_notification_enabled
        self.__meobj = _meobj
        self.__init_done = True

    def __repr__(self):
        return f"<Settings lang={self.language}>"

    def __setattr__(self, key, value):
        if getattr(self, '_Settings__init_done', None):
            if key not in ['spammers_count', 'last_backup_at', 'last_restore_at', 'contact_suspended']:
                if key == 'language':
                    if isinstance(value, str) and len(value) == 2 and value.isalpha():
                        pass
                if not isinstance(value, bool):
                    raise MeException(f"{str(key)} value must be a bool type!")
            else:
                raise MeException("You can't change this setting!")
            if self.__meobj.change_settings(**{key: value})[key] != value:
                raise MeException("not updated")

        return super().__setattr__(key, value)

    def __change_all(self, change_to: bool):
        to_change = {}
        for key, value in self.__dict__.items():
            if isinstance(value, bool) and not key.startswith('_') and key != 'contact_suspended':
                to_change[key] = change_to
        res = self.__meobj.change_settings(**to_change)
        for key in to_change:
            if res[key] != change_to:
                return False
        self.__dict__.update(to_change)
        return True

    def enable_all(self) -> bool:
        return self.__change_all(change_to=True)

    def disable_all(self) -> bool:
        return self.__change_all(change_to=False)
