from typing import TYPE_CHECKING
from meapi.models.me_model import MeModel
from meapi.utils.exceptions import MeException
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me

class BlockedNumber(MeModel):
    """
    Represents a blocked number.
        - `For more information about blocked numbers <https://me.app/block-or-unblock-a-phone-number-me-user/>`_

    Parameters:
        block_contact (``bool``):
            Whether the number is blocked.
        me_full_block (``bool``):
            Whether the profile is blocked by.
        phone_number (``int``):
            The phone number of the contact.
    """
    def __init__(self,
                 _client: 'Me',
                 block_contact: bool,
                 me_full_block: bool,
                 phone_number: int
                 ):
        self.block_contact = block_contact
        self.me_full_block = me_full_block
        self.phone_number = phone_number
        self.__client = _client
        self.__init_done = True

    def unblock(self, me_full_unblock: bool = True, unblock_contact: bool = True) -> bool:
        """
        Unblock this number.
            - Same as :py:func:`~meapi.Me.unblock_profile`.
        """
        if self.__client.unblock_profile(self.phone_number, me_full_unblock, unblock_contact):
            self.block_contact = False
            self.me_full_block = False
            return True
        return False

    def __setattr__(self, key, value):
        if getattr(self, '_BlockedNumber__init_done', None) and key != "phone_number":
            raise MeException(f"{key} cannot be changed!")
        super().__setattr__(key, value)

    def __repr__(self):
        return f"<BlockedNumber phone={self.phone_number}>"

    def __str__(self):
        return str(self.phone_number)

