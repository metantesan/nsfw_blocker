from os import remove, path
from pyrogram import Client, filters,enums
from opennsfw2 import predict_image, predict_video_frames
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions

proxy = {
    "scheme": "socks5",  # "socks4", "socks5" and "http" are supported
    "hostname": "127.0.0.1",
    "port": 2080,
}

bot = Client("my_bot", bot_token="", api_hash="", api_id=12345)

async def check_nsfw_and_restrict(message: Message, probability: float, is_video: bool = False):
    if probability >= 0.65:
        await message.reply_text(f"**❌ User {message.from_user.mention} \nYour Message Was Deleted And You Are Restricted !\n🔞 Reason : Sending inappropriate Content !**",  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👨‍💼 UnMute ( Admins Only )", callback_data=f"unmute-{message.from_user.id}")]]))
        await message.delete()
        await bot.restrict_chat_member(message.chat.id, message.from_user.id, ChatPermissions())


async def handle_media_message(message: Message, is_video: bool = False):
    try:
        file_path = await bot.download_media(message)
        file_type=file_path.split(".")[1]
        if is_video or file_type =="webm":
            nsfw_probability = max(predict_video_frames(file_path, frame_interval=1)[1])

        else:
            nsfw_probability = predict_image(file_path)

        await check_nsfw_and_restrict(message, nsfw_probability, is_video)

    finally:
        if path.exists(file_path):
            remove(file_path)


@bot.on_message(filters.group & filters.chat(-1002038104161) & filters.photo | filters.sticker)
async def media_handler(_, message: Message):
    await handle_media_message(message)


@bot.on_message(filters.group & filters.chat(-1002038104161) & filters.animation)
async def animation_handler(_, message: Message):
    await handle_media_message(message, is_video=True)


@bot.on_callback_query(filters.regex(r'^unmute-'))
async def callback_query_handler(_, query: CallbackQuery):
    admins = []
    async for m in bot.get_chat_members(query.message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        admins.append(m.user.id)
    if query.from_user.id in admins:
        await bot.restrict_chat_member(query.message.chat.id, int(query.data.split('-')[1]), permissions=query.message.chat.permissions)
        await query.answer("▫️ User UnMuted !", show_alert=True)
        await query.edit_message_text('**▫️ The User Was Restricted By the Admin !**')

    else:
        await query.answer("◾️ You Are Not An Admin !", show_alert=True)


bot.run()