
from pyrogram import Client, filters
import requests
import random
import os
import re
import asyncio
import time
from VIPMUSIC import app
from time import time
import asyncio
from VIPMUSIC.utils.extraction import extract_user

# Define a dictionary to track the last message timestamp for each user
user_last_message_time = {}
user_command_count = {}
# Define the threshold for command spamming (e.g., 20 commands within 60 seconds)
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5

from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

SHAYRI = [ "ɪᴄʜɪ ᴛʜᴀ ɪᴛᴄʜɪᴛʜᴀ.. ᴇɴ ᴋɴɴᴀᴛʜᴜʟᴀ ɪᴛᴛᴄʜɪ ᴛʜᴀᴀ💕🙈",
          "ᴋᴏɴᴊᴀᴍ ᴜᴛᴛʜᴜ ᴘᴀᴀᴛʜᴀʟᴇ ᴄʜᴇʟʟᴀᴛᴛʜᴜᴋᴋᴜ ᴍᴀɴᴅᴀɪᴋᴜʟᴀ ᴋᴏɴᴊᴀᴍ ᴋɪʀᴜᴋᴜ ᴘᴜᴅɪᴠʜɪᴅᴜᴍ🤭🤭",
          "ᴋᴀᴅʜᴀʟ ꜱᴀᴅᴜɢᴜᴅᴜ.. ᴋᴀɴɴᴇ ᴛʜᴏᴅᴜᴛʜᴏᴅᴜ🙈👀",
          "ᴇᴛʜᴜᴋᴜ ᴘᴏɴᴅᴀᴛɪ ᴇɴɴᴀ ꜱᴜᴛᴛʜɪ ᴠᴀᴘᴘᴀᴛɪ🥳🥳",
          "ᴍᴀɴᴄʜᴀ ᴍᴀᴄʜᴀ ᴜɴ ᴍᴇʟᴀ ᴀꜱʜᴀ ᴠᴀᴄʜᴀ🙈🙈💕",
          "ɢᴀɴᴛʜᴀ ᴋᴀɴɴᴀʟᴀɢᴀ 👀",
          "ᴍᴀʟᴀʏᴀᴀɪ ᴇʟᴜɴᴛʜᴇɴ ɴᴀᴀɴ ɪᴘᴘᴏᴢɢᴜᴛʜᴜ🙈.. ᴍᴀɴᴀʟᴀᴀɪ ᴠɪʟᴜɴᴛʜᴀɪ ɴᴇᴇ ɪᴘᴘᴏᴢʜᴜᴛʜᴜ 🤩🤩",
          "ᴀʟᴀɢᴇ ᴜɴᴀᴛʜᴜ 🙈🙈ᴘᴀᴀʀᴛʜᴇɴ ᴀᴅᴀᴅᴀ 👀👀",
          "ᴜɴᴀᴋᴋᴜʟ ɴᴀᴀɴᴇ ᴜʀᴜɢᴜᴍ ɪʀᴀᴠɪʟ ❤️ ɴᴀᴀɴ ꜱᴏʟᴀᴠᴀ💕💕",
          "ꜱᴀɪᴠᴀ ᴍᴜᴛᴛʜᴀᴍ💋 ᴋᴏᴅᴜᴛᴛʜᴀ ᴏᴛᴛʀᴜ ᴘᴏɢᴀ ᴍᴀᴛᴛᴇɴ.. ꜱᴀɢᴀꜱᴀᴛᴛʜᴀ ᴋᴀᴀᴛᴜ 🙈 ꜱᴇᴛᴛʜᴜ ᴘᴏᴠᴀ ᴍᴀᴛᴇɴ",
          "ꜱɴᴇɢɪᴛʜᴀɴᴇ ꜱɴᴇɢɪᴛʜᴀɴᴇ.. ʀᴀɢᴀꜱɪʏᴀ ꜱɴᴇɢɪᴛʜᴀɴᴇ🙈",
          "ɴᴇᴇ ᴋᴜʟɪᴋᴋᴀʏɪʟ ɴᴀɴᴜᴍ ᴋᴏɴᴊᴀᴍ ɴᴀɴᴀɪᴠᴇɴ 🌚🌝",
          "ᴜɴɴᴀɪ ᴀʟʟɪ ᴇᴅᴜᴛᴛʜᴜ.. ᴜʟʟᴀɴɢᴀʏɪʟ ᴍᴜᴅɪᴛʜᴜ.. ᴋᴀɪᴋᴜᴛᴛᴀʏɪʟ 💕🙈",
          "ᴍᴜɴ ɢᴏʙᴜʀᴀ ᴀᴢʜᴀɢᴀɪ ᴜɴ ᴅʜᴀᴠᴀɴɪ ᴍᴏᴏᴅɪᴛᴀᴛʜᴇ 👀 ᴀɴᴛʜᴀ ʀᴀɢᴀꜱɪʏᴀᴛᴛʜᴀɪ ᴍᴀᴢʜᴀɪᴛʜᴜʟɪ 🙈🙈 ᴀᴀᴋᴋɪʏᴀᴛʜᴇ",
          "ɴᴇɴᴊᴀᴍʙᴀʟᴀᴍ ᴘᴀʟᴜᴛᴛʜᴀᴄʜᴜ ᴀɴɪʟ ᴋɪᴛᴛᴀ ᴋᴏᴅᴜᴛᴛʜᴀᴄʜᴜ👀 ᴀɴɪʟ ɪᴘᴘᴏ ᴛʜᴜᴋᴋɪ ᴋᴜᴛʜɪᴋᴋᴀʟᴀᴍ ✨ ᴘᴀʟʟᴜᴍ ᴘᴀᴛʜɪᴋᴋᴀʟᴀᴍ 🤭",
          "ᴘᴇɴɴᴜʟᴋᴋᴜʟ ɪᴛᴛʜᴀɴᴀɪ ꜱᴜɢᴀᴍᴀ ᴀɴᴛʜᴀ ʙʀᴀᴍᴍᴀɴɪɴ ᴛʜɪʀᴀᴍ ᴠᴀᴀᴢʜɢᴀ✨ ᴇɴᴀᴋᴋᴜʟ ᴛʜᴏᴏɴɢɪʏᴀ ꜱᴜɢᴀᴛᴛʜᴀɪ ɪɴᴅʀᴜ ᴇᴢʜᴜᴘᴘɪʏᴀ ᴠɪʀᴀʟ ᴠᴀᴀᴢʜɢᴀ🥵",
          "ᴅᴇᴇᴘᴀɴɢᴀʟ ᴀɴᴀɪᴘᴘᴀʏʜᴇ 🕯️ ᴘᴜᴛʜɪʏᴀ ᴘᴏʀᴜʟ ɴᴀᴀᴍ ᴛʜᴇᴅᴀᴛᴛʜᴀɴ",
          "ᴠɪᴅᴀᴠᴇɴᴅᴜᴍ ᴀᴄʜᴀᴛᴛʜᴀɪ 🫶🏻 ᴛʜᴏᴅᴀᴠᴇɴᴅᴜᴍ ᴜᴛᴄʜᴀᴛᴛʜᴀɪ 😝 ᴀᴛʜɪɢᴀʟᴀɪ ꜱᴇʟᴀɪ ꜱᴏʟʟᴜᴍᴀᴅɪ ᴍɪᴛᴄʜᴀʏᴛʜᴀɪ 🙈",
          "ᴛʜᴇʀɪɴᴛʜᴀ ʙᴀᴀɢᴀɴɢᴀʟ ᴜʏɪʀᴀɪ ᴛʜᴀɴᴛʜɪᴅᴀ 👀ᴍᴀʀᴀɪɴᴛʜᴀ ʙᴀᴀɢᴀɴɢᴀʟ ᴜʏɪʀᴀɪ ᴠᴀᴀɴɢɪᴅᴀ 😍",
          "ɴᴀᴀ ᴠᴀʏᴀꜱᴜᴋᴋᴜ ᴠᴀɴᴛʜᴀ ᴠᴀʏᴀʟɪɴᴀꜱᴀ 🙈 ᴇɴɴᴀ ᴍɪɴᴏʀ ᴜʜ ᴘᴏʟᴀ ᴠᴀᴀꜱɪʏᴀᴅᴀ 💋",
          "ᴄʜʟᴏ ᴜɴ ᴋᴀᴅɪᴛʜᴀᴛᴛʜᴀɪ ᴘᴏᴏᴠᴀʟᴇ ᴛʜɪʀᴀᴋᴋɪɴᴅʀᴇɴ 😍 ᴠɪʀᴀʟᴘᴀᴛᴛᴀʟ ᴜɴᴛʜᴀɴ ᴊᴇᴇᴠᴀɴ ᴋᴀᴀʏᴀᴍ ᴘᴀᴅᴜᴍᴀɴᴅʀᴏ ✨💕",
          "ᴋᴀɴɴᴇ ᴜɴ ᴋᴀᴀʟ ᴋᴏᴢʜᴜꜱɪʟ ᴍᴀɴɪʏᴀᴀɢᴀ ᴍᴀᴛʀᴇɴᴀ.. ᴍᴀɴᴊᴀᴛᴛʜɪʟ🤔 ᴜʀᴀɴɢᴜᴍʙᴏᴛʜᴜ ꜱɪɴᴜɴɢᴀ ᴍᴀᴛᴇɴᴀ 😍🙈",
          "ᴛʜᴀᴘᴘᴜꜱᴇᴜʏᴀ ᴘᴀᴀʀᴛʜᴀʟ ᴏᴛʀᴜᴋᴏʟᴠᴀᴀʏᴀ 👀 ᴍᴇʟᴀᴀᴅᴀɪ ɴᴇᴇɴɢᴜᴍʙᴏᴛʜᴜ ᴠᴇᴋᴋᴀᴍ ᴇɴɴᴀ ᴍᴜɴᴛʜᴀᴀɴᴀʏᴀᴀʟ ❤️🫶🏻🦋",
          "ꜱᴏᴋᴋɪ ᴛʜᴀᴀɴᴇ ᴘᴏɢɪʀᴇɴ ᴍᴀᴍᴀɴ ᴋᴏɴᴊᴀ ɴᴀᴀʟᴀ",
          "ᴇᴢʜᴜ ᴋᴀᴅᴀʟ ᴛʜᴀᴀɴᴅɪᴛʜᴀᴀɴ ᴇᴢʜᴜ ᴍᴀʟᴀɪ ᴛʜᴀᴀɴᴅɪᴛʜᴀᴀɴ🫶🏻 ᴍᴀᴄʜᴀɴ ᴋɪᴛᴛᴀ ᴏᴅɪ ᴠᴀʀᴜᴍ ᴍᴀɴᴀꜱᴜ ❤️",
          "ᴋᴏᴏʀᴀᴘᴀᴛᴛᴜ ꜱᴇʟᴀ ᴛʜᴀɴ ᴠᴀɴɢᴀ ꜱᴏʟɪ ᴋᴇᴋᴋᴜʀᴇɴ 🙈 ᴋᴏᴏᴅᴜᴠɪᴛᴛᴜ ᴋᴏᴏᴅᴜᴘᴀᴀʏᴜᴍ ᴋᴀᴅʜᴀʟᴀᴀʟᴀ ꜱᴜᴛᴛʜᴜʀᴇɴ 🫶🏻",
          "ᴋᴀɴɴɪʟᴇ ᴋᴀʟᴍɪꜱʜᴀᴍ 👀 ᴘᴏᴛʜᴜᴍᴇ ꜱɪʟᴍɪꜱʜᴀᴍ 🙈 ꜱᴘᴀʀɪꜱʜᴀᴍᴏ ᴛʜᴜʟɪ ᴠɪꜱᴀᴍ 🤩",
          " ᴜᴅᴀʟ ᴠᴀᴢʜɪ ᴀᴍɪʀᴛʜᴀᴍ ᴠᴀᴢʜɪɢɪɴᴅʀᴀᴛʜᴏ 🥵  ᴜʏɪʀ ᴍᴀᴛᴛᴜᴍ ᴘᴜᴛʜᴜᴠɪᴛʜᴀ ᴠᴀᴢʜɪ ᴋᴀɴᴅᴀᴛʜᴏ 👀",
          "ᴍᴜᴛᴛʜᴀᴍᴛʜɪɴʙᴀᴠᴀᴍ 💋 ᴍᴜʀᴀᴛᴛᴜ ᴘᴏᴏ ɪᴠᴀʟ 🥵 ᴅʜɪɴᴀᴍᴜᴍ ᴛʜᴏʀᴘᴀᴠᴀᴍ ✨ ᴀɴᴛʜᴀ ᴀᴀᴅᴀɪ ꜱᴀɴᴅᴀʏɪʟ 🌚",
          "ɢᴀɴᴅʜᴀ ᴋᴀɴɴᴀʟᴀɢɪ👀ᴛᴀᴋᴋᴜɴᴜᴛʜᴀ ᴛᴀᴛᴛɪ ᴛʜᴜᴋᴋᴜᴍ ᴍᴜᴛᴛʜᴜ ᴘᴀʟʟᴀʟᴀɢɪ 🌝 ᴍᴜᴛᴛʜᴀᴍ ᴏɴɴᴜ ᴛʜᴀᴅɪ 💋",
          "ᴊɪʟʟᴜ ᴊɪʟʟᴜ ᴊɪɢᴀʀᴜᴅᴀɴᴅᴀ ᴋɪᴛᴛᴀᴠᴀᴅɪ 🙈 ᴜɴɴᴀ ᴀᴘᴘᴅɪʏᴇ ꜱᴀᴘᴘɪᴅᴜᴠᴇɴ ɢᴇᴛᴛʜᴀ ᴛʜᴀᴀɴᴅɪ 🥳", ]

# Command
SHAYRI_COMMAND = ["lifeline", "lovebeats", "heartbeat"]

@app.on_message(
    filters.command(SHAYRI_COMMAND)
    & filters.group
    )
async def help(client: Client, message: Message):
    await message.reply_text(
        text = random.choice(SHAYRI),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "💕 𝐍𖽞𖾓𖾟𖽙𖾖ᴋ 🦋", url=f"https://t.me/HeartBeat_Offi"),
                    InlineKeyboardButton(
                        "💕 𝐎𖾟𖽡𖽞𖾖 🦋", url=f"https://t.me/HeartBeat_Muzic")
                    
                ]
            ]
        ),
    )

@app.on_message(
    filters.command(SHAYRI_COMMAND)
    & filters.private
    )
async def help(client: Client, message: Message):
    await message.reply_text(
        text = random.choice(SHAYRI),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                         "💕 𝐍𖽞𖾓𖾟𖽙𖾖ᴋ 🦋", url=f"https://t.me/HeartBeat_Offi"),
                    InlineKeyboardButton(
                        "💕 𝐎𖾟𖽡𖽞𖾖 🦋", url=f"https://t.me/HeartBeat_Muzic")
                    
                ]
            ]
        ),
    )
