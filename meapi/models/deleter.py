from typing import Union
from meapi.utils.helpers import parse_date
from meapi.models.me_model import MeModel
from meapi.models.user import User


class Deleter(MeModel):
    def __init__(self,
                 created_at: Union[str, None] = None,
                 user: Union[dict, None] = None
                 ):
        self.created_at = parse_date(created_at)
        self.user = User.new_from_json_dict(user)
        super().__init__()

    def __repr__(self):
        return f"<Deleter name={self.user.first_name} {self.user.last_name or ''}>"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name or ''}"
