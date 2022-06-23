from base64 import b64encode
from datetime import datetime, date
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


def parse_date(date_str: str, date_only=False) -> Union[datetime, date, None]:
    if date_str is None:
        return date_str
    date_obj = datetime.strptime(str(date_str), '%Y-%m-%d' + ('' if date_only else 'T%H:%M:%S%z'))
    return date_obj.date() if date_only else date_obj


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


def get_img_binary_content(url: str):
    try:
        res = get(url)
        if res.status_code == 200:
            return b64encode(res.content).decode("utf-8")
    except Exception:
        return None


def encode_string(string: str) -> str:
    return encodestring(string.encode('utf-8')).decode("utf-8")


def get_vcard(data: dict, prefix_name: str = "", profile_picture: bool = True, **kwargs) -> str:
    """
    Get vcard format based on data provided
    """
    vcard_data = {'start': "BEGIN:VCARD", 'version': "VERSION:3.0"}

    if prefix_name:
        prefix_name += " - "
    full_name = (prefix_name + (data.get('first_name') or data.get('name')))
    if data.get('last_name'):
        full_name += (" " + data['last_name'])

    vcard_data['name'] = f"FN;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:{encode_string(full_name)}"
    vcard_data['phone'] = f"TEL;CELL:{data['phone_number']}"
    if profile_picture and data.get('profile_picture'):
        vcard_data['photo'] = f"PHOTO;ENCODING=BASE64;JPEG:{get_img_binary_content(data['profile_picture'])}"
    if data.get('email'):
        vcard_data['email'] = f"EMAIL:{data['email']}"
    if data.get('date_of_birth'):
        vcard_data['birthday'] = f"BDAY:{data['date_of_birth']}"

    notes = 'Extracted by meapi https://github.com/david-lev/meapi'
    for key, value in kwargs.items():
        if data.get(key):
            notes += f" | {value}: {data[key]}"

    vcard_data['note'] = f"NOTE;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:{encode_string(notes)}"
    vcard_data['end'] = "END:VCARD"

    return "\n".join([val for val in vcard_data.values()])
