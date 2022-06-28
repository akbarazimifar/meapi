from typing import Union, List


def friendship_raw(meobj, phone_number: Union[int, str]) -> dict:
    """
    Get friendship information between you and another number.
    like count mutual friends, total calls duration, how do you name each other, calls count, your watches, comments, and more.

    :param phone_number: International phone number format.
    :type phone_number: Union[int, str]
    :return: Dict with friendship data.
    :rtype: dict

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
    return meobj._make_request('get', f'/main/contacts/friendship/?phone_number={phone_number}')


def report_spam_raw(meobj, country_code: str, phone_number: str, spam_name: str) -> dict:
    """
    Report a number as spam.

    :param country_code: Country code.
    :type country_code: str
    :param phone_number: International phone number format.
    :type phone_number: Union[int, str]
    :param spam_name: Name of the spammer.
    :type spam_name: str
    :return: Dict with spam report success.
    :rtype: dict

    Example of results::
        {'success': True}
    """
    body = {"country_code": country_code, "is_spam": True, "is_from_v": False,
     "name": spam_name, "phone_number": phone_number}
    return meobj._make_request('post', f'/main/names/suggestion/report/', body=body)


def who_deleted_raw(meobj) -> List[dict]:
    """
    Get a list of users that deleted you from their contacts.

    :return: List of dicts with users.
    :rtype: List[dict]

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
    return meobj._make_request('get', '/main/users/profile/who-deleted/')


def who_watched_raw(meobj) -> List[dict]:
    """
    Get a list of users that watched you.

    :return: List of dicts with users.
    :rtype: List[dict]

    Example of results::

    Example::

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
    return meobj._make_request('get', '/main/users/profile/who-watched/')


def get_comments_raw(meobj, uuid: str) -> dict:
    """
    Get user comments.

    :param uuid: User uuid.
    :type uuid: str
    :return: Dict with list of comments.
    :rtype: dict

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
    return meobj._make_request('get', f'/main/comments/list/{uuid}')


def get_comment_raw(me_obj, comment_id: int) -> dict:
    """
    Get comment details, comment text, who and how many liked, create time and more.

    :param comment_id: Comment id.
    :type comment_id: int
    :return: Dict with comment details.
    :rtype: dict

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
    return me_obj._make_request('get', f'/main/comments/retrieve/{comment_id}')

