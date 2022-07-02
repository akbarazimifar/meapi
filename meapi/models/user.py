from typing import Union
from meapi.models.common import _CommonMethodsForUserContactProfile
from meapi.models.me_model import MeModel


class User(MeModel, _CommonMethodsForUserContactProfile):
    """
    Represents a user.
        - A user is a person who can log in to the app. if you search a phone number with :py:func:`~meapi.Me.phone_search`, you will get a contact, but if this contact registered on the app, you get a user attribute.

    Parameters:
         name (``str``):
            The fullname of the user. combined with ``first_name`` and ``last_name``.
         first_name (``str``):
            The first name of the user.
         last_name (``str``):
            The last name of the user.
         uuid (``str``):
            The unique identifier of the user. can be used to perform actions on the user.
         phone_number (``int``):
            The phone number of the user.
         gender (``str`` *optional*):
            The gender of the user. ``M`` for male, ``F`` for female, and ``None`` if the user didn't specify.
         email (``str`` *optional*):
            The email of the user.
         profile_picture (``str`` *optional*):
            Url to profile picture of the user.
         slogan (``str`` *optional*):
            The bio of the user.
         is_verified (``bool`` *optional*):
            Whether the user is verified (Has at least two social connected accounts).
         is_premium (``bool`` *optional*):
            Whether the user is paying for premium features (Like the ability to use who watch his profile,
            who deleted him from his contacts, no ads, and more).
         location_enabled (``bool`` *optional*):
            Whether the user has enabled location sharing.
         verify_subscription (``bool`` *optional*):
            Whether the user has verified his subscription.
         id (``int`` *optional*):
            The id of the contact.
         comment_count (``int`` *optional*):
            The number of comments the user have in his profile.
         distance (``float`` *optional*):
            The distance between you and the user (Only if the user shared his location with you. See :py:func:`~meapi.Me.suggest_turn_on_location`).

    Methods:

    .. automethod:: get_vcard
    .. automethod:: report_spam
    .. automethod:: get_profile
    .. automethod:: block
    .. automethod:: unblock
    """
    def __init__(self,
                 _client,
                 first_name: str,
                 last_name: str,
                 uuid: str,
                 phone_number: int,
                 email: Union[str, None] = None,
                 profile_picture: Union[str, None] = None,
                 slogan: Union[str, None] = None,
                 gender: Union[str, None] = None,
                 is_verified: Union[bool, None] = None,
                 is_premium: Union[bool, None] = None,
                 location_enabled: Union[bool, None] = None,
                 verify_subscription: Union[bool, None] = None,
                 id: Union[int, None] = None,
                 comment_count: Union[int, None] = None,
                 distance: Union[float, None] = None
                 ):
        self.__client = _client
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

    def get_profile(self):
        """
        Returns the profile of the user.
        """
        return self.__client.get_profile(self.uuid)

    def __repr__(self):
        return f"<User name={self.first_name} {self.last_name or ''}>"

    def __str__(self):
        return self.uuid