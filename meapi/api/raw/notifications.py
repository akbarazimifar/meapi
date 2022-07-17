from typing import List, TYPE_CHECKING
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me


def unread_notifications_count_raw(client: 'Me') -> dict:
    """
    Get number of unread notifications.

    :return: Dict with number of unread notifications.
    :rtype: ``dict``
    """
    return client._make_request('get', '/notification/notification/count/')


def get_notifications_raw(client: 'Me', page_number: int, results_limit: int, categories: List[str] = None) -> dict:
    """
    Get notifications.

    :param page_number: Page number.
    :param results_limit: Number of results per page.
    :param categories: List of categories to filter.
    :return: Dict with notifications.
    :rtype: ``dict``

    Example::

        {
            "count": 94,
            "next": "https://app.mobile.me.app/notification/notification/items/?page=2&page_size=30&status=distributed",
            "previous": None,
            "results": [
                {
                    "id": 103466332,
                    "created_at": "2022-03-18T11:17:09Z",
                    "modified_at": "2022-03-18T11:17:09Z",
                    "is_read": False,
                    "sender": "2e7XXX-84XXXX-4ec7-b6cb-d4XXXXXX",
                    "status": "distributed",
                    "delivery_method": "push",
                    "distribution_date": "2022-03-18T11:17:09Z",
                    "message_subject": None,
                    "message_category": "BIRTHDAY",
                    "message_body": None,
                    "message_lang": "iw",
                    "context": {
                        "name": "Ross geller",
                        "uuid": "2e7XXXX-XXXX-XXXX-b6cXb-d46XXXXX1",
                        "category": "BIRTHDAY",
                        "phone_number": 97849743536,
                        "notification_id": None,
                        "profile_picture": None,
                    },
                },
                {
                    "id": 18987495325,
                    "created_at": "2022-04-06T11:18:03Z",
                    "modified_at": "2022-04-06T11:18:03Z",
                    "is_read": False,
                    "sender": "5XXXXX0e-XXXX-XXXX-XXXX-XXXXXXX",
                    "status": "distributed",
                    "delivery_method": "push",
                    "distribution_date": "2022-04-06T11:18:03Z",
                    "message_subject": None,
                    "message_category": "UPDATED_CONTACT",
                    "message_body": None,
                    "message_lang": "iw",
                    "context": {
                        "name": "Chandler",
                        "uuid": "XXXXXX-XXXX-XXXXX-XXX-XXXXX",
                        "category": "UPDATED_CONTACT",
                        "new_name": "Your new name",
                        "phone_number": 8479843759435,
                        "notification_id": None,
                        "profile_picture": None,
                    },
                },
                {
                    "id": 17983743351,
                    "created_at": "2022-04-11T06:45:27Z",
                    "modified_at": "2022-04-11T06:45:27Z",
                    "is_read": False,
                    "sender": "XXXXXX-XXXX-XXXXX-XXX-XXXXX",
                    "status": "distributed",
                    "delivery_method": "push",
                    "distribution_date": "2022-04-11T06:45:27Z",
                    "message_subject": None,
                    "message_category": "CONTACT_ADD",
                    "message_body": None,
                    "message_lang": "iw",
                    "context": {
                        "name": "Monica",
                        "uuid": "XXXXXX-XXXX-XXXXX-XXX-XXXXX",
                        "category": "CONTACT_ADD",
                        "new_name": "Ross",
                        "phone_number": 878634535436,
                        "notification_id": None,
                        "profile_picture": None,
                    }
                }
            ]
        }
    """
    params = f"?page={page_number}&page_size={results_limit}&status=distributed"
    if categories:
        params += f"&categories=%5B{'%2C%20'.join(categories)}%5D"
    return client._make_request('get', '/notification/notification/items/' + params)


def read_notification_raw(client: 'Me', notification_id: int) -> dict:
    """
    Mark notification as read.

    :param notification_id: Notification ID.
    :type notification_id: ``int``
    :return: Dict with notification.
    :rtype: ``dict``

    Example::

        {
            'id': 3487438454,
            'created_at': '2022-06-28T22:12:36Z',
            'modified_at': '2022-06-30T23:56:59Z',
            'is_read': True,
            'sender': 'fejdsfns-hdiu-ddv-83c1-hdisds',
            'status': 'distributed',
            'delivery_method': 'push',
            'distribution_date': '2022-06-28T22:12:35Z',
            'message_subject': None,
            'message_category': 'NEW_COMMENT',
            'message_body': None,
            'message_lang': 'en',
            'context': {
                'name': 'Monica',
                'uuid': 'dsfsds-dsfd-490a-dfdfg-dfoeiffs',
                'category': 'NEW_COMMENT',
                'phone_number': 972538607327,
                'notification_id': None,
                'profile_picture': 'https://dfsfs.cloudfront.net/dhiucds.jpg'
            }
        }
    """
    return client._make_request('post', '/notification/notification/read/', {'notification_id': notification_id})
