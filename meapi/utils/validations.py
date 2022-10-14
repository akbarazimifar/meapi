from random import randint
from re import match, sub
from typing import Union, List
from meapi.utils.exceptions import MeException
from uuid import UUID


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
    Check if phone number is valid and return it clean without spaces, pluses or any other spacial characters.
     - ``(972) 123-4567890``, ``+9721234567890``, ``972-123-456-7890`` --> ``9721234567890``.

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


def validate_uuid(uuid: str) -> str:
    """
    Check if the UUID is valid.

    :param uuid: uuid in string format.
    :type uuid: ``str``
    :raises MeException: If the uuid is not valid.
    :return: The same uuid
    :rtype: ``str``
    """
    if not isinstance(uuid, str):
        raise MeException("UUID should be a string!")
    try:
        UUID(uuid)
    except ValueError:
        raise MeException("UUID is not valid! " + uuid)
    return uuid


def validate_schema_types(schema: dict, dictionary: dict, enforce=False) -> bool:
    """
    Check if the dictionary contains the expected types for the schema.

    :param schema: dict with the expected types. Example: ``{'name': str, 'phone_number': int}``
    :type schema: dict
    :param dictionary: dict with the values. Example: ``{'name': 'John', 'phone_number': 123456789}``
    :type dictionary: dict
    :return: True if the dictionary contains the expected types.
    :rtype: bool
    :param enforce: enforce all the keys in the schema to be in the dict.
    :type enforce: bool
    :raises MeException: If the dictionary does not valid.
    """
    if enforce:
        if not all(key in dictionary for key in schema):
            raise MeException(f"The dictionary is not contains all the schema keys!"
                              f"\n\tSCHEMA: {schema}\n\tDICT: {dictionary}")
    for key, value in dictionary.items():
        if key not in schema:
            raise MeException(f"The dictionary contains the key '{key}' which is not expected!")
        if not isinstance(value, schema[key]):
            raise MeException(f"The value of the key '{key}' should be {schema[key]} type!")
    return True
