import asyncio
import importlib
import os
import signal
import sys
from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from VIPMUSIC import LOGGER, app, userbot
from VIPMUSIC.core.call import VIP
from VIPMUSIC.misc import sudo
from VIPMUSIC.plugins import ALL_MODULES
from VIPMUSIC.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS
from VIPMUSIC import telethn


# Auto shutdown timer (in seconds)
AUTO_SHUTDOWN_TIMEOUT = 600  # 10 minutes


async def init():
    """Initialize the bot and load all modules."""
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error(
            "❌ Pyrogram string session not filled. Please set STRING1–STRING5!"
        )

    # Load sudo users
    await sudo()

    # Load banned users
    try:
        gbanned_users = await get_gbanned()
        for user_id in gbanned_users:
            BANNED_USERS.add(user_id)

        banned_users = await get_banned_users()
        for user_id in banned_users:
            BANNED_USERS.add(user_id)
    except Exception as e:
        LOGGER(__name__).warning(f"Failed to load banned users: {e}")

    # Start all clients
    await app.start()
    for module in ALL_MODULES:
        importlib.import_module("VIPMUSIC.plugins" + module)
    LOGGER("VIPMUSIC.plugins").info("✅ All features loaded successfully!")

    await userbot.start()
    await VIP.start()
    await VIP.decorators()

    LOGGER("VIPMUSIC").info(
        "╔═════ஜ۩۞۩ஜ════╗\n  ♨️ 𝗠𝗔𝗗𝗘 𝗕𝗬 𝗩𝗜𝗣 𝗕𝗢𝗬 ♨️\n╚═════ஜ۩۞۩ஜ════╝"
    )

    # Run idle and auto-shutdown concurrently
    await asyncio.gather(idle(), auto_shutdown())


async def auto_shutdown():
    """Automatically stop and restart the bot after timeout."""
    LOGGER("VIPMUSIC").info(
        f"🕒 Auto-shutdown timer started ({AUTO_SHUTDOWN_TIMEOUT // 60} minutes)..."
    )
    await asyncio.sleep(AUTO_SHUTDOWN_TIMEOUT)
    LOGGER("VIPMUSIC").warning(
        f"⏳ Timeout reached ({AUTO_SHUTDOWN_TIMEOUT // 60} min). Stopping and restarting..."
    )
    await restart_bot()


async def shutdown():
    """Gracefully stop all services."""
    LOGGER("VIPMUSIC").info("🧹 Cleaning up before shutdown...")

    try:
        # Safely stop voice chat if active
        try:
            if hasattr(VIP, "leave_call"):
                await VIP.leave_call()
            elif hasattr(VIP, "stop_stream"):
                await VIP.stop_stream()
        except NoActiveGroupCall:
            LOGGER("VIPMUSIC").info("🎵 No active group call to stop.")
        except Exception as e:
            LOGGER("VIPMUSIC").warning(f"Could not stop group call: {e}")

        # Stop all clients
        await app.stop()
        await userbot.stop()
        await telethn.disconnect()

    except Exception as e:
        LOGGER("VIPMUSIC").error(f"Error during shutdown: {e}")
    finally:
        LOGGER("VIPMUSIC").info(
            "✅ Shutdown complete.\n╔═════ஜ۩۞۩ஜ════╗\n  ♨️ 𝗠𝗔𝗗𝗘 𝗕𝗬 𝗩𝗜𝗣 𝗕𝗢𝗬 ♨️\n╚═════ஜ۩۞۩ஜ════╝"
        )


async def restart_bot():
    """Shutdown everything and restart the bot process."""
    await shutdown()
    LOGGER("VIPMUSIC").info("🔁 Restarting bot...")
    python = sys.executable
    os.execv(python, [python] + sys.argv)  # restart the current script


if __name__ == "__main__":
    telethn.start(bot_token=config.BOT_TOKEN)
    loop = asyncio.get_event_loop()

    # Graceful signal handlers (Ctrl+C, kill, etc.)
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.ensure_future(shutdown()))

    try:
        loop.run_until_complete(init())
    except KeyboardInterrupt:
        loop.run_until_complete(shutdown())
    finally:
        loop.close()
