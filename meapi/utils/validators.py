from re import match, sub
from typing import Union
from meapi.utils.exceptions import NotValidPhoneNumber
from uuid import UUID


def validate_phone_number(phone_number: Union[str, int]) -> int:
    """
    Check if phone number is valid and return it clean without spaces, pluses or any other spacial characters.
     For example, the following phone numbers are valid:
         - ``972501234567``
         - ``972-50-123-4567``
         - ``972 50 123 4567``
         - ``+972501234567``
         - ``+972-50-123-4567``
         - ``+972 50 123 4567``
     and will be returned as ``972501234567``.

    :param phone_number: phone number in global format.
    :type phone_number:  ``int`` | ``str``
    :return: fixed phone number
    :rtype: int
    :raises NotValidPhoneNumber: If the phone number length is not between 11-15 digits.
    """
    phone_number = sub(r'\D', '', str(phone_number))
    if match(r"^\d{10,15}$", phone_number):
        return int(phone_number)
    raise NotValidPhoneNumber


def validate_uuid(uuid: str) -> str:
    """
    Check if the UUID is valid.

    :param uuid: uuid in string format.
    :type uuid: ``str``
    :raises TypeError: If the uuid is not a string.
    :raises ValueError: If the uuid is not valid.
    :return: The same uuid
    :rtype: ``str``
    """
    if not isinstance(uuid, str):
        raise TypeError("UUID should be a string!")
    try:
        UUID(uuid)
    except ValueError:
        raise ValueError(f"UUID {uuid} is not valid!")
    return uuid


def validate_schema_types(schema: dict, dictionary: dict, enforce: bool = False) -> bool:
    """
    Check if the dictionary contains the expected types for the schema.

    :param schema: dict with the expected types. Example: ``{'name': str, 'phone_number': int}``
    :type schema: dict
    :param dictionary: Example: ``{'name': 'John', 'phone_number': 123456789}``
    :type dictionary: dict
    :return: True if the dictionary contains the expected types.
    :rtype: bool
    :param enforce: enforce all the keys in the schema to be in the dict.
    :type enforce: bool
    :raises TypeError: If one of the values in the dictionary is not the expected type.
    :raises ValueError: if enforce is True and the dictionary does not contain all the keys in the schema.
    """
    if enforce and not all(key in dictionary for key in schema):
        raise ValueError(f"The dictionary is not contains all the schema keys!"
                         f"\n\tSCHEMA: {list(schema.keys())}\n\tDICT: {(dictionary.keys())}")
    for key, value in dictionary.items():
        if not isinstance(value, schema[key]):
            raise TypeError(f"The value of the key '{key}' should be {schema[key]} but got {type(value)}!")
    return True
