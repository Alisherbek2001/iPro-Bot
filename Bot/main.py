import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from middleware import SubscriptionCheckMiddleware
from handlers import router

async def main():
    logging.basicConfig(level=logging.INFO)
    
    default = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=BOT_TOKEN, default=default)
    dp = Dispatcher()
    
    router.message.middleware(SubscriptionCheckMiddleware())
    router.callback_query.middleware(SubscriptionCheckMiddleware())
    
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
