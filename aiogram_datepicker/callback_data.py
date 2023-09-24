from aiogram.filters.callback_data import CallbackData


class DatepickerCallbackData(CallbackData, prefix="datepicker"):
    view: str
    action: str
    year: int | str
    month: int | str
    day: int | str
