import os
import re
from platform import python_version as kontol
from telethon import events, Button
from telegram import __version__ as telever
from telethon import __version__ as tlhver
from pyrogram import __version__ as pyrover
from Flare_Robot.events import register
from Flare_Robot import telethn as tbot


PHOTO = "https://telegra.ph/file/4c228ed665f2885859c19.mp4"


@register(pattern=("/alive"))
async def awake(event):
    TEXT = "**♡ I,m ɴᴀᴛsᴜᴍᴇ ᴀ ʜᴏᴛʏ ʀᴏʙᴏᴛ 愛** \n\n"
    TEXT += f"**♡ I'm Working With sᴇxʏ Speed** \n\n"
    TEXT += f"**♡ ғʟᴀʀᴇ: LATEST Version** \n\n"
    TEXT += f"**♡ My Creator: [ADITYA](http://t.me/adimanus)** \n\n"
    TEXT += f"**♡ ᴀɴʏ ɪssᴜᴇs ᴄᴏɴᴛᴀᴄᴛ ʜᴇʀᴇ @natsumesupport** \n\n"
    TEXT += "**♡ ᴛʜᴀɴᴋ ʏᴏᴜ ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ 💘💘💘**"
    BUTTON = [
        [
            Button.url("📢 Updates", "https://t.me/natsumeupdates"),
            Button.url("🚑 Support", "https://t.me/natsumesupport}"),
        ]
    ]
    await tbot.send_file(event.chat_id, PHOTO, caption=TEXT, buttons=BUTTON)
