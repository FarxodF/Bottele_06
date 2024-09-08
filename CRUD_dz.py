import logging
import random

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from crud_functions import initiate_db, get_all_products

from CRUD_bd import *

logger = logging.getLogger(__name__)

bot = Bot(token='KEY')
dp = Dispatcher(bot, storage=MemoryStorage())

initiate_db()


class UserState(StatesGroup):
    product_selection = State()


def create_product_rows():
    conn = sqlite3.connect('initiate_db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Products VALUES (null, ?, ?, ?)', ('ВитаминA', 'Качество №1.', 100))
    cursor.execute('INSERT INTO Products VALUES (null, ?, ?, ?)', ('ВитаминC', 'Импортная.', 200))
    cursor.execute('INSERT INTO Products VALUES (null, ?, ?, ?)', ('ВитаминD', 'БАД', 300))
    cursor.execute('INSERT INTO Products VALUES (null, ?, ?, ?)', ('ВитаминE', '*НОВИНКА*.', 400))
    conn.commit()
    conn.close()


create_product_rows()


# Основные команды
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Добро пожаловать! Нажмите кнопку, чтобы выбрать товар:", reply_markup=product_inline_kb)
    await UserState.product_selection.set()


# Обработка выбора товара
@dp.callback_query_handler(state=UserState.product_selection)
async def handle_product_selection(call: types.CallbackQuery, state: FSMContext):
    all_products = get_all_products()
    current_state = await state.get_state()
    if current_state is None:
        await call.message.reply("Пожалуйста, выберите товар.")
        return

    for product in all_products:
        await call.message.reply(
            f"Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}")

    await call.message.reply("Продолжить выбор?", reply_markup=product_inline_kb)


# Обработка покупки
@dp.callback_query_handler(text='product_buying')
async def handle_product_buying(call: types.CallbackQuery):
    await call.message.reply("Вы успешно приобрели продукт!")


# Отмена выбора товара
@dp.message_handler(text='Отменить')
async def cancel_product_selection(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Выбор отменен.")


product_inline_kb = InlineKeyboardMarkup(row_width=1)
product_inline_kb.add(InlineKeyboardButton("ВитаминA", callback_data='product_buying'))
product_inline_kb.add(InlineKeyboardButton("ВитаминC", callback_data='product_buying'))
product_inline_kb.add(InlineKeyboardButton("ВитаминD", callback_data='product_buying'))
product_inline_kb.add(InlineKeyboardButton("ВитаминE", callback_data='product_buying'))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
