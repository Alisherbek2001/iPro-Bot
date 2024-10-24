from aiogram import Router, F,types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery,ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from state import ChangeLanguageForm,Form_Check,Form
from texts import TEXTS
from utils import *
from api import *
from typing import Dict


router = Router()
bot = Bot(
    token=BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)


@router.message(Command("start"))
async def start_command(message: Message):
    telegram_id = message.from_user.id
    response = check_user(telegram_id)
    if response.status_code==200:
        language = response.json().get('language', 'uz') 
        main_button = main_button_uz if language=='uz' else main_button_ru
        await message.answer(TEXTS[language]['main_menu'],reply_markup=main_button)
    else:
        await message.answer(
            TEXTS['bilingual']['choose_language'],
            reply_markup=get_language_keyboard()
        )

@router.callback_query(F.data == "check_subs")
async def checker(call: CallbackQuery):
    await call.answer()
    telegram_id = call.from_user.id 
    response = check_user(telegram_id)
    if response.status_code == 200:  
        language = response.json().get('language', 'uz') 
        main_button = main_button_uz if language=='uz' else main_button_ru
        await call.answer(TEXTS[language]['main_menu'],reply_markup=main_button)
    else:
        await call.message.answer(
            TEXTS['bilingual']['choose_language'],
            reply_markup=get_language_keyboard()
        )

    await call.message.delete()


@router.message(F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский"]))
async def handle_language_selection(message: Message):
    language = 'uz' if message.text == "🇺🇿 O'zbekcha" else 'ru'
    response = check_user(message.from_user.id)
    if response.status_code == 404:
        create_user(message.from_user.id, language)
    else:  
        change_language(message.from_user.id, language)
    main_button = main_button_uz if language=='uz' else main_button_ru
    await message.answer(TEXTS[language]['main_menu'],reply_markup=main_button)


@router.message(F.text.in_(["🇺🇿 Tilni o'zgartirish","🇷🇺 Изменить язык"]))
async def prompt_language_change(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    result = check_user(telegram_id=telegram_id)
    
    current_language = 'uz'
    
    if result.status_code == 200:
        current_language = result.json().get('language', 'uz')

    await message.answer(TEXTS[current_language]['language_select'], reply_markup=language_keyboard)
    await state.set_state(ChangeLanguageForm.language_change)


@router.message(ChangeLanguageForm.language_change, F.text.in_(["🇺🇿 O'zbekcha", "🇬🇧 English", "🇷🇺 Русский"]))
async def handle_language_selection(message: types.Message, state: FSMContext):
    selected_language = None
    if message.text == "🇺🇿 O'zbekcha":
        selected_language = 'uz'
    elif message.text == "🇷🇺 Русский":
        selected_language = 'ru'
    
    if selected_language=='uz':
        main_button = main_button_uz
    else:
        main_button = main_button_ru
        
    if selected_language:
        telegram_id = message.from_user.id
        response = change_language(telegram_id, selected_language)
        
        if response.status_code == 200:
            await state.update_data(language=selected_language)
            
            confirmation_message = {
                'uz': "Til o'zgartirildi. \nTugmalardan birini tanlang!",
                'ru': "Язык изменен. \nПожалуйста, выберите одну из кнопок!"
            }.get(selected_language, "Til o'zgartirildi. \nTugmalardan birini tanlang!")
            
            
            await message.answer(confirmation_message, reply_markup=main_button)
        else:
            error_messages = {
                'uz': "Tilni o'zgartirishda xato yuz berdi. \nTugmalardan birini tanlang!",
                'ru': "Произошла ошибка при изменении языка. \nПожалуйста, выберите одну из кнопок!"
            }.get(selected_language,"Tilni o'zgartirishda xato yuz berdi. \nTugmalardan birini tanlang!")

            await message.answer(error_messages, reply_markup=main_button)
    
    await state.clear()


@router.message(F.text.in_(["📋 E'lon berish","📋 Объявление"]))
async def handle_announcement_channel(message: types.Message, state: FSMContext,bot):
    user_data = check_user(message.from_user.id)
    if user_data.status_code == 200:
        language = user_data.json().get("language", "uz") 
    else:
        language = "uz" 
    
    await state.update_data(language=language) 
    keyboard = await get_channel_selection_keyboard_uz(bot) if language == 'uz' else await get_channel_selection_keyboard_ru(bot)
    await message.answer(
        "Qaysi kanalga e'lon joylamoqchisiz:" if language == "uz" else "На каком канале вы хотите разместить объявление:",
        reply_markup=keyboard
    )
    await state.set_state(Form.channel_selection)
    

@router.message(Form.channel_selection)
async def process_channel_selection(message: Message, state: FSMContext,bot):
    data = await state.get_data()
    language = data.get("language", "uz") 
    if message.text ==  '⬅️ Ortga qaytish'  or message.text == '⬅️ Возвращаться':
        await state.clear()
        main_button = main_button_uz if language=='uz' else main_button_ru
        await message.answer(TEXTS[language]['main_menu'],reply_markup=main_button)
    else:
        selected_channel_name = message.text
        selected_channel_username = channel_name_to_username.get(selected_channel_name)
        
        await state.update_data(
            selected_channel_name=selected_channel_name,
            selected_channel_username=selected_channel_username
        )
        get_ad_type_keyboard = get_ad_type_keyboard_uz if language=='uz' else get_ad_type_keyboard_ru
        await message.answer(
            TEXTS[language]['type_select'],
            reply_markup=get_ad_type_keyboard 
        )
        await state.set_state(Form.ad_type)


@router.message(Form.ad_type)
async def process_ad_type_selection(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    ad_type = message.text
    await state.update_data(ad_type=ad_type)
    
    if ad_type == '👨‍💼 Hodim kerak' or ad_type =='👨‍💼 Нужен сотрудник':  
        await message.answer(TEXTS[language]['employee']['skills'],reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.employee_skills)
    elif ad_type == '💼 Ish joyi kerak' or ad_type == '💼 Нужна работа':  
        await message.answer(TEXTS[language]['job']['name'],reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.job_name)
    elif ad_type == '🤝 Sherik kerak' or ad_type=='🤝 Нужен партнер' : 
        await message.answer(TEXTS[language]['partner']['name'],reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.partner_name)
    else:
        await message.answer(TEXTS[language]['error'])


@router.message(Form.employee_skills)
async def process_employee_skills(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(employee_skills=message.text)
    await message.answer(TEXTS[language]['employee']['firm_name'])
    await state.set_state(Form.employee_firm_name)


@router.message(Form.employee_firm_name)
async def process_employee_firm_name(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(employee_firm_name=message.text)
    await message.answer(TEXTS[language]['employee']['activity'])
    await state.set_state(Form.employee_activity)


@router.message(Form.employee_activity)
async def process_employee_activity(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(employee_activity=message.text)
    await message.answer(TEXTS[language]['employee']['contact_person'])
    await state.set_state(Form.employee_contact_person)


@router.message(Form.employee_contact_person)
async def process_employee_contact_person(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(employee_contact_person=message.text)
    await message.answer(TEXTS[language]['employee']['phone'])
    await state.set_state(Form.employee_phone)


@router.message(Form.employee_phone)
async def process_employee_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(employee_phone=message.text)
    await message.answer(TEXTS[language]['employee']['region'])
    await state.set_state(Form.employee_region)


@router.message(Form.employee_region)
async def process_employee_region(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(employee_region=message.text)
    await message.answer(TEXTS[language]['employee']['contact_time'])
    await state.set_state(Form.employee_contact_time)


@router.message(Form.employee_contact_time)
async def process_employee_contact_time(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(employee_contact_time=message.text)
    await message.answer(TEXTS[language]['employee']['work_time'])
    await state.set_state(Form.employee_work_time)


@router.message(Form.employee_work_time)
async def process_employee_work_time(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(employee_work_time=message.text)
    await message.answer(TEXTS[language]['employee']['salary'])
    await state.set_state(Form.employee_salary)


@router.message(Form.employee_salary)
async def process_employee_salary(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(employee_salary=message.text)
    await message.answer(TEXTS[language]['employee']['additional'])
    await state.set_state(Form.employee_additional)


@router.message(Form.employee_additional)
async def process_employee_additional(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(employee_additional=message.text)
    data = await state.get_data()
    confirmation_text_uz = (
        f"🔧 Ko'nikmalar: {data.get('employee_skills', 'N/A')}\n"
        f"🏢 Firma nomi: {data.get('employee_firm_name', 'N/A')}\n"
        f"🔍 Faoliyati: {data.get('employee_activity', 'N/A')}\n"
        f"👤 Ma'sulning ismi: {data.get('employee_contact_person', 'N/A')}\n"
        f"📞 Telefon raqami: {data.get('employee_phone', 'N/A')}\n"
        f"🌍 Hudud: {data.get('employee_region', 'N/A')}\n"
        f"⏰ Murojaat vaqti: {data.get('employee_contact_time', 'N/A')}\n"
        f"🕒 Ish vaqti: {data.get('employee_work_time', 'N/A')}\n"
        f"💰 Maosh: {data.get('employee_salary', 'N/A')}\n"
        f"📋 Qo'shimchalar: {data.get('employee_additional', 'N/A')}\n\n"
        f"Ma'lumotlaringiz to'g'rimi?"
    )
    confirmation_text_ru = (
        f"🔧 Навыки: {data.get('employee_skills', 'N/A')}\n"
        f"🏢 Название компании: {data.get('employee_firm_name', 'N/A')}\n"
        f"🔍 Деятельность: {data.get('employee_activity', 'N/A')}\n"
        f"👤 Имя ответственного лица: {data.get('employee_contact_person', 'N/A')}\n"
        f"📞 Номер телефона: {data.get('employee_phone', 'N/A')}\n"
        f"🌍 Ваш регион: {data.get('employee_region', 'N/A')}\n"
        f"⏰ Время для связи: {data.get('employee_contact_time', 'N/A')}\n"
        f"🕒 Рабочее время: {data.get('employee_work_time', 'N/A')}\n"
        f"💰 Зарплата: {data.get('employee_salary', 'N/A')}\n"
        f"📋 Дополнения: {data.get('employee_additional', 'N/A')}\n\n"
        f"Ваши данные верны?"
    )
    confirmation_text = confirmation_text_uz if language == 'uz' else confirmation_text_ru
    confirm_buttons = confirm_buttons_uz if language=='uz' else confirm_buttons_ru
    await message.answer(confirmation_text, reply_markup=confirm_buttons)
    await state.set_state(Form.confirm)



@router.message(Form.job_name)
async def process_job_name(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz") 
    await state.update_data(job_name=message.text)
    await message.answer(TEXTS[language]['job']['age'])
    await state.set_state(Form.job_age)


@router.message(Form.job_age)
async def process_job_age(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(job_age=message.text)
    await message.answer(TEXTS[language]['job']['profession'])
    await state.set_state(Form.job_profession)


@router.message(Form.job_profession)
async def process_job_profession(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(job_profession=message.text)
    await message.answer(TEXTS[language]['job']['experience'])
    await state.set_state(Form.job_experience)


@router.message(Form.job_experience)
async def process_job_experience(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(job_experience=message.text)
    await message.answer(TEXTS[language]['job']['phone'])
    await state.set_state(Form.job_phone)


@router.message(Form.job_phone)
async def process_job_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(job_phone=message.text)
    await message.answer(TEXTS[language]['job']['region'])
    await state.set_state(Form.job_region)


@router.message(Form.job_region)
async def process_job_region(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(job_region=message.text)
    await message.answer(TEXTS[language]['job']['expected_salary'])
    await state.set_state(Form.job_expected_salary)


@router.message(Form.job_expected_salary)
async def process_job_expected_salary(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(expected_salary=message.text)
    await message.answer(TEXTS[language]['job']['additional'])
    await state.set_state(Form.job_additional)


@router.message(Form.job_additional)
async def process_job_additional(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(job_additional=message.text)

    data = await state.get_data()
    
    confirmation_text_uz = (
        f"👤 Ismingiz: {data.get('job_name', 'N/A')}\n"
        f"📅 Yoshingiz: {data.get('job_age', 'N/A')}\n"
        f"🔧 Kasbingiz: {data.get('job_profession', 'N/A')}\n"
        f"📅 Stajingiz: {data.get('job_experience', 'N/A')}\n"
        f"📞 Telefon raqamingiz: {data.get('job_phone', 'N/A')}\n"
        f"🌍 Hududingiz: {data.get('job_region', 'N/A')}\n"
        f"💰 Kutayotgan oyligingiz: {data.get('job_expected_salary', 'N/A')}\n"
        f"📋 Qo'shimchalar: {data.get('job_additional', 'N/A')}\n\n"
        f"Ma'lumotlaringiz to'g'rimi?"
    )
    confirmation_text_ru = (
        f"👤 Ваше имя: {data.get('job_name', 'N/A')}\n"
        f"📅 Ваш возраст: {data.get('job_age', 'N/A')}\n"
        f"🔧 Ваша профессия: {data.get('job_profession', 'N/A')}\n"
        f"📅 Ваш опыт: {data.get('job_experience', 'N/A')}\n"
        f"📞 Ваш номер телефона: {data.get('job_phone', 'N/A')}\n"
        f"🌍 Ваш регион: {data.get('job_region', 'N/A')}\n"
        f"💰 Ожидаемая зарплата: {data.get('job_expected_salary', 'N/A')}\n"
        f"📋 Дополнения: {data.get('job_additional', 'N/A')}\n\n"
        f"Ваши данные верны?"
    )

    confirmation_text = confirmation_text_uz if language == 'uz' else confirmation_text_ru
    confirm_buttons = confirm_buttons_uz if language == 'uz' else confirm_buttons_ru

    await message.answer(confirmation_text, reply_markup=confirm_buttons)
    await state.set_state(Form.confirm)


@router.message(Form.partner_name)
async def process_partner_name(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz") 
    await state.update_data(name=message.text)
    await message.answer(TEXTS[language]['partner']['activity_type'])  
    await state.set_state(Form.partner_activity_type)


@router.message(Form.partner_activity_type)
async def process_partner_activity_type(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(partner_activity_type=message.text)
    await message.answer(TEXTS[language]['partner']['region'])  
    await state.set_state(Form.partner_region)


@router.message(Form.partner_region)
async def process_partner_region(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(partner_region=message.text)
    await message.answer(TEXTS[language]['partner']['phone'])  
    await state.set_state(Form.partner_phone)


@router.message(Form.partner_phone)
async def process_partner_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(partner_phone=message.text)
    await message.answer(TEXTS[language]['partner']['additional']) 
    await state.set_state(Form.partner_additional)


@router.message(Form.partner_additional)
async def process_partner_additional(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")
    await state.update_data(partner_additional=message.text)

    data = await state.get_data()
    confirmation_text_uz = (
        f"👤 Ismingiz: {data.get('name', 'N/A')}\n"
        f"🔧 Faoliyat turi: {data.get('partner_activity_type', 'N/A')}\n"
        f"🌍 Hudud: {data.get('partner_region', 'N/A')}\n"
        f"📞 Telefon raqamingiz: {data.get('partner_phone', 'N/A')}\n"
        f"📋 Qo'shimchalar: {data.get('partner_additional', 'N/A')}\n\n"
        f"Ma'lumotlaringiz to'g'rimi?"
    )

    confirmation_text_ru = (
        f"👤 Ваше имя: {data.get('name', 'N/A')}\n"
        f"🔧 Вид деятельности: {data.get('partner_activity_type', 'N/A')}\n"
        f"🌍 Территория: {data.get('partner_region', 'N/A')}\n"
        f"📞 Ваш номер телефона: {data.get('partner_phone', 'N/A')}\n"
        f"📋 Дополнения: {data.get('partner_additional', 'N/A')}\n\n"
        f"Ваши данные верны?"
    )

    confirmation_text = confirmation_text_uz if language == 'uz' else confirmation_text_ru
    confirm_buttons = confirm_buttons_uz if language == 'uz' else confirm_buttons_ru

    await message.answer(confirmation_text, reply_markup=confirm_buttons)
    await state.set_state(Form.confirm)


pending_messages: Dict[int, dict] = {}

@router.message(Form.confirm, F.text.in_(["✅ Ha", "✅ Да"]))
async def process_confirm(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    telegram_username = message.from_user.username
    ad_type = data.get('ad_type')
    channel_username = data.get('selected_channel_username') 
    channel_name = data.get('selected_channel_name')
    if not channel_username:
        await message.answer("Kanal tanlanmagan!")
        return
    
    if channel_username.startswith('@'):
        channel_username = channel_username[1:]
    
    if ad_type == "👨‍💼 Hodim kerak" or ad_type == "👨‍💼 Нужен сотрудник":
        announcement_text = format_employee_needed(data, language)
    elif ad_type == "💼 Ish joyi kerak" or ad_type == "💼 Нужна работа":
        announcement_text = format_job_seeker(data, language)
    elif ad_type == "🤝 Sherik kerak" or ad_type == "🤝 Нужен партнер":
        announcement_text = format_partner_needed(data, language)
    else:
        await message.answer("Noto'g'ri e'lon turi!")
        return
    
    announcement_text += f"\nPosted by: @{telegram_username}"
    
    message_key = len(pending_messages) + 1
    
    pending_messages[message_key] = {
        'announcement_text': announcement_text,
        'user_id': message.from_user.id,
        'username': telegram_username,
        'channel_username': channel_username,
        'channel_name':channel_name, 
        'language':language,
        'state_data': data
    }
    
    sent_message = await bot.send_message(
        chat_id=GROUP_ID,
        text=announcement_text,
        reply_markup=get_approval_keyboard(message_key),
        parse_mode="HTML"
    )
    
    await state.set_state(Form_Check.waiting_approval)
    await state.update_data(message_key=message_key)
    
    await message.answer(TEXTS[language]['admin_aprov'], reply_markup=ReplyKeyboardRemove()
    )

def get_approval_keyboard(message_key: int) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"approve_{message_key}"
                ),
                types.InlineKeyboardButton(
                    text="❌ Bekor qilish",
                    callback_data=f"cancel_{message_key}"
                )
            ]
        ]
    )


def format_employee_needed(data: dict, language: str) -> str:
    return (
        f"<b>👨‍💼 HODIM KERAK</b>\n\n"
        f"🎯 Talab qilingan ko'nikmalar: {data.get('employee_skills')}\n"
        f"🏢 Tashkilot nomi: {data.get('employee_firm_name')}\n"
        f"💡 Faoliyat turi: {data.get('employee_activity')}\n"
        f"👤 Mas'ul shaxs: {data.get('employee_contact_person')}\n"
        f"📞 Telefon: {data.get('employee_phone')}\n"
        f"🌍 Hudud: {data.get('employee_region')}\n"
        f"⏰ Murojaat vaqti: {data.get('employee_contact_time')}\n"
        f"📅 Ish vaqti: {data.get('employee_work_time')}\n"
        f"💰 Maosh: {data.get('employee_salary')}\n"
        f"ℹ️ Qo'shimcha: {data.get('employee_additional')}"
    )

def format_job_seeker(data: dict, language: str) -> str:
    return (
        f"<b>💼 ISH JOYI KERAK</b>\n\n"
        f"👤 Ism: {data.get('job_name')}\n"
        f"📅 Yosh: {data.get('job_age')}\n"
        f"🎯 Mutaxassislik: {data.get('job_profession')}\n"
        f"📊 Tajriba: {data.get('job_experience')}\n"
        f"📞 Telefon: {data.get('job_phone')}\n"
        f"🌍 Hudud: {data.get('job_region')}\n"
        f"💰 Kutilayotgan maosh: {data.get('job_expected_salary')}\n"
        f"ℹ️ Qo'shimcha: {data.get('job_additional')}"
    )

def format_partner_needed(data: dict, language: str) -> str:
    return (
        f"<b>🤝 SHERIK KERAK</b>\n\n"
        f"👤 Ism: {data.get('name')}\n"
        f"💡 Faoliyat turi: {data.get('partner_activity_type')}\n"
        f"🌍 Hudud: {data.get('partner_region')}\n"
        f"📞 Telefon: {data.get('partner_phone')}\n"
        f"ℹ️ Qo'shimcha: {data.get('partner_additional')}"
    )

@router.callback_query(F.data.startswith("approve_"))
async def approve_announcement(callback: types.CallbackQuery, state: FSMContext):
    chat_member = await bot.get_chat_member(
        chat_id=GROUP_ID,
        user_id=callback.from_user.id
    )

    if chat_member.status not in ["administrator", "creator"]:
        await callback.answer("Sizda e'lonlarni tasdiqlash huquqi yo'q!")
        return

    try:
        message_key = int(callback.data.split('_')[1])
        message_data = pending_messages.get(message_key)
        
        if not message_data:
            await callback.answer("Xabar topilmadi!")
            return

        announcement_text = message_data['announcement_text']
        user_id = message_data['user_id']
        channel_username = message_data['channel_username'] 
        channel_name = message_data['channel_name']
        language = message_data['language']

        await bot.send_message(
            chat_id=f"@{channel_username}",  
            text=announcement_text,
            parse_mode="HTML"
        )

        await callback.message.edit_text(
            f"{announcement_text}\n\n✅ Tasdiqlandi va {message_data['channel_username']} kanaliga joylandi",
            parse_mode="HTML"
        )
        if language == 'uz':
            await bot.send_message(
                chat_id=user_id,
                text=f"✅ Sizning e'loningiz tasdiqlandi va {channel_name} kanaliga joylandi!",
            )
        else:
            await bot.send_message(
                chat_id=user_id,
                text=f"✅ Ваше объявление одобрено и размещено на канале {channel_name}"
            )
        del pending_messages[message_key]
        
        await callback.answer("E'lon tasdiqlandi va kanalga joylandi!")
        
    except Exception as e:
        print(f"Error during approval: {str(e)}")
        await callback.answer(f"Xatolik yuz berdi: {str(e)}")
        
        
        
@router.callback_query(F.data.startswith("cancel_"))
async def cancel_announcement(callback: types.CallbackQuery, state: FSMContext):
    chat_member = await bot.get_chat_member(
        chat_id=GROUP_ID,
        user_id=callback.from_user.id
    )

    if chat_member.status not in ["administrator", "creator"]:
        await callback.answer("Sizda e'lonlarni boshqarish huquqi yo'q!")
        return

    try:
        message_key = int(callback.data.split('_')[1])
        
        message_data = pending_messages.get(message_key)
        
        if not message_data:
            await callback.answer("Xabar topilmadi!")
            return

        user_id = message_data['user_id']

        await callback.message.edit_text(
            f"{message_data['announcement_text']}\n\n❌ Bekor qilindi",
            parse_mode="HTML"
        )

        await bot.send_message(
            chat_id=user_id,
            text="❌ Sizning e'loningiz admin tomonidan bekor qilindi."
        )

        del pending_messages[message_key]
        
        await callback.answer("E'lon bekor qilindi!")
        
    except Exception as e:
        print(f"Error during cancellation: {str(e)}")
        await callback.answer(f"Xatolik yuz berdi: {str(e)}")
    

@router.message(Form.confirm, F.text.in_(["❌ Yo'q", "❌ Нет"]))
async def process_cancel(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    language = user_data.get('language', 'uz')

    main_button = main_button_uz if language == 'uz' else main_button_ru
    await message.answer(TEXTS[language]['data_cancelled'], reply_markup=main_button)

    await state.clear()