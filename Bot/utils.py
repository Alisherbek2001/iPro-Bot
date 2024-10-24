from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from texts import TEXTS
from config import *
from api import *


def get_language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🇺🇿 O'zbekcha"),
                KeyboardButton(text="🇷🇺 Русский")
            ]
        ],
        resize_keyboard=True
    )

async def check_subscription(user_id: int, channel: str, bot: Bot) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status not in ["left", "kicked"]
    except Exception as err:
        print(f"Checking error: {err}")
        return False

async def check_all_subscriptions(user_id: int, bot: Bot) -> tuple[bool, InlineKeyboardMarkup]:
    final_status = True
    btn = InlineKeyboardMarkup(inline_keyboard=[])

    for channel in CHANNELS:
        status = await check_subscription(user_id=user_id, channel=channel, bot=bot)
        final_status &= status
        
        if not status:
            try:
                channel_info = await bot.get_chat(channel)
                invite_link = await channel_info.export_invite_link()
                btn.inline_keyboard.append([
                    InlineKeyboardButton(text=f"❌ {channel_info.title}", url=invite_link)
                ])
            except Exception as err:
                print(f"Error getting channel info: {err}")
                continue
    
    if len(btn.inline_keyboard) > 0:
        btn.inline_keyboard.append([
            InlineKeyboardButton(
                text=TEXTS['bilingual']['check_subscription'],
                callback_data="check_subs"
            )
        ])
    
    return final_status, btn


def user_exists(telegram_id):
    response = check_user(telegram_id)  
    return response.status_code == 200 


main_button_uz = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📋 E\'lon berish'), KeyboardButton(text='🇺🇿 Tilni o\'zgartirish')]
    ],
    resize_keyboard=True
)

main_button_ru = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📋 Объявление'), KeyboardButton(text='🇷🇺 Изменить язык')]
    ],
    resize_keyboard=True
)

get_ad_type_keyboard_uz = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='👨‍💼 Hodim kerak'), KeyboardButton(text='💼 Ish joyi kerak')],
        [KeyboardButton(text='🤝 Sherik kerak'),]
    ],
    resize_keyboard=True
)

get_ad_type_keyboard_ru = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='👨‍💼 Нужен сотрудник'), KeyboardButton(text='💼 Нужна работа')],
        [KeyboardButton(text='🤝 Нужен партнер'),]
    ],
    resize_keyboard=True
)

language_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🇺🇿 O\'zbekcha'), KeyboardButton(text='🇷🇺 Русский')]
    ],
    resize_keyboard=True
)

channel_name_to_username = {}

async def get_channel_selection_keyboard_uz(bot):
    buttons = []
   
    for channel_username in ANNOUNCEMENT_CHANNELS:
        channel_info = await bot.get_chat(channel_username) 
        channel_name = channel_info.title
        channel_name_to_username[channel_name] = channel_username
        buttons.append([KeyboardButton(text=channel_name)])  
   
    buttons.append([KeyboardButton(text="⬅️ Ortga qaytish")])  
   
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


async def get_channel_selection_keyboard_ru(bot):
    buttons = []
   
    for channel_username in ANNOUNCEMENT_CHANNELS:
        channel_info = await bot.get_chat(channel_username) 
        channel_name = channel_info.title
        channel_name_to_username[channel_name] = channel_username
        buttons.append([KeyboardButton(text=channel_name)])  
   
    buttons.append([KeyboardButton(text="⬅️ Возвращаться")])  
   
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

confirm_buttons_uz = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='✅ Ha'), KeyboardButton(text='❌ Yo\'q')],
    ],
    resize_keyboard=True
)

confirm_buttons_ru = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='✅ Да'), KeyboardButton(text='❌ Нет')],
    ],
    resize_keyboard=True
)


# def get_approval_keyboard(message_id: int):
#     builder = InlineKeyboardBuilder()
#     builder.button(text="✅ Qabul qilish", callback_data=f"approve_{message_id}")
#     builder.button(text="❌ Rad etish", callback_data=f"reject_{message_id}")
#     return builder.as_markup()