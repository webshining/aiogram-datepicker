from abc import ABC, abstractmethod
from datetime import date

from aiogram.types import CallbackQuery, InlineKeyboardButton

from .callback_data import DatepickerCallbackData


class DatepickerCustomAction(ABC):
    action: str
    label: str

    def __init__(self, settings, set_view):
        super().__init__()
        self.settings = settings
        self.set_view = set_view

    def _get_callback(self, view: str, action: str, year: int, month: int, day: int) -> str:
        return DatepickerCallbackData(view=view, action=action, year=year, month=month,
                                      day=day).pack()

    @abstractmethod
    def get_action(self, view: str, year: int, month: int, day: int) -> InlineKeyboardButton:
        pass

    @abstractmethod
    async def process(self, query: CallbackQuery, view: str, _date: date) -> bool:
        pass
