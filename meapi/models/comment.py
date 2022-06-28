from typing import Union
from meapi.utils.exceptions import MeException
from meapi.utils.helpers import parse_date
from meapi.models.me_model import MeModel
from meapi.models.user import User


class Comment(MeModel):
    def __init__(self,
                 _meobj,
                 like_count: Union[int, None] = None,
                 status: Union[str, None] = None,
                 message: Union[str, None] = None,
                 author: Union[dict, None] = None,
                 is_liked: Union[bool, None] = None,
                 id: Union[int, None] = None,
                 comments_blocked: Union[bool, None] = None,
                 created_at: Union[str, None] = None,
                 comment_likes: Union[dict, None] = None,
                 _my_comment: bool = False
                 ):
        self.like_count = like_count
        self.status = status
        self.message = message
        self.author = User.new_from_json_dict(author)
        self.is_liked = is_liked
        self.id = id
        self.comments_blocked = comments_blocked
        self.created_at = parse_date(created_at)
        self.comment_likes = [User.new_from_json_dict(user['author']) for user in
                              comment_likes] if comment_likes else None
        self.__meobj = _meobj
        self.__my_comment = _my_comment
        self.__init_done = True

    def __setattr__(self, key, value):
        if getattr(self, '_Comment__init_done', None):
            if key not in ['message', 'status', 'like_count', 'comment_likes']:
                raise MeException("You can't change this attr!")
        return super().__setattr__(key, value)

    def __repr__(self):
        return f"<Comment id={self.id} status={self.status} msg={self.message}>"

    def __str__(self):
        return self.message

    def approve(self) -> bool:
        if self.__my_comment:
            raise MeException("You can only approve others comments!")
        if self.id:
            if self.__meobj.approve_comment(self.id):
                self.status = 'approved'
                return True
        return False

    def like(self) -> bool:
        if self.id:
            if self.__meobj.like_comment(self.id):
                self.like_count += 1
                return True
        return False

    def delete(self):
        if self.__my_comment:
            raise MeException("You can delete others comments!")
        if self.id:
            if self.__meobj.delete_comment(self.id):
                self.status = 'ignored'
                return True
        return False

