import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery, Message

from aiogram_datepicker import Datepicker, DatepickerSettings

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.environ['API_TOKEN'])
dp = Dispatcher()


@dp.message()
async def _main(message: Message):
    datepicker = Datepicker(DatepickerSettings())

    markup = datepicker.start_calendar()

    await message.answer('Select a date: ', reply_markup=markup)


@dp.callback_query(Datepicker.datepicker_callback.filter())
async def _process_datepicker(callback_query: CallbackQuery, callback_data: dict):
    datepicker = Datepicker(DatepickerSettings())

    _date = await datepicker.process(callback_query, callback_data)
    if _date:
        await callback_query.message.answer(_date.strftime('%d/%m/%Y'))

    await callback_query.answer()


if __name__ == '__main__':
    dp.run_polling(bot)
