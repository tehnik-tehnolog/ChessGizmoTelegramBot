from CONSTANS import TELEGRAM_BOT_TOKEN
from keyboars import *

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
import asyncio



API_TOKEN = TELEGRAM_BOT_TOKEN
# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Определяем состояния
class Form(StatesGroup):
    language = State()  # Состояние выбора языка
    room = State()  # Состояние выбора платформы
    nickname = State()
    game_type = State()
    very_low_games = State()
    wait = State()
    style_report = State()
    pie_chart = State()
    heat_board = State()
    pieces_versus_schema = State()
    marked_raincloud = State()
    other_parameters_info = State
    achievements_report = State()


# /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Choose the language | Выберите язык", reply_markup=language_keyboard)
    await state.set_state(Form.language)


# Обработчик выбора языка (callback)
@dp.callback_query(Form.language)
async def handle_language(callback: types.CallbackQuery, state: FSMContext):
    # Сохраняем выбранный язык в состоянии
    language = callback.data
    messages = get_messages(language)
    await state.update_data(language=language, messages=messages)
    new_state = Form.room
    await callback.message.answer(messages[new_state.state][0])
    await asyncio.sleep(1)
    await callback.message.answer(messages[new_state.state][1], reply_markup=room_keyboard)
    await state.set_state(new_state)


# Обработчик выбора языка (callback)
@dp.callback_query(Form.room)
async def handle_room(callback: types.CallbackQuery, state: FSMContext):
    room = callback.data
    await state.update_data(room=room)
    data = await state.get_data()
    messages = data.get('messages')
    new_state = Form.nickname
    await callback.message.answer(messages[new_state.state])
    await state.set_state(new_state)


# Обработчик выбора платформы (callback)
@dp.message(Form.nickname)
async def handle_nickname(message: types.Message, state: FSMContext):
    nickname = message.text
    await state.update_data(nickname=nickname)
    data = await state.get_data()
    messages = data.get('messages')

    player_info = [nickname, 190, 20]
    GTC = GameTypeKeyboard(blitz_num=player_info[1], rapid_num=player_info[2])
    game_type_keyboard = GTC.keyboard

    new_state = Form.game_type
    await message.answer(messages[new_state.state].format(*player_info), reply_markup=game_type_keyboard)
    await state.set_state(new_state)


@dp.callback_query(Form.game_type)
async def handle_game_type(callback: types.CallbackQuery, state: FSMContext):
    blitz_num, rapid_num = map(lambda n: int(n), (callback.data.split('|')))
    await state.update_data(blitz_num=blitz_num, rapid_num=rapid_num)
    data = await state.get_data()
    messages = data.get('messages')

    new_state = Form.wait
    await callback.message.answer(messages[new_state.state])
    await state.set_state(new_state)

    # Запускаем длительный расчет
    asyncio.create_task(perform_calculation(callback, state))


# Функция для выполнения расчетов
async def perform_calculation(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language, messages, room, nickname, blitz_num, rapid_num =\
        data.get('language', 'messages', 'room', 'nickname', 'blitz_num', 'rapid_num')


    #result = await long_calculation(data)
    #await callback.message.answer(result)
    await state.set_state(Form.style_report)


# Имитация длительного расчета
async def long_calculation(data):
    await asyncio.sleep(6)  # Имитация 10-минутного расчета
    return f"Результат расчета для {data['nickname']}: ⚡ {data['blitz_num']} blitz & 🕑 {data['rapid_num']} rapid"


# Обработчик состояния ожидания
@dp.message(Form.wait)
async def handle_wait(message: types.Message, state: FSMContext):
    await message.answer("Идет расчет. Пожалуйста, подождите...")


    # await state.clear()
    # Подтверждаем обработку callback
    # await callback.answer()


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
