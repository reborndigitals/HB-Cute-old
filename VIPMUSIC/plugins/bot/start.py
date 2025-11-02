import time
from time import time
import asyncio
import random
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
import config
from config import BANNED_USERS, GREET, MENTION_USERNAMES, START_REACTIONS, YUMI_PICS
from VIPMUSIC import app
from VIPMUSIC.misc import _boot_
from VIPMUSIC.utils import bot_up_time
from VIPMUSIC.plugins.sudo.sudoers import sudoers_list
from VIPMUSIC.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from VIPMUSIC.utils.decorators.language import LanguageStart
from VIPMUSIC.utils.formatters import get_readable_time
from VIPMUSIC.utils.inline import first_page, private_panel, start_panel
from VIPMUSIC.utils.database import get_assistant
from VIPMUSIC.utils.extraction import extract_user
from strings import get_string

# 🚫 Anti-spam system
user_last_message_time = {}
user_command_count = {}
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5


# ===================== /start in private =====================
@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message,_):
    print("DEBUG types:", type(_), type(_["start_1"]) if isinstance(_, dict) and "start_1" in _ else "no key")
    _ = await get_lang(message.chat.id)
     # ✅ FIX: Make sure _ is always a dict
    if not isinstance(_, dict):
        _ = {}
        
    user_id = message.from_user.id
    current_time = time()

    # Anti-spam check
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

    await add_served_user(message.from_user.id)

    # Handle special start params
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        # Help page
        if name.startswith("help"):
            keyboard = first_page(_)
            return await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )

        # Sudo list
        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} checked sudo list.\n\n<b>User ID:</b> <code>{message.from_user.id}</code>",
                )
            return

        # Info fetcher
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

            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
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
                chat_id=message.chat.id, photo=thumbnail, caption=searched_text, reply_markup=key
            )
            return

    # ===== NORMAL /START WITH ANIMATIONS =====
    else:
        try:
            out = private_panel(_)

            # Step 1: Greet with random emoji
            loading_1 = await message.reply_text(random.choice(GREET))
            await asyncio.sleep(1)
            await loading_1.delete()

            # Step 2: Ding Dong animation
            vip = await message.reply_text("**ᴅιиg ᴅσиg ꨄ︎❣️.....**")
            for dots in [".❣️....", "..❣️...", "...❣️..", "....❣️.", ".....❣️"]:
                await vip.edit_text(f"**ᴅιиg ᴅσиg ꨄ︎{dots}**")
            await asyncio.sleep(0.5)
            await vip.delete()

            # Step 3: Starting animation
            vips = await message.reply_text("**⚡ѕ**")
            steps = ["⚡ѕт", "⚡ѕтα", "⚡ѕтαя", "⚡ѕтαят", "⚡ѕтαятι", "⚡ѕтαятιи", "⚡ѕтαятιиg"]
            for step in steps:
                await vips.edit_text(f"**{step}**")
                await asyncio.sleep(0.1)
            for _ in range(2):
                await vips.edit_text("**⚡ѕтαятιиg....**")
                await asyncio.sleep(0.2)
                await vips.edit_text("**⚡ѕтαятιиg.**")
                await asyncio.sleep(0.2)
            await vips.delete()

            # Step 4: Normal start panel
            await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["start_2"].format(str(message.from_user.id)),#.format(message.from_user.mention, app.mention),
                reply_markup=InlineKeyboardMarkup(out),
            )

            if await is_on_off(2):
                await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} started the bot.\n\n<b>ID:</b> <code>{message.from_user.id}</code>",
                )

        except Exception as e:
            print(e)


# ===================== /start in groups =====================
@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    user_id = message.from_user.id
    current_time = time()
    last_message_time = user_last_message_time.get(user_id, 0)

    # Anti-spam
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
        caption=_["start_2"].format(app.mention, BOT_UP),
        reply_markup=InlineKeyboardMarkup(out),
    )
    await add_served_chat(message.chat.id)

    # Assistant check
    try:
        userbot = await get_assistant(message.chat.id)
        msg = await message.reply_text(
            f"**ᴄʜᴇᴄᴋɪɴɢ [ᴀssɪsᴛᴀɴᴛ](tg://openmessage?user_id={userbot.id}) ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ...**"
        )
        is_userbot = await app.get_chat_member(message.chat.id, userbot.id)
        if is_userbot:
            await msg.edit_text(
                f"**[ᴀssɪsᴛᴀɴᴛ](tg://openmessage?user_id={userbot.id}) ᴀʟʀᴇᴀᴅʏ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.**"
            )
    except Exception:
        try:
            await msg.edit_text(
                f"**[ᴀssɪsᴛᴀɴᴛ](tg://openmessage?user_id={userbot.id}) ɴᴏᴛ ɪɴ ɢʀᴏᴜᴘ, ɪɴᴠɪᴛɪɴɢ...**"
            )
            invitelink = await app.export_chat_invite_link(message.chat.id)
            await asyncio.sleep(1)
            await userbot.join_chat(invitelink)
            await msg.edit_text(
                f"**[ᴀssɪsᴛᴀɴᴛ](tg://openmessage?user_id={userbot.id}) ɴᴏᴡ ᴀᴄᴛɪᴠᴇ.**"
            )
        except Exception:
            await msg.edit_text(
                f"**ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ᴡɪᴛʜ ɪɴᴠɪᴛᴇ ᴜsᴇʀ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴀᴅᴅ [ᴀssɪsᴛᴀɴᴛ](tg://openmessage?user_id={userbot.id}).**"
            )


# ===================== Welcome new members =====================
@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except Exception:
                    pass

            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    await app.leave_chat(message.chat.id)
                    return
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    await app.leave_chat(message.chat.id)
                    return

                out = start_panel(_)
                try:
                    userbot = await get_assistant(message.chat.id)
                    if message.chat.username:
                        await userbot.join_chat(f"{message.chat.username}")
                    else:
                        invitelink = await app.export_chat_invite_link(message.chat.id)
                        await asyncio.sleep(1)
                        await userbot.join_chat(invitelink)
                except Exception:
                    pass

                await message.reply_photo(
                    random.choice(YUMI_PICS),
                    caption=_["start_3"].format(
                        message.from_user.first_name,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception:
            pass


# ===================== Mention Reaction (Both Private & Groups) =====================
@app.on_message(filters.text & ~BANNED_USERS)
async def react_on_mentions(client, message: Message):
    text = message.text.lower()
    if any(name.lower() in text for name in MENTION_USERNAMES):
        try:
            emoji = random.choice(START_REACTIONS)
            await message.react(emoji)
        except Exception:
            pass
