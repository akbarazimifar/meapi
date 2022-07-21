from copy import deepcopy
from datetime import date
from typing import List, Union, TYPE_CHECKING, Optional
from meapi.utils.exceptions import MeException
from meapi.utils.helpers import parse_date
from meapi.models.comment import Comment
from meapi.models.common import _CommonMethodsForUserContactProfile
from meapi.models.deleter import Deleter
from meapi.models.me_model import MeModel
from meapi.models.social import Social
from meapi.models.user import User
from meapi.models.watcher import Watcher
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me


class Profile(MeModel, _CommonMethodsForUserContactProfile):
    """
    Represents the user's profile. can also be used to update you profile details.
        - Modifiable attributes are marked with *modifiable*.

    Example:
        .. code-block:: python

            # Change your name.
            my_profile = me.get_my_profile()
            my_profile.first_name = "Chandler"
            my_profile.last_name = "Bing"
            my_profile.profile_picture = "/home/david/Downloads/my_profile.jpg"

    Parameters:
        name (``str`` *optional*):
            The user's full name (``first_name`` + ``last_name``).

        first_name (``str`` *optional*):
            The user's first name. *modifiable*.

        last_name (``str`` *optional*):
            The user's last name. *modifiable*.

        profile_picture (``str`` *optional*):
            The user's profile picture url. *modifiable*.

        slogan (``str`` *optional*):
            The user's bio. *modifiable*.

        email (``str`` *optional*):
            The user's email. *modifiable*.

        gender (``str`` *optional*):
            The user's gender: ``M`` for male and ``F`` for female. *modifiable*.

        date_of_birth (:py:obj:`~datetime.date` *optional*):
            The user's date of birth. *modifiable*.

        age (``int``):
            The user's age. calculated from ``date_of_birth`` if exists, else ``0``.

        social (:py:obj:`~meapi.models.social.Social` *optional*):
            The user's social media networks.

        phone_number (``int``):
            The user's phone number.

        uuid (``str``):
            The user's unique ID.

        phone_prefix (``str``):
            The user's phone prefix.

        device_type (``str`` *optional*):
            The user's device type: ``android`` or ``ios``. *modifiable*.

        login_type (``str`` *optional*):
            The user's login type: ``email`` or ``apple``. *modifiable*.

        who_deleted_enabled (``bool``):
            Whether the user can see who deleted him (Only if ``is_premium``, Or if he uses ``meapi`` ;).

        who_deleted (List[:py:obj:`~meapi.models.deleter.Deleter`] *optional*):
            The users who deleted him.

        who_watched_enabled (``bool``):
            Whether the user can see who watched his profile (Only if ``is_premium``, Or if he uses ``meapi`` ;).

        who_watched (List[:py:obj:`~meapi.models.watcher.Watcher`] *optional*):
            The users who watched him.

        friends_distance (List[:py:obj:`~meapi.models.user.User`] *optional*):
            The users who shared their location with you.

        carrier (``str`` *optional*):
            The user's cell phone carrier. *modifiable*.

        comments_enabled (``bool``):
            Whether the user is allowing comments.

        comments_blocked (``bool``):
            Whether the user has blocked comments.

        country_code (``str``):
            The user's two-letter country code.

        location_enabled (``bool`` *optional*):
            Whether the user is allowing location.

        is_shared_location (``bool`` *optional*):
            Whether the user is sharing their location with you.

        share_location (``bool`` *optional*):
            Whether the user is sharing their location with you.

        distance (``float`` *optional*):
            The user's distance from you.

        location_latitude (``float`` *optional*):
            The user's latitude coordinate.

        location_latitude (``float`` *optional*):
            The user's latitude coordinate.

        location_name (``str`` *optional*):
            The user's location name. *modifiable*.

        is_he_blocked_me (``bool`` *optional*):
            Whether the user has blocked you.

        is_permanent (``bool`` *optional*):
            Whether the user is permanent.

        mutual_contacts_available (``bool`` *optional*):
            Whether the user has mutual contacts available.

        mutual_contacts (List[:py:obj:`~meapi.models.user.User`] *optional*):
            `For more information about mutual contacts <https://me.app/mutual-contacts/>`_.


        is_premium (``bool``):
            Whether the user is a premium user.

        is_verified (``bool``):
            Whether the user is verified.

        gdpr_consent (``bool``):
            Whether the user has given consent to the GDPR.

        facebook_url (``str`` *optional*):
            The user's Facebook ID. *modifiable*.

        google_url (``str`` *optional*):
            The user's Google ID. *modifiable*.

        me_in_contacts (``bool`` *optional*):
            Whether you are in the user's contacts.

        user_type (``str`` *optional*):
            The user's type: the color of the user in the app:
                - ``BLUE``: Verified Caller ID from ME users (100% ID).
                - ``GREEN``: Identified call with a very reliable result.
                - ``YELLOW``: Uncertain Identification (Unverified).
                - ``ORANGE``: No identification (can be reported).
                - ``RED``: Spam calls.

        verify_subscription (``bool`` *optional*):
            Whether the user has verified their subscription.

    Methods:

        Get the profile as Vcard: :py:func:`~meapi.models.common._CommonMethodsForUserContactProfile.as_vcard`.
        Block the profile: :py:func:`~meapi.models.common._CommonMethodsForUserContactProfile.block`.
        Unblock this profile: :py:func:`~meapi.models.common._CommonMethodsForUserContactProfile.unblock`.
        Report this profile as spam: :py:func:`~meapi.models.common._CommonMethodsForUserContactProfile.report_spam`.
    """
    def __init__(self,
                 _client: 'Me',
                 comments_blocked: bool = None,
                 is_he_blocked_me: bool = None,
                 is_permanent: bool = None,
                 is_shared_location: bool = None,
                 last_comment: dict = None,
                 mutual_contacts_available: bool = None,
                 mutual_contacts: List[dict] = None,
                 share_location: bool = None,
                 social: dict = None,
                 carrier: str = None,
                 comments_enabled: bool = None,
                 country_code: str = None,
                 date_of_birth: str = None,
                 device_type: str = None,
                 distance: float = None,
                 email: str = None,
                 facebook_url: str = None,
                 first_name: str = None,
                 gdpr_consent: bool = None,
                 gender: str = None,
                 google_url: None = None,
                 is_premium: bool = None,
                 is_verified: bool = None,
                 last_name: str = None,
                 location_enabled: bool = None,
                 location_longitude: float = None,
                 location_latitude: float = None,
                 location_name: str = None,
                 login_type: str = None,
                 me_in_contacts: bool = None,
                 phone_number: int = None,
                 phone_prefix: str = None,
                 profile_picture: str = None,
                 slogan: str = None,
                 user_type: str = None,
                 uuid: str = None,
                 verify_subscription: bool = None,
                 who_deleted_enabled: bool = None,
                 who_deleted: List[dict] = None,
                 who_watched_enabled: bool = None,
                 who_watched: List[dict] = None,
                 friends_distance: dict = None,
                 _my_profile: bool = False
                 ):
        self.__client = _client
        self.comments_blocked = comments_blocked
        self.is_he_blocked_me = is_he_blocked_me
        self.is_permanent = is_permanent
        self.is_shared_location = is_shared_location
        self.last_comment = Comment.new_from_dict(last_comment, _client=_client, profile_uuid=uuid)
        self.mutual_contacts_available = mutual_contacts_available
        self.mutual_contacts: List[User] = [User.new_from_dict(mutual_contact['referenced_user']) for mutual_contact in
                                            mutual_contacts] if mutual_contacts_available else mutual_contacts
        self.share_location = share_location
        self.social: Social = Social.new_from_dict(social, _client=_client, _my_social=_my_profile) if social else social
        self.carrier = carrier
        self.comments_enabled = comments_enabled
        self.country_code = country_code
        self.date_of_birth: Optional[date] = parse_date(date_of_birth, date_only=True)
        self.device_type = device_type
        self.distance = distance
        self.friends_distance = [User.new_from_dict(user.get('author')) for user in friends_distance.get('friends')] if friends_distance else None
        self.email = email
        self.facebook_url = f"https://facebook.com/profile.php?id={facebook_url}" if facebook_url else facebook_url
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
        self.who_deleted = [Deleter.new_from_dict(deleter) for deleter in who_deleted] if who_deleted else None
        self.who_watched_enabled = who_watched_enabled
        self.who_watched = [Watcher.new_from_dict(watcher) for watcher in who_watched] if who_watched else None
        self.__my_profile = _my_profile

    @property
    def name(self) -> Optional[str]:
        """
        Returns the full name of the user. ``first_name`` + ``last_name``.
        """
        return (self.first_name or '') + (' ' if self.first_name and self.last_name else '') + (self.last_name or '') or None

    @property
    def age(self) -> int:
        """
        Calculates the age of the user from ``date_of_birth``.
        """
        if not self.date_of_birth or self.date_of_birth > date.today():
            return 0
        return (date.today() - self.date_of_birth).days // 365

    def refresh(self) -> bool:
        """
        Refresh the profile's data if changes have been made from outside the object.
            - You don't need to call this method if you change the profile by assigning a new value to the attrs (If i'ts your profile).
        """
        self.__my_profile = None  # __setattr__ relies on it to prevent changes
        self.__dict__ = deepcopy(self.__client.get_profile(self.uuid).__dict__)
        if self.__my_profile:
            return True
        return False

    def __setattr__(self, key, value):
        if getattr(self, '_Profile__my_profile', None) is not None:
            if self.__my_profile:
                if key == '_Profile__my_profile':
                    return super().__setattr__(key, value)
                modifiable_attrs = ['first_name', 'last_name', 'email', 'gender', 'slogan', 'profile_picture',
                                    'date_of_birth', 'location_name', 'device_type', 'login_type', 'facebook_url',
                                    'google_url', 'carrier']
                if key not in modifiable_attrs:
                    raise MeException(f"You can not modify this attr!\nThe modifiable attrs are: {modifiable_attrs}")
                success, new_profile = self.__client.update_profile_details(**{key: value})
                if (success and str(getattr(new_profile, key, None)) == str(value)) or key == 'profile_picture':
                    # Can't check if profile picture updated because Me convert's it to their own url.
                    value = getattr(new_profile, key, None)
                    if key == 'date_of_birth':
                        value = parse_date(value, date_only=True)
                    if key == 'facebook_url' and value:
                        value = f"https://facebook.com/profile.php?id={value}"
                else:
                    raise MeException(f"Failed to change '{getattr(self, key)}' to '{value}'!")
            else:
                raise MeException("You cannot update profile if it's not yours!")
        super().__setattr__(key, value)

    def __repr__(self):
        return f"<Profile name={self.name} uuid={self.uuid}>"

    def __str__(self):
        return self.name
