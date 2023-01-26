import os
import pytest
from meapi import Me
from meapi.credentials_managers.memory import MemoryCredentialsManager
from meapi.utils.exceptions import NotValidPhoneNumber, ActivationCodeExpired
from meapi.utils.randomator import get_random_phone_numbers, get_random_names


class MyCredentialsManager(MemoryCredentialsManager):
    def __init__(self):

        self.credentials = {
            os.environ['PHONE_NUMBER']: {
                'access': '',
                'refresh': '',
                'pwd_token': os.environ['PWD_TOKEN']
            }
        }


@pytest.fixture(scope='session')
def phone_number():
    return os.environ['PHONE_NUMBER']


@pytest.fixture(scope='session')
def cm():
    return MyCredentialsManager()


@pytest.fixture(scope='session')
def me(phone_number, cm):
    return Me(phone_number=phone_number, credentials_manager=cm)


def test_me(cm):
    with pytest.raises(NotValidPhoneNumber):
        Me(phone_number='123456789', credentials_manager=cm)
    with pytest.raises(ValueError):
        Me(phone_number='9721234567890', activation_code='123', credentials_manager=cm)
    with pytest.raises(ActivationCodeExpired):
        Me(phone_number='9721234567890', activation_code='123456', credentials_manager=cm)


def test_randomizer():
    phone_numbers = get_random_phone_numbers(country_code='IL', limit=1)
    assert len(phone_numbers) == 1
    assert isinstance(phone_numbers[0], int)
    names = get_random_names(name_type='fullname', limit=1)
    assert len(names) == 1
    assert isinstance(names[0], str)


def test_credentials_manager(phone_number, cm):
    with pytest.raises(TypeError):
        Me(phone_number=phone_number, credentials_manager=True)
    assert isinstance(cm.get(phone_number), dict)
    cm.delete(phone_number)
    assert cm.get(phone_number) is None

