from typing import Union
from meapi.utils.helpers import parse_date
from meapi.models.me_model import MeModel
from meapi.models.user import User


class Call(MeModel):
    def __init__(self,
                 called_at: Union[str, None] = None,
                 duration: Union[int, None] = None,
                 name: Union[str, None] = None,
                 phone_number: Union[int, None] = None,
                 referenced_user: Union[dict, None] = None,
                 tag: Union[str, None] = None,
                 type: Union[str, None] = None
                 ):
        self.called_at = parse_date(called_at)
        self.duration = duration
        self.name = name
        self.phone_number = phone_number
        self.referenced_user = User.new_from_dict(referenced_user) if referenced_user else referenced_user
        self.tag = tag
        self.type = type
        super().__init__()

    def __repr__(self):
        return f"<Call name={self.name} phone={self.phone_number}>"

    def __str__(self):
        return str(self.phone_number)