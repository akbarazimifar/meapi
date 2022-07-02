from datetime import datetime
from meapi.utils.helpers import parse_date
from meapi.models.me_model import MeModel
from meapi.models.user import User


class Watcher(MeModel):
    """
    Represents a Watcher, user who watch your profile.
        - `For more information about Watcher <https://me.app/who-viewed-my-profile/>`_

    Parameters:
        last_view (``datetime``):
            Date of last view.
        user (:py:obj:`~meapi.models.user.User`):
            The user who watch your profile.
        count (``int``):
            The number of views.
        is_search (``bool``):
            Whether the user is searching your profile.
    """
    def __init__(self,
                 last_view: str,
                 user: dict,
                 count: int,
                 is_search: bool
                 ) -> None:
        self.last_view: datetime = parse_date(last_view)
        self.user: User = User.new_from_dict(user)
        self.count = count
        self.is_search = is_search
        super().__init__()

    def __repr__(self):
        return f"<Watcher name={self.user.name} count={self.count}>"

    def __str__(self):
        return self.user.name

