import os

import aiogram.utils.exceptions
from aiogram import types
from aiogram.dispatcher import filters, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import telegram.error

from keyboards.admin import admin_keyboard
from keyboards.basic import cancel_button
from .basic import show_all_dates

from keyboards.client import price_buttons, start_keyboard, get_admin_dates_ikb, service_keyboard
import utils.database as db


class NewOrder(StatesGroup):
    service = State()
    name = State()
    surname = State()
    date_client = State()
    phone = State()


class NewDate(StatesGroup):
    date_admin = State()


def setup(dp, bot):
    @dp.message_handler(text='Доступные даты')
    async def cmd_show_all_dates(message: types.Message):
        dates = await db.get_admin_date()
        if not dates:
            await message.answer('На данный момент нет доступных дат')
        await show_all_dates(message, dates)
        if message.from_user.id != int(os.getenv('SUDO_ID')):
            if not dates:
                pass
            else:
                await message.answer(
                    'Уважаемый клиент, если ни одна из предложенных дат вам не подходит,'
                    ' мы предлагаем связаться с мастером и договориться о более удобной для вас дате и времени.\n'
                    f'<i> Спасибо за понимание! </i>',
                    parse_mode='HTML',
                    reply_markup=price_buttons
                )

    @dp.message_handler(filters.Text(equals='Услуги'))
    async def cmd_services(message: types.Message):
        price = '50 рублей'
        service = 'Коллагенирование ресниц'
        text = f'Услуга: {service}\n Цена услуги: <b>{price}</b>'
        await message.answer(text, parse_mode='HTML')

        price1 = '15 рублей'
        service1 = 'Брови'
        text1 = f'Услуга: {service1}\n Цена услуги: <b>{price1}</b>'
        await message.answer(text1, parse_mode='HTML', reply_markup=price_buttons)

    @dp.message_handler(text='Записаться')
    async def cmd_add_service(message: types.Message):
        await NewOrder.service.set()

        await message.answer('Выберите услугу:', reply_markup=service_keyboard)

    @dp.message_handler(state=NewOrder.service)
    async def add_service(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['service'] = message.text

        await NewOrder.next()
        await message.answer('Напишите ваше имя:', reply_markup=cancel_button)

    @dp.message_handler(state=NewOrder.name)
    async def add_service(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['name'] = message.text

        await NewOrder.next()
        await message.answer('Напишите вашу фамилию:', reply_markup=cancel_button)

    @dp.message_handler(state=NewOrder.surname)
    async def add_service(message: types.Message, state: FSMContext):
        date_admin = await db.get_admin_date()
        async with state.proxy() as data:
            data['surname'] = message.text
        await NewOrder.next()
        if date_admin is None or len(date_admin) == 0:
            await message.answer('На данный момент нет доступных дат')
        else:
            await message.answer('выберите дату:', reply_markup=get_admin_dates_ikb(date_admin))

    @dp.callback_query_handler(state=NewOrder.date_client)
    async def callback_query_keyboard(call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            data['date_client'] = call.data

        await call.answer()
        await NewOrder.next()
        await call.message.answer('Введите ваш номер телефона', reply_markup=cancel_button)

    @dp.message_handler(state=NewOrder.phone)
    async def add_service(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['phone'] = message.text
        if message.from_user.id != int(os.getenv('SUDO_ID')):
            await message.answer('Вы записаны, как только мастер будет свободен, он с вами свяжется!\n'
                                 'Возникли вопросы?\n'
                                 ' Напиши мне в pm', reply_markup=start_keyboard)
        else:
            await message.answer('Вы на главном меню', reply_markup=admin_keyboard)
        await db.add_item(state)
        await state.finish()

        try:
            await bot.send_message(chat_id='6468691028', text='К вам новый клиент')

        except (telegram.error.BadRequest, aiogram.utils.exceptions.ChatNotFound) as e:

            print('При отправке сообщения произошла ошибка:', e)
