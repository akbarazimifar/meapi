from base64 import b64encode
from quopri import encodestring
from re import match, sub
from typing import Union
from requests import get
from meapi.exceptions import MeException


def valid_phone_number(phone_number: Union[str, int]) -> int:
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
