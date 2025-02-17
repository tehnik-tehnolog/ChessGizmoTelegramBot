from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

language_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="EN_en"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="RU_ru")
        ]
    ]
)

room_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🧩 Chess․com", callback_data="chess.com"),
            InlineKeyboardButton(text="♘ Lichess", callback_data="lichess")
        ]
    ]
)


def get_messages(language='EN_en'):
    if language == 'En_en':
        messages = {
            'Form:room': ['This bot determines your playing style and calculates some interesting statistics'
                          ' based on your games', 'On which platform do you play?'],
            'Form:nickname': 'Enter your nickname',
            'Form:game_type': '{}, you have played {} blitz games and {} rapid games. How would you like to analyze?',
            'Form:wait': 'Calculating all games will take about 10 minutes',
            'Form:style_report': 'Your style is: {} /n {}',
            'Form:heat_board': 'Heatmap for White | for Black',
            'Form:pieces_versus_scheme': 'How much better you are at developing bishops/knights and attacking/defending',
            'Form:marked_raincloud': 'Your parameters compared to other players at your rating'
        }
    elif language == 'RU_ru':
        messages = {
            'Form:room': ['Этот бот анализирует ваш стиль игры и предоставляет интересную статистику по вашим партиям',
                          'На какой платформе вы играете?'],
            'Form:nickname': 'Напишите свой ник',
            'Form:game_type': '{}, Вы сыграли игр blitz: {} и rapid:{}. Как лучше проанализировать?',
            'Form:wait': 'Обсчёт всех партий займет около 10 минут',
            'Form:style_report': 'Ваш стиль это: {} /n {}',
            'Form:heat_board': 'Тепловая карта за белых | за чёрных',
            'Form:pieces_versus_scheme': 'То насколько лучше вы умеете развивать слонов/коней и атакавать/защищаться',
            'Form:marked_raincloud': 'Ваши параметры относительно других игроков на вашем рейтинге'
        }
    return messages


class GameTypeKeyboard:
    def __init__(self, blitz_num, rapid_num, max_num_games=100):
        self.blitz_num = blitz_num
        self.rapid_num = rapid_num
        self.max_num_games = max_num_games
        self.inline_keyboard = []
        self.keyboard = None

        self.get_keyboard()

    def add_button(self, text: str, callback_data: str):
        self.inline_keyboard.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    def get_keyboard(self):
        if self.rapid_num >= self.max_num_games:
            text = f'🕑 {self.max_num_games} rapid'
            callback_data = f'{0}|{self.max_num_games}'
            self.add_button(text, callback_data)
        elif 5 <= self.rapid_num <= self.max_num_games:
            surplus = min(self.max_num_games - self.rapid_num, self.blitz_num)
            text = f'⚡ {surplus} blitz & 🕑 {self.rapid_num} rapid'
            callback_data = f'{surplus}|{self.rapid_num}'
            self.add_button(text, callback_data)

        if self.blitz_num >= self.max_num_games:
            text = f'⚡ {self.max_num_games} blitz'
            callback_data = f'{self.max_num_games}|{0}'
            self.add_button(text, callback_data)
        elif 5 <= self.blitz_num <= self.max_num_games:
            surplus = min(self.max_num_games - self.blitz_num, self.rapid_num)
            text = f'⚡ {self.blitz_num} blitz & 🕑 {surplus} rapid'
            callback_data = f'{self.blitz_num}|{surplus}'
            self.add_button(text, callback_data)

        self.keyboard = InlineKeyboardMarkup(
            inline_keyboard=self.inline_keyboard
        )
