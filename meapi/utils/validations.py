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
    :type phone_number: Union[int, str]
    :raises MeException: If length of phone number not between 9-15.
    :return: fixed phone number
    :rtype: int
    """
    if phone_number:
        phone_number = sub(r'[\D]', '', str(phone_number))
        if match(r"^\d{9,15}$", phone_number):
            return int(phone_number)
    raise MeException("Not a valid phone number! " + phone_number)


def validate_profile_details(key: str, value: str) -> str:
    if value is not None:
        if key == 'country_code':
            value = str(value).upper()[:2]
        elif key == 'date_of_birth':
            if not match(r'^\d{4}(\-)([0-2]\d|(3)[0-1])(\-)(((0)\d)|((1)[0-2]))$', str(value)):
                raise MeException("Birthday must be in YYYY-MM-DD format!")
        elif key == 'device_type':
            device_types = ['android', 'ios']
            if value not in device_types:
                raise MeException(f"Device type not in the available device types ({', '.join(device_types)})!")
        elif key == 'login_type':
            login_types = ['email', 'apple']
            if value not in login_types:
                raise MeException(f"Login type not in the available login types ({', '.join(login_types)})!")
        elif key == 'email':
            if not match(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$', str(value)):
                raise MeException("Email must be in user@domain.com")
        elif key in ['first_name', 'last_name', 'slogan']:
            if not isinstance(value, str):
                raise MeException(f"{key.replace('_', '').capitalize()} must be a string!")
        elif key == 'gender':
            genders = {'M': 'M', 'F': 'F', 'N': None, None: None}
            if str(value).upper() not in genders.keys():
                raise MeException("Gender must be: 'F' for Female, 'M' for Male, and 'None' for null.")
            value = str(value).upper()
        elif key == 'profile_picture_url':
            if not match(r'(https?:\/\/.*\.(?:png|jpg))', str(value)):
                raise MeException("Profile picture url must be a image link!")
        elif key == 'facebook_url':
            if not match(r'^\d+$', str(value)):
                raise MeException("Facebook url must be numbers!")

    if key not in ['country_code', 'date_of_birth', 'device_type', 'login_type', 'email', 'first_name',
                   'last_name', 'slogan', 'gender', 'profile_picture_url', 'facebook_url', '_MeModel__init_done']:
        raise MeException("You cannot change this field!")

    return value
