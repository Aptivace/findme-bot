from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.filters.callback_data import CallbackData


class Anonimation(CallbackData, prefix='ano'): # создание класса для обработки колбэка инлайн-кнопок
    action: str

def anonim(): # функция создания инлайн-кнопок
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='📢 Публично', callback_data=Anonimation(action='send').pack()),
        InlineKeyboardButton(text='😶‍🌫️ Анонимно', callback_data=Anonimation(action='anon').pack()),
        InlineKeyboardButton(text='🗑️ Отменить объявление', callback_data=Anonimation(action='otkat').pack()),
        width=1 # этот параметр отвечает за кол-во кнопок в одном столбце
    )
    return builder.as_markup() # возвращаем инлайн-клавиатуру


class Postination(CallbackData, prefix='post'):
    action: str

def choose_type():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='📸 Найди меня', callback_data=Postination(action='naydi').pack()),
        InlineKeyboardButton(text='🔎 Потеряшка', callback_data=Postination(action='poteryashka').pack()),
        width=1
    )
    return builder.as_markup()