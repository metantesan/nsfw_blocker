#!python3
import os
import time
from datetime import datetime, timedelta

from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired
from pyrogram.types import (Message, BotCommand, InlineQuery, InlineKeyboardMarkup, InlineKeyboardButton,
                            InlineQueryResultPhoto, CallbackQuery, ChatPermissions)
from pyrogram.enums import parse_mode
from pyrogram.raw.functions import help
import opennsfw2 as n2

api_id = 000
api_hash = "000000000000000000"
bot_token = "00000000000"

proxy = {
    "scheme": "socks5",  # "socks4", "socks5" and "http" are supported
    "hostname": "127.0.0.1",
    "port": 2080,
}
app = Client("my_bot", bot_token=bot_token, api_hash=api_hash, api_id=api_id)
async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")

@app.on_message(filters.photo,1)
async def onphoto(_,message:Message):
    op=await app.download_media(message,progress=progress)
    nsfw_probability = n2.predict_image(op)
    if nsfw_probability>=0.65 :
        try:
            await message.reply(
                f"user:{message.from_user.mention} is send a nsfw \n so user can not send any message {nsfw_probability}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "UnMute (only admins)",
                                callback_data=f"{message.from_user.id}"
                            )
                        ]
                    ]
                ), )
            await message.delete()
            await _.restrict_chat_member(message.chat.id, message.from_user.id,
                                         ChatPermissions())
        except ChatAdminRequired:
            await message.reply_text("Bot needs admin permissions to unmute users.")
        except Exception as e:
            await message.reply_text(f"An error occurred: {e}")
    # else:
        # await message.reply(f"is not nude {nsfw_probability}")
    os.remove(op)
    time.sleep(1)

@app.on_callback_query()
async def answer(client, callback_query: CallbackQuery):
    try:
        admins = []
        async for m in app.get_chat_members(callback_query.message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            admins.append(m.user.id)
        if callback_query.from_user.id in admins:
            await app.restrict_chat_member(callback_query.message.chat.id,callback_query.data,callback_query.message.chat.permissions)
            await callback_query.answer("user unmuted", show_alert=True)
        else:
            await callback_query.answer("you are not a admin",show_alert=True)
    except ChatAdminRequired:
        await callback_query.answer("Bot needs admin permissions to mute users.",show_alert=True)
    except Exception as e:
        await callback_query.answer(f"An error occurred: {e}",show_alert=True)

@app.on_message(filters.animation,1)
async def onphoto(_,message:Message):
    op=await app.download_media(message,progress=progress)
    nsfw_probability = n2.predict_video_frames(op,frame_interval=1)
    is_nude=False
    ns=0.0
    for i in nsfw_probability[1]:
        if i>=0.65 :
            is_nude=True
        if ns < i:
            ns = i
    if is_nude:
        try:
            await message.reply(
                f"user:{message.from_user.mention} is send a nsfw \n so user can not send any message {ns}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "UnMute (only admins)",
                                callback_data=f"{message.from_user.id}"
                            )
                        ]
                    ]
                ), )
            await message.delete()
            await _.restrict_chat_member(message.chat.id, message.from_user.id,
                                         ChatPermissions())
        except ChatAdminRequired:
            await message.reply_text("Bot needs admin permissions to unmute users.")
        except Exception as e:
            await message.reply_text(f"An error occurred: {e}")
    # else:
        # await message.reply(f"is not nude {ns}")
    os.remove(op)
    time.sleep(1)
#@app.on_message(filters.video,1)
async def onphoto(_,message:Message):
    op=await app.download_media(message,progress=progress)
    nsfw_probability = n2.predict_video_frames(op,frame_interval=20)
    is_nude=False
    ns=0.0
    for i in nsfw_probability[1]:
        if i>=0.65 :
            is_nude=True
        if ns < i:
            ns = i
    if is_nude:
        try:
            await message.reply(
                f"user:{message.from_user.mention} is send a nsfw \n so user can not send any message {ns}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "UnMute (only admins)",
                                callback_data=f"{message.from_user.id}"
                            )
                        ]
                    ]
                ), )
            await message.delete()
            await _.restrict_chat_member(message.chat.id, message.from_user.id,
                                         ChatPermissions())
        except ChatAdminRequired:
            await message.reply_text("Bot needs admin permissions to unmute users.")
        except Exception as e:
            await message.reply_text(f"An error occurred: {e}")
    # else:
        # await message.reply(f"is not nude {ns}")
    os.remove(op)
    time.sleep(1)



app.run()
