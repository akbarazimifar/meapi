from typing import Union, TYPE_CHECKING
from meapi.models.common import _CommonMethodsForUserContactProfile
from meapi.models.me_model import MeModel
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me


class User(MeModel, _CommonMethodsForUserContactProfile):
    """
    Represents a user.
        - A user is a person who log in to the app.
        - If you search a phone number with :py:func:`~meapi.Me.phone_search`, you will get a contact, but if this contact registered on the app, you get a user attribute.

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
        in_contact_list (``bool`` *optional*):
            Whether the contact is in your contacts book.
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

        Get the user as Vcard: :py:func:`~meapi.models.common._CommonMethodsForUserContactProfile.as_vcard`.
        Block the user: :py:func:`~meapi.models.common._CommonMethodsForUserContactProfile.block`.
        Unblock this user: :py:func:`~meapi.models.common._CommonMethodsForUserContactProfile.unblock`.
        Report this user as spam: :py:func:`~meapi.models.common._CommonMethodsForUserContactProfile.report_spam`.
    """
    def __init__(self,
                 _client: 'Me',
                 first_name: str,
                 last_name: str,
                 uuid: str,
                 phone_number: int,
                 email: str = None,
                 profile_picture: str = None,
                 slogan: str = None,
                 gender: str = None,
                 is_verified: bool = None,
                 is_premium: bool = None,
                 location_enabled: bool = None,
                 verify_subscription: bool = None,
                 id: int = None,
                 comment_count: int = None,
                 distance: float = None,
                 in_contact_list: bool = None
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
        self.in_contact_list = in_contact_list
        super().__init__()

    @property
    def name(self) -> str:
        """
        Returns the full name of the user. ``first_name`` + ``last_name``.
        """
        return (self.first_name or '') + (' ' if self.first_name and self.last_name else '') + (self.last_name or '')

    def __repr__(self):
        return f"<User name={self.name} uuid={self.uuid}>"

    def __str__(self):
        return str(self.name)
