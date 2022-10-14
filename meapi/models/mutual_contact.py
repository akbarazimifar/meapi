from datetime import date
from typing import Optional
from meapi.models.me_model import MeModel
from meapi.utils.helpers import parse_date


class MutualContact(MeModel):
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
    """
    def __init__(self,
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
        super().__init__()

    def __repr__(self):
        return f"<MutualContact name={self.name} phone={self.phone_number}>"
