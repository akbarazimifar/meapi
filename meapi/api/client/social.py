from re import match, sub
from typing import Union, Optional
from meapi.models.contact import Contact
from meapi.models.profile import Profile
from meapi.models.user import User
from meapi.utils.exceptions import MeException, MeApiException
from datetime import date
from meapi.utils.validations import validate_phone_number
from meapi.models import deleter, watcher, group, social, user, comment, friendship
from meapi.api.raw.social import *
from operator import attrgetter
from logging import getLogger
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me

_logger = getLogger(__name__)


class Social:
    """
    This class is not intended to create an instance's but only to be inherited by ``Me``.
    The separation is for order purposes only.
    """

    def __init__(self: 'Me'):
        raise MeException("Social class is not intended to create an instance's but only to be inherited by Me class.")

    def friendship(self: 'Me', phone_number: Union[int, str]) -> friendship.Friendship:
        """
        Get friendship information between you and another number.
        like count mutual friends, total calls duration, how do you name each other, calls count, your watches, comments, and more.

        :param phone_number: International phone number format.
        :type phone_number: ``int`` | ``str``
        :return: Friendship object.
        :rtype: :py:obj:`~meapi.models.friendship.Friendship`
        """
        return friendship.Friendship.new_from_dict(friendship_raw(self, validate_phone_number(phone_number)))

    def report_spam(self: 'Me', country_code: str, spam_name: str, phone_number: Union[str, int]) -> bool:
        """
        Report spam on another phone number.
            - You get notify when your report is approved. See :py:func:`get_notifications`.

        :param country_code: Two letters code, ``IL``, ``IT``, ``US`` etc. // `Country codes <https://countrycode.org/>`_.
        :type country_code: str
        :param spam_name: The spam name that you want to give to the spammer.
        :type spam_name: str
        :param phone_number: spammer phone number in international format.
        :type phone_number: int | str
        :return: Is report success
        :rtype: bool
        """
        return report_spam_raw(self, country_code.upper(), str(validate_phone_number(phone_number)), spam_name)['success']

    def who_deleted(self: 'Me', incognito: bool = False, sorted_by: Optional[str] = 'created_at') -> List[deleter.Deleter]:
        """
        Get list of users who deleted you from their contacts.

         The ``who_deleted_enabled`` setting must be ``True`` in your settings account in order to see who deleted you. See :py:func:`change_settings`.
         You can use ``incognito=True`` to automatically enable and disable before and after.

        :param incognito: If ``True``, this will set ``who_deleted`` to ``True``, and in the end, return it back to ``False``. *Default:* ``False``.
         (Required two more API calls to enable ``who_deleted`` and to disable it after.)
        :type incognito: bool
        :param sorted_by: Sort by ``created_at`` or ``None``. *Default:* ``created_at``.
        :type sorted_by: str
        :return: List of Deleter objects sorted by their creation time.
        :rtype: List[:py:obj:`~meapi.models.deleter.Deleter`]
        """
        if sorted_by not in ['created_at', None]:
            raise MeException("sorted_by must be 'created_at' or None.")
        if incognito:
            self.change_settings(who_deleted_enabled=True)
        res = who_deleted_raw(self)
        if incognito:
            self.change_settings(who_deleted_enabled=False)
        deleters = [deleter.Deleter.new_from_dict(dlt) for dlt in res]
        return sorted(deleters, key=attrgetter(sorted_by), reverse=True) if sorted_by else deleters

    def who_watched(self: 'Me', incognito: bool = False, sorted_by: str = 'count') -> List[watcher.Watcher]:
        """
        Get list of users who watched your profile.

         The ``who_watched_enabled`` setting must be ``True`` in your settings account in order to see who watched your profile. See :py:func:`change_settings`.
         You can use ``incognito=True`` to automatically enable and disable before and after.

        :param incognito: If ``True``, this will set ``who_watched`` to ``True``, and in the end, return it back to ``False``. *Default:* ``False``.
         (Required two more API calls to enable ``who_watched`` and to disable it after.)
        :type incognito: bool
        :param sorted_by: Sort by ``count`` or ``last_view``. *Default:* ``count``.
        :type sorted_by: str
        :return: List of Watcher objects sorted by watch count (By default) or by last view.
        :rtype: List[:py:obj:`~meapi.models.watcher.Watcher`]
        """
        if sorted_by not in ['count', 'last_view']:
            raise MeException("sorted_by must be 'count' or 'last_view'.")
        if incognito:
            self.change_settings(who_watched_enabled=True)
        res = who_watched_raw(self)
        if incognito:
            self.change_settings(who_watched_enabled=False)
        return sorted([watcher.Watcher.new_from_dict(watch) for watch in
                       res], key=attrgetter(sorted_by), reverse=True)

    def get_comments(self: 'Me', uuid: Union[str, Profile, User, Contact] = None) -> List[comment.Comment]:
        """
        Get comments in user's profile.
            - Call the method with no parameters to get comments in your profile.

        Example:
            .. code-block:: python

                # By uuid
                comments = me.get_comments('xx-yy-zz')
                # By User object
                search = me.phone_search('+1234567890')
                if getattr(search, 'user', None): # search can be None if no user found
                    comments = me.get_comments(search.user)

        :param uuid: User uuid. See :py:func:`get_uuid`.
         Or just :py:obj:`~meapi.models.user.User`/:py:obj:`~meapi.models.profile.Profile`/:py:obj:`~meapi.models.contact.Contact` objects. *Default:* Your uuid.
        :type uuid: ``str`` | :py:obj:`~meapi.models.user.User` | :py:obj:`~meapi.models.profile.Profile` | :py:obj:`~meapi.models.contact.Contact`
        :return: List of :py:obj:`~meapi.models.comment.Comment` objects sorted by their like count.
        :rtype: List[:py:obj:`~meapi.models.comment.Comment`]
        """
        if isinstance(uuid, (User, Profile)):
            uuid = uuid.uuid
        if isinstance(uuid, Contact):
            if uuid.user:
                uuid = uuid.user.uuid
            else:
                raise MeException("Contact has no user.")
        if not uuid or uuid == self.uuid:
            if self.phone_number:
                _my_comment = True
                uuid = self.uuid
            else:
                raise MeException("In the official-auth-method mode you must to provide user uuid.")
        else:
            _my_comment = False
        comments = get_comments_raw(self, str(uuid))['comments']
        return sorted([comment.Comment.new_from_dict(com, _client=self, _my_comment=_my_comment, profile_uuid=uuid)
                       for com in comments], key=lambda x: x.like_count, reverse=True)

    def get_comment(self: 'Me', comment_id: Union[int, str]) -> dict:
        """
        Get comment details, comment text, who and how many liked, create time and more.
            - This methods return :py:obj:`~meapi.models.comment.Comment` object with just ``message``, ``like_count`` and ``comment_likes`` atrrs.

        :param comment_id: Comment id from :py:func:`get_comments`.
        :type comment_id: ``int`` | ``str``
        :return: Comment object.
        :rtype: :py:obj:`~meapi.models.comment.Comment`
        """
        if isinstance(comment_id, comment.Comment):
            comment_id = comment_id.id
        return comment.Comment.new_from_dict(get_comment_raw(self, int(comment_id)), _client=self, id=int(comment_id))

    def publish_comment(self: 'Me', uuid: Union[str, Profile, User, Contact], your_comment: str, remove_credit: bool = False) -> comment.Comment:
        """
        Publish comment in user's profile.
            - You can publish comment on your own profile or on someone else's profile.
            - When you publish comment on someone else's profile, the user need to approve your comment before it will be visible.
            - You can edit your comment by simple calling :py:func:`publish_comment` again. The comment status will be changed to ``waiting`` until the user approves it.

        :param uuid: uuid of the commented user. See :py:func:`get_uuid`.
         Or just :py:obj:`~meapi.models.user.User`/:py:obj:`~meapi.models.profile.Profile`/:py:obj:`~meapi.models.contact.Contact` objects. *Default:* Your uuid.
        :type uuid: ``str`` | :py:obj:`~meapi.models.profile.Profile` | :py:obj:`~meapi.models.user.User` | :py:obj:`~meapi.models.contact.Contact`]
        :param your_comment: Your comment.
        :type your_comment: ``str``
        :param remove_credit: If ``True``, this will remove the credit from the comment. *Default:* ``False``.
        :type remove_credit: ``bool``
        :return: :py:obj:`~meapi.models.comment.Comment` object.
        :rtype: :py:obj:`~meapi.models.comment.Comment`
        """
        if isinstance(uuid, (User, Profile)):
            uuid = uuid.uuid
        if isinstance(uuid, Contact):
            if uuid.user:
                uuid = uuid.user.uuid
            else:
                raise MeException("Contact has no user.")
        if not remove_credit:
            your_comment += ' • Commented with meapi <https://github.com/david-lev/meapi>'

        return comment.Comment.new_from_dict(publish_comment_raw(self, str(uuid), str(your_comment)),
                                             _client=self, profile_uuid=uuid, _my_comment=True if self.uuid == uuid else False)

    def approve_comment(self: 'Me', comment_id: Union[str, int, comment.Comment]) -> bool:
        """
        Approve comment. (You can always delete it with :py:func:`delete_comment`.)
            - You can only approve comments in your profile!
            - If the comment already approved, you get ``True`` anyway.

        :param comment_id: Comment id from :py:func:`get_comments`. or just :py:obj:`~meapi.models.comment.Comment` object.
        :type comment_id: ``str`` | ``int`` | :py:obj:`~meapi.models.comment.Comment`
        :return: Is approve success.
        :rtype: ``bool``
        """
        if isinstance(comment_id, comment.Comment):
            if comment_id._Comment__my_comment:
                if comment_id.status == 'approved':
                    return True  # already approved
                comment_id = comment_id.id
            else:
                raise MeException("You cannot approve comment of someone else profile!")
        try:
            return bool(approve_comment_raw(self, int(comment_id))['status'] == 'approved')
        except MeApiException as err:
            if err.http_status == 400 and err.msg == 'comment_already_approved':
                return True
            else:
                raise err

    def delete_comment(self: 'Me', comment_id: Union[str, int, comment.Comment]) -> bool:
        """
        Delete (Ignore) comment. (you can always approve it with :py:func:`approve_comment`.)
            - You can only delete comments from your profile!

        :param comment_id: Comment id from :py:func:`get_comments`. or just :py:obj:`~meapi.models.comment.Comment` object.
        :type comment_id: ``int`` | ``str`` | :py:obj:`~meapi.models.comment.Comment`
        :return: Is deleting success.
        :rtype: ``bool``
        """
        if isinstance(comment_id, comment.Comment):
            if comment_id._Comment__my_comment:
                if comment_id.status == 'ignored':
                    return True  # already ignored
                comment_id = comment_id.id
            else:
                raise MeException("You cannot delete comment of someone else profile!")
        try:
            return bool(delete_comment_raw(self, int(comment_id))['status'] == 'ignored')
        except MeApiException as err:
            if err.http_status == 400 and err.msg == 'comment_already_ignored':
                return True
            else:
                raise err

    def like_comment(self: 'Me', comment_id: Union[int, str, comment.Comment]) -> bool:
        """
        Like comment.
            - If the comment is already liked, you get ``True`` anyway.
            - If the comment not approved, you get ``False``.

        :param comment_id: Comment id from :py:func:`get_comments`. or just :py:obj:`~meapi.models.comment.Comment` object.
        :type comment_id: ``int`` | ``str`` | :py:obj:`~meapi.models.comment.Comment`
        :return: Is like success.
        :rtype: ``bool``
        """
        if isinstance(comment_id, comment.Comment):
            if getattr(comment_id, 'comment_likes', None):
                if self.uuid in [usr.uuid for usr in comment_id.comment_likes]:
                    return True
            comment_id = comment_id.id
        try:
            return like_comment_raw(self, int(comment_id))['author']['uuid'] == self.uuid
        except MeApiException as err:
            if err.http_status == 404:
                return False
            raise err

    def unlike_comment(self: 'Me', comment_id: Union[int, str, comment.Comment]) -> bool:
        """
        Unlike comment.
            - If the comment is already unliked, you get ``True`` anyway.
            - If the comment not approved, you get ``False``.

        :param comment_id: Comment id from :py:func:`get_comments`. or just :py:obj:`~meapi.models.comment.Comment` object.
        :type comment_id: ``int`` | ``str`` | :py:obj:`~meapi.models.comment.Comment`
        :return: Is unlike success.
        :rtype: ``bool``
        """
        if isinstance(comment_id, comment.Comment):
            if getattr(comment_id, 'comment_likes', None):
                if self.uuid not in [usr.uuid for usr in comment_id.comment_likes]:
                    return True
            comment_id = comment_id.id
        try:
            return unlike_comment_raw(self, int(comment_id))['status'] == 'approved'
        except MeApiException as err:
            if err.http_status == 404:
                return False
            raise err

    def get_groups(self: 'Me', sorted_by: str = 'count') -> List[group.Group]:
        """
        Get groups of names and see how people named you.
            - `For more information about Group: <https://me.app/who-saved-my-number/>`_

        :param sorted_by: Sort by ``count`` or ``last_contact_at``. *Default:* ``count``.
        :type sorted_by: ``str``
        :return: List of :py:obj:`~meapi.models.group.Group` objects.
        :rtype: List[:py:obj:`~meapi.models.group.Group`]
        """
        if sorted_by not in ['count', 'last_contact_at']:
            raise MeException("sorted_by must be one of 'count' or 'last_contact_at'.")
        return sorted([group.Group.new_from_dict(grp, _client=self, is_active=True) for grp in
                       get_groups_raw(self)['groups']],
                      key=attrgetter(sorted_by), reverse=True)

    def get_deleted_groups(self: 'Me') -> List[group.Group]:
        """
        Get group names that you deleted.

        :return: List of :py:obj:`~meapi.models.group.Group` objects sorted by their count.
        :rtype: List[:py:obj:`~meapi.models.group.Group`]
        """
        groups = {}
        for name in get_deleted_groups_raw(self)['names']:  # group names together.
            if name['name'] not in groups.keys():
                groups[name['name']] = {'contacts': [{'user': name['user'], 'id': name['contact_id'],
                                                      'in_contact_list': name['in_contact_list']}], 'contact_ids': [name['contact_id']]}
            else:
                groups[name['name']]['contact_ids'].append(name['contact_id'])
                groups[name['name']]['contacts'].append({'user': name['user'], 'id': name['contact_id'],
                                                         'in_contact_list': name['in_contact_list']})
            groups[name['name']]['name'] = name['name']

        return sorted([group.Group.new_from_dict(grp, _client=self, is_active=False, count=len(grp['contact_ids']))
                       for grp in groups.values()], key=lambda x: x.count, reverse=True)

    def delete_group(self: 'Me', contacts_ids: Union[group.Group, int, str, List[Union[int, str]]]) -> bool:
        """
        Delete group name.
            - You can restore deleted group with :py:func:`restore_name`.
            - You can also ask for rename with :py:func:`ask_group_rename`.

        :param contacts_ids: :py:obj:`~meapi.models.group.Group` object, single or list of contact ids from the same group. See :py:func:`get_groups`.
        :type contacts_ids: :py:obj:`~meapi.models.group.Group` | ``int`` | ``str`` | List[``int``, ``str``]
        :return: Is delete success.
        :rtype: ``bool``
        """
        if isinstance(contacts_ids, group.Group):
            contacts_ids = contacts_ids.contact_ids
        if isinstance(contacts_ids, (int, str)):
            contacts_ids = [contacts_ids]
        return delete_group_raw(self, [int(_id) for _id in contacts_ids])['success']

    def restore_group(self: 'Me', contacts_ids: Union[int, str, List[Union[int, str]]]) -> bool:
        """
        Restore deleted group from.
            - You can get deleted groups with :py:func:`get_deleted_groups`.

        :param contacts_ids: :py:obj:`~meapi.models.group.Group` object, single or list of contact ids from the same group. See :py:func:`get_groups`.
        :type contacts_ids: :py:obj:`~meapi.models.group.Group` | ``int`` | ``str`` | List[``int``, ``str``]
        :return: Is delete success.
        :rtype: ``bool``
        """
        if isinstance(contacts_ids, group.Group):
            contacts_ids = contacts_ids.contact_ids
        if isinstance(contacts_ids, (int, str)):
            contacts_ids = [contacts_ids]
        return restore_group_raw(self, [int(_id) for _id in contacts_ids])['success']

    def ask_group_rename(self: 'Me', contacts_ids: Union[group.Group, int, str, List[Union[int, str]]], new_name: Optional[str] = None) -> bool:
        """
        Suggest new name to group of people and ask them to rename you in their contacts book.

        :param contacts_ids: :py:obj:`~meapi.models.group.Group` object, single or list of contact ids from the same group. See :py:func:`get_groups`.
        :type contacts_ids: :py:obj:`~meapi.models.group.Group` | ``int`` | ``str`` | List[``int``, ``str``]
        :param new_name: Suggested name, Default: Your profile name from :py:func:`get_profile`.
        :type new_name: ``str`` | ``None``
        :return: Is asking success.
        :rtype: ``bool``
        """
        if not new_name:  # suggest your name in your profile
            new_name = self.get_my_profile().name
        if isinstance(contacts_ids, (int, str)):
            contacts_ids = [contacts_ids]
        if isinstance(contacts_ids, group.Group):
            if contacts_ids.name == new_name:
                raise MeException("The name of the group is already the same as the suggested name.")
            contacts_ids = contacts_ids.contact_ids
        return ask_group_rename_raw(self, [int(_id) for _id in contacts_ids], new_name)['success']

    def get_socials(self: 'Me', uuid: Union[str, Profile, User, Contact] = None) -> social.Social:
        """
        Get connected social networks to ``Me`` account.

        :param uuid: uuid of the commented user. See :py:func:`get_uuid`.
         Or just :py:obj:`~meapi.models.user.User`/:py:obj:`~meapi.models.profile.Profile`/:py:obj:`~meapi.models.contact.Contact` objects. *Default:* Your uuid.
        :type uuid: ``str`` | :py:obj:`~meapi.models.profile.Profile` | :py:obj:`~meapi.models.user.User` | :py:obj:`~meapi.models.contact.Contact`]
        :return: :py:obj:`~meapi.models.social.Social` object with social media accounts.
        :rtype: :py:obj:`~meapi.models.social.Social`
        """
        if isinstance(uuid, (User, Profile)):
            uuid = uuid.uuid
        if isinstance(uuid, Contact):
            if uuid.user:
                uuid = uuid.user.uuid
            else:
                raise MeException("Contact has no user.")
        if not uuid:
            return social.Social.new_from_dict(get_my_social_raw(self), _client=self, _my_social=True)
        return self.get_profile(uuid).social

    def add_social(self: 'Me',
                   twitter_token: str = None,
                   spotify_token: str = None,
                   instagram_token: str = None,
                   facebook_token: str = None,
                   tiktok_token: str = None,
                   pinterest_url: str = None,
                   linkedin_url: str = None, ) -> bool:
        """
        Connect social network to your me account.
            - If you have at least ``2`` socials, you get ``is_verified=True`` in your profile (Blue check).

        :param twitter_token: `Twitter Token. Default = ``None``.
        :type twitter_token: str
        :param spotify_token: Log in to `Spotify <https://accounts.spotify.com/authorize?client_id=0b1ea72f7dce420583038b49fd04be50&response_type=code&redirect_uri=https://app.mobile.me.app/&scope=user-read-email%20playlist-read-private>`_ and copy the token after the ``https://app.mobile.me.app/?code=``. Default = ``None``.
        :type spotify_token: str
        :param instagram_token: Log in to `Instagram <https://api.instagram.com/oauth/authorize/?app_id=195953705182737&redirect_uri=https://app.mobile.me.app/&response_type=code&scope=user_profile,user_media>`_ and copy the token after the ``https://app.mobile.me.app/?code=``. Default = ``None``.
        :type instagram_token: str
        :param facebook_token: `Facebook token <https://m.facebook.com/v12.0/dialog/oauth?cct_prefetching=0&client_id=799397013456724&cbt=1658355617803&e2e=%7B%22init%22%3A1658355617803%7D&ies=1&sdk=android-12.3.0&sso=chrome_custom_tab&nonce=19c3a497-9a95-4414-838e-34a789163b1d&scope=openid%2Cemail%2C%20user_birthday%2C%20user_gender%2C%20user_link&state=%7B%220_auth_logger_id%22%3A%22a173f481-ccb8-4738-850b-2fcd6a07ae88%22%2C%223_method%22%3A%22custom_tab%22%2C%227_challenge%22%3A%221vcvqpm5ftpf9qvcb3ao%22%7D&default_audience=friends&login_behavior=NATIVE_WITH_FALLBACK&redirect_uri=fbconnect%3A%2F%2Fcct.com.nfo.me.android&auth_type=rerequest&response_type=id_token%2Ctoken%2Csigned_request%2Cgraph_domain&return_scopes=true>`_. Default = ``None``.
        :type facebook_token: str
        :param tiktok_token: Log in to `TikTok <https://www.tiktok.com/auth/authorize?response_type=code&redirect_uri=https%3A%2F%2Fopen-api.tiktok.com%2Foauth%2Fauthorize%2Fcallback%2F&client_key=awwprdkduitl3ym8&state=xxx&from=opensdk&scope=user.info.basic%2Cvideo.list&optionalScope=&signature=f906b98d2febaad72580c16652d737ef&app_identity=02fc9e030144d785e61407f04a0ff171&device_platform=android>`_ and copy the token from ``data`` > ``code``. Default = ``None``.
        :type tiktok_token: str
        :param pinterest_url: Profile url - ``https://www.pinterest.com/username/``. Default = ``None``.
        :type pinterest_url: str
        :param linkedin_url: Profile url - ``https://www.linkedin.com/in/username``. Default = ``None``.
        :type linkedin_url: str
        :return: Tuple of: is_success, list of failed.
        :rtype: bool
        """
        args = locals()
        del args['self']
        not_null_values = sum(bool(i) for i in args.values())
        if not_null_values < 1:
            raise MeException("You need to provide at least one social!")
        successes = 0
        for soc, token_or_url in args.items():
            if token_or_url is not None:
                if soc.endswith('url'):
                    if match(r"^https?:\/\/.*{domain}.*$".format(domain=soc.replace('_url', '')), token_or_url):
                        is_token = False
                    else:
                        raise MeException(f"You must provide a valid link to the {soc.replace('_url', '').capitalize()} profile!")
                else:
                    is_token = True
                social_name = sub(r'_(token|url)$', '', soc)
                results = add_social_token_raw(self, social_name, token_or_url) if is_token else add_social_url_raw(self, social_name, token_or_url)
                if results['success'] if is_token else bool(results[social_name]['profile_id'] == token_or_url):
                    successes += 1
        return bool(successes == not_null_values)

    def remove_social(self: 'Me',
                      twitter: bool = False,
                      spotify: bool = False,
                      instagram: bool = False,
                      facebook: bool = False,
                      pinterest: bool = False,
                      linkedin: bool = False,
                      tiktok: bool = False,
                      ) -> bool:
        """
        Remove social networks from your profile.
            - You can also hide social instead of deleting it: :py:func:`switch_social_status`.

        :param twitter: To remove Twitter. Default: ``False``.
        :type twitter: bool
        :param spotify: To remove Spotify. Default: ``False``.
        :type spotify: bool
        :param instagram: To remove Instagram. Default: ``False``.
        :type instagram: bool
        :param facebook: To remove Facebook. Default: ``False``.
        :type facebook: bool
        :param pinterest: To remove Pinterest. Default: ``False``.
        :type pinterest: bool
        :param linkedin: To remove Linkedin. Default: ``False``.
        :type linkedin: bool
        :param tiktok: To remove Tiktok. Default: ``False``.
        :type tiktok: bool
        :return: Is removal success.
        :rtype: bool
        """
        args = locals()
        del args['self']
        true_values = sum(args.values())
        if true_values < 1:
            raise MeException("You need to remove at least one social!")
        successes = 0
        for soc, value in args.items():
            if value is True:
                if remove_social_raw(self, str(soc))['success']:
                    successes += 1
        return bool(true_values == successes)

    def switch_social_status(self: 'Me',
                             twitter: bool = None,
                             spotify: bool = None,
                             instagram: bool = None,
                             facebook: bool = None,
                             tiktok: bool = None,
                             pinterest: bool = None,
                             linkedin: bool = None,
                             ) -> bool:
        """
        Switch social network status: Show (``True``) or Hide (``False``).

        :param twitter: Switch Twitter status. Default: ``None``.
        :type twitter: bool
        :param spotify: Switch Spotify status Default: ``None``.
        :type spotify: bool
        :param instagram: Switch Instagram status Default: ``None``.
        :type instagram: bool
        :param facebook: Switch Facebook status Default: ``None``.
        :type facebook: bool
        :param tiktok: Switch TikTok status Default: ``None``.
        :type tiktok: bool
        :param pinterest: Switch Pinterest status Default: ``None``.
        :type pinterest: bool
        :param linkedin: Switch Linkedin status Default: ``None``.
        :type linkedin: bool
        :return: is switch success (you get ``True`` even if social active or was un/hidden before).
        :rtype: bool
        """
        args = locals()
        del args['self']
        not_null_values = sum(True for i in args.values() if i is not None)
        if not_null_values < 1:
            raise MeException("You need to switch status to at least one social!")
        successes = 0
        my_socials = self.get_socials()
        for soc, status in args.items():
            if status is not None and isinstance(status, bool):
                is_active, is_hidden = attrgetter(f'{soc}.is_active', f'{soc}.is_hidden')(my_socials)
                if not is_active or (not is_hidden and status) or (is_hidden and not status):
                    successes += 1
                    continue
                else:
                    if status != switch_social_status_raw(self, str(soc))['is_hidden']:
                        successes += 1
        return bool(not_null_values == successes)

    def numbers_count(self: 'Me') -> int:
        """
        Get total count of numbers on Me.

        :return: total count.
        :rtype: int
        """
        return numbers_count_raw(self)['count']

    def suggest_turn_on_comments(self: 'Me', uuid: Union[str, Profile, User, Contact]) -> bool:
        """
        Ask another user to turn on comments in his profile.

        :param uuid: uuid of the user. See :py:func:`get_uuid`.
         Or just :py:obj:`~meapi.models.user.User`/:py:obj:`~meapi.models.profile.Profile`/:py:obj:`~meapi.models.contact.Contact` objects. *Default:* Your uuid.
        :type uuid: ``str`` | :py:obj:`~meapi.models.profile.Profile` | :py:obj:`~meapi.models.user.User` | :py:obj:`~meapi.models.contact.Contact`]
        :return: Is request success.
        :rtype: ``bool``
        """
        if isinstance(uuid, Profile):
            if uuid.comments_enabled:
                return True
            uuid = uuid.uuid
        if isinstance(uuid, User):
            uuid = uuid.uuid
        if isinstance(uuid, Contact):
            if uuid.user:
                uuid = uuid.user.uuid
            else:
                raise MeException("Contact has no user.")
        if uuid == self.uuid:
            raise MeException("You can't suggest to yourself!")

        return suggest_turn_on_comments_raw(self, str(uuid))['requested']

    def suggest_turn_on_mutual(self: 'Me', uuid: Union[str, Profile, User, Contact]) -> bool:
        """
        Ask another user to turn on mutual contacts on his profile.

        :param uuid: uuid of the user. See :py:func:`get_uuid`.
         Or just :py:obj:`~meapi.models.user.User`/:py:obj:`~meapi.models.profile.Profile`/:py:obj:`~meapi.models.contact.Contact` objects. *Default:* Your uuid.
        :type uuid: ``str`` | :py:obj:`~meapi.models.profile.Profile` | :py:obj:`~meapi.models.user.User` | :py:obj:`~meapi.models.contact.Contact`]
        :return: Is request success.
        :rtype: ``bool``
        """
        if isinstance(uuid, Profile):
            if uuid.mutual_contacts_available:
                return True
            uuid = uuid.uuid
        if isinstance(uuid, User):
            uuid = uuid.uuid
        if isinstance(uuid, Contact):
            if uuid.user:
                uuid = uuid.user.uuid
            else:
                raise MeException("Contact has no user.")
        if uuid == self.uuid:
            raise MeException("You can't suggest to yourself!")

        return suggest_turn_on_mutual_raw(self, str(uuid))['requested']

    def suggest_turn_on_location(self: 'Me', uuid: Union[str, Profile, User, Contact]) -> bool:
        """
        Ask another user to share his location with you.

        :param uuid: uuid of the user. See :py:func:`get_uuid`.
         Or just :py:obj:`~meapi.models.user.User`/:py:obj:`~meapi.models.profile.Profile`/:py:obj:`~meapi.models.contact.Contact` objects. *Default:* Your uuid.
        :type uuid: ``str`` | :py:obj:`~meapi.models.profile.Profile` | :py:obj:`~meapi.models.user.User` | :py:obj:`~meapi.models.contact.Contact`]
        :return: Is request success.
        :rtype: ``bool``
        """
        if isinstance(uuid, (Profile, User)):
            uuid = uuid.uuid
        if isinstance(uuid, Contact):
            if uuid.user:
                uuid = uuid.user.uuid
            else:
                raise MeException("Contact has no user.")
        if uuid == self.uuid:
            raise MeException("You can't suggest to yourself!")

        return suggest_turn_on_location_raw(self, str(uuid))['requested']

    def get_age(self: 'Me', uuid: Union[str, Profile, User, Contact] = None) -> int:
        """
        Get user age. calculate from ``date_of_birth``, provided by :py:func:`get_profile`.

        :param uuid: uuid of the user. See :py:func:`get_uuid`.
         Or just :py:obj:`~meapi.models.user.User`/:py:obj:`~meapi.models.profile.Profile`/:py:obj:`~meapi.models.contact.Contact` objects. *Default:* Your uuid.
        :type uuid: ``str`` | :py:obj:`~meapi.models.profile.Profile` | :py:obj:`~meapi.models.user.User` | :py:obj:`~meapi.models.contact.Contact`]
        :return: User age if date of birth exists. else - ``0``.
        :rtype: ``int``
        """
        if isinstance(uuid, Profile):
            return uuid.age
        if isinstance(uuid, User):
            uuid = uuid.uuid
        if isinstance(uuid, Contact):
            if uuid.user:
                uuid = uuid.user.uuid
            else:
                raise MeException("Contact has no user.")
        if uuid is None:
            uuid = self.uuid
        profile = self.get_profile(uuid)
        if profile.date_of_birth:
            today = date.today()
            if profile.date_of_birth > today:
                return 0
            return int((today - profile.date_of_birth).days / 365)
        return 0

    def is_spammer(self: 'Me', phone_number: Union[int, str]) -> int:
        """
        Check on phone number if reported as spam.

        :param phone_number: International phone number format.
        :type phone_number: ``int`` | ``str``
        :return: count of spam reports. ``0`` if None.
        :rtype: ``int``
        """
        results = self.phone_search(phone_number)
        if results:
            return results.suggested_as_spam
        return 0

    def update_location(self: 'Me', latitude: float, longitude: float) -> bool:
        """
        Update your location. See :py:func:`upload_random_data`.

        :param latitude: location latitude coordinates.
        :type latitude: float
        :param longitude: location longitude coordinates.
        :type longitude: float
        :return: Is location update success.
        :rtype: bool
        """
        if not isinstance(latitude, float) or not isinstance(longitude, float):
            raise MeException("Not a valid coordination!")
        return update_location_raw(self, latitude, longitude)['success']

    def share_location(self: 'Me', uuid: Union[str, Profile, User, Contact]) -> bool:
        """
        Share your location with another user.

        :param uuid: uuid of the user. See :py:func:`get_uuid`.
         Or just :py:obj:`~meapi.models.user.User`/:py:obj:`~meapi.models.profile.Profile`/:py:obj:`~meapi.models.contact.Contact` objects. *Default:* Your uuid.
        :type uuid: ``str`` | :py:obj:`~meapi.models.profile.Profile` | :py:obj:`~meapi.models.user.User` | :py:obj:`~meapi.models.contact.Contact`]
        :return: Is sharing success.
        :rtype: ``bool``
        """
        if isinstance(uuid, (Profile, User)):
            uuid = uuid.uuid
        if isinstance(uuid, Contact):
            if uuid.user:
                uuid = uuid.user.uuid
            else:
                raise MeException("Contact has no user.")
        if uuid == self.uuid:
            raise MeException("You can't share location with yourself!")
        return share_location_raw(self, uuid)['success']

    def stop_sharing_location(self: 'Me', uuids: Union[str, Profile, User, Contact, List[Union[str, Profile, User, Contact]]]) -> bool:
        """
        Stop sharing your :py:func:`update_location` with users.

        :param uuids: uuid/s of the user/s that you want to stop sharing your location with.
        :type uuids: ``str`` | :py:obj:`~meapi.models.profile.Profile` | :py:obj:`~meapi.models.user.User` | :py:obj:`~meapi.models.contact.Contact` | List[``str`` | :py:obj:`~meapi.models.profile.Profile` | :py:obj:`~meapi.models.user.User` | :py:obj:`~meapi.models.contact.Contact`]
        :return: is stopping success.
        :rtype: ``bool``
        """
        if not isinstance(uuids, list):
            uuids = [uuids]
        if isinstance(uuids, list):
            for uuid, index in enumerate(uuids):
                if isinstance(uuid, (Profile, User)):
                    uuids[index] = uuid.uuid
                if isinstance(uuid, Contact):
                    if uuid.user:
                        uuids[index] = uuid.user.uuid
                    else:
                        _logger.warning(f"Skip contact {uuid.name} with no user.")

        return stop_sharing_location_raw(self, uuids)['success']

    def stop_shared_location(self: 'Me', uuids: Union[str, Profile, User, Contact, List[Union[str, Profile, User, Contact]]]) -> bool:
        """
        Stop locations that shared with you.

        :param uuids: uuid/s of the user/s that you want to stop sharing your location with.
        :type uuids: ``str`` | :py:obj:`~meapi.models.profile.Profile` | :py:obj:`~meapi.models.user.User` | :py:obj:`~meapi.models.contact.Contact` | List[``str`` | :py:obj:`~meapi.models.profile.Profile` | :py:obj:`~meapi.models.user.User` | :py:obj:`~meapi.models.contact.Contact`]
        :return: is stopping success.
        :rtype: ``bool``
        """
        if not isinstance(uuids, list):
            uuids = [uuids]
        if isinstance(uuids, list):
            for uuid, index in enumerate(uuids):
                if isinstance(uuid, (Profile, User)):
                    uuids[index] = uuid.uuid
                if isinstance(uuid, Contact):
                    if uuid.user:
                        uuids[index] = uuid.user.uuid
                    else:
                        _logger.warning(f"Skip contact {uuid.name} with no user.")

        return stop_shared_locations_raw(self, uuids)['success']

    def locations_shared_by_me(self: 'Me') -> List[user.User]:
        """
        Get list of users that you shared your location with them.

        :return: List of :py:obj:`~meapi.models.user.User` objects.
        :rtype: List[:py:obj:`~meapi.models.user.User`]
        """
        return [user.User.new_from_dict(usr, _client=self) for usr in locations_shared_by_me_raw(self)]

    def locations_shared_with_me(self: 'Me') -> List[user.User]:
        """
        Get users who have shared their location with you.

        :return: List of :py:obj:`~meapi.models.user.User` objects (with ``distance`` attribute).
        :rtype: List[:py:obj:`~meapi.models.user.User`]
        """
        users = locations_shared_with_me_raw(self)['shared_location_users']
        return [user.User.new_from_dict(usr['author'], _client=self, distance=usr['distance']) for usr in users]
