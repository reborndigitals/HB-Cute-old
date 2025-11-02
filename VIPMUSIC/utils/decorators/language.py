from VIPMUSIC.misc import SUDOERS
from VIPMUSIC.utils.database import get_lang, is_maintenance
from strings import get_string
from config import SUPPORT_CHAT
from VIPMUSIC import app


def language(mystic):
    async def wrapper(_, message, **kwargs):
        # Maintenance check
        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    text=f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ.\nVisit <a href={SUPPORT_CHAT}>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> ғᴏʀ ᴅᴇᴛᴀɪʟs.",
                    disable_web_page_preview=True,
                )
        try:
            await message.delete()
        except Exception:
            pass

        try:
            lang_code = await get_lang(message.chat.id)
            _ = get_string(lang_code)
        except Exception:
            _ = get_string("en")
        return await mystic(_, message, _)

    return wrapper


def languageCB(mystic):
    async def wrapper(_, CallbackQuery, **kwargs):
        # Maintenance check
        if await is_maintenance() is False:
            if CallbackQuery.from_user.id not in SUDOERS:
                return await CallbackQuery.answer(
                    f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ.\nVisit sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ ғᴏʀ ᴅᴇᴛᴀɪʟs.",
                    show_alert=True,
                )
        try:
            lang_code = await get_lang(CallbackQuery.message.chat.id)
            _ = get_string(lang_code)
        except Exception:
            _ = get_string("en")
        return await mystic(_, CallbackQuery, _)

    return wrapper


def LanguageStart(mystic):
    async def wrapper(_, message, **kwargs):
        try:
            lang_code = await get_lang(message.chat.id)
            _ = get_string(lang_code)
        except Exception:
            _ = get_string("en")
        return await mystic(_, message, _)

    return wrapper
