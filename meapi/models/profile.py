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
    """
    **Represents the user's profile. can also be used to update you profile details.**

    Example:
        .. code-block:: python

            # Change your name.
            my_profile = me.get_my_profile()
            my_profile.first_name = "Chandler"
            my_profile.last_name = "Bing"

    Parameters:
        name (``str``):
            The user's full name (``first_name`` + ``last_name``).

        first_name (``str``):
            The user's first name.

        last_name (``str`` *optional*):
            The user's last name.

        profile_picture (``str`` *optional*):
            The user's profile picture url.

        slogan (``str`` *optional*):
            The user's bio.

        email (``str`` *optional*):
            The user's email.

        gender (``str`` *optional*):
            The user's gender: ``N`` for male and ``F`` for female.

        social (:py:obj:`~meapi.models.social.Social` *optional*):
            The user's social media networks.

        phone_number (``int`` *optional*):
            The user's phone number.

        uuid (``str``):
            The user's unique ID.

        phone_prefix (``int`` *optional*):
            The user's phone prefix.

        date_of_birth (:py:obj:`~datetime.date` *optional*):
            The user's date of birth.

        device_type (``str`` *optional*):
            The user's device type: ``android`` or ``ios``.

        login_type (``str`` *optional*):
            The user's login type: ``email`` or ``apple``.

        who_deleted_enabled (``bool``):
            Whether the user can see who deleted him (Only if ``is_premium``, Or if he uses meapi ;).

        who_deleted (List[:py:obj:`~meapi.models.deleter.Deleter`] *optional*):
            The users who deleted him.

        who_watched_enabled (``bool``):
            Whether the user can see who watched his profile (Only if ``is_premium``, Or if he uses meapi ;).

        who_watched (List[:py:obj:`~meapi.models.watcher.Watcher`] *optional*):
            The users who watched him.

        friends_distance (List[:py:obj:`~meapi.models.user.User`] *optional*):
            The users who shared their location with you.

        carrier (``str`` *optional*):
            The user's cell phone carrier.

        comments_enabled (``bool``):
            Whether the user is allowing comments.

        comments_blocked (``bool``):
            Whether the user has blocked comments.

        country_code (``str`` *optional*):
            The user's country code.

        location_enabled (``bool`` *optional*):
            Whether the user is allowing location.

        is_shared_location (``bool``):
            Whether the user is sharing their location with you.

        share_location (``bool``):
            Whether the user is sharing their location with you.

        distance (``float`` *optional*):
            The user's distance from you.

        location_latitude (``float`` *optional*):
            The user's latitude coordinate.

        location_latitude (``float`` *optional*):
            The user's latitude coordinate.

        location_name (``str`` *optional*):
            The user's location name.

        is_he_blocked_me (``bool``):
            Whether the user has blocked you.

        is_permanent (``bool``):
            Whether the user is permanent.

        mutual_contacts_available (``bool``):
            Whether the user has mutual contacts available.

        mutual_contacts (List[:py:obj:`~meapi.models.mutual_contact.MutualContact`] *optional*):
            The user's mutual contacts.

        is_premium (``bool`` *optional*):
            Whether the user is a premium user.

        is_verified (``bool`` *optional*):
            Whether the user is verified.

        gdpr_consent (``bool`` *optional*):
            Whether the user has given consent to the GDPR.

        facebook_url (``str`` *optional*):
            The user's Facebook ID.

        google_url (``str`` *optional*):
            The user's Google ID.

        me_in_contacts (``bool`` *optional*):
            Whether you are in the user's contacts.

        user_type (``str`` *optional*):
            The user's type: the color of the user in the app.

        verify_subscription (``bool`` *optional*):
            Whether the user has verified their subscription.

    Methods:

    .. automethod:: get_vcard
    .. automethod:: block
    .. automethod:: unblock
    """
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
                 distance: Union[float, None] = None,
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
                 _my_profile: bool = False
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
        self.__my_profile = _my_profile

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

    @property
    def name(self) -> str:
        return str(self.first_name or '' + ((' ' if self.first_name else '') + self.last_name or ''))

