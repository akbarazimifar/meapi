import time
from base64 import b64encode
from datetime import datetime, date
from quopri import encodestring
from random import choice
from typing import Union, Optional, TYPE_CHECKING
from requests import get
from string import ascii_letters, digits
from hashlib import sha256
from os import urandom, path
from meapi.api.raw.account import upload_image_raw

if TYPE_CHECKING:
    from meapi.me import Me

ANDROID_VERSION_CODE = 444
ANDROID_VERSION_NAME = '7.2.6'
HEADERS = {
    'accept-encoding': 'gzip',
    'user-agent': f'A({ANDROID_VERSION_CODE}):545b7fc43d93',
    'content-type': 'application/json; charset=UTF-8'
}


def upload_picture(client: 'Me', image: str) -> str:
    """
    Upload a profile picture from a local file or a direct url.
    :param client: Me client
    :type client: Me
    :param image: Path or url to the image. for example: ``https://example.com/image.png``, ``/path/to/image.png``.
    :type image: ``str``
    :return: The url of the uploaded image.
    :rtype: ``str``
    :raises FileNotFoundError: If the file does not exist.
    """
    if not str(image).startswith("http"):
        if not path.isfile(image):
            raise FileNotFoundError(f"File {image} does not exist!")
        with open(image, 'rb') as f:
            image_data = f.read()
    else:
        image_data = get(url=str(image)).content
    return upload_image_raw(client, image_data)['url']


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
