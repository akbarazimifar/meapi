import re
import random
import time
from datetime import date, datetime
import requests
from typing import List
from meapi.models.others import Contact, Call, Location, CallType
from meapi.utils.exceptions import NotValidPhoneNumber
from meapi.utils.validators import validate_phone_number

RANDOM_API = "https://randommer.io"


class RandomData:
    def __init__(self,
                 contacts: List[Contact] = None,
                 calls: List[Call] = None,
                 location: Location = None
                 ):
        self.contacts = contacts or list()
        self.calls = calls or list()
        self.location = location


def random_date(start_year: int = None, end_year: int = None) -> str:
    """
    Generate a random datetime between two years.
    """
    start_year = start_year if start_year else date.today().year - 5
    end_year = end_year if end_year else start_year + 5

    start, end, date_format = \
        f'{start_year}-05-12T00:00:11Z', f'{end_year}-06-24T00:00:11Z', '%Y-%m-%dT%H:%M:%S%z'
    try:
        stime = time.mktime(time.strptime(start, date_format))
        etime = time.mktime(time.strptime(end, date_format))
        ptime = stime + random.random() * (etime - stime)
        return datetime.strptime(time.strftime(date_format, time.localtime(ptime)), date_format).strftime(date_format)
    except ValueError:
        return random.choice((start, end))


def grft() -> str:
    return requests.post(
        RANDOM_API+"/phone-id-address?deviceIdType=FirebaseCloudMessaging&X-Requested-With=XMLHttpRequest"
    ).json()


def get_random_phone_numbers(country_code: str, limit: int = 50) -> List[int]:
    """
    Getting random phone numbers from https://randommer.io

    Args:
        country_code: Two letters country code. 'IL', 'US' etc.
        limit: Limit of phone numbers (Maybe less than limit if some numbers are invalid).

    Returns:
        List of random phone numbers.
    """
    raw_phone_numbers = requests.post(
        RANDOM_API+f"/free-valid-bulk-telephones-generator?number={limit}&"
                   f"twoLettersCode={country_code}&X-Requested-With=XMLHttpRequest"
    ).json()
    phone_numbers = []
    for phone_num in raw_phone_numbers:
        try:
            phone_numbers.append(validate_phone_number(phone_num))
        except NotValidPhoneNumber:
            pass
    return phone_numbers


def get_random_names(name_type: str, limit: int = 50) -> List[str]:
    """
    Getting random american names from https://randommer.io

    Args:
        name_type: One of: 'fullname', 'surname', 'firstname'
        limit: Limit of names.

    Returns:
        List of random names.
    """
    if name_type not in ('fullname', 'surname', 'firstname'):
        raise ValueError("name_type must be one of: 'fullname', 'surname', 'firstname'")
    return requests.post(RANDOM_API+f"/Name?type={name_type}&number={limit}&X-Requested-With=XMLHttpRequest").json()


def get_random_carrier() -> str:
    """
    Getting random carrier

    Returns:
        Random carrier.
    """
    return random.choice(('Verizon', 'AT&T', 'T-Mobile', 'Hot-Mobile', '012 Mobile', 'Cellcom', 'Pelephone'))


def get_random_adv_id() -> str:
    """
    Generating random adv_id

    Returns:
        Random adv_id.
    """
    return ''.join(random.choice('0123456789abcdef') for _ in range(32))


def get_random_country_code() -> str:
    """
    Getting random country code

    Returns:
        Random country code.


    """
    return random.choice(('IL', 'US', 'GB', 'RU', 'DE', 'FR', 'ES', 'IT', 'CA', 'AU'))


def generate_random_data(count: int = 50, contacts=False, calls=False, location=False) -> RandomData:
    """
    Generate random data.

    :param count: Number of random data to generate (10-20 more or less).
    :param contacts: Generate random contacts.
    :param calls: Generate random calls.
    :param location: Generate random location.
    :return: RandomData object.
    :raises ValueError: If you didn't set True at least one of the random data types: contacts, calls, location.
    """
    if not contacts and not calls and not location:
        raise ValueError("You need to set True at least one of the random data types: contacts, calls, location")
    data = RandomData()
    count = random.randint(count - 10 if count > 10 else 1, count + 10)

    if contacts or calls:
        country_code = random.choice(('IL', 'US', 'GB'))
        phone_numbers = get_random_phone_numbers(country_code=country_code, limit=count)
        names = get_random_names(name_type='fullname', limit=count)

        if contacts:
            data.contacts = [
                Contact(
                    phone_number=int(re.sub(r'\D', '', str(phone_numbers[i]))),
                    name=names[i],
                    country_code=country_code,
                ) for i in range(count)
            ]

        if calls:
            data.calls = [
                Call(
                    name=names[i],
                    phone_number=int(re.sub(r'\D', '', str(phone_numbers[i]))),
                    call_type=random.choice(CallType.all()),
                    called_at=random_date(),
                    duration=random.randint(10, 300)
                ) for i in range(count)
            ]

    if location:
        data.location = Location(
            latitude=round(random.uniform(-90, 90), 5),
            longitude=round(random.uniform(-180, 180), 5)
        )

    return data
