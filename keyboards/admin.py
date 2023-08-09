from aiogram import types
from aiogram.utils.callback_data import CallbackData

from keyboards.client import clients_date_cb

user_cb = CallbackData('product', 'id', 'action')

start_admin_buttons = [
    'Услуги', 'Доступные даты', 'Помощь', 'Админ-панель'
]
start_admin_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*start_admin_buttons)

admin_buttons = [
    'Добавить дату/время', 'Доступные даты', 'Все записи'
]
admin_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*admin_buttons).row('Главное меню')


def get_edit_ikb(user_id: int) -> types.InlineKeyboardMarkup:
    ikb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton('Удалить запись', callback_data=user_cb.new(user_id, 'delete'))]
    ])
    return ikb


def get_dates_ikb(user_id: int) -> types.InlineKeyboardMarkup:
    ikb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton('Удалить дату', callback_data=clients_date_cb.new(user_id, 'delete_date'))]
    ])
    return ikb
