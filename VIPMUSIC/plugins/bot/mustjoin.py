
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from VIPMUSIC import app

#--------------------------

MUST_JOIN = "HeartBeat_Fam"
#------------------------
@app.on_message(filters.incoming & filters.private, group=-1)
async def must_join_channel(app: Client, msg: Message):
    if not MUST_JOIN:
        return
    try:
        try:
            await app.get_chat_member(MUST_JOIN, msg.from_user.id)
        except UserNotParticipant:
            if MUST_JOIN.isalpha():
                link = "https://t.me/" + MUST_JOIN
            else:
                chat_info = await app.get_chat(MUST_JOIN)
                link = chat_info.invite_link
            try:
                await msg.reply_photo(
                    photo="https://graph.org/file/ffdb1be822436121cf5fd.png", caption=f"☆ . * ● ¸ . ✦ .★　° :. ★ * • ○ ° ★\n\n┏━━━━•❅•°• - ⭕️ - •°•❅•━━━━┓\n ⊰●⊱┈─★ 𝐽𝑜𝑖𝑛 𝑈𝑠 ★─┈⊰●⊱\n\n  💕‌𝞖𝘌𝘈𝘙𝘛𝂬♡𝂬‌𝞑𝘌𝘈𝘛▹ᴴᴮ⸳⸳ⷮ⸳⸳ⷨ🦋\n┗━━━━•❅•°• - ⭕️ - •°•❅•━━━━┛\n\n➽───────────────❥\n\n[1𝗌ᴛ ᴇɴɴᴏᴅᴀ ɢʀᴏᴜᴘ-ʟᴀ ᴊᴏɪɴ ᴘᴀɴᴜ. ᴀᴘʀᴀᴍ ᴇɴɴᴀ ᴜ𝗌ᴇ ᴘᴀɴɴᴜ.]({link})\n\n[ᴊᴏɪɴ ᴍʏ ɢʀᴏᴜᴘ 1𝗌ᴛ. ᴀɴᴅ  𝗌ᴛᴀʀᴛ ᴀɢᴀɪɴ.]({link})\n\n➽───────────────❥\n\n💕 𝐍𝔢𝔱𝔴𝔬𝔯𝔨 🦋\n[ 𝅗ـﮩ٨ـ𝅽𝅾𓆩𝞖𝘌𝘈𝘙𝘛𝂬♡𝂬𝞑𝘌𝘈𝘛▹ᴴᴮ⸳⸳ⷮ⸳⸳ⷨ𓆪ﮩ٨ـ𝅽𝅾‐𝅘]({link}) \n\n☆ . * ● ¸ . ✦ .★　° :. ★ * • ○ ° ★ ",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("💕𝐉𝖔𝖎𝖓🦋", url=link),
                            ]
                        ]
                    )
                )
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        print(f"๏ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ ᴀs ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴍᴜsᴛ_Jᴏɪɴ ᴄʜᴀᴛ ๏: {MUST_JOIN} !")
