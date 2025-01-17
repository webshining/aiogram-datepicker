import logging
import os
from datetime import datetime, date

from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardButton, Message, CallbackQuery

from aiogram_datepicker import Datepicker, DatepickerSettings, DatepickerCustomAction

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.environ['API_TOKEN'])
dp = Dispatcher()


def _get_datepicker_settings():
    class CancelAction(DatepickerCustomAction):
        action: str = 'cancel'
        label: str = 'Cancel'

        def get_action(self, view: str, year: int, month: int, day: int) -> InlineKeyboardButton:
            return InlineKeyboardButton(text=self.label,
                                        callback_data=self._get_callback(view, self.action, year, month, day))

        async def process(self, query: CallbackQuery, view: str, _date: date) -> bool:
            if view == 'day':
                await query.message.delete()
                return False

    return DatepickerSettings(
        initial_view='month',
        initial_date=datetime.now().date(),
        views={
            'day': {
                'show_weekdays': False,
                'weekdays_labels': ['Mo', 'Tus', 'We', 'Th', 'Fr', 'Sa', 'Su'],
                'header': ['prev-year', 'days-title', 'next-year'],
                'footer': ['prev-month', 'ignore', 'next-month', ['cancel']],
            },
            'month': {
                'months_labels': ['Jan', 'Feb❤', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                'header': ['prev-year', 'year', 'next-year'],
                'footer': []
            },
            'year': {
                'header': [],
                'footer': ['prev-years', 'next-years']
            }
        },
        labels={
            'prev-year': '<<',
            'next-year': '>>',
            'prev-years': '<<',
            'next-years': '>>',
            'days-title': '{month} {year}',
            'selected-day': '{day} *',
            'selected-month': '{month} *',
            'present-day': '• {day} •',
            'prev-month': '<',
            'select': 'Select',
            'next-month': '>',
            'ignore': '⠀'
        },
        custom_actions=[CancelAction]
    )


@dp.message()
async def _main(message: Message):
    datepicker = Datepicker(_get_datepicker_settings())

    markup = datepicker.start_calendar()
    await message.answer('Select a date: ', reply_markup=markup)


@dp.callback_query(Datepicker.datepicker_callback.filter())
async def _process_datepicker(callback_query: CallbackQuery, callback_data: dict):
    datepicker = Datepicker(_get_datepicker_settings())

    _date = await datepicker.process(callback_query, callback_data)
    if _date:
        await callback_query.message.answer(_date.strftime('%d/%m/%Y'))

    await callback_query.answer()


if __name__ == '__main__':
    dp.run_polling(bot)
