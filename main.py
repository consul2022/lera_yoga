import logging
import os

import asyncio
import ssl

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

load_dotenv()

from yookassa import Configuration, Payment

# Укажите ваш Shop ID и секретный ключ
Configuration.account_id = os.getenv('SHOP_ID')
Configuration.secret_key = os.getenv('YOOKASSA_ID')

SSL_CERTFILE = "/etc/letsencrypt/live/yogalera.ru/fullchain.pem"
SSL_KEYFILE = "/etc/letsencrypt/live/yogalera.ru/privkey.pem"
@web.middleware
async def cors_middleware(request, handler):
    # Если это preflight-запрос (OPTIONS), возвращаем пустой ответ с заголовками CORS
    if request.method == "OPTIONS":
        return web.Response(
            status=204,  # Нет содержимого
            headers={
                "Access-Control-Allow-Origin": "*",  # Разрешаем все источники
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",  # Разрешённые методы
                "Access-Control-Allow-Headers": "Authorization, Content-Type",  # Разрешённые заголовки
            },
        )

    # Обрабатываем остальные запросы (например, GET, POST)
    response = await handler(request)
    # Добавляем заголовки CORS в ответ
    response.headers["Access-Control-Allow-Origin"] = "*"  # Разрешаем все источники
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    return response


logger = logging.getLogger(__name__)


async def on_startup(app):
    bot = app["bot"]
    await bot.set_webhook(os.getenv("WEBHOOK_URL"))
    logger.info(f"Webhook set to: {os.getenv('WEBHOOK_URL')}")


async def on_shutdown(app):
    bot = app["bot"]
    await bot.delete_webhook()
    await bot.session.close()
    logger.info("Webhook deleted and aiohttp session closed.")


async def main():
    dp = Dispatcher(store=MemoryStorage())
    dp.include_router(start_router)
    dp.include_router(callback_router)
    app = web.Application(middlewares=[cors_middleware])
    app["bot"] = bot
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    app.router.add_post("/payment/success",successful_payment_approve)
    try:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(SSL_CERTFILE, SSL_KEYFILE)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(
            runner,
            os.getenv("WEBHOOK_URL"),
            443,
            ssl_context=ssl_context
        )
        await site.start()
    except:
        pass
    await dp.start_polling(bot)


asyncio.run(main())
