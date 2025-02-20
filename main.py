import logging
import os
import asyncio
import ssl
import requests
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from dotenv import load_dotenv
from bot.bot import bot
from bot.handlers.callback import callback_router
from bot.handlers.start import start_router
from bot.handlers.webhook import successful_payment_approve
from yookassa import Configuration

# Загрузка переменных окружения
load_dotenv()

# Укажите ваш Shop ID и секретный ключ
Configuration.account_id = os.getenv('SHOP_ID')
Configuration.secret_key = os.getenv('YOOKASSA_ID')

SSL_CERTFILE = "/etc/letsencrypt/live/yogalera.ru/fullchain.pem"
SSL_KEYFILE = "/etc/letsencrypt/live/yogalera.ru/privkey.pem"

logger = logging.getLogger(__name__)



dp = Dispatcher(store=MemoryStorage())
dp.include_router(start_router)
dp.include_router(callback_router)


async def start_web_server():
    """
    Запускаем aiohttp Web-сервер на 443 (с SSL) или на 8080, если сертификаты не найдены.
    """
    app = web.Application()

    # Роуты
    app.router.add_post("/payment/success", successful_payment_approve)


    runner = web.AppRunner(app)
    await runner.setup()

    try:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(
            certfile=SSL_CERTFILE,
            keyfile=SSL_KEYFILE
        )
        site = web.TCPSite(runner, '0.0.0.0', 443, ssl_context=ssl_context)
        logger.info("Запускаем веб-сервер на 443 с SSL")
    except Exception as e:
        logger.error(f"Ошибка настройки SSL, запускаем без SSL: {e}")
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        logger.info("Запускаем веб-сервер на 8080 без SSL")

    await site.start()


async def main():
    logger.info("Starting bot and web server")

    # Отключаем вебхук, чтобы бот работал через polling
    await bot.delete_webhook(drop_pending_updates=True)

    # Параллельный запуск бота (polling) и веб-сервера
    await asyncio.gather(
        dp.start_polling(bot),
        start_web_server()
    )

if __name__ == '__main__':
    asyncio.run(main())