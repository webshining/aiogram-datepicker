from abc import ABC, abstractmethod
from datetime import date
from typing import Union

from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..callback_data import DatepickerCallbackData


class BaseView(ABC):
    def _get_callback(self, view: str, action: str, year: int, month: int, day: int) -> str:
        return DatepickerCallbackData(view=view, action=action, year=year, month=month, day=day).pack()

    def _insert_actions(self, markup, actions, view, year, month, day):
        if len(actions):
            builder = InlineKeyboardBuilder()
            for action in actions:
                if isinstance(action, list):
                    builder.row(*[self._get_action(view, _action, year, month, day) for _action in action])
                else:
                    builder.add(self._get_action(view, action, year, month, day))
            markup.attach(builder)
        return markup

    @abstractmethod
    def __init__(self, settings: dict, set_view):
        pass

    @abstractmethod
    def _get_action(self, view: str, action: str, year: int, month: int, day: int) -> InlineKeyboardButton:
        pass

    @property
    def datepicker_callback(self) -> DatepickerCallbackData:
        return self._datepicker_callback

    @abstractmethod
    def get_markup(self, _date: date = None) -> InlineKeyboardMarkup:
        pass

    @abstractmethod
    async def process(self, query: CallbackQuery, action: str, _date: date) -> Union[date, bool]:
        pass
