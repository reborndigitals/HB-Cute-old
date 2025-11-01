# start.py — robust surrogate-safe version
import asyncio
import random
import re
import time
from pyrogram import filters, Client
from pyrogram.enums import ChatType
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
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

# -------------------- Unicode cleaning helpers --------------------
# Remove UTF-16 surrogate codepoints U+D800 - U+DFFF which cause
# "surrogates not allowed" when Pyrogram/TG encodes strings.
_surrogate_re = re.compile(r'[\ud800-\udfff]')

def clean_surrogates(text):
    """Remove broken surrogate unicode characters from text (and ensure str)."""
    if text is None:
        return text
    if not isinstance(text, str):
        text = str(text)
    # remove surrogate codepoints
    return _surrogate_re.sub('', text)

def sanitize_button(button: InlineKeyboardButton) -> InlineKeyboardButton:
    """
    Return a new InlineKeyboardButton with all string fields sanitized.
    We sanitize: text, url, callback_data, switch_inline_query, switch_inline_query_current_chat,
                   callback_game (ignored), pay (boolean), etc.
    Only relevant string fields are cleaned.
    """
    # Extract attributes and clean strings where appropriate
    text = clean_surrogates(button.text) if getattr(button, "text", None) is not None else None

    # Some constructors use different param names; prepare a dict for constructor
    params = {"text": text}

    # possible optional attributes on InlineKeyboardButton
    # we check and add them if present (cleaning strings)
    if getattr(button, "url", None) is not None:
        params["url"] = clean_surrogates(button.url)
    if getattr(button, "callback_data", None) is not None:
        params["callback_data"] = clean_surrogates(button.callback_data)
    if getattr(button, "switch_inline_query", None) is not None:
        params["switch_inline_query"] = clean_surrogates(button.switch_inline_query)
    if getattr(button, "switch_inline_query_current_chat", None) is not None:
        params["switch_inline_query_current_chat"] = clean_surrogates(button.switch_inline_query_current_chat)
    # 'pay' is a boolean flag; pass through if present
    if getattr(button, "pay", None) is not None:
        params["pay"] = button.pay

    return InlineKeyboardButton(**params)

def sanitize_markup(markup):
    """
    Return a sanitized InlineKeyboardMarkup if markup is that type,
    otherwise attempt to walk common nested structures (list of lists of buttons).
    """
    if markup is None:
        return None

    if isinstance(markup, InlineKeyboardMarkup):
        # InlineKeyboardMarkup.keyboard is list[list[InlineKeyboardButton]]
        out_rows = []
        for row in getattr(markup, "inline_keyboard", getattr(markup, "keyboard", [])):
            new_row = []
            for btn in row:
                try:
                    new_btn = sanitize_button(btn)
                except Exception:
                    # If something unexpected, fallback to creating a button with cleaned text
                    new_btn = InlineKeyboardButton(text=clean_surrogates(getattr(btn, "text", "")))
                new_row.append(new_btn)
            out_rows.append(new_row)
        return InlineKeyboardMarkup(out_rows)

    # If it's a simple python nested list of InlineKeyboardButton-like objects
    if isinstance(markup, (list, tuple)):
        out_rows = []
        for row in markup:
            new_row = []
            for btn in row:
                if isinstance(btn, InlineKeyboardButton):
                    new_row.append(sanitize_button(btn))
                elif isinstance(btn, (list, tuple)):
                    # nested (unlikely) — flatten conservatively
                    inner_text = clean_surrogates(str(btn))
                    new_row.append(InlineKeyboardButton(text=inner_text))
                else:
                    new_row.append(InlineKeyboardButton(text=clean_surrogates(str(btn))))
            out_rows.append(new_row)
        return InlineKeyboardMarkup(out_rows)

    # Unknown markup type: try string conversion
    return markup

# -------------------- Monkey-patch Pyrogram senders to auto-sanitize --------------------
# Patch Message.reply_photo and Message.reply_text, and Client.send_photo/send_message
# so any caption/text and reply_markup passed will be cleaned automatically.

# Message.reply_photo
_old_reply_photo = Message.reply_photo
async def _safe_reply_photo(self, *args, **kwargs):
    if "caption" in kwargs and kwargs["caption"] is not None:
        kwargs["caption"] = clean_surrogates(kwargs["caption"])
    if "reply_markup" in kwargs and kwargs["reply_markup"] is not None:
        kwargs["reply_markup"] = sanitize_markup(kwargs["reply_markup"])
    return await _old_reply_photo(self, *args, **kwargs)
Message.reply_photo = _safe_reply_photo

# Message.reply_text
_old_reply_text = Message.reply_text
async def _safe_reply_text(self, *args, **kwargs):
    # 'text' might be passed as first positional arg or as 'text' kw
    if args and isinstance(args[0], str):
        args = (clean_surrogates(args[0]),) + args[1:]
    if "text" in kwargs and kwargs["text"] is not None:
        kwargs["text"] = clean_surrogates(kwargs["text"])
    if "reply_markup" in kwargs and kwargs["reply_markup"] is not None:
        kwargs["reply_markup"] = sanitize_markup(kwargs["reply_markup"])
    return await _old_reply_text(self, *args, **kwargs)
Message.reply_text = _safe_reply_text

# Client.send_message
_old_send_message = Client.send_message
async def _safe_send_message(self, chat_id, text, *args, **kwargs):
    text = clean_surrogates(text) if text is not None else text
    if "reply_markup" in kwargs and kwargs["reply_markup"] is not None:
        kwargs["reply_markup"] = sanitize_markup(kwargs["reply_markup"])
    return await _old_send_message(self, chat_id, text, *args, **kwargs)
Client.send_message = _safe_send_message

# Client.send_photo
_old_send_photo = Client.send_photo
async def _safe_send_photo(self, chat_id, photo, *args, **kwargs):
    if "caption" in kwargs and kwargs["caption"] is not None:
        kwargs["caption"] = clean_surrogates(kwargs["caption"])
    if "reply_markup" in kwargs and kwargs["reply_markup"] is not None:
        kwargs["reply_markup"] = sanitize_markup(kwargs["reply_markup"])
    return await _old_send_photo(self, chat_id, photo, *args, **kwargs)
Client.send_photo = _safe_send_photo

# ------------------------------------------------------------------------------

# Spam protection
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
                reply_markup=sanitize_markup(keyboard),
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
                reply_markup=sanitize_markup(key),
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
            reply_markup=sanitize_markup(out),
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
        reply_markup=sanitize_markup(out),
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
                    print(clean_surrogates(e))
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
                    reply_markup=sanitize_markup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(clean_surrogates(ex))
