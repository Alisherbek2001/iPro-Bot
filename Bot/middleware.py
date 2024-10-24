from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Callable, Any, Awaitable, Union
from utils import check_all_subscriptions
from texts import TEXTS

class SubscriptionCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        bot = data['bot']
        
        final_status, btn = await check_all_subscriptions(user_id, bot)
        
        if not final_status:
            if isinstance(event, CallbackQuery):
                await event.message.answer(
                    TEXTS['bilingual']['subscribe_channels'],
                    disable_web_page_preview=True,
                    reply_markup=btn
                )
                await event.answer()
            else:
                await event.answer(
                    TEXTS['bilingual']['subscribe_channels'],
                    disable_web_page_preview=True,
                    reply_markup=btn
                )
            return
        
        return await handler(event, data)
