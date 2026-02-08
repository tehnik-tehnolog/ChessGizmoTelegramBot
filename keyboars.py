from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

database_exists_button_text = {'EN_en': ['📥 load done', '🔄 generate again'],
                               'RU_ru': ['📥 загрузить существующие', '🔄 сгенерировать снова']}

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


database_exists_keyboard = lambda lang: InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=database_exists_button_text[lang][0], callback_data="load")],
        [InlineKeyboardButton(text=database_exists_button_text[lang][1], callback_data="generate")]
    ]
)



def get_messages(language='EN_en'):
    if language == 'EN_en':
        style_report_dict = {
            'style': 'You play like {}\n{}',
            'opening_tree': 'Your opening branches as White | as Black',
            'heat_board': 'Frequency of moves on all squares | on squares where pieces are captured',
            'pieces_versus_scheme': 'Strengths: bishops vs knights, attack vs defense',
            'marked_raincloud': 'Your stats compared to players at your rating level',
            'achievements_report': '🧩 Interesting stats and achievements reflecting your playstyle ♟️🔥'
        }
        messages = {
            'Form:room': ['This bot determines your playing style and calculates some interesting statistics'
                          ' based on your games', 'On which platform do you play?'],
            'Form:nickname': 'Enter your nickname',
            'Form:database_exists': '{}, your data is already loaded. Update or keep it?',
            'Form:game_type': '{}, you have played {} blitz games and {} rapid games. How would you like to analyze?',
            'Form:wait': 'Calculating all games will take about 10 minutes',
            'Form:style_report': style_report_dict
        }
    elif language == 'RU_ru':
        style_report_dict = {
            'style': 'Вы играете как {}\n{}',
            'opening_tree': 'Ваши дебютные ветки за белых | за чёрных',
            'heat_board': 'Частота ходов по всем полям | по полям, где происходят взятия фигур',
            'pieces_versus_scheme': 'Сильные стороны: слоны vs кони, атака vs защита',
            'marked_raincloud': 'Ваши параметры относительно других игроков на вашем рейтинге',
            'achievements_report': '🧩 Интересная статистика и достижения, отражающие стиль игры ♟️🔥'
        }
        messages = {
            'Form:room': ['Этот бот анализирует ваш стиль игры и предоставляет интересную статистику по вашим партиям',
                          'На какой платформе вы играете?'],
            'Form:nickname': 'Напишите свой ник',
            'Form:database_exists': '{}, ваши данные уже есть. Обновить или оставить?',
            'Form:game_type': '{}, вы сыграли игр blitz: {} и rapid: {}. Как лучше проанализировать?',
            'Form:wait': 'Обсчёт всех партий займет около 10 минут',
            'Form:style_report': style_report_dict
        }
    return messages


class GameTypeKeyboard:
    def __init__(self, blitz_num, rapid_num, max_num_games=5):
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
            game_type_index = 1
            callback_data = f'{0}|{self.max_num_games}|{game_type_index}'
            self.add_button(text, callback_data)
        elif 5 <= self.rapid_num <= self.max_num_games:
            surplus = min(self.max_num_games - self.rapid_num, self.blitz_num)
            text = f'⚡ {surplus} blitz & 🕑 {self.rapid_num} rapid'
            game_type_index = 1
            callback_data = f'{surplus}|{self.rapid_num}|{game_type_index}'
            self.add_button(text, callback_data)

        if self.blitz_num >= self.max_num_games:
            text = f'⚡ {self.max_num_games} blitz'
            game_type_index = 0
            callback_data = f'{self.max_num_games}|{0}|{game_type_index}'
            self.add_button(text, callback_data)
        elif 5 <= self.blitz_num <= self.max_num_games:
            surplus = min(self.max_num_games - self.blitz_num, self.rapid_num)
            text = f'⚡ {self.blitz_num} blitz & 🕑 {surplus} rapid'
            game_type_index = 0
            callback_data = f'{self.blitz_num}|{surplus}|{game_type_index}'
            self.add_button(text, callback_data)

        self.keyboard = InlineKeyboardMarkup(
            inline_keyboard=self.inline_keyboard
        )


sticker_id_dict = {
    'Alexander Alekhine': 'CAACAgIAAxkBAAEP1f9oTD39FiSqbhW9kY48zsCPr44BTQACq38AArUVWEqhWZvmCiYSITYE',
    'Alexander Grischuk': 'CAACAgIAAxkBAAEP1gFoTD4Jp-KXSlvJ5l5RsOu9zCT11wACb3oAAn0vWUqfcRlQ6HnoKTYE',
    'Alireza Firouzja': 'CAACAgIAAxkBAAEP1gNoTD4Luu9hatk-UnEQL9HqkpnIgQAC43UAApRgWErXOUUKfXLF5DYE',
    'Anatoly Karpov': 'CAACAgIAAxkBAAEP1gVoTD4M5Y7RWg846BRmh7cf4gUloAACGHsAAoeqWUo6goDh6jTSGzYE',
    'Anish Giri': 'CAACAgIAAxkBAAEP1gdoTD4OJzfXLP-KKgWPgpBOO5BBvQACjncAA81YSpREMNbLIQy5NgQ',
    'Arjun Erigaisi': 'CAACAgIAAxkBAAEP1gloTD4PJRv4fHHlzQ-xO-iMlD4eQAACbXoAAmqxWUqhLF8EV4t6UzYE',
    'Aron Nimzowitsch': 'CAACAgIAAxkBAAEP1gtoTD4Q6GN5EGkPxStSxIyQRI9-wQACNHUAArqRWEqbwmHHb41WITYE',
    'Bobby Fischer': 'CAACAgIAAxkBAAEP1g1oTD4R77JOor-QkuoqPMpfiTz9sQACB3UAAqC3WEqDRPOlo0OYYDYE',
    'Daniil Dubov': 'CAACAgIAAxkBAAEP1g9oTD4SVUpP7CI0LDBD-6FE_1larwACgH4AAvFxWErg-6dh8zT7-zYE',
    'Ding Liren': 'CAACAgIAAxkBAAEP1hFoTD4UKeh8R86DrX38aOsp8Wns1AACjoMAAuzAWEpx1F9v0kgpiDYE',
    'Emanuel Lasker': 'CAACAgIAAxkBAAEP1hNoTD4VEnnMXA1jXOXLLbDjcLwAATQAAlh3AAJuq1hKovVLeqMEhuc2BA',
    'Fabiano Caruana': 'CAACAgIAAxkBAAEP1kVoTD42qZ2J-JxXeTuLEhOqfjSWxwACfIYAAm28WEr_LMutAa0pDTYE',
    'Farrukh Amonatov': 'CAACAgIAAxkBAAEP1hVoTD4WILC1u9sYatbLLC-mSlqxAAN_dQACFyRYSqkTvCEDJ12wNgQ',
    'Garry Kasparov': 'CAACAgIAAxkBAAEP1hdoTD4X79qn3cyRAhihlSJQTfs7sgACvX8AAnTZWUpqEFwpYel3GjYE',
    'Gukesh Dommaraju': 'CAACAgIAAxkBAAEP1hloTD4Z_4MPui--iLvfYvVuxo8vNwACp3sAAvuNWErqAxfs15u3nzYE',
    'Hikaru Nakamura': 'CAACAgIAAxkBAAEP1htoTD4aF2Cfa0WL1py7KsYwWT-t-QACTXsAAt7uWErabEykcmB_kTYE',
    'Ian Nepomniachtchi': 'CAACAgIAAxkBAAEP1h1oTD4bKz2QCRyxzDCIlie3xsF_UgACYmwAApseYEqYxgr0BTo0_DYE',
    'Jose Capablanca': 'CAACAgIAAxkBAAEP1h9oTD4cIQitL3uP2JJkmZjSmSC3DgACF2sAAmOYYEq746Olc1ssBjYE',
    'Judit Polgar': 'CAACAgIAAxkBAAEP1iFoTD4eiv0RXkORjyKdyWZy5PU_CgACJ38AAmx-WUocDpLMM46hGzYE',
    'Kateryna Lagno': 'CAACAgIAAxkBAAEP1iNoTD4fSXOBAVQplWr1PcIgvlVjOQACgngAAuoLWUo7YkFi_q9FsjYE',
    'Levan Pantsulaia': 'CAACAgIAAxkBAAEP1iVoTD4iNBxfh_xB8vBx6i339CFQxAACEoYAAqIfWEpErv7OUo1XeDYE',
    'Levon Aronian': 'CAACAgIAAxkBAAEP1idoTD4jxFAi3-pFSnQoo7-GRXmuVAACpX8AAhlQWUoBlt9t1GeTFTYE',
    'Magnus Carlsen': 'CAACAgIAAxkBAAEP1iloTD4knQRRECSQkHczVAkSCgHW3QACkXMAAqVAWUodhSKGyNnwVzYE',
    'Max Euwe': 'CAACAgIAAxkBAAEP1itoTD4loHUPre1p6aoBEGq8Px7R_QACu4EAAkj2WUr_FFTL0YuEijYE',
    'Maxime Vachier-Lagrave': 'CAACAgIAAxkBAAEP1i1oTD4mN1jeH9CeruDpH4MNXjBzAgACx3EAAvwXWUp1bG74-rf8AjYE',
    'Miguel Najdorf': 'CAACAgIAAxkBAAEP1i9oTD4oDqsNiUfHBEJvUdBwS2vpIgAC3noAAjkVWEpmTQL7SJabMDYE',
    'Mikhail Botvinnik': 'CAACAgIAAxkBAAEP1jFoTD4q-y9K6R32x3sQJ9YDEWDVqQACg48AAnheWEoNpKvsTerFFjYE',
    'Mikhail Tal': 'CAACAgIAAxkBAAEP1kloTD46UqIfR5WkHRTbRwq73PdsSwACdX8AArduWUpB8ZDkC4TSlzYE',
    'Peter Leko': 'CAACAgIAAxkBAAEP1jNoTD4r3BZWx9d3K_cTb2Ah_tSJtQACnoIAAluCWEqIMWSJV0dm7jYE',
    'Richard Rapport': 'CAACAgIAAxkBAAEP1jVoTD4s_Yn_D6L2EvXGYP8chhvMZgACom0AAuzSWEou-Lmfk1Nz_zYE',
    'Sergey Karjakin': 'CAACAgIAAxkBAAEP1jdoTD4t_UHfmijJ9T13bGA4OHVTwgAClYEAAjIRWUrM3LE9ohLT7jYE',
    'Tigran Petrosian': 'CAACAgIAAxkBAAEP1jloTD4umseTOijPy2AJglbc1KHHvwACv3AAAtDMYUrQZqgHQICiiTYE',
    'Viktor Korchnoi': 'CAACAgIAAxkBAAEP1jtoTD4vWd0LK1OXUqbeqiiJ6lZW7QACiHUAAjOjWEpGgb6EhCHzRzYE',
    'Vincent Keymer': 'CAACAgIAAxkBAAEP1j1oTD4xN63Lb8xbKWVr5Osk4sw6ygACHHgAAg2yWEqIL7H4E3_HiDYE',
    'Viswanathan Anand': 'CAACAgIAAxkBAAEP1j9oTD4yQncmXenJYwP-61nWOKZ_6wACrHgAAi2UWUo5xo0bljrANzYE',
    'Vladimir Kramnik': 'CAACAgIAAxkBAAEP1kFoTD4z-0o6JDb1WqI1tyM7dhJPAwACaHkAAvhGWEq5xAn_1COcdDYE',
    'Wilhelm Steinitz': 'CAACAgIAAxkBAAEP1kNoTD41jdNlV0yJ98kCpmRhNleCvQAC2W4AAoHBYUpbSKh8p6z_TDYE',
	'Wait': 'CAACAgIAAxkBAAEP1kdoTD43B5PLEM5RbeFTrtnL3597OwACPHYAAuzzYUpC2lb9-8SrQDYE'}

RU_ru_player_dict = {
    'Alexander Alekhine': 'Александр Алехин',
    'Alexander Grischuk': 'Александр Грищук',
    'Alireza Firouzja': 'Алиреза Фируджа',
    'Anatoly Karpov': 'Анатолий Карпов',
    'Anish Giri': 'Аниш Гири',
    'Arjun Erigaisi': 'Арджун Эригаиси',
    'Aron Nimzowitsch': 'Арон Нимцович',
    'Bobby Fischer': 'Бобби Фишер',
    'Daniil Dubov': 'Даниил Дубов',
    'Ding Liren': 'Дин Лижэнь',
    'Emanuel Lasker': 'Эммануил Ласкер',
    'Fabiano Caruana': 'Фабиано Каруана',
    'Farrukh Amonatov': 'Фаррух Амонатов',
    'Garry Kasparov': 'Гарри Каспаров',
    'Gukesh Dommaraju': 'Гукеш Доммараджу',
    'Hikaru Nakamura': 'Хикару Накамура',
    'Ian Nepomniachtchi': 'Ян Непомнящий',
    'Jose Capablanca': 'Хосе Рауль Капабланка',
    'Judit Polgar': 'Юдит Полгар',
    'Kateryna Lagno': 'Екатерина Лагно',
    'Levan Pantsulaia': 'Леван Панцулая',
    'Levon Aronian': 'Левон Аронян',
    'Magnus Carlsen': 'Магнус Карлсен',
    'Max Euwe': 'Макс Эйве',
    'Maxime Vachier-Lagrave': 'Максим Вашье-Лаграв',
    'Miguel Najdorf': 'Мигель Найдорф',
    'Mikhail Botvinnik': 'Михаил Ботвинник',
    'Mikhail Tal': 'Михаил Таль',
    'Peter Leko': 'Петер Леко',
    'Richard Rapport': 'Рихард Раппорт',
    'Sergey Karjakin': 'Сергей Карякин',
    'Tigran Petrosian': 'Тигран Петросян',
    'Viktor Korchnoi': 'Виктор Корчной',
    'Vincent Keymer': 'Винсент Каймер',
    'Viswanathan Anand': 'Вишванатан Ананд',
    'Vladimir Kramnik': 'Владимир Крамник',
    'Wilhelm Steinitz': 'Вильгельм Стейниц'
}

EN_en_player_dict = {ru_name: en_name for en_name, ru_name in RU_ru_player_dict.items()}

EN_en_chess_styles_desc = {
    'Alexander Alekhine': 'An attacking, combinative style with deep calculation. Known for spectacular sacrifices and endgame mastery, often creating "chaos" on the board for tactical advantage.',
    'Alexander Grischuk': 'A universal style with exceptional blitz and rapid skills. Excels in counterplay, renowned for defending difficult positions and squeezing draws from seemingly lost games.',
    'Alireza Firouzja': 'A risky, aggressive style willing to sharpen positions. Possesses exceptional intuition in unconventional positions and rapid calculation, especially in sharp openings.',
    'Anatoly Karpov': 'The epitome of positional play, emphasizing strategic control and exploiting weaknesses. A virtuoso of endgames and restrained structures.',
    'Anish Giri': 'An ultra-solid, hard-to-beat style with minimal risk-taking. A draw master, often using deep opening preparation to neutralize games.',
    'Arjun Erigaisi': 'A creative, tactically sharp style with unorthodox solutions. Known for generating dynamic play in "quiet" positions others dismiss.',
    'Aron Nimzowitsch': 'A hypermodern pioneer of prophylaxis and blockade. Developed theories of pawn centers and piece pressure—famous for "the threat is stronger than its execution."',
    'Bobby Fischer': 'A universal style with relentless initiative and precise calculation. Dominant in open positions, endgames, and psychological pressure. Creator of Fischer Random.',
    'Daniil Dubov': 'An experimental, unorthodox style embracing sharp, unexplored positions. Famous for unexpected opening novelties and tactical surprises at elite levels.',
    'Ding Liren': 'A flexible universal style with deep positional understanding and unconventional strategic ideas. Master of sudden defense-to-counterattack transitions and atypical pawn structures.',
    'Emanuel Lasker': 'A psychological style adapting to opponents’ weaknesses. Blended strategic depth with practicality and a relentless will to win.',
    'Fabiano Caruana': 'A fundamental style with encyclopedic opening prep and precise calculation. Excels in tense middlegames with pawn tensions.',
    'Garry Kasparov': 'A dynamic attacking style with boundless energy and pressure. Masterfully combined strategic vision with tactical clarity, especially in sharp positions.',
    'Gukesh Dommaraju': 'An ambitious, fearless style embracing risk. Notable for rapid tactical calculation and confidence in unconventional positions.',
    'Hikaru Nakamura': 'A blitz/bullet specialist with lightning calculation. Deadly in tactical chaos and time trouble—a master of resourceful defense.',
    'Magnus Carlsen': 'A universal "pragmatic" style with elite endgame skills and maximizing minimal advantages. Renowned for resilience and grinding opponents in long games.',
    'Mikhail Tal': 'A combinative genius with unpredictable sacrifices and chaos creation. His attacks relied on intuition and psychological pressure over brute-force calculation.',
    'Viswanathan Anand': 'A universal style with lightning calculation and elegant tactics. Exceptional in dynamic positions with mutual chances.',
    'Vladimir Kramnik': 'A deep positional style emphasizing strategic control without undue risk. A virtuoso of simplifying to winning endgames.',
    'Ian Nepomniachtchi': 'A dynamic style willing to sharpen play with unorthodox ideas. Strong in asymmetrical positions with counterchances.',
    'Levon Aronian': 'A creative, artistic style with unconventional solutions. Famous for quality sacrifices and unexpected tactical blows.',
    'Sergey Karjakin': 'A technical style focused on precise calculation and solid defense. Master of survival in difficult positions and exploiting minimal counterplay.',
    'Tigran Petrosian': 'A prophylactic master, neutralizing opponents’ ideas. Virtuoso of intermezzos and building "defensive fortresses."',
    'Viktor Korchnoi': 'An uncompromising fighter with unmatched willpower and original thinking. Thrived in complex, double-edged positions.',
    'Wilhelm Steinitz': 'The father of positional chess, emphasizing pawn structures and accumulating small advantages. Pioneered positional evaluation and systematic attack.',
    'Jose Capablanca': 'Natural positional understanding and effortless endgame mastery. Preferred clear positions, avoiding unnecessary complications.',
    'Max Euwe': 'A logical, academic style with deep theoretical grounding. Blended strategic depth with tactical alertness.',
    'Mikhail Botvinnik': 'A scientific approach with meticulous preparation. Pioneer of systematic opening study and typical position mastery.',
    'Judit Polgar': 'An attacking style with "masculine" aggression and tactical sharpness. Often chose the sharpest, most ambiguous continuations.',
    'Richard Rapport': 'An eccentric, experimental style with unconventional opening ideas. Famous for piece sacrifices and positions with unique dynamics.',
    'Maxime Vachier-Lagrave': 'A tactically sharp style with deep theoretical knowledge and willingness to complicate. Excels in mutual zugzwang positions.',
    'Peter Leko': 'A super-solid style minimizing risk and emphasizing correctness. Master of drawish tendencies in balanced positions.',
    'Kateryna Lagno': 'A universal style with tactical vision and positional discipline. Strong in technical positions with minimal advantages.',
    'Vincent Keymer': 'A disciplined style with positional maturity and precise calculation. Known for seizing initiative in seemingly quiet positions.',
    'Levan Pantsulaia': 'A strategically flexible style with a keen sense of pawn structure dynamics. Master of maneuvering in cramped positions.',
    'Farrukh Amonatov': 'An active style seeking counterplay in any position. Renowned for resilient defense and generating counterplay from passive setups.',
    'Miguel Najdorf': 'A combinative vision and love for sharp, initiative-driven positions. Creator of the famed Sicilian variation and attacking setups.',
    'Neither': 'Your playstyle doesn’t distinctly align with any single archetype. Games show balanced tactical/positional traits—no clear preference for sharp attacks or solid structures. Adapts fluidly without signature patterns.',
}

RU_ru_chess_styles_desc = {
    'Alexander Alekhine': 'Атакующий комбинационный стиль с глубоким расчетом вариантов. Известен эффектными жертвами и эндшпильным мастерством, часто создавал "хаос" на доске для тактического преимущества.',
    'Alexander Grischuk': 'Универсальный стиль с выдающимся мастерством в быстрых шахматах и блице. Склонен к контригре, славится умением защищать сложные позиции и выжимать ничьи из казалось бы проигранных партий.',
    'Alireza Firouzja': 'Рискованный, агрессивный стиль с готовностью идти на обострение. Обладает исключительной интуицией в нестандартных позициях и быстрым расчетом вариантов, особенно в острых дебютах.',
    'Anatoly Karpov': 'Эталон позиционного стиля с акцентом на стратегическое превосходство и контроль ключевых пунктов. Виртуозно эксплуатировал малейшие позиционные слабости соперника, особенно силен в эндшпиле и сковывающих структурах :cite[4].',
    'Anish Giri': 'Чрезвычайно солидный и труднопобедимый стиль с минимизацией рисков. Мастер ничейных позиций, часто использует глубокую дебютную подготовку для достижения ровной игры.',
    'Arjun Erigaisi': 'Креативный и тактически острый стиль с нестандартными решениями. Известен способностью генерировать динамические ресурсы в позициях, которые другие считают "спокойными".',
    'Aron Nimzowitsch': 'Пионер гипермодернизма с концепциями профилактики ("профилактики") и блокады. Разработал теорию центра пешками и фигурного давления, автор принципа "угроза сильнее ее исполнения".',
    'Bobby Fischer': 'Универсальный стиль с бескомпромиссным стремлением к инициативе и точностью расчета. Особенно силен в открытых позициях, эндшпиле и психологическом давлении на соперника. Автор "шахмат Фишера".',
    'Daniil Dubov': 'Экспериментальный и неортодоксальный стиль с готовностью к острым и неисследованным позициям. Известен неожиданными дебютными новинками и тактическими сюрпризами даже на высшем уровне.',
    'Ding Liren': 'Гибкий универсальный стиль с глубоким позиционным пониманием и неочевидными стратегическими решениями. Способен резко переключаться между защитой и контратакой, мастер нестандартных пешечных структур.',
    'Emanuel Lasker': 'Психологический стиль с адаптацией под слабости конкретного соперника. Сочетал глубокое стратегическое понимание с практичностью и волей к победе в любых позициях.',
    'Fabiano Caruana': 'Фундаментальный стиль с энциклопедической дебютной подготовкой и точным расчетом. Силен в сложных миттельшпильных позициях с пешечным напряжением.',
    'Garry Kasparov': 'Динамичный атакующий стиль с неограниченной энергией и давлением на соперника. Виртуозно сочетал стратегическое видение с тактической ясностью, особенно в острых позициях.',
    'Gukesh Dommaraju': 'Амбициозный стиль с бесстрашием и готовностью идти на риск. Отличается быстрым расчетом в тактических осложнениях и уверенностью в нестандартных позициях.',
    'Hikaru Nakamura': 'Специалист по быстрым шахматам и блицу с молниеносным расчетом. Особо опасен в тактических осложнениях и цейтноте, мастер ресурсной защиты.',
    'Magnus Carlsen': 'Универсальный "прагматичный" стиль с выдающимся эндшпильным мастерством и умением выжимать максимум из малейших преимуществ. Известен феноменальной устойчивостью и способностью "мучить" соперников в длительных партиях.',
    'Mikhail Tal': 'Комбинационный гений с непредсказуемыми жертвами и созданием хаоса. Его атаки часто основывались на интуиции и психологическом давлении, а не на точном расчете всех вариантов.',
    'Viswanathan Anand': 'Универсальный стиль с молниеносным расчетом вариантов и элегантными тактическими ударами. Особенно силен в динамичных позициях с обоюдными шансами.',
    'Vladimir Kramnik': 'Глубокий позиционный стиль с акцентом на стратегическое превосходство без лишнего риска. Виртуозно упрощал позиции до выигранных эндшпилей.',
    'Ian Nepomniachtchi': 'Динамичный стиль с готовностью к обострениям и нестандартным идеям. Силен в асимметричных позициях с взаимными шансами.',
    'Levon Aronian': 'Креативный стиль с художественным подходом и нешаблонными решениями. Известен жертвами качества и неожиданными тактическими ударами.',
    'Sergey Karjakin': 'Техничный стиль с упором на точный расчет и солидную защиту. Мастер выживания в сложных позициях и использования малейших контригровых шансов.',
    'Tigran Petrosian': 'Выдающийся мастер профилактики и защиты с акцентом на нейтрализацию идей соперника. Виртуоз межходовой игры и создания "защитных редутов".',
    'Viktor Korchnoi': 'Бескомпромиссный боец с огромной волей к победе и нестандартным мышлением. Силен в сложных, запутанных позициях с обоюдными шансами.',
    'Wilhelm Steinitz': 'Отец позиционной школы с акцентом на важность пешечной структуры и накопление мелких преимуществ. Разработал принципы оценки позиции и планомерной атаки.',
    'Jose Capablanca': 'Природное позиционное понимание и эндшпильное мастерство с минимальными усилиями. Стремился к ясным позициям, избегая ненужных осложнений.',
    'Max Euwe': 'Логичный и академический стиль с глубоким теоретическим обоснованием решений. Сочетал стратегическую глубину с тактической зоркостью.',
    'Mikhail Botvinnik': 'Фундаментальный научный подход с тщательной подготовкой и анализом. Пионер систематической дебютной подготовки и глубокого изучения типовых позиций.',
    'Judit Polgar': 'Атакующий стиль с мужской агрессивностью и готовностью к тактическим осложнениям. Часто выбирала наиболее острые и неоднозначные продолжения.',
    'Richard Rapport': 'Экстравагантный и экспериментальный стиль с нестандартными дебютными идеями. Известен жертвами качества и созданием позиций с уникальной динамикой.',
    'Maxime Vachier-Lagrave': 'Тактически острый стиль с глубоким знанием теории и готовностью к осложнениям. Особенно силен в вариантах с взаимным цугцвангом.',
    'Peter Leko': 'Суперсолидный стиль с минимизацией риска и акцентом на позиционную корректность. Мастер ничейных тенденций в выравненных позициях.',
    'Kateryna Lagno': 'Универсальный стиль с хорошим тактическим зрением и позиционной дисциплиной. Сильна в техничных позициях с минимальным преимуществом.',
    'Vincent Keymer': 'Дисциплинированный стиль с позиционной зрелостью и точным расчетом. Известен умением перехватывать инициативу в казалось бы спокойных позициях.',
    'Levan Pantsulaia': 'Стратегически гибкий стиль с пониманием динамики пешечных структур. Мастер маневрирования в стесненных позициях.',
    'Farrukh Amonatov': 'Активный стиль с поиском контригровых возможностей в любой позиции. Известен упорством в защите и умением создавать контригру из пассивных позиций.',
    'Miguel Najdorf': 'Комбинационное зрение и любовь к острым, инициативным позициям. Автор знаменитого варианта в сицилианской защите и мастер атакующих построений.',
    'Neither': 'Ваш стиль игры не соответствует четко какому-либо одному архетипу. Ваши игры демонстрируют сбалансированные черты — в равной степени сочетающие '
               'тактическую и позиционную игру, без явного предпочтения резким атакам или прочным структурам. Универсальный подход, адаптация к противникам без фирменных шаблонов.',
}