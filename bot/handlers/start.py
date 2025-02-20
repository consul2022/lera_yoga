from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

from bot.bot import bot

start_router = Router()


@start_router.message(CommandStart())
async def hello(message):
    buttons = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Пробный урок", callback_data="start|lesson")],
                         [InlineKeyboardButton(text="Оформить подписку", callback_data="start|subscription")],
                         #[InlineKeyboardButton(text="Купить сертификат", callback_data="start|courses")],
                         [InlineKeyboardButton(text="Отдел заботы❤️", url="https://t.me/iam_leraaa")]])

    await message.answer_photo(photo=FSInputFile("images/IMG_9052.JPEG"), caption="""<b>Здравствуйте!</b>

Я — Валерия Дубатова, преподаватель хатха-йоги с психологическим образованием. Рада видеть тебя здесь! 

Что вас ждет?  
- Мой авторский курс хатха-йоги для трансформации тела и духа.  
- Короткие мини-курсы для тех, где результаты ощутимы уже после первых занятий.  
- Бесплатные трекеры привычек и вводный урок, чтобы вы могли попробовать йогу уже сегодня!  
- Подарочные сертификаты — отличный способ подарить близким моменты заботы и покоя.

Почему это работает?  
Все курсы объединяют мой уникальный опыт, древние практики йоги с современными знаниями психологии, помогая вам:  
- Снизить уровень стресса.  
- Улучшить гибкость и здоровье тела.  
- Почувствовать гармонию и баланс в жизни.  
- Разбудить свою внутреннюю силу и желания.
- Приблизиться к своим настоящим желаниям и целям.

Вы готовы начать свою практику и получить подарок? Нажмите на кнопку ниже, и выберите свой курс!

До встречи на коврике!"""
                               , reply_markup=buttons)
