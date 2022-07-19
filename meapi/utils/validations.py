from random import randint
from re import match, sub
from typing import Union, List
from meapi.utils.exceptions import MeException


def validate_contacts(contacts: List[dict]) -> List[dict]:
    """
    Gets list of dict of contacts and return the valid contacts in the same format. to use of add_contacts and remove_contacts methods
    """
    contacts_list = []
    for con in contacts:
        if isinstance(con, dict):
            if con.get('name') and con.get('phone_number'):
                contacts_list.append(con)
    if not contacts_list:
        raise MeException("Valid contacts not found! check this example for valid contact syntax: "
                          "https://gist.github.com/david-lev/b158f1cc0cc783dbb13ff4b54416ceec#file-contacts-py")
    return contacts_list


def validate_calls(calls: List[dict]) -> List[dict]:
    """
    Gets list of dict of calls and return the valid calls in the same format. to use of add_calls_to_log and remove_calls_from_log methods
    """
    calls_list = []
    for cal in calls:
        if isinstance(cal, dict):
            if not cal.get('name') or not cal.get('phone_number'):
                if cal.get('phone_number'):
                    cal['name'] = str(cal.get('phone_number'))
                else:
                    raise MeException("Phone number must be provided!!")
            if cal.get('type') not in ['incoming', 'missed', 'outgoing']:
                raise MeException("No such call type as " + str(cal.get('type')) + "!")
            if not cal.get('duration'):
                cal['duration'] = randint(10, 300)
            if not cal.get('tag'):
                cal['tag'] = None
            if not cal.get('called_at'):
                cal['called_at'] = f"{randint(2018, 2022)}-{randint(1, 12)}-{randint(1, 31)}T{randint(1, 23)}:{randint(10, 59)}:{randint(10, 59)}Z"
            calls_list.append(cal)
    if not calls_list:
        raise MeException("Valid calls not found! check this example for valid call syntax: "
                          "https://gist.github.com/david-lev/b158f1cc0cc783dbb13ff4b54416ceec#file-calls_log-py")
    return calls_list


def validate_phone_number(phone_number: Union[str, int]) -> int:
    """
    Check if phone number is valid and return it clean without spaces, pluses or other spacial characters.
     - ``(972) 123-4567890``, ``+9721234567890``, ``123-456-7890`` --> ``9721234567890``.

    :param phone_number: phone number in global format.
    :type phone_number:  ``int`` | ``str``
    :raises MeException: If length of phone number not between 9-15.
    :return: fixed phone number
    :rtype: int
    """
    if phone_number:
        phone_number = sub(r'[\D]', '', str(phone_number))
        if match(r"^\d{9,15}$", phone_number):
            return int(phone_number)
    raise MeException("Not a valid phone number! " + phone_number)


def validate_auth_response(auth_data: dict) -> dict:
    """
    Check if the CredentialsManager gets or return the expected data format

    :param auth_data: dict with ``access``, ``refresh``, ``uuid``, and ``pwd_token``.
    :type auth_data: dict
    :return: The same information he received.
    :rtype: dict
    :raises MeException: If the data does not valid.
    """
    if not isinstance(auth_data, dict):
        raise MeException("auth_data should be a dict!")
    expected_keys = ['access', 'refresh', 'uuid', 'pwd_token']
    if sorted(expected_keys) != sorted(auth_data.keys()):
        raise MeException(f"The auth_data should contain the following keys: {expected_keys}. Your data contains this keys: {list(auth_data.keys())}")
    if not all(isinstance(val, str) for val in auth_data.values()):
        raise MeException("The auth_data values should be strings!")
    return auth_data
