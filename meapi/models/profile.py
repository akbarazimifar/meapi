from datetime import date
from typing import List, Union
from meapi.utils.exceptions import MeException
from meapi.utils.validations import validate_profile_details
from meapi.utils.helpers import parse_date
from meapi.models.comment import Comment
from meapi.models.common import _CommonMethodsForUserContactProfile
from meapi.models.deleter import Deleter
from meapi.models.me_model import MeModel
from meapi.models.mutual_contact import MutualContact
from meapi.models.social import Social
from meapi.models.user import User
from meapi.models.watcher import Watcher


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
                 who_deleted: Union[List[dict], None] = None,
                 who_watched_enabled: Union[bool, None] = None,
                 who_watched: Union[List[dict], None] = None,
                 friends_distance: Union[dict, None] = None,
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
        self.social: Social = Social.new_from_json_dict(social, _meobj=_meobj) if social else social
        self.carrier = carrier
        self.comments_enabled = comments_enabled
        self.country_code = country_code
        self.date_of_birth: Union[date, None] = parse_date(date_of_birth, date_only=True)
        self.device_type = device_type
        self.distance = distance
        self.friends_distance = [User.new_from_json_dict(user.get('author')) for user in friends_distance.get('friends')] if friends_distance else None
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
        self.who_deleted = [Deleter.new_from_json_dict(deleter) for deleter in who_deleted] if who_deleted else None
        self.who_watched_enabled = who_watched_enabled
        self.who_watched = [Watcher.new_from_json_dict(watcher) for watcher in who_watched] if who_watched else None
        self.__my_profile = my_profile

    def __setattr__(self, key, value):
        if getattr(self, '_Profile__my_profile', None) is not None:
            if self.__my_profile:
                value = validate_profile_details(key, value)
                res = self.__meobj.update_profile_info(**{key: value})
                if res[key] == value or key == 'profile_picture':
                    # Can't check if profile picture updated because Me convert's it to their own url.
                    if key == 'date_of_birth':
                        value = parse_date(value, date_only=True)
                    return super().__setattr__(key, value)
                else:
                    raise MeException(f"Failed to change '{getattr(self, key)}' to '{value}'!")
            else:
                raise MeException("You cannot update profile if it's not yours!")
        super().__setattr__(key, value)

    def __repr__(self):
        return f"<Profile name={self.first_name} {self.last_name or ''} uuid={self.uuid}>"

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}"
