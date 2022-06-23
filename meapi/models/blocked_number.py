from typing import Union
from meapi.models.me_model import MeModel


class BlockedNumber(MeModel):
    def __init__(self,
                 block_contact: Union[bool, None] = None,
                 me_full_block: Union[bool, None] = None,
                 phone_number: Union[int, None] = None
                 ):
        self.block_contact = block_contact
        self.me_full_block = me_full_block
        self.phone_number = phone_number
        super().__init__()

    def __repr__(self):
        return f"<BlockedNumber phone={self.phone_number}>"

    def __str__(self):
        return str(self.phone_number)