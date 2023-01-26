from datetime import datetime
from typing import Optional, TYPE_CHECKING
from meapi.utils.exceptions import FrozenInstance
from meapi.utils.helpers import parse_date
from meapi.models.me_model import MeModel, _logger
from meapi.models.user import User
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me


class Comment(MeModel):
    """
    Represents a comment.

    Examples:
        >>> my_comments = me.get_comments()
        >>> my_comments[0].message
        'We were on a break!'
        >>> my_comments[0].like_count
        7
        >>> my_comments[0].author.name
        'Ross Geller'
        >>> my_comments[0].like()
        True
        >>> my_comments[0].reply("I got off the plane.")
        <Comment id=123 status=waiting msg=I got off the plane. author=Rachel Green>


    Parameters:
        message (``str``):
            The message of the comment.
        id (``int``):
            The id of the comment.
        status (``str``):
            The status of the comment: ``approved``, ``ignored``, ``waiting``, ``deleted``.
        author (:py:obj:`~meapi.models.user.User`):
            The creator of the comment.
        like_count (``int``):
            The number of likes of the comment.
        comment_likes (``list`` of :py:obj:`~meapi.models.user.User`):
            The list of users who liked the comment.
        created_at (``datetime``):
            The date of the comment creation.
        is_liked (``bool``):
            Whether the creator liked his comment.
        comments_blocked (``bool``):
            Whether the user blocked the comments of the comment.

    Methods:

    .. automethod:: approve
    .. automethod:: edit
    .. automethod:: ignore
    .. automethod:: delete
    .. automethod:: like
    .. automethod:: unlike
    .. automethod:: reply
    .. automethod:: block
    """
    def __init__(self,
                 _client: 'Me',
                 like_count: int = None,
                 status: str = None,
                 message: str = None,
                 author: dict = None,
                 is_liked: bool = None,
                 id: int = None,
                 comments_blocked: bool = None,
                 created_at: str = None,
                 comment_likes: dict = None,
                 profile_uuid: str = None,
                 _my_comment: bool = False
                 ):
        self.like_count = like_count
        self.status = status
        self.message = message
        self.author = User.new_from_dict(author)
        self.is_liked = is_liked
        self.id = id
        self.profile_uuid = profile_uuid
        self.comments_blocked = comments_blocked
        self.created_at: Optional[datetime] = parse_date(created_at)
        self.comment_likes = [User.new_from_dict(user['author']) for user in
                              comment_likes] if comment_likes else None
        self.__client = _client
        self.__my_comment = _my_comment
        self.__init_done = True

    def approve(self) -> bool:
        """
        Approve the comment.
            - You can only approve comments that posted by others on your own profile.
            - The same as :py:func:`~meapi.Me.approve_comment`.

        Returns:
            ``bool``: Is approve success.
        """
        if self.__client.approve_comment(self):
            self.status = 'approved'
            return True
        return False

    def edit(self, new_msg: str, remove_credit: bool = False) -> bool:
        """
        Edit the comment.
            - You can only edit comments that posted by you.
            - The same as :py:func:`~meapi.Me.publish_comment`.

        Parameters:
            new_msg (``str``):
                The new message of the comment.
            remove_credit (``bool``):
                Whether to remove the credit to ``meapi`` from the comment.

        Returns:
            ``bool``: Is edit success.
        """
        if self.author.uuid == self.__client.uuid:
            if self.status == 'deleted':
                _logger.warning("EDIT_COMMENT: You can't edit deleted comment!")
                return False
            if self.__client.publish_comment(self.profile_uuid, new_msg, remove_credit):
                self.message = new_msg
                self.status = 'waiting'
                return True
            return False
        else:
            _logger.warning("EDIT_COMMENT: You can only edit comments that posted by you.")
            return False

    def ignore(self) -> bool:
        """
        Ignore and hide the comment.
            - You can only ignore and hide comments that posted by others on your own profile.
            - The same as :py:func:`~meapi.Me.ignore_comment`.

        Returns:
            ``bool``: Is ignore success.
        """
        if self.__client.ignore_comment(self):
            self.status = 'ignored'
            return True
        return False

    def delete(self) -> bool:
        """
        Delete the comment.
            - You can only delete comments that posted on your own profile or by you.
            - The same as :py:func:`~meapi.Me.delete_comment`.

        Returns:
            ``bool``: Is delete success.
        """
        if self.__client.delete_comment(self):
            self.status = 'deleted'
            return True
        return False

    def like(self) -> bool:
        """
        Like the comment.
            - The same as :py:func:`~meapi.Me.like_comment`.

        Returns:
            ``bool``: Is like success.
        """
        if self.__client.like_comment(self.id):
            self.like_count += 1
            return True
        return False

    def unlike(self) -> bool:
        """
        Unlike the comment.
            - The same as :py:func:`~meapi.Me.unlike_comment`.

        Returns:
            ``bool``: Is unlike success.
        """
        if self.__client.unlike_comment(self.id):
            self.like_count -= 1
            return True
        return False

    def reply(self, your_comment: str) -> Optional['Comment']:
        """
        Publish a comment in the profile of the comment author.
            - The same as :py:func:`~meapi.Me.publish_comment`.
            - if you already replied to the comment, this will edit the comment like :py:func:`~meapi.models.comment.Comment.edit`.

        Parameters:
            your_comment (``str``):
                The message of the comment.

        Returns:
            :py:obj:`~meapi.models.comment.Comment`: The new comment.
        """
        return self.__client.publish_comment(self.profile_uuid, your_comment)

    def block(self):
        """
        Block the author of the comment from posting comments on your profile.
            - The same as :py:func:`~meapi.Me.block_comments`.
            - This will not delete the comment. It will just block the author from editing or posting comments on your profile.

        Returns:
            ``bool``: Is block success.
        """
        if self.__client.block_comments(self):
            self.comments_blocked = True
            return True
        return False

    def __setattr__(self, key, value):
        if getattr(self, '_Comment__init_done', None):
            if key not in ('message', 'status', 'like_count', 'comment_likes', 'comments_blocked'):
                raise FrozenInstance(self, key)
        return super().__setattr__(key, value)
