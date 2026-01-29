from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_keyboard(
        *buttons: str,
        placeholder: str | None = None,
        request_contact: int | None = None,
        request_location: int | None = None,
        sizes: tuple[int] = (2,)
):
    keyboard = ReplyKeyboardBuilder()
    for index, text in enumerate(buttons,start=0):
        if request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))
        elif request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, input_field_placeholder=placeholder)