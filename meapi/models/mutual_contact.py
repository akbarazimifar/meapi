from datetime import date
from typing import Optional, TYPE_CHECKING
from meapi.models.common import _CommonMethodsForUserContactProfile
from meapi.models.me_model import MeModel
from meapi.utils.helpers import parse_date
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me


class MutualContact(MeModel, _CommonMethodsForUserContactProfile):
    """
    Represents a Mutual contact between you and another user.


    Parameters:
        name (``str``):
            The user's fullname.
        phone_number(``int``)
            The user's phone number.
        date_of_birth (:py:obj:`~datetime.date`):
            The user's date of birth.
        uuid (``str`` *optional*):
            The user's unique ID.

    Methods:

        Get the contact as Vcard: :py:func:`~meapi.models.common._CommonMethodsForUserContactProfile.as_vcard`.
        Block this contact: :py:func:`~meapi.models.common._CommonMethodsForUserContactProfile.block`.
        Unblock this contact: :py:func:`~meapi.models.common._CommonMethodsForUserContactProfile.unblock`.
        Report this contact as spam: :py:func:`~meapi.models.common._CommonMethodsForUserContactProfile.report_spam`.
    """
    def __init__(self,
                 _client: 'Me',
                 name: str,
                 phone_number: int,
                 date_of_birth: str,
                 referenced_user: dict = None,
                 uuid: str = None
                 ):
        self.name = name
        self.phone_number = phone_number
        self.date_of_birth: Optional[date] = parse_date(date_of_birth, date_only=True)
        if isinstance(referenced_user, dict):
            self.uuid = referenced_user.get('uuid')
        else:
            self.uuid = None
        self.__client = _client
        super().__init__()
