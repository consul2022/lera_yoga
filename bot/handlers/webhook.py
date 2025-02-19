import json
import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hlink
from aiohttp import web
from yookassa.domain.notification import WebhookNotification

from bot.bot import bot

logger = logging.getLogger(__name__)


async def successful_payment_approve(request):
    try:
        # Чтение данных из POST-запроса
        event_json = json.loads(await request.text())

        # Аутентификация уведомления с помощью WebhookNotification
        try:
            notification_object = WebhookNotification(event_json)
        except Exception as e:
            logger.error(f"Failed to parse notification: {e}")
            return web.json_response({"status": "error", "message": "Invalid notification"}, status=400)

        # Извлечение объекта платежа из уведомления
        payment = notification_object.object

        # Проверка типа события
        if notification_object.event != "payment.succeeded":
            logger.warning(f"Unhandled event type: {notification_object.event}")
            return web.json_response({"status": "ignored", "message": "Event ignored"}, status=200)

        # Проверка статуса платежа
        if payment.status != "succeeded":
            logger.warning(f"Payment status is not 'succeeded': {payment.status}")
            return web.json_response({"status": "ignored", "message": "Payment not succeeded"}, status=400)

        # Получение user_id из metadata платежа
        user_id = payment.metadata.get("client_id")
        if user_id is None:
            logger.error("Missing user_id in payment metadata")
            return web.json_response({"status": "error", "message": "Missing user_id"}, status=200)
        CHANNEL_ID = 1002339239961
        try:
            chat_member = await bot.get_chat_member(CHANNEL_ID, user_id)
            if chat_member.status in ["member", "administrator", "creator"]:
                return
        except Exception as e:
            pass

            # Генерируем ссылку-приглашение (одноразовую)
        invite_link = await bot.create_chat_invite_link(CHANNEL_ID, expire_date=None, member_limit=1)
        buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Присоединиться",
                                  url=invite_link.invite_link)]
        ])
        # Отправляем пользователю ссылку
        invite_text = f"Присоединяйтесь к нашему закрытому каналу"
        await bot.send_message(invite_text, reply_markup=buttons)

        return web.json_response({"status": "success", "message": "Payment processed"})

    except Exception as e:
        logger.exception("Error processing payment")
        return web.json_response({"status": "error", "message": "Internal Server Error"}, status=500)
