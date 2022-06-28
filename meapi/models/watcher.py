from datetime import datetime
from typing import Union
from meapi.utils.helpers import parse_date
from meapi.models.me_model import MeModel
from meapi.models.user import User


class Watcher(MeModel):
    """
        - For more information about Watcher <https://me.app/who-viewed-my-profile/>
    """
    def __init__(self, last_view: Union[str, None] = None,
                 user: Union[dict, None] = None,
                 count: Union[int, None] = None,
                 is_search: Union[bool, None] = None) -> None:
        self.last_view: datetime = parse_date(last_view)
        self.user: User = User.new_from_json_dict(user)
        self.count = count
        self.is_search = is_search
        super().__init__()

    def __repr__(self):
        return f"<Watcher name={self.user.first_name} {self.user.last_name or ''} count={self.count}>"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name or ''}"

