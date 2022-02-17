import html
from typing import Optional

from telegram import Chat, Message, User, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters, CallbackContext
from telegram.utils.helpers import mention_html

from Flare_Robot import dispatcher, LOGGER
from Flare_Robot.modules.disable import DisableAbleCommandHandler
from Flare_Robot.modules.helper_funcs.admin_rights import user_can_ban
from Flare_Robot.modules.helper_funcs.alternate import typing_action
from Flare_Robot.modules.helper_funcs.chat_status import (
    bot_admin,
    user_admin,
    is_user_ban_protected,
    can_restrict,
    is_user_admin,
    is_user_in_chat,
    can_delete,
)
from Flare_Robot.modules.helper_funcs.extraction import extract_user_and_text
from Flare_Robot.modules.helper_funcs.string_handling import extract_time
from Flare_Robot.log_channel import loggable


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot = context.bot
    args = context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Dude at least refer some user to ban!")
        return log_message
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("Can't seem to find this person.")
        return log_message
    if user_id == bot.id:
        message.reply_text("Oh yeah, ban myself, noob!")
        return log_message

    if is_user_ban_protected(chat, user_id, member) and user not in DEV_USERS:
        if user_id == OWNER_ID:
            message.reply_text("Trying to put me against a Master huh?")
        elif user_id in DEV_USERS:
            message.reply_text("I can't act against our own.")
        elif user_id in DRAGONS:
            message.reply_text(
                "Fighting this Bersekser here will put user lives at risk."
            )
        elif user_id in DEMONS:
            message.reply_text(
                "Bring an order from Master Servant to fight a Assasin servant."
            )
        elif user_id in TIGERS:
            message.reply_text(
                "Bring an order from Master Servant to fight a Lancer servant."
            )
        elif user_id in WOLVES:
            message.reply_text("Rider abilities make them ban immune!")
        else:
            message.reply_text("This user has immunity and cannot be banned.")
        return log_message
    if message.text.startswith("/s"):
        silent = True
        if not can_delete(chat, context.bot.id):
            return ""
    else:
        silent = False
    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#{'S' if silent else ''}BANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.ban_member(user_id)

        if silent:
            if message.reply_to_message:
                message.reply_to_message.delete()
            message.delete()
            return log

        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        reply = (
            f"<code>❕</code><b>Ban Event</b>\n"
            f"<code> </code><b>• User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            reply += f"\n<code> </code><b>• Reason:</b> \n{html.escape(reason)}"

        bot.sendMessage(
            chat.id,
            reply,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Unban", callback_data=f"unbanb_unban={user_id}"
                        ),
                        InlineKeyboardButton(text="Delete", callback_data="unbanb_del"),
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            if silent:
                return log
            message.reply_text("Banned!", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR banning user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Uhm...that didn't work...")

    return log_message


@bot_admin
@can_restrict
@user_admin
@loggable
@typing_action
def kick(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    if user_can_ban(chat, user, bot.id) is False:
        message.reply_text("You don't have enough rights to kick users!")
        return ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Dude! at least refer some user to kick...")
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise

        message.reply_text("I can't seem to find this user")
        return ""
    if is_user_ban_protected(chat, user_id):
        message.reply_text("Yeahh... let's start kicking admins?")
        return ""

    if user_id == context.bot.id:
        message.reply_text("Yeahhh I'm not gonna do that")
        return ""

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        # context.bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        context.bot.sendMessage(
            chat.id,
            "Untill we meet again {}!.".format(
                mention_html(member.user.id, member.user.first_name)
            ),
            parse_mode=ParseMode.HTML,
        )
        log = (
            "<b>{}:</b>"
            "\n#KICKED"
            "\n<b>Admin:</b> {}"
            "\n<b>User:</b> {} (<code>{}</code>)".format(
                html.escape(chat.title),
                mention_html(user.id, user.first_name),
                mention_html(member.user.id, member.user.first_name),
                member.user.id,
            )
        )
        if reason:
            log += "\n<b>Reason:</b> {}".format(reason)

        return log
    message.reply_text("Get Out!.")

    return ""


@bot_admin
@can_restrict
@loggable
@typing_action
def banme(update: Update, _: CallbackContext):
    user_id = update.effective_message.from_user.id
    chat = update.effective_chat
    user = update.effective_user
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("Yeahhh.. not gonna ban an admin.")
        return

    res = update.effective_chat.ban_member(user_id)
    if res:
        update.effective_message.reply_text("Yes, you're right! GTFO..")
        return (
            "<b>{}:</b>"
            "\n#BANME"
            "\n<b>User:</b> {}"
            "\n<b>ID:</b> <code>{}</code>".format(
                html.escape(chat.title),
                mention_html(user.id, user.first_name),
                user_id,
            )
        )
    update.effective_message.reply_text("Huh? I can't :/")


@bot_admin
@can_restrict
@typing_action
def kickme(update: Update, _: CallbackContext):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("Yeahhh.. not gonna kick an admin.")
        return

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text("Yeah, you're right Get Out!..")
    else:
        update.effective_message.reply_text("Huh? I can't :/")


@bot_admin
@can_restrict
@user_admin
@loggable
@typing_action
def unban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message  # type: Optional[Message]
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]

    if message.reply_to_message and message.reply_to_message.sender_chat:
        r = bot.unban_chat_sender_chat(
            chat_id=chat.id, sender_chat_id=message.reply_to_message.sender_chat.id
        )
        if r:
            message.reply_text(
                f"Unbanned channel <b>{html.escape(message.reply_to_message.sender_chat.title)}</b> "
                f"from <b>{html.escape(chat.title)}</b>\n\n💡 Now this users can send the messages "
                f"with they channel again",
                parse_mode=ParseMode.HTML,
            )
        else:
            message.reply_text("Failed to unban channel")
        return
    if user_can_ban(chat, user, context.bot.id) is False:
        message.reply_text("You don't have enough rights to unban people here!")
        return ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise

        message.reply_text("I can't seem to find this user")
        return ""
    if user_id == context.bot.id:
        message.reply_text("How would I unban myself if I wasn't here...?")
        return ""

    if is_user_in_chat(chat, user_id):
        message.reply_text(
            "Why are you trying to unban someone who's already in this chat?"
        )
        return ""

    chat.unban_member(user_id)
    message.reply_text("Done, they can join again!")

    log = (
        "<b>{}:</b>"
        "\n#UNBANNED"
        "\n<b>Admin:</b> {}"
        "\n<b>User:</b> {} (<code>{}</code>)".format(
            html.escape(chat.title),
            mention_html(user.id, user.first_name),
            mention_html(member.user.id, member.user.first_name),
            member.user.id,
        )
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    return log


__help__ = """
Some people need to be publicly banned; spammers, annoyances, or just trolls.
This module allows you to do that easily, by exposing some common actions, so everyone will see!
× /kickme: Kicks the user who issued the command.
× /banme: Bans the user who issued the command.
*Admin only:*
× /ban `<userhandle>`: Bans a user. (via handle, or reply).
× /sban `<userhandle>`: Silently ban a user. Deletes command, Replied message and doesn't reply. (via handle, or reply).
× /dban: Bans a user and delete the message. (via handle, or reply).
× /tban `<userhandle> x(m/h/d)`: Bans a user for x time. (via handle, or reply). m = minutes, h = hours, d = days.
× /unban `<userhandle>`: Unbans a user. (via handle, or reply).
× /kick `<userhandle>`: Kicks a user, (via handle, or reply).
An example of temporarily banning someone:
`/tban @username 2h`; this bans a user for 2 hours.
"""

__mod_name__ = "Bans"

BAN_HANDLER = CommandHandler(
    ["ban", "dban", "sban"],
    ban,
    pass_args=True,
    filters=Filters.chat_type.groups,
    run_async=True,
)
TEMPBAN_HANDLER = CommandHandler(
    ["tban", "tempban"],
    temp_ban,
    pass_args=True,
    filters=Filters.chat_type.groups,
    run_async=True,
)
KICK_HANDLER = CommandHandler(
    "kick", kick, pass_args=True, filters=Filters.chat_type.groups, run_async=True
)
UNBAN_HANDLER = CommandHandler(
    "unban", unban, pass_args=True, filters=Filters.chat_type.groups, run_async=True
)
KICKME_HANDLER = DisableAbleCommandHandler(
    "kickme", kickme, filters=Filters.chat_type.groups, run_async=True
)
BANME_HANDLER = DisableAbleCommandHandler(
    "banme", banme, filters=Filters.chat_type.groups, run_async=True
)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(KICK_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(KICKME_HANDLER)
dispatcher.add_handler(BANME_HANDLER)
