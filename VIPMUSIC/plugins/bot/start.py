import asyncio
import random
import re
import time
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from VIPMUSIC import app
from VIPMUSIC.misc import _boot_
from VIPMUSIC.plugins.sudo.sudoers import sudoers_list
from VIPMUSIC.utils import bot_up_time
from VIPMUSIC.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
    get_assistant,
)
from VIPMUSIC.utils.decorators.language import LanguageStart
from VIPMUSIC.utils.formatters import get_readable_time
from VIPMUSIC.utils.inline import first_page, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

# --- FIX for UnicodeEncodeError ---
_surrogate_re = re.compile(r'[\ud800-\udfff]')

def clean_surrogates(text):
    """Removes broken surrogate unicode characters that crash Telegram API"""
    if not isinstance(text, str):
        text = str(text)
    return _surrogate_re.sub('', text)


# --- Monkey patch Pyrogram to auto-clean captions ---
from pyrogram.types import Message

old_reply_photo = Message.reply_photo
async def safe_reply_photo(self, *args, **kwargs):
    if "caption" in kwargs:
        kwargs["caption"] = clean_surrogates(kwargs["caption"])
    return await old_reply_photo(self, *args, **kwargs)

Message.reply_photo = safe_reply_photo
# -----------------------------------

user_last_message_time = {}
user_command_count = {}
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5

YUMI_PICS = [
    "https://graph.org/file/f21bcb4b8b9c421409b64.png",
    "https://graph.org/file/f21bcb4b8b9c421409b64.png",
    "https://graph.org/file/f21bcb4b8b9c421409b64.png",
]


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    user_id = message.from_user.id
    current_time = time.time()

    last_message_time = user_last_message_time.get(user_id, 0)

    if current_time - last_message_time < SPAM_WINDOW_SECONDS:
        user_last_message_time[user_id] = current_time
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            hu = await message.reply_text(
                f"**{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴᴛ sᴘᴀᴍ, ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 sᴇᴄ**"
            )
            await asyncio.sleep(3)
            await hu.delete()
            return
    else:
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time

    await add_served_user(user_id)

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name.startswith("help"):
            keyboard = first_page(_)
            return await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=clean_surrogates(_["help_1"].format(config.SUPPORT_CHAT)),
                reply_markup=keyboard,
            )

        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=clean_surrogates(
                        f"{message.from_user.mention} started bot to check <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n"
                        f"<b>ᴜsᴇʀ ɪᴅ :</b> <code>{user_id}</code>\n"
                        f"<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}"
                    ),
                )
            return

        if name.startswith("inf"):
            m = await message.reply_text("🔎")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = clean_surrogates(
                _["start_6"].format(title, duration, views, published, channellink, channel, app.mention)
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="💕 𝐕𖽹𖽴𖽞𖽙 🦋", callback_data=f"downloadvideo {query}"),
                        InlineKeyboardButton(text="💕 𝐀𖽪𖽴𖽹𖽙 🦋", callback_data=f"downloadaudio {query}"),
                    ],
                    [InlineKeyboardButton(text="🎧 sᴇᴇ ᴏɴ ʏᴏᴜᴛᴜʙᴇ 🎧", url=link)],
                ]
            )
            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
            if await is_on_off(2):
                await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=clean_surrogates(
                        f"{message.from_user.mention} checked <b>ᴛʀᴀᴄᴋ ɪɴғᴏ</b>.\n\n"
                        f"<b>ᴜsᴇʀ ɪᴅ :</b> <code>{user_id}</code>\n"
                        f"<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}"
                    ),
                )
    else:
        out = private_panel(_)
        caption = clean_surrogates(_["start_2"].format(message.from_user.mention, app.mention))
        await message.reply_photo(
            photo=config.START_IMG_URL,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(out),
        )
        if await is_on_off(2):
            await app.send_message(
                chat_id=config.LOGGER_ID,
                text=clean_surrogates(
                    f"{message.from_user.mention} started the bot.\n\n"
                    f"<b>ᴜsᴇʀ ɪᴅ :</b> <code>{user_id}</code>\n"
                    f"<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}"
                ),
            )


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    user_id = message.from_user.id
    current_time = time.time()

    last_message_time = user_last_message_time.get(user_id, 0)
    if current_time - last_message_time < SPAM_WINDOW_SECONDS:
        user_last_message_time[user_id] = current_time
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            hu = await message.reply_text(
                f"**{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴᴛ sᴘᴀᴍ, ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 sᴇᴄ**"
            )
            await asyncio.sleep(3)
            await hu.delete()
            return
    else:
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time

    out = start_panel(_)
    BOT_UP = await bot_up_time()
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=clean_surrogates(_["start_1"].format(app.mention, BOT_UP)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    await add_served_chat(message.chat.id)

    try:
        userbot = await get_assistant(message.chat.id)
        checking = await message.reply_text(
            f"**Checking [Assistant](tg://openmessage?user_id={userbot.id}) availability...**"
        )
        is_userbot = await app.get_chat_member(message.chat.id, userbot.id)
        if is_userbot:
            await checking.edit_text(
                f"**[Assistant](tg://openmessage?user_id={userbot.id}) is active here! You can play music.**"
            )
    except Exception:
        try:
            await checking.edit_text(
                f"**Inviting [Assistant](tg://openmessage?user_id={userbot.id})...**"
            )
            invitelink = await app.export_chat_invite_link(message.chat.id)
            await asyncio.sleep(1)
            await userbot.join_chat(invitelink)
            await checking.edit_text(
                f"**[Assistant](tg://openmessage?user_id={userbot.id}) joined the chat successfully!**"
            )
        except Exception:
            await checking.edit_text(
                f"**Make me admin with invite permissions to add my [Assistant](tg://openmessage?user_id={userbot.id}).**"
            )


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except Exception as e:
                    print(e)
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    await app.leave_chat(message.chat.id)
                    return
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        clean_surrogates(
                            _["start_5"].format(
                                app.mention,
                                f"https://t.me/{app.username}?start=sudolist",
                                config.SUPPORT_CHAT,
                            )
                        ),
                        disable_web_page_preview=True,
                    )
                    await app.leave_chat(message.chat.id)
                    return

                out = start_panel(_)
                chid = message.chat.id
                try:
                    userbot = await get_assistant(chid)
                    if message.chat.username:
                        await userbot.join_chat(f"{message.chat.username}")
                        await message.reply_text(
                            f"**My [Assistant](tg://openmessage?user_id={userbot.id}) joined via username.**"
                        )
                    else:
                        invitelink = await app.export_chat_invite_link(chid)
                        msg = await message.reply_text(
                            f"**Joining my [Assistant](tg://openmessage?user_id={userbot.id}) via invite link...**"
                        )
                        await userbot.join_chat(invitelink)
                        await msg.delete()
                        await message.reply_text(
                            f"**My [Assistant](tg://openmessage?user_id={userbot.id}) joined successfully.**"
                        )
                except Exception:
                    await message.reply_text(
                        f"**Make me admin to invite my [Assistant](tg://openmessage?user_id={userbot.id}).**"
                    )

                await message.reply_photo(
                    random.choice(YUMI_PICS),
                    caption=clean_surrogates(
                        _["start_3"].format(
                            message.from_user.first_name,
                            app.mention,
                            message.chat.title,
                            app.mention,
                        )
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex)
