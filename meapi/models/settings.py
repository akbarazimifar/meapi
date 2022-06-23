from typing import Union
from meapi.exceptions import MeException
from meapi.models.me_model import MeModel


class Settings(MeModel):
    def __init__(self,
                 _meobj,
                 birthday_notification_enabled: Union[bool, None] = None,
                 comments_enabled: Union[bool, None] = None,
                 comments_notification_enabled: Union[bool, None] = None,
                 contact_suspended: Union[bool, None] = None,
                 distance_notification_enabled: Union[bool, None] = None,
                 language: Union[str, None] = None,
                 last_backup_at: Union[None, None] = None,
                 last_restore_at: Union[None, None] = None,
                 location_enabled: Union[bool, None] = None,
                 mutual_contacts_available: Union[bool, None] = None,
                 names_notification_enabled: Union[bool, None] = None,
                 notifications_enabled: Union[bool, None] = None,
                 spammers_count: Union[int, None] = None,
                 system_notification_enabled: Union[bool, None] = None,
                 who_deleted_enabled: Union[bool, None] = None,
                 who_deleted_notification_enabled: Union[bool, None] = None,
                 who_watched_enabled: Union[bool, None] = None,
                 who_watched_notification_enabled: Union[bool, None] = None,
                 ):
        self.birthday_notification_enabled = birthday_notification_enabled
        self.comments_enabled = comments_enabled
        self.comments_notification_enabled = comments_notification_enabled
        self.contact_suspended = contact_suspended
        self.distance_notification_enabled = distance_notification_enabled
        self.language = language
        self.last_backup_at = last_backup_at
        self.last_restore_at = last_restore_at
        self.location_enabled = location_enabled
        self.mutual_contacts_available = mutual_contacts_available
        self.names_notification_enabled = names_notification_enabled
        self.notifications_enabled = notifications_enabled
        self.spammers_count = spammers_count
        self.system_notification_enabled = system_notification_enabled
        self.who_deleted_enabled = who_deleted_enabled
        self.who_deleted_notification_enabled = who_deleted_notification_enabled
        self.who_watched_enabled = who_watched_enabled
        self.who_watched_notification_enabled = who_watched_notification_enabled
        self.__meobj = _meobj
        self.__init_done = True

    def __repr__(self):
        return f"<Settings lang={self.language}>"

    def __setattr__(self, key, value):
        if getattr(self, '_Settings__init_done', None):
            if key not in ['spammers_count', 'last_backup_at', 'last_restore_at', 'contact_suspended']:
                if key == 'language':
                    if isinstance(value, str) and len(value) == 2 and value.isalpha():
                        pass
                if not isinstance(value, bool):
                    raise MeException(f"{str(key)} value must be a bool type!")
            else:
                raise MeException("You can't change this setting!")
            if self.__meobj.change_settings(**{key: value})[key] != value:
                raise MeException("not updated")

        return super().__setattr__(key, value)

    def __change_all(self, change_to: bool):
        to_change = {}
        for key, value in self.__dict__.items():
            if isinstance(value, bool) and not key.startswith('_') and key != 'contact_suspended':
                to_change[key] = change_to
        res = self.__meobj.change_settings(**to_change)
        for key in to_change:
            if res[key] != change_to:
                return False
        self.__dict__.update(to_change)
        return True

    def enable_all(self) -> bool:
        return self.__change_all(change_to=True)

    def disable_all(self) -> bool:
        return self.__change_all(change_to=False)
