from keyboars import *
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InputMediaPhoto, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Union
import asyncio
import io

from chess_gizmo_functions import PlayerInfo, PopulateDB, ChessStorage, HOST, USER, PASSWORD, TGBotDataGenerator, check_database_exists

load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# Initializing the bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Define states
class Form(StatesGroup):
    language = State()
    room = State()
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


@dp.callback_query(Form.language)
async def handle_language(callback: types.CallbackQuery, state: FSMContext):
    # Save the selected language in the state
    language = callback.data
    messages = get_messages(language)
    await state.update_data(language=language, messages=messages)
    new_state = Form.room
    await callback.message.answer(messages[new_state.state][0])
    await asyncio.sleep(1)
    await callback.message.answer(messages[new_state.state][1], reply_markup=room_keyboard)
    await state.set_state(new_state)


@dp.callback_query(Form.room)
async def handle_room(callback: types.CallbackQuery, state: FSMContext):
    room = callback.data
    await state.update_data(room=room)
    data = await state.get_data()
    messages = data.get('messages')
    new_state = Form.nickname
    await callback.message.answer(messages[new_state.state])
    await state.set_state(new_state)


@dp.message(Form.nickname)
async def handle_nickname(message: types.Message,  state: FSMContext):
    output_nickname = message.text
    player_info = PlayerInfo(output_nickname)
    nickname = player_info.username
    await state.update_data(nickname=nickname,blitz_num=player_info.blitz_num, rapid_num=player_info.rapid_num,
                            blitz_rating=player_info.blitz_rating, rapid_rating=player_info.rapid_rating)
    data = await state.get_data()
    language = data.get('language')
    messages = data.get('messages')
    database_type = check_database_exists(username=nickname.lower())
    if database_type is not None:
        new_state = Form.database_exists
        await state.update_data(game_type=database_type)
        await message.answer(messages[new_state.state].format(nickname), reply_markup=database_exists_keyboard(language))
        await state.set_state(new_state)
    else:
        new_state = Form.game_type
        await state.set_state(new_state)
        await handle_game_type(message, state)


@dp.callback_query(Form.game_type)
async def handle_game_type(event: Union[types.Message, types.CallbackQuery], state: FSMContext):
    data = await state.get_data()
    messages = data.get('messages')
    nickname = data.get('nickname')
    blitz_num = data.get('blitz_num')
    rapid_num = data.get('rapid_num')
    game_type_keyboard = GameTypeKeyboard(blitz_num=blitz_num, rapid_num=rapid_num).keyboard
    player_info_list = [nickname, blitz_num, rapid_num]
    if isinstance(event, types.Message):
        await event.answer(
            messages[Form.game_type.state].format(*player_info_list),
            reply_markup=game_type_keyboard
        )
    elif isinstance(event, types.CallbackQuery):
        await event.message.edit_text(
            messages[Form.game_type.state].format(*player_info_list),
            reply_markup=game_type_keyboard
        )
        await event.answer()
    await state.set_state(Form.num_games)


@dp.callback_query(Form.database_exists)
async def handle_database_exists(callback: types.CallbackQuery, state: FSMContext):
    operation = callback.data
    data = await state.get_data()
    nickname = data.get('nickname')
    game_type = data.get('game_type')
    if operation == 'load':
        language = data.get('language')
        storage = ChessStorage()
        style_dict = await storage.download_json(f'{nickname}/style_dict.json')

        # Preparing the style line
        player_dict = RU_ru_player_dict if language == 'RU_ru' else EN_en_player_dict
        style_players_list = [player_dict.get(k, k) for k in style_dict.keys()]
        style_players_str = ', '.join(style_players_list)

        await state.update_data(
            style_players_str=style_players_str,
            style_dict=style_dict
        )

        await state.set_state(Form.style_report)
        await callback.answer()
        await handle_style_report(callback.message, state)

    elif operation == 'generate':
        populate_db = PopulateDB(schema_name=f'chess_{game_type}_{nickname.lower()}')
        populate_db.drop_database()
        new_state = Form.game_type
        await state.set_state(new_state)
        await handle_game_type(callback, state)


@dp.callback_query(Form.num_games)
async def handle_num_games(callback: types.CallbackQuery, state: FSMContext):
    blitz_num, rapid_num, game_type_index = map(int, callback.data.split('|'))
    game_type = ['blitz', 'rapid'][game_type_index]

    await state.update_data(
        blitz_num=blitz_num,
        rapid_num=rapid_num,
        game_type=game_type
    )

    data = await state.get_data()
    messages = data['messages']
    new_state = Form.wait

    await callback.message.answer(messages[new_state.state])
    await callback.message.answer_sticker(sticker_id_dict['Wait'])
    await state.set_state(new_state)

    # Run the calculation in the background
    asyncio.create_task(perform_calculation(state, callback.message))


async def perform_calculation(state: FSMContext, message: types.Message):
    data = await state.get_data()
    language = data['language']
    messages = data['messages']
    room = data['room']
    nickname = data['nickname']
    blitz_num = data['blitz_num']
    rapid_num = data['rapid_num']
    game_type = data['game_type']
    blitz_rating = data['blitz_rating']
    rapid_rating = data['rapid_rating']

    main_rating = blitz_rating if game_type == 'blitz' else rapid_rating

    # Data generation
    generator = TGBotDataGenerator(
        language=language,
        nickname=nickname,
        messages=messages,
        room=room,
        blitz_num=blitz_num,
        rapid_num=rapid_num,
        game_type=game_type,
        rating=main_rating
    )
    style_dict = generator.create_visualization()

    # Preparing the style line
    player_dict = RU_ru_player_dict if language == 'RU_ru' else EN_en_player_dict
    style_players_list = [player_dict.get(k, k) for k in style_dict.keys()]
    style_players_str = ', '.join(style_players_list)

    # Saving data in state
    await state.update_data(
        style_players_str=style_players_str,
        style_dict=style_dict
    )

    await state.set_state(Form.style_report)
    await handle_style_report(message, state)


async def handle_style_report(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data['language']
    style_players_str = data['style_players_str']
    nickname = data['nickname']
    style_dict = data['style_dict']

    # Defining the basic style
    main_style = next(iter(style_dict.keys()), '')

    # Localization
    desc_dict = RU_ru_chess_styles_desc if language == 'RU_ru' else EN_en_chess_styles_desc

    # Forming messages
    current_state = await state.get_state()
    style_messages = data['messages'][current_state]

    # Submitting style information
    if style_players_str:
        await message.answer(style_messages['style'].format(
            style_players_str,
            desc_dict.get(main_style, '')
        ))
        await message.answer_sticker(sticker_id_dict.get(main_style, sticker_id_dict[main_style]))
    else:
        await message.answer(style_messages['Neither'])
        await message.answer_sticker(sticker_id_dict.get('Neither'))

    # Initializing the B2 storage
    storage = ChessStorage()

    nickname = data.get('nickname')
    style_messages = data['messages'][await state.get_state()]

    async def get_photo(file_name):
        # Asynchronous file download
        buffer = io.BytesIO()
        await storage.download_to_buffer(f"{nickname}/{file_name}", buffer)
        return BufferedInputFile(buffer.getvalue(), filename=file_name)

    # 1. Sending PieChart
    white_pie, black_pie = await asyncio.gather(
        get_photo('PieChart_for_white.png'),
        get_photo('PieChart_for_black.png')
    )

    await message.answer_media_group([
        InputMediaPhoto(media=white_pie),
        InputMediaPhoto(media=black_pie, caption=style_messages['opening_tree'])
    ])

    # 2. Sending Heatmaps
    heat_all, heat_cap = await asyncio.gather(
        get_photo('Heatmap_all.png'),
        get_photo('Heatmap_is_captured.png')
    )

    await message.answer_media_group([
        InputMediaPhoto(media=heat_all),
        InputMediaPhoto(media=heat_cap, caption=style_messages['heat_board'])
    ])

    # 3. Sending Versus Violin
    violin = await get_photo('VersusViolin.png')
    await message.answer_photo(
        photo=violin,
        caption=style_messages['pieces_versus_scheme']
    )

    # 4. Sending Marked Raincloud
    rain_open, rain_mid = await asyncio.gather(
        get_photo('MarkedRaincloud_in_opening.png'),
        get_photo('MarkedRaincloud_in_mittelspiel_endgame.png')
    )

    await message.answer_media_group([
        InputMediaPhoto(media=rain_open),
        InputMediaPhoto(media=rain_mid, caption=style_messages['marked_raincloud'])
    ])

    # 5. Sending Achievements Report
    achievements = await get_photo('AchievementsReport.png')
    await message.answer_photo(
        photo=achievements,
        caption=style_messages['achievements_report']
    )

    # await storage.delete_user_folder(nickname)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())