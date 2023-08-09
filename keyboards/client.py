from aiogram import types
from aiogram.utils.callback_data import CallbackData

clients_date_cb = CallbackData('product', 'id', 'action')

start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
    'Услуги', 'Доступные даты', 'Помощь'
).add('Обо мне')

service_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
    'Коллагенирование ресниц', 'Брови'
).add('Отмена')

price_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True).row(
    types.KeyboardButton('Записаться')
).row('Главное меню')


def get_admin_dates_ikb(data):
    dates_ik = types.InlineKeyboardMarkup()

    for i in map(lambda x: str(x[0]), data):
        dates_ik.add(types.InlineKeyboardButton(text=i, callback_data=i))
    return dates_ik
