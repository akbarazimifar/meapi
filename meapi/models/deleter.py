from datetime import datetime
from meapi.utils.helpers import parse_date
from meapi.models.me_model import MeModel
from meapi.models.user import User


class Deleter(MeModel):
    """
    Represents a Deleter, user who delete you from his contacts.
        - `For more information about Deleter <https://me.app/who-deleted-my-phone-number/>`_

    Examples:
        >>> my_deleters = me.who_deleted()
        >>> deleter = my_deleters[0]
        >>> deleter.user.name
        'Janine Lecroix'
        >>> me.publish_comment(uuid=deleter.user,your_comment="How You Doin'?")
        <Comment id=456 status=waiting msg=How You Doin'? author=Joey Tribbiani>


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
