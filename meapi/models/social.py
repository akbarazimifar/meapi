import copy
from datetime import datetime
from typing import Union, List
from meapi.utils.exceptions import MeException
from meapi.utils.helpers import parse_date
from meapi.models.me_model import MeModel


class Social(MeModel):
    """
    **Represents user's social media accounts.**

    Parameters:
        facebook (~meapi.models.social.SocialMediaAccount):
            Facebook account.
        fakebook (~meapi.models.social.SocialMediaAccount):
            Fakebook account.
        instagram (~meapi.models.social.SocialMediaAccount):
            Instagram account.
        linkedin (~meapi.models.social.SocialMediaAccount):
            LinkedIn account.
        pinterest (~meapi.models.social.SocialMediaAccount):
            Pinterest account.
        spotify (~meapi.models.social.SocialMediaAccount):
            Spotify account.
        tiktok (~meapi.models.social.SocialMediaAccount):
            Tiktok account.
        twitter (~meapi.models.social.SocialMediaAccount):
            Twitter account.
    """
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
                 _client = None
                 ):
        self.facebook: SocialMediaAccount = SocialMediaAccount.new_from_dict(facebook, _client=_client, _my_social=_my_social, name='facebook')
        self.fakebook: SocialMediaAccount = SocialMediaAccount.new_from_dict(fakebook, _client=_client, _my_social=_my_social, name='fakebook')
        self.instagram: SocialMediaAccount = SocialMediaAccount.new_from_dict(instagram, _client=_client, _my_social=_my_social, name='instagram')
        self.linkedin: SocialMediaAccount = SocialMediaAccount.new_from_dict(linkedin, _client=_client, _my_social=_my_social, name='linkedin')
        self.pinterest: SocialMediaAccount = SocialMediaAccount.new_from_dict(pinterest, _client=_client, _my_social=_my_social, name='pinterest')
        self.spotify: SocialMediaAccount = SocialMediaAccount.new_from_dict(spotify, _client=_client, _my_social=_my_social, name='spotify')
        self.tiktok: SocialMediaAccount = SocialMediaAccount.new_from_dict(tiktok, _client=_client, _my_social=_my_social, name='tiktok')
        self.twitter: SocialMediaAccount = SocialMediaAccount.new_from_dict(twitter, _client=_client, _my_social=_my_social, name='twitter')
        super().__init__()


class SocialMediaAccount(MeModel):
    """
    **Represents user's social media account.**

    Parameters:
        name (``str``):
            Name of social media account.
        profile_id (``str``):
            Profile ID or username of social media account.
        posts (List[:py:obj:`~meapi.models.social.Post`]):
            List of posts from social media account.
        is_active (``bool``):
            Is social media account active.
        is_hidden (``bool``):
            Is social media account hidden by the user (You can see it because the API sends it anyway ;).

    Methods:

    .. automethod:: add
    .. automethod:: remove
    .. automethod:: hide
    .. automethod:: unhide
    """
    def __init__(self,
                 name: str,
                 _my_social: bool,
                 _client = None,
                 posts: Union[List[dict], None] = None,
                 profile_id: Union[str, None] = None,
                 is_active: Union[bool, None] = None,
                 is_hidden: Union[bool, None] = None,
                 ):
        self.name = name
        self.posts: Union[List[Post], None] = [Post.new_from_dict(post) for post in posts] if posts else posts
        self.profile_id = profile_id
        self.is_active = is_active
        self.is_hidden = is_hidden
        self.__my_social = _my_social
        self.__client = _client
        self.__init_done = True

    def __setattr__(self, key, value):
        if getattr(self, '_SocialMediaAccount__init_done', None):
            if not self.__my_social:
                raise MeException(f"You cannot change social of another user!")
        return super().__setattr__(key, value)

    def __repr__(self):
        return f"<{self.name.capitalize()} profile_id={self.profile_id} is_active={self.is_active}>"

    def __str__(self):
        return str(self.name)

    def add(self, token_or_url: str) -> bool:
        """
        Add social media account to your Me profile.
            - If you have at least two social media accounts, you get verification tag on your profile. ``is_verified`` = ``True``.

        Parameters:
            token_or_url (``str``):
                Token or URL of social media account.
                    - See :py:func:`~meapi.Me.add_social` for more information.

        Returns:
            ``bool``: ``True`` if successfully added, ``False`` otherwise.
        """
        if not self.__my_social:
            raise MeException(f"You cannot add social to another user!")
        if self.is_active:
            raise MeException("This social is already active, No need to add it again!")
        key = f'{self.name}_url' if self.name in ['linkedin', 'pinterest'] else f'{self.name}_token'
        if self.__client.add_social(**{key: token_or_url}):
            self.__dict__ = copy.deepcopy(getattr(self.__client.get_socials(), self.name).__dict__)
            return True
        return False

    def remove(self) -> bool:
        """
        Remove social media account from your Me profile.

        Returns:
            ``bool``: ``True`` if successfully removed, ``False`` otherwise.
        """
        if not self.__my_social:
            raise MeException("You cannot remove social from another user!")
        if not self.is_active:
            raise MeException("This social is already not active!")
        if self.__client.remove_social(**{self.name: True}):
            self.profile_id = None
            self.is_active = False
            self.is_hidden = True
            self.posts = None
            return True
        return False

    def hide(self) -> bool:
        """
        Hide social media account in your Me profile.

        Returns:
            ``bool``: ``True`` if successfully hidden, ``False`` otherwise.
        """
        if not self.__my_social:
            raise MeException("You cannot remove social from another user!")
        if not self.is_active:
            raise MeException("This social is not active!")
        if self.is_hidden:
            raise MeException("This social is already hidden!")
        if self.__client.switch_social_status(**{self.name: False}):
            self.is_hidden = True
            return True
        return False

    def unhide(self) -> bool:
        """
        Unhide social media account in your Me profile.

        Returns:
            ``bool``: ``True`` if successfully unhidden, ``False`` otherwise.
        """
        if not self.__my_social:
            raise MeException("You cannot remove social from another user!")
        if not self.is_active:
            raise MeException("This social is not active!")
        if not self.is_hidden:
            raise MeException("This social is already unhidden!")
        if self.__client.switch_social_status(**{self.name: True}):
            self.is_hidden = False
            return True
        return False


class Post(MeModel):
    """
    Represents Social Media post.
        - Not every social media account has posts.

    Parameters:
        author (``str`` *optional*):
            Author of post.
        owner (``str`` *optional*):
            Owner of post.
        text_first (``str`` *optional*):
            First text of post.
        text_second (``str`` *optional*):
            Second text of post.
        redirect_id (``str`` *optional*):
            Redirect ID of post.
        photo (``str`` *optional*):
            Photo of post.
    """
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
