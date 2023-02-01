import time
from base64 import b64encode
from datetime import datetime, date
from quopri import encodestring
from random import choice
from typing import Union, Optional
from requests import get
from string import ascii_letters, digits
from hashlib import sha256
from os import urandom


AVC = 444
AVN = '7.2.6'
GIB = '545b7fc43d93'
HEADERS = {
    'accept-encoding': 'gzip',
    'user-agent': f'A({AVC}):{GIB}',
    'content-type': 'application/json; charset=UTF-8'
}

logo = \
"""
Welcome to meapi!
                            _ 
 _ __ ___   ___  __ _ _ __ (_)
| '_ ` _ \ / _ \/ _` | '_ \| |
| | | | | |  __/ (_| | |_) | |
|_| |_| |_|\___|\__,_| .__/|_|
                     |_|
>> MeAPI v{version}
>> Copyright (C) {copyright}
>> Source Code: https://github.com/david-lev/meapi
>> Documentation: https://meapi.readthedocs.io
>> License: {license}
>> meapi is free software and comes with ABSOLUTELY NO WARRANTY.
"""


def parse_date(date_str: Optional[str], date_only=False) -> Optional[Union[datetime, date]]:
    """
    Parse a date string to a datetime/date object.
    """
    if date_str is None:
        return date_str
    date_obj = datetime.strptime(str(date_str), '%Y-%m-%d' + ('' if date_only else 'T%H:%M:%S%z'))
    return date_obj.date() if date_only else date_obj


def get_img_binary_content(img_url: str) -> Optional[str]:
    try:
        res = get(img_url)
        if res.status_code == 200:
            return b64encode(res.content).decode("utf-8")
    except (ConnectionError, Exception):
        return None


def encode_string(string: str) -> str:
    return encodestring(string.encode('utf-8')).decode("utf-8")


def generate_session_token(seed: str, phone_number: int) -> str:
    try:
        from Crypto.Cipher import AES
    except ImportError:
        raise ImportError('You need to install the `Crypto` package in order to generate session token!')
    last_digit = int(str(phone_number)[-1])
    a1 = str(int(phone_number * (last_digit + 2)))
    a2 = str(int(int(time.time()) * (last_digit + 2)))
    a3 = ''.join(choice(ascii_letters + digits) for _ in range(abs(48 - len(a1 + a2) - 2)))
    iv = urandom(16)
    aes = AES.new(sha256(seed.encode()).digest(), AES.MODE_CBC, iv)
    data_to_encrypt = "{}-{}-{}".format(a1, a2, a3).encode()
    padding = (len(data_to_encrypt) % 16) or 16
    final_token = b64encode(iv + aes.encrypt(data_to_encrypt + bytes((chr(padding) * padding).encode())))
    return final_token.decode()
