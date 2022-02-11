from typing import List, Optional

from telegram import Message, MessageEntity
from telegram.error import BadRequest

from Flare_Robot import LOGGER
from Flare_Robot.modules.users import get_user_id



def extract_user(message: Message, args: List[str]) -> Optional[int]:
    return extract_user_and_text(message, args)[0]
