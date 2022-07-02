from typing import Union
from meapi.models.me_model import MeModel


class Friendship(MeModel):
    """
    Represents a Friendship.
        - Friendship is a relationship between you and another user.
        - `For more information about Friendship <https://me.app/friendship/>`_

    Parameters:
        calls_duration (``int``):
            The duration of your calls in seconds.
        he_called (``int``):
            The number of times the other user has called you.
        i_called (``int``):
            The number of times you have called the other user.
        he_named (``str``):
            How the other user named you in his contacts book.
        i_named (``str``):
            How you named the other user in your contacts book.
        he_watched (``int``):
            The number of times the other user has watched your profile.
        his_comment (``str``):
            The comment the other user has comment on your profile.
        my_comment (``str`` *optional*):
            The comment you have comment on the other user's profile.
        i_watched (``int``):
            The number of times you have watched the other user's profile.
        mutual_friends_count (``int``):
            The number of mutual contacts between you and the other user.
        is_premium (``bool``):
            Whether the other user is a premium user.
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
        return f"<Friendship you={self.i_named} he/she={self.he_named}>"

    def __str__(self):
        return f"{self.i_named} {self.he_named}"
