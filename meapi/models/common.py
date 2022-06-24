from meapi.utils.exceptions import MeException
from meapi.utils.helpers import get_vcard


class _CommonMethodsForUserContactProfile:
    """
    Common methods for user, profile and contact
    """
    def block(self, block_contact=True, me_full_block=True) -> bool:
        if getattr(self, f'_{self.__class__.__name__}__my_profile', None):
            raise MeException("you can't block yourself!")
        return getattr(self, f'_{self.__class__.__name__}__meobj').block_profile(phone_number=self.phone_number, block_contact=block_contact, me_full_block=me_full_block)

    def unblock(self, unblock_contact=True, me_full_unblock=True) -> bool:
        if getattr(self, f'_{self.__class__.__name__}__my_profile', None):
            raise MeException("you can't unblock yourself!")
        return getattr(self, f'_{self.__class__.__name__}__meobj').unblock_profile(phone_number=self.phone_number, unblock_contact=unblock_contact, me_full_unblock=me_full_unblock)

    def get_vcard(self, prefix_name: str = "", profile_picture: bool = True, **kwargs) -> str:
        return get_vcard(self.__dict__, prefix_name, profile_picture, **kwargs)

