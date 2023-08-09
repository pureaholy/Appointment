import utils.database as db
import os

from aiogram import types
from aiogram.dispatcher import filters, FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.admin import admin_keyboard
from keyboards.client import start_keyboard


async def show_all_dates(message: types.Message, dates: list):
    if message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
        keyboard = InlineKeyboardMarkup(row_width=1)
        for date_tuple in dates:
            date = date_tuple[0]

            button_text = f"{date} ❌"
            callback_data = f"delete_date#{date}"
            keyboard.add(InlineKeyboardButton(button_text, callback_data=callback_data))
        if not dates:
            pass
        else:
            await message.answer("Доступные даты:", reply_markup=keyboard)

    elif message.from_user.id != int(os.getenv('SUDO_ID')):
        if not dates:
            pass
        else:
            date_str = '\n'.join(date_tuple[0] for date_tuple in dates)
            await message.answer(f'Доступные даты: \n{date_str}')


def setup(dp, bot):
    @dp.message_handler(commands=['start'])
    async def cmd_start(message: types.Message):
        if message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
            await message.answer('Привет Босс, вы вошли в Админ-панель',
                                 reply_markup=admin_keyboard)
        else:
            await message.answer(f'{message.from_user.first_name}, привет!',
                                 reply_markup=start_keyboard)

    @dp.message_handler(text='Главное меню')
    async def cmd_panel(message: types.Message):
        if message.from_user.id != int(os.getenv('SUDO_ID')):
            await message.answer('Вы вернулись в главное меню', reply_markup=start_keyboard)

        elif message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
            await message.answer('Вы вернулись в главное меню', reply_markup=admin_keyboard)

    @dp.message_handler(filters.Text(equals='Помощь'))
    async def cmd_help(message: types.Message):
        await message.answer('Возникли проблемы в работе бота?\n'
                             'Напиши мне в pm')

    @dp.message_handler(commands=['help'])
    async def cmd_help(message: types.Message):
        await message.answer('Возникли проблемы в работе бота?\n'
                             'Напиши мне в pm')

    @dp.message_handler(text='Отмена', state='*')
    async def cmd_panel(message: types.Message, state: FSMContext):
        if message.from_user.id != int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
            if state is None:
                return

            await state.finish()
            await message.answer('Вы вернулись обратно', reply_markup=start_keyboard)

        elif message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
            if state is None:
                return

            await state.finish()
            await message.answer('Вы вернулись обратно', reply_markup=admin_keyboard)
