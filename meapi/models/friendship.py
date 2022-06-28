from typing import Union
from meapi.models.me_model import MeModel


class Friendship(MeModel):
    """
    - `For more information about Friendship <https://me.app/friendship/>`_
    """
    def __init__(self,
                 calls_duration: Union[None, None] = None,
                 he_called: Union[int, None] = None,
                 he_named: Union[str, None] = None,
                 he_watched: Union[int, None] = None,
                 his_comment: Union[None, None] = None,
                 i_called: Union[int, None] = None,
                 i_named: Union[str, None] = None,
                 i_watched: Union[int, None] = None,
                 is_premium: Union[bool, None] = None,
                 mutual_friends_count: Union[int, None] = None,
                 my_comment: Union[str, None] = None
                 ):
        self.calls_duration = calls_duration
        self.he_called = he_called
        self.he_named = he_named
        self.he_watched = he_watched
        self.his_comment = his_comment
        self.i_called = i_called
        self.i_named = i_named
        self.i_watched = i_watched
        self.is_premium = is_premium
        self.mutual_friends_count = mutual_friends_count
        self.my_comment = my_comment
        super().__init__()

    def __repr__(self):
        return f"<Friendship of={self.i_named} and={self.he_named}>"

    def __str__(self):
        return self.i_named
