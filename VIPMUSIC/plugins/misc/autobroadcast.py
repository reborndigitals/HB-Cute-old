import asyncio
import datetime
from VIPMUSIC import app
from pyrogram import Client
from VIPMUSIC.utils.database import get_served_chats
from config import START_IMG_URL, AUTO_GCAST_MSG, AUTO_GCAST, LOGGER_ID
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

AUTO_GCASTS = f"{AUTO_GCAST}" if AUTO_GCAST else False

START_IMG_URLS = "https://graph.org/file/ffdb1be822436121cf5fd.png"

MESSAGE = f"""𝘽𝙊𝙏 𝙁𝙀𝘼𝙏𝙐𝙍𝙀𝙎: (•‌ᴗ•‌)و

⍟𝗌ᴜᴘᴘᴏʀᴛ ʏᴏᴜᴛᴜʙᴇ ʟɪɴᴋ𝗌 ⍟ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪᴄᴇ ⍟ ᴠᴄ-ɪɴᴠɪᴛᴇ ᴄᴀʀᴅ ⍟ ᴘʟᴀʏ ᴡɪᴛʜᴏᴜᴛ 𝗌ʟᴀ𝗌ʜ

✰ 𝐏𝐥𝐚𝐲𝐢𝐧𝐠 𝐒𝐨𝐧𝐠𝐬 & 𝐕𝐢𝐝𝐞𝐨𝐬 💫 (𝑆𝑢𝑝𝑝𝑜𝑟𝑡 𝑌𝑜𝑢𝑡𝑢𝑏𝑒 𝑙𝑖𝑛𝑘𝑠) 
➻ /play or play
➻ /vplay or vplay

✰ 𝐌𝐞𝐧𝐭𝐢𝐨𝐧/𝐓𝐚𝐠𝐀𝐥𝐥:💫
➻ /tagall
➻ /vctag
➻ /heartbeat /honeymoon
➻ /gmtag /gntag
➻ /tamiltag

😻ᴘʀᴏ ғᴇᴀᴛᴜʀᴇ𝗌 ᴜɴʟᴏᴄᴋᴇᴅ🥳
✰ 𝑭𝒖𝒏 𝑻𝒂𝒈𝒔:🥂
➻ /lifeline
➻ /lovebeats
➻ /heartbeat
➻ /couples
➻ /love (BoyName) (GirlName)

✰ 𝐖𝐡𝐢𝐬𝐩𝐞𝐫 𝐌𝐞𝐬𝐬𝐚𝐠𝐞𝐬:🥂
(𝑆𝑢𝑝𝑝𝑜𝑟𝑡 𝘗𝘔/𝑂𝑛𝑒 𝑇𝑖𝑚𝑒 𝑉𝑖𝑒𝑤)
➻ @BotUsername @User_UserName (Text Message)

✰ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐒𝐨𝐧𝐠𝐬 𝐕𝐢𝐝𝐞𝐨𝐬:🥂
(𝑆𝑢𝑝𝑝𝑜𝑟𝑡 𝐼𝑛𝑠𝑡𝑎 𝑅𝑒𝑎𝑙𝑠 𝑑𝑜𝑤𝑛𝑙𝑜𝑎𝑑)
➻ /song Song Name
➻ /video Song Name
➻ /insta InstaLink

✰ 𝐓𝐨𝐩 𝐔𝐬𝐞𝐫𝐬🥂
➻ /ranking

✰ 𝐍𝐚𝐦𝐞 𝐇𝐢𝐬𝐭𝐨𝐫𝐲🥂
➻ /sg (replay user message|id)

✰ 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞 𝐒𝐭𝐲𝐥𝐢𝐬𝐡 𝐅𝐨𝐧𝐭𝐬:🥂
➻ /font (Text)

💕Sᴜᴘᴘᴏʀᴛ Mᴀɴᴀɢᴇᴍᴇɴᴛ Bᴏᴛ Fᴇᴀᴛᴜʀᴇ𝗌 Lɪᴋᴇ:🦋
𝙸𝙳, 𝙸𝚗𝚏𝚘, 𝙵𝚒𝚕𝚝𝚎𝚛𝚜, 𝙱𝚊𝚗𝚜, 𝙼𝚞𝚝𝚎𝚜, 𝚎𝚝𝚌,.

----------------------------------
😈😈𝘼𝙇𝙇 𝙁𝙀𝘼𝙏𝙐𝙍𝙀𝙎 𝘼𝙍𝙀 𝘼𝙑𝘼𝙄𝙇𝘼𝘽𝙇𝙀 𝑶𝑵𝑳𝒀  𝙄𝙉 𝙏𝙃𝙄𝙎 𝘽𝙊𝙏🥵🥵
----------------------------------

𝑃𝑜𝑤𝑒𝑟 𝐵𝑦 - [𝞖𝘌𝘈𝘙𝘛𝂬♡𝂬𝞑𝘌𝘈𝘛▹ᴴᴮ⸳⸳ⷮ⸳⸳ⷨ](https://t.me/HeartBeat_Muzic)😎✨

𝑂𝑤𝑛𝑒𝑟 - [𝅗ـﮩ٨ـ𝅽𝅾𓆩𑫏ⳢⅬᤌໍᤌ᭄ᰈⅬᤌໍᤌ𑂞ⳣവᰈᮀ།ໍᴮᴬᵀ🦇𓆪ﮩ٨ـ𝅽𝅾‐𝅘](https://t.me/rajeshrakis) 

𝑁𝑒𝑡𝑤𝑜𝑟𝑘 - [𝞖𝘌𝘈𝘙𝘛𝂬♡𝂬𝞑𝘌𝘈𝘛▹ᴴᴮ⸳⸳ⷮ⸳⸳ⷨ](https://t.me/HeartBeat_Offi) 😎✨"""

BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("💕‌𝞖𝘌𝘈𝘙𝘛𝂬♡𝂬‌𝞑𝘌𝘈𝘛𝆺𝅥🦋", url=f"https://t.me/HeartBeat_Muzic")
        ]
    ]
)


caption = f"""{AUTO_GCAST_MSG}""" if AUTO_GCAST_MSG else MESSAGES

TEXT = """**ᴀᴜᴛᴏ ɢᴄᴀsᴛ ɪs ᴇɴᴀʙʟᴇᴅ sᴏ ᴀᴜᴛᴏ ɢᴄᴀsᴛ/ʙʀᴏᴀᴅᴄᴀsᴛ ɪs ᴅᴏɪɴ ɪɴ ᴀʟʟ ᴄʜᴀᴛs ᴄᴏɴᴛɪɴᴜᴏᴜsʟʏ. **\n**ɪᴛ ᴄᴀɴ ʙᴇ sᴛᴏᴘᴘᴇᴅ ʙʏ ᴘᴜᴛ ᴠᴀʀɪᴀʙʟᴇ [ᴀᴜᴛᴏ_ɢᴄᴀsᴛ = (ᴋᴇᴇᴘ ʙʟᴀɴᴋ & ᴅᴏɴᴛ ᴡʀɪᴛᴇ ᴀɴʏᴛʜɪɴɢ)]**"""

async def send_text_once():
    try:
        await app.send_message(LOGGER_ID, TEXT)
    except Exception as e:
        pass

async def send_message_to_chats():
    try:
        chats = await get_served_chats()

        for chat_info in chats:
            chat_id = chat_info.get('chat_id')
            if isinstance(chat_id, int):  # Check if chat_id is an integer
                try:
                    await app.send_photo(chat_id, photo=START_IMG_URLS, caption=caption, reply_markup=BUTTONS)
                    await asyncio.sleep(20)  # Sleep for 100 second between sending messages
                except Exception as e:
                    pass  # Do nothing if an error occurs while sending message
    except Exception as e:
        pass  # Do nothing if an error occurs while fetching served chats

async def continuous_broadcast():
    await send_text_once()  # Send TEXT once when bot starts

    while True:
        if AUTO_GCAST:
            try:
                await send_message_to_chats()
            except Exception as e:
                pass

        # Wait for 100000 seconds before next broadcast
        await asyncio.sleep(100000)

# Start the continuous broadcast loop if AUTO_GCAST is True
if AUTO_GCAST:  
    asyncio.create_task(continuous_broadcast())
