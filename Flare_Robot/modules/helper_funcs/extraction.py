from typing import List, Optional

from telegram import Message, MessageEntity
from telegram.error import BadRequest

from Flare_Robot import LOGGER



def extract_user(message: Message, args: List[str]) -> Optional[int]:
    return extract_user_and_text(message, args)[0]
