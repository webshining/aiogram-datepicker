import calendar
from datetime import datetime, date
from typing import Union

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .base import BaseView
from ..helpers import merge_list
from ..settings import DatepickerSettings


class DayView(BaseView):
    def __init__(self, settings: DatepickerSettings, set_view):
        super().__init__(settings, set_view)
        self.custom_actions = []
        for custom_action in settings.custom_actions:
            self.custom_actions.append(custom_action(settings, set_view))

        self.settings = settings.views['day']
        self.labels = settings.labels
        self.set_view = set_view
        self.select_disabled = 'select' not in merge_list(self.settings['header']) \
                               and 'select' not in merge_list(self.settings['footer'])

    def _get_action(self, view: str, action: str, year: int, month: int, day: int) -> InlineKeyboardButton:
        if action in ['prev-year', 'next-year', 'prev-month', 'next-month', 'ignore']:
            return InlineKeyboardButton(text=self.labels[action],
                                        callback_data=self._get_callback(view, action, year, month, day))

        elif action == 'days-title':
            label = self.labels['days-title'].replace('{month}', calendar.month_name[month]) \
                .replace('{year}', str(year))

            return InlineKeyboardButton(text=label,
                                        callback_data=self._get_callback('month', 'set-view', year, month, day))

        elif action == 'select':
            return InlineKeyboardButton(text=self.labels[action],
                                        callback_data=self._get_callback(view, action, year, month, day))

        for custom_action in self.custom_actions:
            if custom_action.action == action:
                return custom_action.get_action(view, year, month, day)

    def get_markup(self, _date: date = None) -> InlineKeyboardMarkup:
        year, month, day = _date.year, _date.month, _date.day

        markup = InlineKeyboardBuilder()
        markup = self._insert_actions(markup, self.settings['header'], 'day', year, month, day)

        if self.settings['show_weekdays']:
            builder = InlineKeyboardBuilder()
            builder.add(*[InlineKeyboardButton(text=week_day,
                                               callback_data=self._get_callback('day', 'ignore', year, month, day))
                          for week_day in self.settings['weekdays_labels']])
            markup.attach(builder)

        month_calendar = calendar.monthcalendar(year, month)
        builder = InlineKeyboardBuilder()
        for week in month_calendar:
            for week_day in week:
                if week_day == 0:
                    builder.add(
                        InlineKeyboardButton(text=' ',
                                             callback_data=self._get_callback('day', 'ignore', year, month, day)))
                    continue

                label = f'{week_day}'
                if date(year, month, week_day) == _date and not self.select_disabled:
                    label = f'{week_day} *'
                elif date(year, month, week_day) == datetime.now().date():
                    label = f'• {week_day} •'

                builder.add(InlineKeyboardButton(
                    text=label, callback_data=self._get_callback('day', 'set-day', year, month, week_day)
                ))
        builder.adjust(7)
        markup.attach(builder)

        markup = self._insert_actions(markup, self.settings['footer'], 'day', year, month, day)

        return markup.as_markup()

    async def process(self, query: CallbackQuery, action: str, _date: date) -> Union[date, bool]:
        if action == 'select':
            return _date

        elif action == 'set-day':
            if self.select_disabled:
                return _date
            await query.message.edit_reply_markup(reply_markup=self.get_markup(_date))

        elif action == 'prev-year':
            prev_date = date(_date.year - 1, _date.month, _date.day)
            await query.message.edit_reply_markup(reply_markup=self.get_markup(prev_date))

        elif action == 'next-year':
            next_date = date(_date.year + 1, _date.month, _date.day)
            await query.message.edit_reply_markup(reply_markup=self.get_markup(next_date))

        elif action == 'prev-month':
            prev_date = date(_date.year - int(_date.month == 1), 12 if _date.month == 1 else _date.month - 1, _date.day)
            await query.message.edit_reply_markup(reply_markup=self.get_markup(prev_date))

        elif action == 'next-month':
            next_date = date(_date.year + int(_date.month == 12), ((_date.month % 12) + 1), _date.day)
            await query.message.edit_reply_markup(reply_markup=self.get_markup(next_date))

        else:
            for custom_action in self.custom_actions:
                if custom_action.action == action:
                    return await custom_action.process(query, 'day', _date)

        return False
