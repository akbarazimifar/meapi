from copy import deepcopy
from datetime import date
from typing import List, TYPE_CHECKING, Optional
from meapi.models.mutual_contact import MutualContact
from meapi.utils.exceptions import FrozenInstance
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
        - Modifiable attributes are marked with ``modifiable``.
        - For more information about the modifiable attributes, see :py:func:`~meapi.Me.update_profile_details`.

    Example:

        >>> # Update your profile details.
        >>> my_profile = me.get_my_profile()
        >>> my_profile.name = "Chandler Bing"
        >>> my_profile.date_of_birth = "1968-04-08"
        >>> my_profile.slogan = "Hi, I'm Chandler. I make jokes when I'm uncomfortable."
        >>> my_profile.profile_picture = "/home/chandler/Downloads/my_profile.jpg"

    Parameters:
        name (``str`` *optional*, *modifiable*):
            The user's full name (``first_name`` + ``last_name``).

        first_name (``str`` *optional*, *modifiable*):
            The user's first name.

        last_name (``str`` *optional*, *modifiable*):
            The user's last name.

        profile_picture (``str`` *optional*, *modifiable*):
            The user's profile picture url.

        slogan (``str`` *optional*, *modifiable*):
            The user's bio.

        email (``str`` *optional*, *modifiable*):
            The user's email.

        gender (``str`` *optional*, *modifiable*):
            The user's gender: ``M`` for male and ``F`` for female.

        date_of_birth (:py:obj:`~datetime.date` *optional*, *modifiable*):
            The user's date of birth.

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

        device_type (``str`` *optional*, *modifiable*):
            The user's device type: ``android`` or ``ios``.

        login_type (``str`` *optional*, *modifiable*):
            The user's login type: ``email`` or ``apple``.

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

        carrier (``str`` *optional*, *modifiable*):
            The user's cell phone carrier.

        comments_enabled (``bool``):
            Whether the user is allowing comments. You can ask the user to turn on comments with :py:func:`~meapi.Me.suggest_turn_on_comments`.

        comments_blocked (``bool``):
            Whether the user blocked you from commenting on his profile.

        country_code (``str``):
            The user's two-letter country code.

        location_enabled (``bool`` *optional*):
            Whether the user is allowing location.

        is_shared_location (``bool`` *optional*):
            Whether the user is sharing their location with you. You can ask the user to share his location with :py:func:`~meapi.Me.suggest_turn_on_location`.

        share_location (``bool`` *optional*):
            Whether the user is sharing their location with you.

        distance (``float`` *optional*):
            The user's distance from you.

        location_longitude (``float`` *optional*):
            The user's location longitude coordinate.

        location_latitude (``float`` *optional*):
            The user's location latitude coordinate.

        location_name (``str`` *optional*, *modifiable*):
            The user's location name.

        is_he_blocked_me (``bool`` *optional*):
            Whether the user has blocked you from seeing his profile (``me_full_block``, See :py:func:`~meapi.Me.block_profile`).
                - If ``True``, this profile will contain only the basic information, like ``name``, ``uuid`` and ``phone_number``.

        is_permanent (``bool`` *optional*):
            Whether the user is permanent.

        mutual_contacts_available (``bool`` *optional*):
            Whether the user has mutual contacts available. You can ask the user to turn on this feature with :py:func:`~meapi.Me.suggest_turn_on_mutual`.

        mutual_contacts (List[:py:obj:`~meapi.models.mutual_contact.MutualContact`] *optional*):
            `For more information about mutual contacts <https://me.app/mutual-contacts/>`_.

        is_premium (``bool``):
            Whether the user is a premium user.

        is_verified (``bool``):
            Whether the user is verified.

        gdpr_consent (``bool``):
            Whether the user has given consent to the GDPR.

        facebook_url (``str`` *optional*, *modifiable*):
            The user's Facebook ID.

        google_url (``str`` *optional*, *modifiable*):
            The user's Google ID.

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
                 profile_deletes_left: bool = None,
                 _my_profile: bool = False
                 ):
        self.__client = _client
        self.comments_blocked = comments_blocked
        self.is_he_blocked_me = is_he_blocked_me
        self.is_permanent = is_permanent
        self.is_shared_location = is_shared_location
        self.last_comment = Comment.new_from_dict(last_comment, _client=_client, profile_uuid=uuid)
        self.mutual_contacts_available = mutual_contacts_available
        self.mutual_contacts: List[MutualContact] = [MutualContact.new_from_dict(mutual_contact, _client=_client) for mutual_contact in
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
        self.profile_deletes_left = profile_deletes_left
        self.__my_profile = _my_profile

    @property
    def name(self) -> Optional[str]:
        """
        Returns the full name of the user. ``first_name`` + ``last_name``.
        """
        return (self.first_name or '') + (' ' if self.first_name and self.last_name else '') + (self.last_name or '') or None

    @name.setter
    def name(self, new_name: str):
        """
        Sets the full name of the user. ``first_name`` + ``last_name``.
        """
        if ' ' in new_name:
            self.first_name, self.last_name = new_name.split(' ', 1)
        else:
            self.last_name, self.first_name = new_name, ''

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
                if key == '_Profile__my_profile' or key == 'name':
                    return super().__setattr__(key, value)
                modifiable_attrs = ('first_name', 'last_name', 'email', 'gender', 'slogan', 'profile_picture',
                                    'date_of_birth', 'location_name', 'device_type', 'login_type', 'facebook_url',
                                    'google_url', 'carrier')
                if key not in modifiable_attrs:
                    raise FrozenInstance(
                        self, key,
                        f"You can not modify this attr!\nThe modifiable attrs are: {', '.join(modifiable_attrs)}")
                success, new_profile = self.__client.update_profile_details(**{key: value})
                if (success and str(getattr(new_profile, key, None)) == str(value)) or key == 'profile_picture':
                    # Can't check if profile picture updated because Me convert's it to their own url.
                    value = getattr(new_profile, key, None)
                    if key == 'date_of_birth':
                        value = parse_date(value, date_only=True)
                    if key == 'facebook_url' and value:
                        value = f"https://facebook.com/profile.php?id={value}"
                else:
                    raise ValueError(f"Failed to change '{getattr(self, key)}' to '{value}'!")
            else:
                raise FrozenInstance(self, key, "You cannot update profile if it's not yours!")
        super().__setattr__(key, value)
