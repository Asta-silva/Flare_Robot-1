from math import ceil
from typing import Dict, List

from telegram import InlineKeyboardButton
from Flare_Robot import BOT_USERNAME


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text



def paginate_modules(page_n: int, module_dict: Dict, prefix, chat=None) -> List:
    if not chat:
        modules = sorted(
            [EqInlineKeyboardButton(x.__mod_name__,
                                    callback_data="{}_module({})".format(prefix, x.__mod_name__.lower())) for x
             in module_dict.values()])
    else:
        modules = sorted(
            [EqInlineKeyboardButton(x.__mod_name__,
                                    callback_data="{}_module({},{})".format(prefix, chat, x.__mod_name__.lower())) for x
             in module_dict.values()])

    pairs = [
    modules[i * 3:(i + 1) * 3] for i in range((len(modules) + 3 - 1) // 3)
    ]

    round_num = len(modules) / 3
    calc = len(modules) - round(round_num)
    if calc == 1:
        pairs.append((modules[-1], ))
    elif calc == 2:
        pairs.append((modules[-1], ))

    max_num_pages = ceil(len(pairs) / 10)
    modulo_page = page_n % max_num_pages

    # can only have a certain amount of buttons side by side
    if len(pairs) > 8:
        pairs = pairs[modulo_page * 8:8 * (modulo_page + 1)] + [
            (EqInlineKeyboardButton("<", callback_data="{}_prev({})".format(prefix, modulo_page)),
             EqInlineKeyboardButton("Back", url="https://t.me/@{BOT_USERNAME}?start="),
             EqInlineKeyboardButton(">", callback_data="{}_next({})".format(prefix, modulo_page)))]

    else:
        pairs += [[EqInlineKeyboardButton("Back", callback_data="saitama_back")]]

    return pairs

