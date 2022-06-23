from datetime import datetime
from typing import Union, List
from meapi.exceptions import MeException
from meapi.helpers import parse_date
from meapi.models.me_model import MeModel


class Social(MeModel):
    def __init__(self=None,
                 facebook: Union[dict, None] = None,
                 fakebook: Union[dict, None] = None,
                 instagram: Union[dict, None] = None,
                 linkedin: Union[dict, None] = None,
                 pinterest: Union[dict, None] = None,
                 spotify: Union[dict, None] = None,
                 tiktok: Union[dict, None] = None,
                 twitter: Union[dict, None] = None,
                 _my_social: bool = False,
                 _meobj = None
                 ):
        self.facebook = SocialMediaAccount.new_from_json_dict(facebook, _meobj=_meobj, _my_social=_my_social, name='facebook')
        self.fakebook = SocialMediaAccount.new_from_json_dict(fakebook, _meobj=_meobj, _my_social=_my_social, name='fakebook')
        self.instagram = SocialMediaAccount.new_from_json_dict(instagram, _meobj=_meobj, _my_social=_my_social, name='instagram')
        self.linkedin = SocialMediaAccount.new_from_json_dict(linkedin, _meobj=_meobj, _my_social=_my_social, name='linkedin')
        self.pinterest = SocialMediaAccount.new_from_json_dict(pinterest, _meobj=_meobj, _my_social=_my_social, name='pinterest')
        self.spotify = SocialMediaAccount.new_from_json_dict(spotify, _meobj=_meobj, _my_social=_my_social, name='spotify')
        self.tiktok = SocialMediaAccount.new_from_json_dict(tiktok, _meobj=_meobj, _my_social=_my_social, name='tiktok')
        self.twitter = SocialMediaAccount.new_from_json_dict(twitter, _meobj=_meobj, _my_social=_my_social, name='twitter')
        super().__init__()


class SocialMediaAccount(MeModel):
    def __init__(self,
                 name: str,
                 _my_social: bool,
                 _meobj = None,
                 posts: Union[List[dict], None] = None,
                 profile_id: Union[str, None] = None,
                 is_active: Union[bool, None] = None,
                 is_hidden: Union[bool, None] = None,
                 ):
        self.name = name
        self.posts: Union[List[Post], None] = [Post.new_from_json_dict(post) for post in posts] if posts else posts
        self.profile_id = profile_id
        self.is_active = is_active
        self.is_hidden = is_hidden
        self.__my_social = _my_social
        self.__meobj = _meobj
        self.__init_done = True

    def __setattr__(self, key, value):
        if getattr(self, '_SocialMediaAccount__init_done', None):
            if not self.__my_social:
                raise MeException(f"You cannot change social of another user!")
        return super().__setattr__(key, value)

    def __repr__(self):
        return f"<Social profile_id={self.profile_id} is_active={self.is_active}>"

    def __str__(self):
        return str(self.profile_id)

    def add(self, token_or_url) -> bool:
        if not self.__my_social:
            raise MeException(f"You cannot add social to another user!")
        if self.name in ['linkedin', 'pinterest']:
            key = f'{self.name}_url'
        else:
            key = f'{self.name}_token'

    def remove(self) -> bool:
        if not self.__my_social:
            raise MeException("You cannot remove social from another user!")
        if not self.is_active:
            raise MeException("This social is already not active!")
        if self.__meobj.remove_social(**{self.name: True}):
            self.profile_id = None
            self.is_active = False
            self.is_hidden = True
            self.posts = None
            return True
        return False

    def hide(self) -> bool:
        if not self.__my_social:
            raise MeException("You cannot remove social from another user!")
        if not self.is_active:
            raise MeException("This social is not active!")
        if self.is_hidden:
            raise MeException("This social is already hidden!")
        if self.__meobj.switch_social_status(**{self.name: True}):  # todo create separate methods to hide and to unhide
            self.is_hidden = True
            return True
        return False

    def unhide(self) -> bool:
        if not self.__my_social:
            raise MeException("You cannot remove social from another user!")
        if not self.is_active:
            raise MeException("This social is not active!")
        if not self.is_hidden:
            raise MeException("This social is already unhidden!")
        if self.__meobj.switch_social_status(**{self.name: True}):  # todo create separate methods to hide and to hide
            self.is_hidden = False
            return True
        return False


class Post(MeModel):
    def __init__(self,
                 posted_at: Union[str, None] = None,
                 photo: Union[str, None] = None,
                 text_first: Union[str, None] = None,
                 text_second: Union[str, None] = None,
                 author: Union[str, None] = None,
                 redirect_id: Union[str, None] = None,
                 owner: Union[str, None] = None
                 ):
        self.posted_at: Union[datetime, None] = parse_date(posted_at) if posted_at else posted_at
        self.photo = photo
        self.text_first = text_first
        self.text_second = text_second
        self.author = author
        self.redirect_id = redirect_id
        self.owner = owner
        super().__init__()

    def __repr__(self):
        return f"<Post text={self.text_first} id={self.redirect_id}>"

    def __str__(self):
        return str(self.text_first)
