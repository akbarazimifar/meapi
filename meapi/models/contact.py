from datetime import datetime
from typing import Union
from meapi.utils.helpers import parse_date
from meapi.models.common import _CommonMethodsForUserContactProfile
from meapi.models.me_model import MeModel
from meapi.models.user import User


class Contact(MeModel, _CommonMethodsForUserContactProfile):
    """
    Represents a contact.

    Parameters:
        name (``str``):
            The name of the contact.
        phone_number (``int``):
            The phone number of the contact.
        id (``int``):
            The id of the contact.
        picture (``str`` *optional*):
            The url picture of the contact.
        user (:py:obj:`~meapi.models.user.User` *optional*):
            The user of the contact. if the user register on the app.
        suggested_as_spam (``int`` *optional*):
            The number of times the contact has been suggested as spam.
        user_type (``str`` *optional*):
            The user's type: the color of the user in the app:
                - ``BLUE``: Verified Caller ID from ME users (100% ID).
                - ``GREEN``: Identified call with a very reliable result.
                - ``YELLOW``: Uncertain Identification (Unverified).
                - ``ORANGE``: No identification (can be reported).
                - ``RED``: Spam calls.
        is_permanent (``bool`` *optional*):
            Whether the contact is permanent.
        is_pending_name_change (``bool`` *optional*):
            Whether the contact is pending name change.
        cached (``bool`` *optional*):
            Whether the results from the api is cached.
        is_shared_location (``bool`` *optional*):
            Whether the contact is shared location.
        created_at (``datetime`` *optional*):
            The date of the contact creation.
        modified_at (``datetime`` *optional*):
            The date of the contact modification.
        in_contact_list (``bool`` *optional*):
            Whether the contact is in the contact list.
        is_my_contact (``bool`` *optional*):
            Whether the contact is my contact.

    Methods:

    .. automethod:: get_profile
    .. automethod:: get_vcard
    .. automethod:: block
    .. automethod:: unblock
    .. automethod:: report_spam
    """
    def __init__(self,
                 _client,
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
        self.__client = _client
        self.name = name
        self.id = id
        self.picture = picture
        self.user: User = User.new_from_dict(user, _client=self.__client) if user else None
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

    def get_profile(self):
        """
        Returns the profile of the contact.

        Returns:
            :py:obj:`~meapi.models.profile.Profile` | ``None``: The profile of the contact or ``None`` if the contact has no user.
        """
        return self.user.get_profile() if self.user else self.user

    def __repr__(self):
        return f"<Contact name={self.name} phone={self.phone_number} id={self.id}>"

    def __str__(self):
        return self.name or "Not found"
