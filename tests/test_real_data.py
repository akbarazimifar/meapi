import datetime
import os
import pytest
from meapi import Me
from meapi.credentials_managers.memory import MemoryCredentialsManager
from meapi.models.others import NewAccountDetails, AuthData
from meapi.models.settings import Settings
from meapi.utils.exceptions import NewAccountException


@pytest.fixture(scope='session')
def phone_number():
    return os.environ['PHONE_NUMBER']


@pytest.fixture(scope='session')
def activation_code():
    return os.environ['ACTIVATION_CODE']


@pytest.fixture(scope='session')
def new_account_details():
    return NewAccountDetails(
        first_name=os.environ.get('FIRST_NAME', 'John'),
        last_name=os.environ.get('LAST_NAME', 'Doe'),
        email=os.environ.get('EMAIL', 'john.doe@gmail.com')
    )


@pytest.fixture(scope='session')
def cm():
    return MemoryCredentialsManager()


@pytest.fixture(scope='session', name='me')
def test_login(phone_number, cm, new_account_details, activation_code):
    try:
        me = Me(
            phone_number=phone_number,
            activation_code=activation_code,
            credentials_manager=cm,
            raise_new_account_exception=True
        )
    except NewAccountException:
        me = Me(phone_number=phone_number, credentials_manager=cm, new_account_details=new_account_details)

    assert isinstance(me._auth_data, AuthData), 'me._auth_data should be an instance of AuthData'
    assert me._auth_data.pwd_token is not None, 'me._auth_data.pwd_token should not be None'
    return me


@pytest.fixture(scope='session', name='profile')
def test_account(me):
    assert me.get_uuid() == me.uuid, 'me.get_uuid() should be equal to me.uuid'
    profile = me.get_my_profile()
    assert profile.phone_number == me.phone_number, 'profile.phone_number should be equal to me.phone_number'
    with pytest.raises(ValueError):
        profile.device_type = 'invalid'
    me.update_profile_details(device_type='ios' if profile.device_type != 'ios' else 'android')
    assert me.get_my_profile().device_type != profile.device_type, 'device type should be changed'
    profile.device_type = profile.device_type
    me.get_blocked_numbers()
    me.block_profile(972123456789)
    assert 972123456789 in [x.phone_number for x in me.get_blocked_numbers()], '972123456789 should be blocked'
    me.unblock_profile('972123456789')
    assert 972123456789 not in [x.phone_number for x in me.get_blocked_numbers()], '972123456789 should be unblocked'
    return profile


def test_notifications(me):
    count = me.unread_notifications_count()
    if count > 0:
        notifications = me.get_notifications()
        if notifications:
            assert len(notifications) <= count, 'len(notifications) should be less than or' \
                                                ' equal to count of unread notifications'
            notifications[0].read()
            assert notifications[0].is_read is True, 'notification should be marked as read'


@pytest.fixture(scope='session', name='settings')
def test_settings(me):
    settings = me.get_settings()
    assert isinstance(settings, Settings), 'settings should be an instance of Settings'
    settings.notifications_enabled = not settings.notifications_enabled
    assert me.get_settings().notifications_enabled is settings.notifications_enabled, 'settings.notifications_enabled should be changed'
    settings.notifications_enabled = not settings.notifications_enabled
    return settings


def test_social(me, settings, profile):
    who_deleted_enabled = settings.who_deleted_enabled
    who_watched_enabled = settings.who_watched_enabled
    settings.who_deleted_enabled = False
    settings.who_watched_enabled = False
    assert me.who_deleted() == [], 'who_deleted should be empty'
    assert me.who_watched() == [], 'who_watched should be empty'
    settings.who_deleted_enabled = who_deleted_enabled
    settings.who_watched_enabled = who_watched_enabled
    socials = me.get_socials()
    old_linkedin_url = socials.linkedin.profile_url
    if not socials.linkedin.is_active:
        socials.linkedin.add('https://www.linkedin.com/in/username')
        new_socials = me.get_socials()
        assert new_socials.linkedin.is_active, 'linkedin should be active'
        assert new_socials.linkedin.profile_url == 'https://www.linkedin.com/in/username', 'linkedin url should be https://www.linkedin.com/in/username'
        me.switch_social_status(linkedin=False)
        assert me.get_socials().linkedin.is_hidden, 'linkedin should be hidden'
        socials.linkedin.unhide()
        socials.linkedin.remove()
    else:
        me.add_social(linkedin_url=old_linkedin_url)
    me.get_comments()
    groups = me.get_groups()
    if len(groups) > 0:
        groups[0].delete()
        assert groups[0] not in me.get_groups(), 'Group should be deleted'
        groups[0].restore()

    year_now = datetime.date.today().year
    old_date_of_birth = profile.date_of_birth
    profile.date_of_birth = f'{year_now - 20}-01-01'
    assert me.get_age() == 20, 'Age should be 20'
    profile.date_of_birth = old_date_of_birth
