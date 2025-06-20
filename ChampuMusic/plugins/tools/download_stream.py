import asyncio
import os
import time
from time import time

import wget
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL

from ChampuMusic import app
from ChampuMusic.platforms.Youtube import YouTubeAPI

# Define a dictionary to track the last query timestamp for each user
user_last_CallbackQuery_time = {}
user_CallbackQuery_count = {}

# Define the threshold for query spamming (e.g., 1 query within 60 seconds)
SPAM_THRESHOLD = 1
SPAM_WINDOW_SECONDS = 30

SPAM_AUDIO_THRESHOLD = 1
SPAM_AUDIO_WINDOW_SECONDS = 30

BANNED_USERS = []

# Initialize YouTube API
youtube = YouTubeAPI()


@app.on_callback_query(filters.regex("downloadvideo") & ~filters.user(BANNED_USERS))
async def download_video(client, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    current_time = time.time()

    # Check if the user has exceeded the query limit
    last_Query_time = user_last_CallbackQuery_time.get(user_id, 0)
    if current_time - last_Query_time < SPAM_WINDOW_SECONDS:
        # If the limit is exceeded, send a response and return
        await CallbackQuery.answer(
            "➻ ʏᴏᴜ ʜᴀᴠᴇ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ʏᴏᴜʀ ᴠɪᴅᴇᴏ (ᴄʜᴇᴄᴋ ᴍʏ ᴅᴍ/ᴘᴍ).\n\n➥ ɴᴇxᴛ sᴏɴɢ ᴅᴏᴡɴʟᴏᴀᴅ ᴀғᴛᴇʀ 30 sᴇᴄᴏɴᴅs.",
            show_alert=True,
        )
        return
    else:
        # Update the last query time and query count
        user_last_CallbackQuery_time[user_id] = current_time
        user_CallbackQuery_count[user_id] = user_CallbackQuery_count.get(user_id, 0) + 1

    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    user_name = CallbackQuery.from_user.first_name
    chutiya = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    await CallbackQuery.answer("ᴏᴋ sɪʀ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...", show_alert=True)
    pablo = await client.send_message(
        CallbackQuery.message.chat.id,
        f"**ʜᴇʏ {chutiya} ᴅᴏᴡɴʟᴏᴅɪɴɢ ʏᴏᴜʀ ᴠɪᴅᴇᴏ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...**",
    )
    if not videoid:
        await pablo.edit(
            f"**ʜᴇʏ {chutiya} ʏᴏᴜʀ sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ. ᴛʀʏ ᴀɢᴀɪɴ...**"
        )
        return

    # Use your new YouTubeAPI methods
    try:
        # Get video details using your new API
        title, duration_min, duration_sec, thumbnail, vidid = await youtube.details(videoid, videoid=True)
        url = f"https://www.youtube.com/watch?v={videoid}"
        
        # Download thumbnail
        sedlyf = wget.download(thumbnail)
        
        # Download video using your new API
        downloaded_file, direct = await youtube.download(
            link=url,
            mystic=pablo,
            video=True,
            videoid=False
        )
        
        if not downloaded_file:
            await pablo.edit(
                f"**ʜᴇʏ {chutiya} ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʏᴏᴜʀ ᴠɪᴅᴇᴏ.**"
            )
            return

        capy = f"❄ **ᴛɪᴛʟᴇ :** [{title}]({url})\n\n💫 **ᴅᴜʀᴀᴛɪᴏɴ :** {duration_min}\n\n🥀 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {chutiya}"
        
        try:
            if direct:
                # File is downloaded locally
                await client.send_video(
                    CallbackQuery.from_user.id,
                    video=open(downloaded_file, "rb"),
                    duration=duration_sec,
                    file_name=f"{title}.mp4",
                    thumb=sedlyf,
                    caption=capy,
                    supports_streaming=True,
                )
            else:
                # Direct streaming URL
                await client.send_video(
                    CallbackQuery.from_user.id,
                    video=downloaded_file,
                    duration=duration_sec,
                    file_name=f"{title}.mp4",
                    thumb=sedlyf,
                    caption=capy,
                    supports_streaming=True,
                )
            
            await client.send_message(
                CallbackQuery.message.chat.id,
                f"**ʜᴇʏ** {chutiya}\n\n**✅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ.**\n**➻ ᴠɪᴅᴇᴏ sᴇɴᴛ ɪɴ ʏᴏᴜʀ ᴘᴍ/ᴅᴍ.**\n**➥ ᴄʜᴇᴄᴋ ʜᴇʀᴇ » [ʙᴏᴛ ᴘᴍ/ᴅᴍ](tg://openmessage?user_id={app.id})**🤗",
            )
            await pablo.delete()
            
            # Clean up files
            for files in [sedlyf, downloaded_file if direct else None]:
                if files and os.path.exists(files):
                    os.remove(files)

        except Exception as e:
            await pablo.delete()
            return await client.send_message(
                CallbackQuery.message.chat.id,
                f"**ʜᴇʏ {chutiya} ᴘʟᴇᴀsᴇ ᴜɴʙʟᴏᴄᴋ ᴍᴇ ғᴏʀ ᴅᴏᴡɴʟᴏᴀᴅ ʏᴏᴜʀ ᴠɪᴅᴇᴏ ʙʏ ᴄʟɪᴄᴋ ʜᴇʀᴇ 👇👇**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                f"👉ᴜɴʙʟᴏᴄᴋ ᴍᴇ🤨",
                                url=f"https://t.me/{app.username}?start=info_{videoid}",
                            )
                        ]
                    ]
                ),
            )

    except Exception as e:
        await pablo.edit(
            f"**ʜᴇʏ {chutiya} ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʏᴏᴜʀ ᴠɪᴅᴇᴏ.** \n**ᴇʀʀᴏʀ:** `{str(e)}`"
        )
        return


@app.on_callback_query(filters.regex("downloadaudio") & ~filters.user(BANNED_USERS))
async def download_audio(client, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    current_time = time.time()

    # Check if the user has exceeded the query limit
    last_Query_time = user_last_CallbackQuery_time.get(user_id, 0)
    if current_time - last_Query_time < SPAM_AUDIO_WINDOW_SECONDS:
        # If the limit is exceeded, send a response and return
        await CallbackQuery.answer(
            "➻ ʏᴏᴜ ʜᴀᴠᴇ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ʏᴏᴜʀ ᴀᴜᴅɪᴏ (ᴄʜᴇᴄᴋ ᴍʏ ᴅᴍ/ᴘᴍ).\n\n➥ ɴᴇxᴛ sᴏɴɢ ᴅᴏᴡɴʟᴏᴀᴅ ᴀғᴛᴇʀ 30 sᴇᴄᴏɴᴅs.",
            show_alert=True,
        )
        return
    else:
        # Update the last query time and query count
        user_last_CallbackQuery_time[user_id] = current_time
        user_CallbackQuery_count[user_id] = user_CallbackQuery_count.get(user_id, 0) + 1

    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    user_name = CallbackQuery.from_user.first_name
    chutiya = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    await CallbackQuery.answer("ᴏᴋ sɪʀ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...", show_alert=True)
    pablo = await client.send_message(
        CallbackQuery.message.chat.id,
        f"**ʜᴇʏ {chutiya} ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ʏᴏᴜʀ ᴀᴜᴅɪᴏ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...**",
    )
    if not videoid:
        await pablo.edit(
            f"**ʜᴇʏ {chutiya} ʏᴏᴜʀ sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ. ᴛʀʏ ᴀɢᴀɪɴ...**"
        )
        return

    # Use your new YouTubeAPI methods
    try:
        # Get video details using your new API
        title, duration_min, duration_sec, thumbnail, vidid = await youtube.details(videoid, videoid=True)
        url = f"https://www.youtube.com/watch?v={videoid}"
        
        # Download thumbnail
        sedlyf = wget.download(thumbnail)
        
        # Download audio using your new download_song function
        from ChampuMusic.platforms.Youtube import download_song
        downloaded_file = await download_song(url)
        
        if not downloaded_file:
            await pablo.edit(
                f"**ʜᴇʏ {chutiya} ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʏᴏᴜʀ ᴀᴜᴅɪᴏ.**"
            )
            return

        capy = f"❄ **ᴛɪᴛʟᴇ :** [{title}]({url})\n\n💫 **ᴅᴜʀᴀᴛɪᴏɴ :** {duration_min}\n\n🥀 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {chutiya}"
        
        try:
            await client.send_audio(
                CallbackQuery.from_user.id,
                audio=open(downloaded_file, "rb"),
                duration=duration_sec,
                title=title,
                thumb=sedlyf,
                caption=capy,
            )
            
            await client.send_message(
                CallbackQuery.message.chat.id,
                f"**ʜᴇʏ** {chutiya}\n\n**✅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ.**\n**➻ ᴀᴜᴅɪᴏ sᴇɴᴛ ɪɴ ʏᴏᴜʀ ᴘᴍ/ᴅᴍ.**\n**➥ ᴄʜᴇᴄᴋ ʜᴇʀᴇ » [ʙᴏᴛ ᴘᴍ/ᴅᴍ](tg://openmessage?user_id={app.id})**🤗",
            )
            await pablo.delete()
            
            # Clean up files
            for files in [sedlyf, downloaded_file]:
                if files and os.path.exists(files):
                    os.remove(files)

        except Exception as e:
            await pablo.delete()
            return await client.send_message(
                CallbackQuery.message.chat.id,
                f"**ʜᴇʏ {chutiya} ᴘʟᴇᴀsᴇ ᴜɴʙʟᴏᴄᴋ ᴍᴇ ғᴏʀ ᴅᴏᴡɴʟᴏᴀᴅ ʏᴏᴜʀ ᴀᴜᴅɪᴏ ʙʏ ᴄʟɪᴄᴋ ʜᴇʀᴇ 👇👇**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                f"👉ᴜɴʙʟᴏᴄᴋ ᴍᴇ🤨",
                                url=f"https://t.me/{app.username}?start=info_{videoid}",
                            )
                        ]
                    ]
                ),
            )

    except Exception as e:
        await pablo.edit(
            f"**ʜᴇʏ {chutiya} ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʏᴏᴜʀ ᴀᴜᴅɪᴏ.** \n**ᴇʀʀᴏʀ:** `{str(e)}`"
        )
        return
