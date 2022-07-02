from typing import Union
from meapi.models.me_model import MeModel
from meapi.models.user import User


class MutualContact(MeModel):
    """
    - `For more information about MutualContact <https://me.app/mutual-contacts/>`_
    """
    def __init__(self,
                 phone_number: Union[int, None] = None,
                 name: Union[str, None] = None,
                 referenced_user: Union[dict, None] = None,
                 date_of_birth: Union[str, None] = None
                 ):
        self.phone_number = phone_number
        self.name = name
        self.referenced_user: User = User.new_from_dict(referenced_user)
        self.date_of_birth = date_of_birth
        super().__init__()

    def __repr__(self):
        return f"<MutualContact name={self.name} phone={self.phone_number}>"

    def __str__(self):
        return self.name