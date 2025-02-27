from CONSTANS import TELEGRAM_BOT_TOKEN
from keyboars import *

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
import asyncio

import pandas as pd
from chess_gizmo_functions import PlayerInfo, PopulateDB, HOST, USER, PASSWORD, TGBotDataGenerator, check_database_exists




API_TOKEN = TELEGRAM_BOT_TOKEN
# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Определяем состояния
class Form(StatesGroup):
    language = State()  # Состояние выбора языка
    room = State()  # Состояние выбора платформы
    nickname = State()
    database_exists = State()
    game_type = State()
    num_games = State()
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
@dp.message(Command('start'))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer('Choose the language | Выберите язык', reply_markup=language_keyboard)
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
async def handle_nickname(message: types.Message, callback: types.CallbackQuery,  state: FSMContext):
    output_nickname = message.text
    player_info = PlayerInfo(output_nickname)
    nickname = player_info.username
    await state.update_data(nickname=nickname, blitz_rating=player_info.blitz_rating, rapid_rating=player_info.rapid_rating)
    data = await state.get_data()
    messages = data.get('messages')
    database_type = check_database_exists(username=nickname)
    if database_type is not None:
        new_state = Form.database_exists
        await state.update_data(game_type=database_type)
        await message.answer(messages[new_state.state], reply_markup=database_exists_keyboard)
        await state.set_state(new_state)
    else:
        new_state = Form.game_type
        await state.set_state(new_state)
        await handle_game_type(callback, state)

@dp.callback_query(Form.game_type)
async def handle_game_type(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    messages = data.get('messages')
    nickname = data.get('nickname')
    blitz_num = data.get('blitz_num')
    rapid_num = data.get('rapid_num')
    game_type_keyboard = GameTypeKeyboard(blitz_num=blitz_num, rapid_num=rapid_num).keyboard
    player_info_list = [nickname, blitz_num, rapid_num]
    await callback.answer(messages[Form.game_type.state].format(*player_info_list), reply_markup=game_type_keyboard)
    await state.set_state(Form.num_games)



@dp.callback_query(Form.database_exists)
async def handle_database_exists(callback: types.CallbackQuery, state: FSMContext):
    operation = callback.data
    data = await state.get_data()
    nickname = data.get('nickname')
    game_type = data.get('game_type')
    if operation == 'load':
        language = data.get('language')
        messages = data.get('messages')
        room = data.get('room')
        blitz_num = data.get('blitz_num')
        rapid_num = data.get('rapid_num')
        blitz_rating = data.get('blitz_rating')
        rapid_rating = data.get('rapid_rating')
        main_rating = blitz_rating if game_type == 'blitz' else rapid_rating
        TGBotDataGenerator(language=language, nickname=nickname, messages=messages, room=room, blitz_num=blitz_num,
                           rapid_num=rapid_num, game_type=game_type, rating=main_rating, rapid_rating=rapid_rating,
                           calculate=False)
    elif operation == 'generate':
        populate_db = PopulateDB(db_name=f'chess_{game_type}_{nickname}')
        populate_db.drop_database()
        await state.set_state(Form.game_type)
        await handle_game_type


@dp.callback_query(Form.num_games)
async def handle_num_games(callback: types.CallbackQuery, state: FSMContext):
    blitz_num, rapid_num, game_type_index = map(lambda n: int(n), (callback.data.split('|')))
    game_type = ['blitz', 'rapid'][game_type_index]
    await state.update_data(blitz_num=blitz_num, rapid_num=rapid_num, game_type=game_type)
    data = await state.get_data()
    messages = data.get('messages')

    new_state = Form.wait
    await callback.message.answer(messages[new_state.state])
    await state.set_state(new_state)

    # Запускаем длительный расчет
    asyncio.create_task(perform_calculation(state))


# Функция для выполнения расчетов
async def perform_calculation(state: FSMContext):
    data = await state.get_data()
    language = data.get('language')
    messages = data.get('messages')
    room = data.get('room')
    nickname = data.get('nickname')
    blitz_num = data.get('blitz_num')
    rapid_num = data.get('rapid_num')
    game_type = data.get('game_type')
    blitz_rating = data.get('blitz_rating')
    rapid_rating = data.get('rapid_rating')

    main_rating = blitz_rating if game_type == 'blitz' else rapid_rating
    TGBotDataGenerator(language=language, nickname=nickname, messages=messages, room=room, blitz_num=blitz_num,
                       rapid_num=rapid_num, game_type=game_type, rating=main_rating, rapid_rating=rapid_rating)

    await state.set_state(Form.style_report)


# Обработчик состояния ожидания
@dp.message(Form.wait)
async def handle_wait(message: types.Message, state: FSMContext):
    data = await state.get_data()
    messages = data.get('messages')
    await message.answer('Идет расчет. Пожалуйста, подождите...')


    # await state.clear()
    # Подтверждаем обработку callback
    # await callback.answer()


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
