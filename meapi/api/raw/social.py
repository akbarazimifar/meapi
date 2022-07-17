from typing import List, TYPE_CHECKING
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me


def friendship_raw(client: 'Me', phone_number: int) -> dict:
    """
    Get friendship information between you and another number.
    like count mutual friends, total calls duration, how do you name each other, calls count, your watches, comments, and more.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param phone_number: International phone number format.
    :type phone_number: ``int``
    :return: Dict with friendship data.
    :rtype: ``dict``

    Example of friendship::

        {
            "calls_duration": None,
            "he_called": 0,
            "he_named": "He named",
            "he_watched": 3,
            "his_comment": None,
            "i_called": 0,
            "i_named": "You named",
            "i_watched": 2,
            "is_premium": False,
            "mutual_friends_count": 6,
            "my_comment": None,
        }
    """
    return client._make_request('get', f'/main/contacts/friendship/?phone_number={phone_number}')


def report_spam_raw(client: 'Me', country_code: str, phone_number: str, spam_name: str) -> dict:
    """
    Report a number as spam.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param country_code: Country code.
    :type country_code: ``str``
    :param phone_number: International phone number format.
    :type phone_number: ``str``
    :param spam_name: Name of the spammer.
    :type spam_name: ``str``
    :return: Dict with spam report success.
    :rtype: dict

    Example of results::
        {'success': True}
    """
    body = {"country_code": country_code, "is_spam": True, "is_from_v": False,
     "name": spam_name, "phone_number": phone_number}
    return client._make_request('post', f'/main/names/suggestion/report/', body=body)


def who_deleted_raw(client: 'Me') -> List[dict]:
    """
    Get a list of users that deleted you from their contacts.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :return: List of dicts with users.
    :rtype: List[``dict``]

    Example of results::

        [
            {
                "created_at": "2021-09-12T15:42:57Z",
                "user": {
                    "email": "",
                    "profile_picture": None,
                    "first_name": "Test",
                    "last_name": "Test",
                    "gender": None,
                    "uuid": "aa221ae8-XXX-4679-XXX-91307XXX5a9a2",
                    "is_verified": False,
                    "phone_number": 123456789012,
                    "slogan": None,
                    "is_premium": False,
                    "verify_subscription": True,
                },
            }
        ]
    """
    return client._make_request('get', '/main/users/profile/who-deleted/')


def who_watched_raw(client: 'Me') -> List[dict]:
    """
    Get a list of users that watched you.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :return: List of dicts with users.
    :rtype: List[``dict``]

    Example of results::

        [
            {
                "last_view": "2022-04-16T17:13:24Z",
                "user": {
                    "email": "eliezXXXXXXXXX94@gmail.com",
                    "profile_picture": "https://d18zXXXXXXXXXXXXXcb14529ccc7db.jpg",
                    "first_name": "Test",
                    "last_name": None,
                    "gender": None,
                    "uuid": "f8d03XXX97b-ae86-35XXXX9c6e5",
                    "is_verified": False,
                    "phone_number": 97876453245,
                    "slogan": None,
                    "is_premium": True,
                    "verify_subscription": True,
                },
                "count": 14,
                "is_search": None,
            }
        ]
    """
    return client._make_request('get', '/main/users/profile/who-watched/')


def get_comments_raw(client: 'Me', uuid: str) -> dict:
    """
    Get user comments.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param uuid: User uuid.
    :type uuid: ``str``
    :return: Dict with list of comments.
    :rtype: ``dict``

    Example::

        {
            "comments": [
                {
                    "like_count": 2,
                    "status": "approved",
                    "message": "Test comment",
                    "author": {
                        "email": "user@domain.com",
                        "profile_picture": "https://d18zaexen4dp1s.cloudfront.net/593a9XXXXXXd7437XXXX7.jpg",
                        "first_name": "Name test",
                        "last_name": "",
                        "gender": None,
                        "uuid": "8a0XXXXXXXXXXX0a-83XXXXXXb597",
                        "is_verified": True,
                        "phone_number": 123456789098,
                        "slogan": "https://example.com",
                        "is_premium": False,
                        "verify_subscription": True,
                    },
                    "is_liked": False,
                    "id": 662,
                    "comments_blocked": False,
                },
                {
                    "like_count": 2,
                    "status": "approved",
                    "message": "hhaha",
                    "author": {
                        "email": "haXXXXiel@gmail.com",
                        "profile_picture": None,
                        "first_name": "Test",
                        "last_name": "Test",
                        "gender": None,
                        "uuid": "59XXXXXXXXXXXX-b6c7-f2XXXXXXXXXX26d267",
                        "is_verified": False,
                        "phone_number": 914354653176,
                        "slogan": None,
                        "is_premium": False,
                        "verify_subscription": True,
                    },
                    "is_liked": True,
                    "id": 661,
                    "comments_blocked": False,
                },
            ],
            "count": 2,
            "user_comment": None,
        }
    """
    return client._make_request('get', f'/main/comments/list/{uuid}')


def get_comment_raw(client: 'Me', comment_id: int) -> dict:
    """
    Get comment details, comment text, who and how many liked, create time and more.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param comment_id: Comment id.
    :type comment_id: ``int``
    :return: Dict with comment details.
    :rtype: ``dict``

    Example::

        {
            "comment_likes": [
                {
                    "author": {
                        "email": "yonXXXXXX@gmail.com",
                        "first_name": "Jonatan",
                        "gender": "M",
                        "is_premium": False,
                        "is_verified": True,
                        "last_name": "Fa",
                        "phone_number": 97655764547,
                        "profile_picture": "https://d18zaexXXXp1s.cloudfront.net/2eXXefea6dXXXXXXe3.jpg",
                        "slogan": None,
                        "uuid": "807XXXXX2-414a-b7XXXXX92cd679",
                        "verify_subscription": True,
                    },
                    "created_at": "2022-04-17T16:53:49Z",
                    "id": 194404,
                }
            ],
            "like_count": 1,
            "message": "Test comment",
        }
    """
    return client._make_request('get', f'/main/comments/retrieve/{comment_id}')


def publish_comment_raw(client: 'Me', uuid: str, your_comment: str) -> dict:
    """
    Publish comment.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param uuid: User uuid.
    :type uuid: ``str``
    :param your_comment: Comment text.
    :type your_comment: ``str``
    :return: Dict with comment details.
    :rtype: ``dict``

    Example::

        {
            'like_count': 0,
            'status': 'waiting',
            'message': 'your comment',
            'author': {
                'email': 'exmaple@gmail.com',
                'profile_picture': 'https://d18zp1s.cloudfront.net/b.jpg',
                'first_name': 'Ross',
                'last_name': '',
                'gender': None,
                'uuid': 'ds-dfdf-dcd-af6a-sdffdfdf',
                'is_verified': True,
                'phone_number': 9125342435483,
                'slogan': 'bla bla',
                'is_premium': False,
                'verify_subscription': True
            },
            'is_liked': False,
            'id': 123565,
            'comments_blocked': False
        }
    """
    body = {"message": your_comment}
    return client._make_request('post', f'/main/comments/add/{uuid}/', body)


def approve_comment_raw(client: 'Me', comment_id: int) -> dict:
    """
    Approve comment.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param comment_id: Comment id.
    :type comment_id: ``int``
    :return: Dict with comment details.
    :rtype: ``dict``

    Example::

        {
            'like_count': 0,
            'status': 'approved',
            'message': 'your comment',
            'author': {
                'email': 'exmaple@gmail.com',
                'profile_picture': 'https://d18zp1s.cloudfront.net/b.jpg',
                'first_name': 'Ross',
                'last_name': '',
                'gender': None,
                'uuid': 'ds-dfdf-dcd-af6a-sdffdfdf',
                'is_verified': True,
                'phone_number': 9125342435483,
                'slogan': 'bla bla',
                'is_premium': False,
                'verify_subscription': True
            },
            'is_liked': False,
            'id': 123565,
            'comments_blocked': False
        }
    """
    return client._make_request('post', f'/main/comments/approve/{comment_id}/')


def delete_comment_raw(client: 'Me', comment_id: int) -> dict:
    """
    Delete comment.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param comment_id: Comment id.
    :type comment_id: ``int``
    :return: Dict with comment details.
    :rtype: ``dict``

    Example::

        {
            'like_count': 0,
            'status': 'ignored',
            'message': 'your comment',
            'author': {
                'email': 'exmaple@gmail.com',
                'profile_picture': 'https://d18zp1s.cloudfront.net/b.jpg',
                'first_name': 'Ross',
                'last_name': '',
                'gender': None,
                'uuid': 'ds-dfdf-dcd-af6a-sdffdfdf',
                'is_verified': True,
                'phone_number': 9125342435483,
                'slogan': 'bla bla',
                'is_premium': False,
                'verify_subscription': True
            },
            'is_liked': False,
            'id': 123565,
            'comments_blocked': False
        }
    """
    return client._make_request('delete', f'/main/comments/approve/{comment_id}/')


def like_comment_raw(client: 'Me', comment_id: int) -> dict:
    """
    Like comment.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param comment_id: Comment id.
    :type comment_id: ``int``
    :return: Dict with comment details.
    :rtype: ``dict``

    Example::

        {
            'id': 12345,
            'created_at': '2022-07-04T21:58:23Z',
            'author': {
                'email': 'user@domain.com',
                'profile_picture': 'https://ehdiued.cloudfront.net/hfidsfds.jpg',
                'first_name': 'Ross',
                'last_name': 'Geller',
                'gender': None,
                'uuid': 'dhius-fdsfs3f7e-fefs-dihoids-odhfods',
                'is_verified': True,
                'phone_number': 9723743824244,
                'slogan': 'Pivot.',
                'is_premium': False,
                'verify_subscription': True
            }
        }
    """
    return client._make_request('post', f'/main/comments/like/{comment_id}/')


def unlike_comment_raw(client: 'Me', comment_id: int) -> dict:
    """
    Unlike comment.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param comment_id: Comment id.
    :type comment_id: ``int``
    :return: Dict with comment details.
    :rtype: ``dict``

    Example::

        {
            'like_count': 0,
            'status': 'approved',
            'message': 'Test',
            'author': {
                'email': 'user@domain.com',
                'profile_picture': 'https://hiiu.cloudfront.net/hdiufds.jpg',
                'first_name': 'Monica',
                'last_name': '',
                'gender': None,
                'uuid': 'djhids-oiehda-huds-dhcuds-dhfidsdsf',
                'is_verified': True,
                'phone_number': 973437824255,
                'slogan': 'I know!',
                'is_premium': False,
                'verify_subscription': True
            },
            'is_liked': False,
            'id': 123456,
            'comments_blocked': False
        }
    """
    return client._make_request('delete', f'/main/comments/like/{comment_id}/')


def get_groups_raw(client: 'Me') -> dict:
    """
    Get groups of names and see how people named you.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :return: Dict with groups.
    :rtype: ``dict``

    Example::

        {
            "cached": False,
            "groups": [
                {
                    "name": "This is how they name you",
                    "count": 1,
                    "last_contact_at": "2020-06-09T12:24:51Z",
                    "contacts": [
                        {
                            "id": 2218840161,
                            "created_at": "2020-06-09T12:24:51Z",
                            "modified_at": "2020-06-09T12:24:51Z",
                            "user": {
                                "profile_picture": "https://XXXXp1s.cloudfront.net/28d5XXX96953feX6.jpg",
                                "first_name": "joz",
                                "last_name": "me",
                                "uuid": "0577XXX-1XXXe-d338XXX74483",
                                "is_verified": False,
                                "phone_number": 954353655531,
                            },
                            "in_contact_list": True,
                        }
                    ],
                    "contact_ids": [2213546561],
                }
            ],
        }
    """
    return client._make_request('get', '/main/names/groups/')


def get_deleted_groups_raw(client: 'Me') -> dict:
    """
    Get group names that you deleted.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :return: dict with names and contact ids.
    :rtype: ``dict``

    Example::

        {
            "names": [
                {
                    "contact_id": 40108734246,
                    "created_at": "2022-04-18T06:08:33Z",
                    "hidden_at": "2022-04-23T20:45:19Z",
                    "name": "My delivery guy",
                    "user": {
                        "email": "pnhfdishfois@gmail.com",
                        "profile_picture": None,
                        "first_name": "Joe",
                        "last_name": "",
                        "gender": None,
                        "uuid": "52XXXXX-b952-XXXX-853e-XXXXXX",
                        "is_verified": False,
                        "phone_number": 9890987986,
                        "slogan": None,
                        "is_premium": False,
                        "verify_subscription": True,
                    },
                    "in_contact_list": True,
                }
            ],
            "count": 1,
            "contact_ids": [409879786],
        }
    """
    return client._make_request('get', '/main/settings/hidden-names/')


def delete_group_raw(client: 'Me', contact_ids: List[int]) -> dict:
    """
    Delete group.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param contact_ids: list with contacts ids in the same group.
    :type contact_ids: List[``int``]
    :return: dict with delete success.
    :rtype: ``dict``

    Example::

        {
            'success': True
        }
    """
    return client._make_request('post', '/main/contacts/hide/', {'contact_ids': contact_ids})


def restore_group_raw(client: 'Me', contact_ids: List[int]) -> dict:
    """
    Restore group.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param contact_ids: list with contacts ids in the same group.
    :type contact_ids: List[``int``]
    :return: dict with restore success.
    :rtype: ``dict``

    Example::

        {
            'success': True
        }
    """
    return client._make_request('post', '/main/settings/hidden-names/', {'contact_ids': contact_ids})


def ask_group_rename_raw(client: 'Me', contact_ids: List[int], new_name: str) -> dict:
    """
    Ask contacts in a group to rename you in their contact book.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param contact_ids: list with contacts ids in the same group.
    :type contact_ids: List[``int``]
    :param new_name: New name.
    :type new_name: ``str``
    :return: dict with rename success.
    :rtype: ``dict``

    Example::

        {
            'success': True
        }
    """
    return client._make_request('post', '/main/names/suggestion/', {'contact_ids': contact_ids, 'name': new_name})


def get_my_social_raw(client: 'Me') -> dict:
    """
    Get connected social networks to your Me account.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param uuid: UUID of the user.
    :type uuid: ``str``
    :return: Dict with social networks and posts.
    :rtype: ``dict``

    Example::

        {
            "social": {
                "facebook": {
                    "posts": [],
                    "profile_id": "https://www.facebook.com/app_scoped_user_id/XXXXXXXXXXX/",
                    "is_active": True,
                    "is_hidden": True,
                },
                "fakebook": {
                    "is_active": False,
                    "is_hidden": True,
                    "posts": [],
                    "profile_id": None,
                },
                "instagram": {
                    "posts": [
                        {
                            "posted_at": "2021-12-23T22:21:06Z",
                            "photo": "https://d18zaexen4dp1s.cloudfront.net/XXXXXXXXXXXXXX.jpg",
                            "text_first": None,
                            "text_second": "IMAGE",
                            "author": "username",
                            "redirect_id": "CXXXXIz-0",
                            "owner": "username",
                        }
                    ],
                    "profile_id": "username",
                    "is_active": True,
                    "is_hidden": False,
                },
                "linkedin": {
                    "is_active": True,
                    "is_hidden": False,
                    "posts": [],
                    "profile_id": "https://www.linkedin.com/in/username",
                },
                "pinterest": {
                    "posts": [],
                    "profile_id": "https://pin.it/XXXXXXXX",
                    "is_active": True,
                    "is_hidden": False,
                },
                "spotify": {
                    "is_active": True,
                    "is_hidden": False,
                    "posts": [
                        {
                            "author": "Chandler bing",
                            "owner": "4xgXXXXXXXt0pv",
                            "photo": "https://d18zaexen4dp1s.cloudfront.net/9bcXXXfa7dXXXXXXXac.jpg",
                            "posted_at": None,
                            "redirect_id": "4KgES5cs3SnMhuAXuBREW2",
                            "text_first": "My friends playlist songs",
                            "text_second": "157",
                        },
                        {
                            "author": "Chandler Bing",
                            "owner": "4xgoXcoriuXXXXpt0pv",
                            "photo": "https://d18zaexen4dp1s.cloudfront.net/55d3XXXXXXXXXXXXXXXXXX4.jpg",
                            "posted_at": None,
                            "redirect_id": "3FjSXXXCQPB14Xt",
                            "text_first": "My favorite songs!",
                            "text_second": "272",
                        },
                    ],
                    "profile_id": "4xgot8coriuXXXXXpt0pv",
                },
                "tiktok": {
                    "is_active": False,
                    "is_hidden": True,
                    "posts": [],
                    "profile_id": None,
                },
                "twitter": {
                    "is_active": True,
                    "is_hidden": False,
                    "posts": [
                        {
                            "author": "username",
                            "owner": "username",
                            "photo": "https://pbs.twimg.com/profile_images/13XXXXX76/AvBXXXX_normal.jpg",
                            "posted_at": "2021-08-24T10:02:45Z",
                            "redirect_id": "https://twitter.com/username/status/1XXXXXX423",
                            "text_first": "My tweet #1 https://t.co/PLXXXX2Tw https://t.co/zXXXXkk",
                            "text_second": None,
                        },
                        {
                            "author": "username",
                            "owner": "username",
                            "photo": "https://pbs.twimg.com/profile_images/1318XXXX0976/AvBXXXUk_normal.jpg",
                            "posted_at": "2021-08-12T10:09:23Z",
                            "redirect_id": "https://twitter.com/username/status/142XXXXX86624",
                            "text_first": "My second tweet https://t.co/xtqXXXtAC",
                            "text_second": None,
                        },
                    ],
                    "profile_id": "username",
                },
            },
        }
    """
    return client._make_request('post', '/main/social/update/')


def add_social_token_raw(client: 'Me', social_name: str, token: str) -> dict:
    """
    Connect social network (that required token) to your Me account.
        - Available social networks: ``facebook``, ``instagram``, ``spotify``, ``twitter``, ``tiktok``.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param social_name: Social network name.
    :type social_name: ``str``
    :param token: Token from the social network.
    :type token: ``str``
    :return: Dict with added success.
    :rtype: ``dict``

    Example::

        {
            "success": True
        }
    """
    return client.self._make_request('post', f'/main/social/save-auth-token/', {'social_name': social_name, 'code_first': token})


def add_social_url_raw(client: 'Me', social_name: str, url: str) -> dict:
    """
    Connect social network (that required url) to your Me account.
        - Available for ``linkedin`` and ``pintrest``.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param social_name: Social network name.
    :type social_name: ``str``
    :param url: Url to your social profile.
    :type url: ``str``
    :return: Dict with added success.
    :rtype: ``dict``

    Example::

        {
            "success": True
        }
    """
    return client._make_request('post', '/main/social/update-url/', {'social_name': social_name, 'profile_id': url})


def remove_social_raw(client: 'Me', social_name: str) -> dict:
    """
    Remove social network from your Me account.
        - Available social networks: ``facebook``, ``instagram``, ``spotify``, ``twitter``, ``tiktok``, ``linkedin``, ``pintrest``.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param social_name: Social network name.
    :type social_name: ``str``
    :return: Dict with removed success.
    :rtype: ``dict``

    Example::

        {
            "success": True
        }
    """
    return client._make_request('post', '/main/social/delete/', {'social_name': social_name})


def switch_social_status_raw(client: 'Me', social_name: str) -> dict:
    """
    Switch social network status (hidden or shown) from your Me account.
        - Available social networks: ``facebook``, ``instagram``, ``spotify``, ``twitter``, ``tiktok``, ``linkedin``, ``pintrest``.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param social_name: Social network name.
    :type social_name: ``str``
    :return: Dict with switched success.
    :rtype: ``dict``

    Example::

        {
            'is_hidden': False
        }
    """
    return client._make_request('post', '/main/social/hide/', {'social_name': social_name})


def numbers_count_raw(client: 'Me') -> dict:
    """
    Get total count of numbers on Me.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :return: Dict with numbers count.
    :rtype: ``dict``

    Example::

        {
            'count': 5783726484
        }
    """
    return client._make_request('get', '/main/contacts/count/')


def suggest_turn_on_comments_raw(client: 'Me', uuid: str):
    """
    Ask from user to turn on comments in his profile.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param uuid: UUID of the user.
    :type uuid: ``str``
    :return: Dict with turned on comments success.
    :rtype: ``dict``

    Example::

        {
            'requested': True
        }
    """
    return client._make_request('post', '/main/users/profile/suggest-turn-on-comments/', {'uuid': uuid})


def suggest_turn_on_mutual_raw(client: 'Me', uuid: str):
    """
    Ask from user to turn on mutual contacts in his profile.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param uuid: UUID of the user.
    :type uuid: ``str``
    :return: Dict with turned on mutual success.
    :rtype: ``dict``

    Example::

        {
            'requested': True
        }
    """
    return client._make_request('post', '/main/users/profile/suggest-turn-on-mutual/', {'uuid': uuid})


def suggest_turn_on_location_raw(client: 'Me', uuid: str):
    """
    Ask from user to share his location with you.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param uuid: UUID of the user.
    :type uuid: ``str``
    :return: Dict with requested location success.
    :rtype: ``dict``

    Example::

        {
            'requested': True
        }
    """
    return client._make_request('post', '/main/users/profile/suggest-turn-on-location/', {'uuid': uuid})


def update_location_raw(client: 'Me', latitude: float, longitude: float):
    """
    Update your location.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param latitude: Latitude.
    :type latitude: ``float``
    :param longitude: Longitude.
    :type longitude: ``float``
    :return: Dict with updated location success.
    :rtype: ``dict``

    Example::

        {
            'success': True
        }
    """
    body = {"location_latitude": latitude, "location_longitude": longitude}
    return client._make_request('post', '/main/location/update/', body)


def share_location_raw(client: 'Me', uuid: str):
    """
    Share your location with user.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param uuid: UUID of the user that you want to share the location with him.
    :type uuid: ``str``
    :return: Dict with shared location success.
    :rtype: ``dict``

    Example::

        {
            'success': True
        }
    """
    return client._make_request('post', f'/main/users/profile/share-location/{uuid}/')


def stop_sharing_location_raw(client: 'Me', uuids: List[str]) -> dict:
    """
    Stop sharing your location with user.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param uuids: List of users UUID's that you want to stop sharing the location with them.
    :type uuids: List[``str``]
    :return: Dict with stopped sharing location success.
    :rtype: ``dict``

    Example::

        {
            'success': True
        }
    """
    return client._make_request('post', '/main/users/profile/share-location/stop-for-me/', {"uuids": uuids})


def stop_shared_locations_raw(client: 'Me', uuids: List[str]) -> dict:
    """
    Stop location that shared with you.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :param uuids: List of users UUID's that you want get their location.
    :type uuids: List[``str``]
    :return: Dict with stopped shared location success.
    :rtype: ``dict``

    Example::

        {
            'success': True
        }
    """
    return client._make_request('post', '/main/users/profile/share-location/stop/', {"uuids": uuids})


def locations_shared_by_me_raw(client: 'Me') -> List[dict]:
    """
    Get list of users that you shared your location with them.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :return: list of dicts with contacts details.
    :rtype: List[``dict``]

    Example::

        [
            {
                "first_name": "Rachel Green",
                "last_name": "",
                "phone_number": 1234567890,
                "profile_picture": "https://d18zaexen4dp1s.cloudfront.net/59XXXXXXXXXfa67.jpg",
                "uuid": "XXXXX-XXXXX-XXXX-XXXX-XXXXXX"
            }
        ]
    """
    return client._make_request('get', '/main/users/profile/share-location/')


def locations_shared_with_me_raw(client: 'Me') -> dict:
    """
    Get users who have shared a location with you. See also :py:func:`locations_shared_by_me`.

    :param client: :py:obj:`~meapi.Me` client object.
    :type client: :py:obj:`~meapi.Me`
    :return: dict with list of uuids and list with users.
    :rtype: ``dict``

    Example::

        {
            "shared_location_user_uuids": [
                "3850XXX-XXX-XXX-XXX-XXXXX"
            ],
            "shared_location_users": [
                {
                    "author": {
                        "first_name": "Gunther",
                        "last_name": "",
                        "phone_number": 3647632874324,
                        "profile_picture": "https://d18zaexen4dp1s.cloudfront.net/dXXXXXXXXXXXXXXXXXXb.jpg",
                        "uuid": "3850XXX-XXX-XXX-XXX-XXXXX"
                    },
                    "distance": 1.4099551982832228,
                    "i_shared": False
                }
            ]
        }
    """
    return client._make_request('get', '/main/users/profile/share-location/for-me/')