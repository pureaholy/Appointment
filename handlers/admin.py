import os
from aiogram import types
from aiogram.dispatcher import filters, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import utils.database as db
from keyboards.admin import user_cb, get_edit_ikb, admin_keyboard
from keyboards.basic import cancel_button


class NewDate(StatesGroup):
    date_admin = State()


def setup(dp, bot):
    @dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('delete_date#'))
    async def cb_delete_date(callback_query: types.CallbackQuery):
        date_to_delete = callback_query.data.split('#')[1]
        await db.delete_date(date_to_delete)

        await callback_query.answer()
        await callback_query.message.edit_text(f"Дата {date_to_delete} была удалена.")

    @dp.callback_query_handler(user_cb.filter(action='delete'))
    async def cb_delete_user(callback: types.CallbackQuery, callback_data: dict):
        if callback.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(callback.from_user.id):
            await db.delete_user(callback_data['id'])
            await callback.answer()
            await callback.message.reply('Запись была удалена')

    @dp.message_handler(filters.Text(equals='Админ-панель'))
    async def cmd_admin(message: types.Message):
        if message.from_user.id != int(os.getenv('SUDO_ID')):
            await message.answer('Нет доступа.')

        elif message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
            await message.answer('Админ-панель открыта', reply_markup=admin_keyboard)

    @dp.message_handler(text='Добавить дату/время')
    async def add_date(message: types.Message):
        if message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
            await NewDate.date_admin.set()
            await message.answer('Напишите дату и время\nМожно также через строчку '
                                 'Например:\n01.01.2023\n02.02.2023\nи т.д...', reply_markup=cancel_button)

    @dp.message_handler(state=NewDate.date_admin)
    async def cmd_add_date(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if 'date_admin' in data:
                data['date_admin'].extend(message.text.split('\n'))
            else:
                data['date_admin'] = message.text.split('\n')
        await message.answer('Дата и время были успешно записаны', reply_markup=admin_keyboard)

        await db.write_date(state)

        await state.finish()

    async def show_all_clients(message: types.Message, clients: list):
        for client in clients:
            client_info = f"ID заказа: {client[0]}\n" \
                          f"Тип услуги: {client[1]}\n" \
                          f"Имя: {client[2]} {client[3]}\n" \
                          f"Дата: {client[4]}\n" \
                          f"Номер: {client[5]}"
            await bot.send_message(chat_id=message.chat.id,
                                   text=client_info,
                                   reply_markup=get_edit_ikb(client[0])
                                   )

    @dp.message_handler(text='Все записи')
    async def cmd_get_all_clients(message: types.Message):
        if message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
            clients = await db.get_all_clients()
            if not clients:
                await message.answer('На данный момент нету записей')

            await show_all_clients(message, clients)

    @dp.message_handler(commands=['aadmin'])
    async def cmd_add_admin(message: types.Message):
        args = message.get_args().strip()
        if message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
            user_id = int(args)
            result = await db.add_admin(user_id)
            chat_info = await bot.get_chat(user_id)
            if result:
                await message.reply(f"Пользователь с {chat_info.first_name}  добавлен в админы")
            else:
                await message.reply(f'{chat_info.first_name} уже админ!')
        if not args.isdigit():
            await message.reply("Пожалуйста, укажите корректный user_id администратора.")
            return

    @dp.message_handler(commands=['dadmin'])
    async def cmd_remove_admin(message: types.Message):
        args = message.get_args().strip()
        if message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
            user_id = int(args)
            result = await db.remove_admin(user_id)
            if result:
                await message.reply(
                    f"Пользователь с user_id {message.from_user.first_name} удален из списка администраторов.")
            else:
                await message.reply(f"{message.from_user.first_name} не является админом!"
                                    )
        if not args.isdigit():
            await message.reply("Пожалуйста, укажите корректный user_id администратора для удаления.")
            return
