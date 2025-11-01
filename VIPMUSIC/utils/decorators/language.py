from VIPMUSIC.misc import SUDOERS
from VIPMUSIC.utils.database import get_lang, is_maintenance
from strings import get_string
from config import SUPPORT_CHAT
from VIPMUSIC import app


# ===================== General Language Decorator =====================
def language(mystic):
    async def wrapper(client, message, **kwargs):
        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    text=f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, "
                         f"ᴠɪsɪᴛ <a href={SUPPORT_CHAT}>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> ғᴏʀ ᴋɴᴏᴡɪɴɢ ᴛʜᴇ ʀᴇᴀsᴏɴ.",
                    disable_web_page_preview=True,
                )
        try:
            await message.delete()
        except:
            pass

        try:
            lang_code = await get_lang(message.chat.id)
            language = get_string(lang_code)
        except:
            language = get_string("en")

        return await mystic(client, message, language)
    return wrapper


# ===================== CallbackQuery Language Decorator =====================
def languageCB(mystic):
    async def wrapper(client, CallbackQuery, **kwargs):
        if await is_maintenance() is False:
            if CallbackQuery.from_user.id not in SUDOERS:
                return await CallbackQuery.answer(
                    f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, "
                    f"ᴠɪsɪᴛ sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ ғᴏʀ ᴋɴᴏᴡɪɴɢ ᴛʜᴇ ʀᴇᴀsᴏɴ.",
                    show_alert=True,
                )

        try:
            lang_code = await get_lang(CallbackQuery.message.chat.id)
            language = get_string(lang_code)
        except:
            language = get_string("en")

        return await mystic(client, CallbackQuery, language)
    return wrapper


# ===================== Language Decorator for /start and similar =====================
def LanguageStart(mystic):
    async def wrapper(client, message, **kwargs):
        try:
            lang_code = await get_lang(message.chat.id)
            language = get_string(lang_code)
        except:
            language = get_string("en")

        return await mystic(client, message, language)
    return wrapper
