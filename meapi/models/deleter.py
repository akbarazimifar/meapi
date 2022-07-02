from datetime import datetime
from typing import Union
from meapi.utils.helpers import parse_date
from meapi.models.me_model import MeModel
from meapi.models.user import User


class Deleter(MeModel):
    """
    Represents a Deleter, user who delete you from his contacts.
        - `For more information about Deleter <https://me.app/who-deleted-my-phone-number/>`_

    Parameters:
        created_at (``str``):
            Date of delete.
        user (:py:obj:`~meapi.models.user.User`):
            User who delete you.
    """
    def __init__(self,
                 created_at: str,
                 user: dict
                 ):
        self.created_at: datetime = parse_date(created_at)
        self.user = User.new_from_dict(user)
        super().__init__()

    def __repr__(self):
        return f"<Deleter name={self.user.name}>"

    def __str__(self):
        return f"{self.user.name}"
