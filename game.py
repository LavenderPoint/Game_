import pygame
import sys
import random
import math
from pygame.locals import *

# Инициализация Pygame
pygame.init()
pygame.font.init()

# Константы
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
BACKGROUND_COLOR = (255, 255, 200)  # Светло-желтый фон
TEXT_COLOR = (80, 50, 50)
BUTTON_COLOR = (255, 182, 193)
BUTTON_HOVER_COLOR = (255, 105, 180)
PANEL_COLOR = (255, 250, 240)
CATEGORY_COLORS = [
    (255, 182, 193),  # Розовый (девушки): Загадки
    (173, 216, 230),  # Голубой (девушки): Творчество
    (144, 238, 144),  # Зеленый (парни): Словесные
    (255, 99, 71)     # Красный (парни): Физподготовка
]

# Создание экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Подарочек")

# Шрифты
title_font = pygame.font.SysFont("Arial", 48, bold=True)
header_font = pygame.font.SysFont("Arial", 32, bold=True)
normal_font = pygame.font.SysFont("Arial", 24)
small_font = pygame.font.SysFont("Arial", 20)

# Глобальная переменная для мобильных контролов
mobile_control = None

class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        self.avatar = self.generate_avatar()
        
    def add_score(self, points):
        self.score += points
        
    def generate_avatar(self):
        # Создаем простой аватар с инициалами
        avatar = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(avatar, self.color, (40, 40), 40)
        initials = "".join([n[0] for n in self.name.split()]).upper()[:2]
        text = header_font.render(initials, True, (255, 255, 255))
        avatar.blit(text, (40 - text.get_width()//2, 40 - text.get_height()//2))
        return avatar

class Game:
    def __init__(self):
        self.players = []
        self.current_player_idx = 0
        self.state = "SETUP"  # SETUP, PLAYING, GAME_OVER, INTERMEDIATE_RESULTS
        self.tasks_per_category = 50  # Увеличено до 50 заданий
        self.setup_tasks()
        self.selected_category = None
        self.selected_difficulty = None
        self.task_window_open = False
        self.task_result = None
        self.tasks_count_input = str(self.tasks_per_category)
        self.show_answer = False
        self.round_counter = 0
        self.completed_tasks = 0
        self.total_tasks = 0
        self.tasks_remaining = 0
        self.task_offset = [0, 0, 0, 0]  # Смещение для листания заданий
        
    def setup_tasks(self):
        # Инициализация заданий для каждой категории
        self.categories = [
            "Загадки",
            "Творчество",
            "Слова",
            "Физподготовка"
        ]
        
        # Создание структуры для хранения состояния заданий
        self.tasks = []
        for cat_idx in range(4):
            category_tasks = []
            for diff in range(self.tasks_per_category):
                # Каждое задание - словарь с описанием и состоянием
                task = {
                    "description": self.generate_task(cat_idx, diff),
                    "completed": False,
                    "difficulty": diff + 1,
                    "answer": self.get_answer(cat_idx, diff)
                }
                category_tasks.append(task)
            self.tasks.append(category_tasks)
        
        self.total_tasks = 4 * self.tasks_per_category
        self.tasks_remaining = self.total_tasks
    
    def get_answer(self, category, difficulty):
        # Для заданий с ответом возвращаем правильный ответ
        if category == 0:  # Только для загадок
            return self.generate_answer(category, difficulty)
        return ""
    
    def generate_task(self, category, difficulty):
        # Генерация задания в зависимости от категории и сложности
        diff_factor = difficulty + 1
        
        if category == 0:  # Загадки
            riddles = [
                "Какое слово всегда пишется неправильно?",
                "Сколько месяцев в году имеют 28 дней?",
                "Собака была привязана к десятиметровой веревке, а прошла 200 метров. Как?",
                "Как спрыгнуть с десятиметровой лестницы и не ушибиться?",
                "Что можно видеть с закрытыми глазами?",
                "Что в огне не горит и в воде не тонет?",
                "Кого австралийцы называют морской осой?",
                "Что нужно делать, когда видишь зелёного человечка?",
                "Москву раньше называли белокаменной. А какой город называли чёрным?",
                "В каком процессе вода заменила солнце, через 600 лет песок, а еще через 1100 лет механизм?",
                "При Петре I на гербе орёл держал карты четырёх морей. Каких?",
                "Почему в дикой природе белые медведи не едят пингвинов?",
                "Назовите пять дней, не называя чисел и названий дней",
                "У тридцати двух воинов один командир. Что это?",
                "Двенадцать братьев друг за другом бродят, друг друга не обходят. Что это?",
                "Как правильно говорить: 'не вижу белый желток' или 'не вижу белого желтка'?",
                "Когда черной кошке лучше всего пробраться в дом?",
                "Из какой посуды нельзя ничего поесть?",
                "Маленький, серенький на слона похож. Кто это?",
                "Какой рукой лучше размешивать чай?",
                "На какой вопрос нельзя ответить 'да'?",
                "На какой вопрос нельзя ответить 'нет'?",
                "Чем оканчиваются день и ночь?",
                "Что надо сделать, чтобы пять парней остались в одном сапоге?",
                "В каком месяце болтливая Светочка говорит меньше всего?",
                "Что принадлежит вам, однако другие им пользуются чаще?",
                "Какое слово всегда звучит неверно?",
                "У человека — одно, у коровы — два, у ястреба – ни одного. Что это?",
                "Сидит человек, но вы не можете сесть на его место. Где он сидит?",
                "Каких камней в море нет?",
                "Какой знак нужно поставить между 4-мя и 5-ю?",
                "Какой болезнью на земле никто не болел?",
                "Что можно приготовить, но нельзя съесть?",
                "Что у коровы впереди, а у быка позади?",
                "Что не имеет длины, глубины, ширины, высоты, а можно измерить?",
                "Что все люди на земле делают одновременно?",
                "Как брошенное яйцо пролететь 3 метра и не разбиться?",
                "Где край света?",
                "Что с земли легко поднимешь, но далеко не закинешь?",
                "Каким гребнем голову не расчешешь?",
                "Что бросают, когда нуждаются, и поднимают, когда не нуждаются?",
                "Вы сидите в самолёте, впереди лошадь, сзади автомобиль. Где вы?",
                "Деревянная река, деревянный катерок, над катером деревянный дымок. Что это?",
                "В одной руке килограмм железа, в другой - пуха. Что тяжелее?",
                "Чем бег отличается от ходьбы?",
                "Если в 12 ночи идет дождь, можно ли через 72 часа ждать солнца?",
                "Дурачок выбирал 10-рублевую монету вместо 100-рублевой купюры. Почему?",
                "Что легче: 1 кг ваты или 1 кг железа?",
                "Два раза родится, один раз умирает. Кто?",
                "Что с пола за хвост не поднимешь?",
                "Что всегда увеличивается и не уменьшается?",
                "На дереве сидели 7 воробьёв. Одного съела кошка. Сколько осталось?",
                # Добавленные загадки
                "Что становится влажным, пока сохнет?",
                "Что идет, не двигаясь с места?",
                "Что можно разбить, даже если его никто не трогает?",
                "Что имеет много ключей, но не может открыть ни одного замка?",
                "Что принадлежит вам, но другие используют его чаще, чем вы?",
                "Что можно поймать, но нельзя бросить?",
                "Что становится больше, если его перевернуть?",
                "Что имеет голову и хвост, но нет тела?",
                "Что можно видеть в закрытой коробке?",
                "Что летает без крыльев и плачет без глаз?",
                "Что можно держать в правой руке, но нельзя в левой?",
                "Что проходит сквозь города и поля, но не двигается?",
                "Что можно сломать, даже не прикасаясь к нему?",
                "Что имеет четыре ноги, но не может ходить?",
                "Что можно слышать, но нельзя увидеть или потрогать?",
                "Что становится мокрым, пока сохнет?",
                "Что имеет кольцо, но нет пальца?",
                "Что можно съесть, но не проглотить?",
                "Что идет вверх и вниз, но не двигается?",
                "Что можно открыть, но нельзя закрыть?",
                "Что имеет руки, но не может хлопать?",
                "Что можно видеть с закрытыми глазами?",
                "Что становится тяжелее, когда вы берете больше?",
                "Что можно сломать, не прикасаясь к нему?",
                "Что имеет ключ, но не может открыть замок?",
                "Что можно увидеть только в темноте?",
                "Что всегда идет, но никогда не приходит?",
                "Что можно сломать, даже не прикоснувшись к нему?",
                "Что имеет зубы, но не может есть?",
                "Что можно поймать, но нельзя бросить?",
                "Что становится больше, чем больше вы берете?",
                "Что имеет лицо и две руки, но нет ног?",
                "Что можно увидеть дважды в минуте и один раз в году?",
                "Что можно сломать, не прикасаясь к нему?",
                "Что имеет корень, которого никто не видит?",
                "Что можно услышать, но нельзя увидеть?",
                "Что становится меньше, когда вы добавляете к нему?",
                "Что можно сломать, не прикасаясь к нему?",
                "Что имеет кольцо, но нет пальца?",
                "Что можно съесть, но не проглотить?",
                "Что идет вверх и вниз, но не двигается?",
                "Что можно открыть, но нельзя закрыть?",
                "Что имеет руки, но не может хлопать?",
                "Что можно видеть с закрытыми глазами?",
                "Что становится тяжелее, когда вы берете больше?",
                "Что можно сломать, не прикасаясь к нему?",
                "Что имеет ключ, но не может открыть замок?",
                "Что можно увидеть только в темноте?",
                "Что всегда идет, но никогда не приходит?",
                "Что можно сломать, даже не прикоснувшись к нему?",
                "Что имеет зубы, но не может есть?",
                "Что можно поймать, но нельзя бросить?",
                "Что становится больше, чем больше вы берете?",
                "Что имеет лицо и две руки, но нет ног?",
                "Что можно увидеть дважды в минуте и один раз в году?",
                "Что можно сломать, не прикасаясь к нему?",
                "Что имеет корень, которого никто не видит?",
                "Что можно услышать, но нельзя увидеть?",
                "Что становится меньше, когда вы добавляете к нему?",
                "Что можно сломать, не прикасаясь к нему?"
            ]
            return riddles[difficulty % len(riddles)]
        
        elif category == 1:  # Творчество (без указания уровня)
            actions = ["Изобразите", "Спойте", "Расскажите", "Придумайте", "Нарисуйте", "Покажите", "Создайте", "Опишите"]
            themes = ["известную картину", "куплет из песни 90-х", "рифму к слову 'любовь'", 
                     "стих наизусть", "животное так, чтобы все угадали", 
                     "историю с тремя случайными словами", "что-то с закрытыми глазами",
                     "известного человека без слов", "песню, заменяя все слова на 'ля-ля'",
                     "анекдот", "рекламу для обычного предмета", "эмоцию без слов",
                     "новый танец", "сказку от лица злодея", "комплимент каждому игроку",
                     "новый закон и обоснуйте его", "работу известного прибора",
                     "слоган для этой игры", "историю, где каждое слово начинается на одну букву",
                     "скульптуру на заданную тему", "известную песню без слов",
                     "диалог между двумя историческими личностями", "костюм из подручных средств",
                     "сказку на современный лад", "новый алфавит", "рецепт блюда для инопланетян",
                     "эволюцию человека за 1 минуту", "тост на несуществующем языке",
                     "историю в обратном порядке", "работу компьютера", "новые правила для известной игры",
                     "танец, используя только ноги", "анекдот от лица животного", "известную памятку",
                     "диалог между солнцем и луной", "рекламу для несуществующей планеты", 
                     "как работает интернет", "известный логотип жестами", "эмоциональное состояние через звуки",
                     "новый вид спорта", "абстрактную концепцию (любовь, время)", "ритуал приветствия для инопланетян",
                     "музыкальный номер по мотивам этого вечера", "пародию на известного политика",
                     "интервью с вымышленным персонажем", "сценку из немого кино", 
                     "пародийную рекламу обычного предмета", "танец в стиле робота",
                     # Добавленные темы
                     "мировую проблему в виде пантомимы", "идеальный подарок для каждого игрока",
                     "свой день в виде комикса", "новую планету и её обитателей",
                     "речь в защиту невидимых существ", "инопланетный язык общения",
                     "свою жизнь в виде фильма ужасов", "путешествие во времени",
                     "диалог между прошлым и будущим", "мир без интернета",
                     "новую социальную сеть", "жизнь бабочки от гусеницы до бабочки",
                     "эмоцию радости через танец", "печаль через музыку",
                     "удивление через рисунок", "гнев через поэзию",
                     "любовь через скульптуру", "страх через рассказ",
                     "надежду через песню", "разочарование через пантомиму",
                     "вдохновение через живопись", "усталость через танец",
                     "счастье через музыку", "одиночество через поэзию",
                     "дружбу через рисунок", "предательство через рассказ",
                     "верность через скульптуру", "измену через песню",
                     "прощение через танец", "зависть через пантомиму",
                     "щедрость через живопись", "жадность через музыку",
                     "скромность через поэзию", "гордость через рисунок",
                     "смирение через рассказ", "упрямство через скульптуру",
                     "терпение через песню", "нетерпение через танец",
                     "мужество через пантомиму", "трусость через живопись",
                     "мудрость через музыку", "глупость через поэзию",
                     "остроумие через рисунок", "юмор через рассказ",
                     "иронию через скульптуру", "сарказм через песню",
                     "самоиронию через танец", "философию через пантомиму",
                     "науку через живопись", "искусство через музыку",
                     "технику через поэзию", "природу через рисунок"]
            
            action = random.choice(actions)
            theme = random.choice(themes)
            return f"{action} {theme}"
        
        elif category == 2:  # Словесные
            themes = ["животные", "растения", "профессии", "города", "еда", "спорт", "техника", "искусство"]
            letters = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ"
            theme = random.choice(themes)
            letter = random.choice(letters)
            count = min(5 + difficulty // 2, 15)  # Количество слов от 5 до 15
            return f"Назовите {count} слов на букву '{letter}' на тему '{theme}'"
        
        else:  # Физподготовка (с формулами)
            exercises = [
                f"Сделайте {diff_factor * 2} приседаний",
                f"Пройдите {diff_factor} метров на цыпочках",
                f"Стойте в планке {diff_factor * 5} секунд",
                f"Сделайте {diff_factor * 3} отжиманий от стены",
                f"Пробегите на месте {diff_factor * 10} секунд",
                f"Сделайте {diff_factor * 2} выпадов на каждую ногу",
                f"Стойте на одной ноге {diff_factor * 5} секунд",
                f"Сделайте {diff_factor * 4} подъёмов на носки",
                f"Сделайте {diff_factor * 3} наклонов вперед",
                f"Стойте в позе дерева {diff_factor * 5} секунд",
                f"Сделайте {diff_factor * 4} махов ногами",
                f"Сделайте {diff_factor * 2} скручиваний на пресс",
                f"Сделайте {diff_factor * 4} вращений руками",
                f"Постойте на цыпочках {diff_factor * 5} секунд",
                f"Сделайте растяжку на {diff_factor * 5} секунд",
                f"Сделайте {diff_factor * 2} отжиманий с паузой",
                f"Пройдите {diff_factor} метров гусиным шагом",
                f"Сделайте {diff_factor * 3} приседаний с прыжком",
                f"Стойте в позе воина {diff_factor * 4} секунд",
                f"Сделайте {diff_factor * 3} прыжков в длину с места",
                f"Пробегите с высоким поднимаением бедра {diff_factor * 10} шагов",
                f"Сделайте {diff_factor * 4} махов руками по кругу",
                f"Попрыгайте как кенгуру {diff_factor * 3} раз",
                f"Сделайте {diff_factor * 5} прыжков с разворотом на 180 градусов",
                f"Попрыгайте через воображаемое препятствие {diff_factor * 5} раз",
                f"Стойте в мостике {diff_factor * 2} секунд",
                f"Сделайте {diff_factor * 3} подтягиваний (воображаемых)",
                f"Пробегите дистанцию до стены и обратно {diff_factor} раз",
                f"Сделайте {diff_factor * 4} подъемов корпуса на пресс",
                f"Попрыгайте как боксер на ринге {diff_factor * 10} секунд",
                f"Сделайте {diff_factor * 4} выпадов с прыжком",
                f"Пробегите спиной вперед {diff_factor * 5} метров",
                f"Сделайте {diff_factor} пируэтов на одной ноге",
                f"Попрыгайте на месте с высоким подниманием коленей {diff_factor * 10} раз",
                f"Стойте в стойке на голове {diff_factor} секунд (с поддержкой)",
                f"Сделайте {diff_factor * 3} прыжков с приседанием",
                f"Поплавайте {diff_factor * 10} секунд (на суше)",
                f"Сделайте {diff_factor * 2} берпи",
                f"Попрыгайте через воображаемую скакалку {diff_factor * 10} раз",
                f"Сделайте {diff_factor * 4} махов руками в стороны",
                f"Пройдите {diff_factor * 2} метров на руках (с поддержкой)",
                f"Сделайте {diff_factor} сальто вперед (воображаемых)",
                f"Пробегите змейкой вокруг стульев {diff_factor} раз",
                f"Сделайте {diff_factor * 4} прыжков с хлопком над головой",
                f"Попрыгайте как лягушка {diff_factor * 3} раз",
                f"Сделайте {diff_factor * 3} отжиманий с хлопком за спиной",
                f"Пробегите с захлестыванием голени {diff_factor * 10} шагов",
                f"Сделайте {diff_factor * 4} выпадов в сторону",
                f"Пройдите {diff_factor} метров с книгой на голове",
                f"Сделайте {diff_factor} глубоких вдохов и выдохов",
                # Добавленные упражнения
                f"Сделайте {diff_factor * 2} подъемов ног лежа на спине",
                f"Выполните {diff_factor * 3} круговых вращений головой",
                f"Сделайте {diff_factor * 4} наклонов в стороны",
                f"Попрыгайте на одной ноге {diff_factor * 10} раз",
                f"Сделайте {diff_factor * 3} приседаний с выпрыгиванием",
                f"Пройдите {diff_factor * 2} метров в приседе",
                f"Стойте в ласточке {diff_factor * 5} секунд",
                f"Сделайте {diff_factor * 4} скручиваний корпуса сидя",
                f"Поплавайте на спине {diff_factor * 5} секунд (на суше)",
                f"Сделайте {diff_factor * 3} отжиманий от пола",
                f"Пробегите с высоким подниманием коленей {diff_factor * 15} шагов",
                f"Сделайте {diff_factor * 5} махов ногой вперед-назад",
                f"Выполните {diff_factor * 4} поворотов корпуса стоя",
                f"Сделайте {diff_factor * 3} прыжков в сторону",
                f"Попрыгайте как мячик {diff_factor * 20} раз",
                f"Сделайте {diff_factor * 4} выпадов вперед",
                f"Пройдите {diff_factor} метров спиной вперед",
                f"Стойте на носочках {diff_factor * 10} секунд",
                f"Сделайте {diff_factor * 3} глубоких приседаний",
                f"Выполните {diff_factor * 4} круговых вращений руками вперед",
                f"Сделайте {diff_factor * 5} круговых вращений руками назад",
                f"Попрыгайте через воображаемый барьер {diff_factor * 8} раз",
                f"Сделайте {diff_factor * 3} отжиманий с узкой постановкой рук",
                f"Пробегите с захлестыванием голени назад {diff_factor * 10} шагов",
                f"Сделайте {diff_factor * 4} подъемов корпуса из положения лежа",
                f"Выполните {diff_factor * 3} махов ногой в сторону",
                f"Стойте на одной ноге с закрытыми глазами {diff_factor * 3} секунд",
                f"Сделайте {diff_factor * 5} прыжков на месте",
                f"Пройдите {diff_factor * 2} метров в полуприседе",
                f"Сделайте {diff_factor * 4} наклонов к носкам ног",
                f"Выполните {diff_factor * 3} поворотов головы влево-вправо",
                f"Сделайте {diff_factor * 5} круговых движений плечами",
                f"Попрыгайте как зайчик {diff_factor * 15} раз",
                f"Сделайте {diff_factor * 4} выпадов назад",
                f"Пробегите с высоким подниманием бедра и захлестом {diff_factor * 10} шагов",
                f"Сделайте {diff_factor * 3} отжиманий с широкой постановкой рук",
                f"Выполните {diff_factor * 4} подъемов на носки сидя",
                f"Стойте в позе треугольника {diff_factor * 5} секунд",
                f"Сделайте {diff_factor * 5} махов руками вверх-вниз",
                f"Попрыгайте через воображаемый ручеек {diff_factor * 8} раз",
                f"Сделайте {diff_factor * 4} скручиваний лежа на спине",
                f"Выполните {diff_factor * 3} поворотов корпуса сидя",
                f"Стойте в позе орла {diff_factor * 4} секунд",
                f"Сделайте {diff_factor * 5} прыжков с поворотом на 90 градусов"
            ]
            return exercises[difficulty % len(exercises)]
    
    def generate_answer(self, category, difficulty):
        # Ответы для загадок
        if category == 0:
            answers = [
                "Неправильно",
                "Все",
                "Веревка не была привязана",
                "Прыгать с нижней ступени",
                "Сон",
                "Лед",
                "Медузу",
                "Переходить улицу",
                "Чернигов",
                "Измерение времени",
                "Белое, Каспийское, Азовское, Балтийское",
                "Они живут на разных полюсах",
                "Позавчера, вчера, сегодня, завтра, послезавтра",
                "Зубы и язык",
                "Месяцы",
                "Желток обычно желтый",
                "Когда дверь открыта",
                "Из пустой",
                "Слоненок",
                "Той, в которой ложка",
                "Ты спишь?",
                "Ты жив?",
                "Мягким знаком",
                "Каждому снять по сапогу",
                "В феврале",
                "Имя",
                "Неверно",
                "Буква О",
                "На ваших коленях",
                "Сухих",
                "Запятую",
                "Морской",
                "Уроки",
                "Хвост",
                "Время, температура",
                "Становятся старше",
                "Бросить его более чем на 3 метра",
                "Там, где кончается тень",
                "Пух",
                "Петушиным",
                "Якорь",
                "На карусели",
                "Рубанок",
                "Одинаково",
                "При беге есть фаза полета",
                "Нет, снова будет ночь",
                "Пока он выбирал монету, ему давали деньги",
                "Одинаково",
                "Цыпленок",
                "Клубок ниток",
                "Возраст",
                "0 (остальные улетели)",
                # Ответы на добавленные загадки
                "Полотенце",
                "Часы",
                "Обещание",
                "Пианино",
                "Ваше имя",
                "Простуду",
                "Число 6",
                "Монета",
                "Темноту",
                "Левый локоть",
                "Дорога",
                "Обещание",
                "Стол",
                "Звук",
                "Полотенце",
                "Телефон",
                "Жвачка",
                "Лестница",
                "Открытие",
                "Часы",
                "Сон",
                "Дыра",
                "Ключ",
                "Звезды",
                "Завтра",
                "Сердце",
                "Расческа",
                "Тень",
                "Дыра",
                "Лук",
                "Дорога",
                "Открытие",
                "Часы",
                "Сон",
                "Дыра",
                "Ключ",
                "Звезды",
                "Завтра",
                "Сердце",
                "Расческа",
                "Тень",
                "Дыра",
                "Лук"
            ]
            return answers[difficulty % len(answers)]
        
        return ""
    
    def start_game(self):
        if len(self.players) < 2:
            return False
        
        try:
            count = int(self.tasks_count_input)
            if count < 5 or count > 50:
                return False
            self.tasks_per_category = count
            self.setup_tasks()
            self.state = "PLAYING"
            self.round_counter = 0
            self.completed_tasks = 0
            return True
        except:
            return False
    
    def add_player(self, name):
        if name and len(self.players) < 15:
            self.players.append(Player(name))
            return True
        return False
    
    def next_player(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        
        # Если вернулись к первому игроку - завершился круг
        if self.current_player_idx == 0:
            self.round_counter += 1
            
            # Проверяем, осталось ли достаточно заданий для следующего круга
            if self.tasks_remaining < len(self.players):
                self.state = "GAME_OVER"
            else:
                self.state = "INTERMEDIATE_RESULTS"
    
    def select_task(self, category, difficulty):
        if not self.task_window_open and 0 <= category < 4 and 0 <= difficulty < self.tasks_per_category:
            task = self.tasks[category][difficulty]
            if not task["completed"]:
                self.selected_category = category
                self.selected_difficulty = difficulty
                self.task_window_open = True
                self.show_answer = False
                return True
        return False
    
    def complete_task(self, success):
        if self.selected_category is not None and self.selected_difficulty is not None:
            task = self.tasks[self.selected_category][self.selected_difficulty]
            if not task["completed"]:
                # Помечаем задание как завершенное
                task["completed"] = True
                # Увеличиваем счетчик выполненных заданий
                self.completed_tasks += 1
                # Уменьшаем счетчик оставшихся заданий
                self.tasks_remaining -= 1
                
                # Начисляем очки только при успешном выполнении
                if success:
                    points = task["difficulty"]
                    self.players[self.current_player_idx].add_score(points)
                    
                self.task_window_open = False
                self.next_player()  # Переход к следующему игроку
                return True
        return False

class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (50, 50, 80), self.rect, 2, border_radius=10)
        
        text_surf = normal_font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class InputBox:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.active = False
        
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        if event.type == KEYDOWN and self.active:
            if event.key == K_RETURN:
                return True
            elif event.key == K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
        return False
        
    def draw(self, surface):
        color = (100, 160, 210) if self.active else (200, 200, 200)
        pygame.draw.rect(surface, (255, 255, 255), self.rect)
        pygame.draw.rect(surface, color, self.rect, 2)
        
        text_surf = normal_font.render(self.text, True, (0, 0, 0))
        surface.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))
        
        if self.active:
            cursor_pos = text_surf.get_rect().width + 5
            pygame.draw.line(surface, (0, 0, 0), 
                            (self.rect.x + cursor_pos, self.rect.y + 5),
                            (self.rect.x + cursor_pos, self.rect.y + self.rect.height - 5), 2)

def draw_setup_screen(game, tasks_input, player_input, start_btn, add_player_btn):
    screen.fill(BACKGROUND_COLOR)
    
    # Заголовок
    title = title_font.render("Подарочек", True, (220, 20, 60))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    
    # Декоративные элементы
    pygame.draw.circle(screen, (255, 182, 193), (200, 150), 80)
    pygame.draw.circle(screen, (173, 216, 230), (SCREEN_WIDTH - 200, 150), 80)
    pygame.draw.circle(screen, (144, 238, 144), (200, SCREEN_HEIGHT - 150), 80)
    pygame.draw.circle(screen, (255, 99, 71), (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 150), 80)
    
    # Панель настройки
    pygame.draw.rect(screen, PANEL_COLOR, (100, 150, SCREEN_WIDTH - 200, 500), border_radius=20)
    pygame.draw.rect(screen, TEXT_COLOR, (100, 150, SCREEN_WIDTH - 200, 500), 2, border_radius=20)
    
    # Заголовок панели
    setup_title = header_font.render("Настройка игры", True, TEXT_COLOR)
    screen.blit(setup_title, (SCREEN_WIDTH // 2 - setup_title.get_width() // 2, 180))
    
    # Ввод количества заданий
    tasks_label = normal_font.render("Количество заданий в категории (5-50):", True, TEXT_COLOR)
    screen.blit(tasks_label, (200, 250))
    
    # Ввод имени игрока
    player_label = normal_font.render("Имя игрока:", True, TEXT_COLOR)
    screen.blit(player_label, (200, 320))
    
    # Информация об игроках
    players_label = normal_font.render("Добавленные игроки:", True, TEXT_COLOR)
    screen.blit(players_label, (200, 420))
    
    # Список игроков
    for i, player in enumerate(game.players):
        player_text = small_font.render(f"{i+1}. {player.name}", True, TEXT_COLOR)
        screen.blit(player_text, (220, 460 + i * 30))
    
    # Кнопки
    start_btn.draw(screen)
    add_player_btn.draw(screen)
    
    # Отрисовка полей ввода
    tasks_input.draw(screen)
    player_input.draw(screen)

def draw_game_screen(game):
    screen.fill(BACKGROUND_COLOR)
    
    # Декоративные элементы
    for i in range(20):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        pygame.draw.circle(screen, CATEGORY_COLORS[i % 4], (x, y), 5)
    
    # Заголовок
    title = title_font.render("Подарочек", True, (220, 20, 60))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
    
    # Информация о раунде
    round_text = header_font.render(f"Раунд: {game.round_counter}", True, TEXT_COLOR)
    screen.blit(round_text, (SCREEN_WIDTH - 200, 20))
    
    # Прогресс выполнения
    progress = game.completed_tasks / game.total_tasks
    pygame.draw.rect(screen, (200, 200, 200), (50, 80, SCREEN_WIDTH - 100, 20))
    pygame.draw.rect(screen, (0, 150, 0), (50, 80, (SCREEN_WIDTH - 100) * progress, 20))
    progress_text = small_font.render(f"Выполнено: {game.completed_tasks}/{game.total_tasks} ({int(progress*100)}%)", True, TEXT_COLOR)
    screen.blit(progress_text, (SCREEN_WIDTH // 2 - progress_text.get_width() // 2, 82))
    
    # Информация о текущем игроке
    if game.players:
        current_player = game.players[game.current_player_idx]
        player_text = header_font.render(f"Текущий игрок: {current_player.name}", True, current_player.color)
        screen.blit(player_text, (50, 110))
    
    # Панель категорий
    category_width = (SCREEN_WIDTH - 100) // 4 - 10
    for i, category in enumerate(game.categories):
        x = 50 + i * (category_width + 10)
        pygame.draw.rect(screen, CATEGORY_COLORS[i], (x, 150, category_width, 600), border_radius=15)
        pygame.draw.rect(screen, TEXT_COLOR, (x, 150, category_width, 600), 2, border_radius=15)
        
        # Название категории
        cat_text = header_font.render(category, True, TEXT_COLOR)
        screen.blit(cat_text, (x + category_width // 2 - cat_text.get_width() // 2, 170))
        
        # Задания (кружочки)
        tasks_per_row = 5
        task_size = 30
        spacing = 10
        start_y = 230
        
        # Кнопки для листания заданий
        if game.task_offset[i] > 0:
            prev_btn = pygame.Rect(x + 10, 600, 30, 30)
            pygame.draw.polygon(screen, (255, 255, 255), [(prev_btn.x+20, prev_btn.y+5), (prev_btn.x+5, prev_btn.y+15), (prev_btn.x+20, prev_btn.y+25)])
            pygame.draw.rect(screen, (100, 100, 150), prev_btn, 2)
        
        max_offset = max(0, (game.tasks_per_category // tasks_per_row) - 10) * tasks_per_row
        if game.task_offset[i] < max_offset:
            next_btn = pygame.Rect(x + category_width - 40, 600, 30, 30)
            pygame.draw.polygon(screen, (255, 255, 255), [(next_btn.x+10, next_btn.y+5), (next_btn.x+25, next_btn.y+15), (next_btn.x+10, next_btn.y+25)])
            pygame.draw.rect(screen, (100, 100, 150), next_btn, 2)
        
        # Рассчитаем общую ширину всех кружков в ряду
        total_width = tasks_per_row * task_size + (tasks_per_row - 1) * spacing
        start_x = x + (category_width - total_width) // 2
        
        # Отображаем только видимую часть заданий
        start_idx = game.task_offset[i]
        end_idx = min(start_idx + tasks_per_row * 10, game.tasks_per_category)
        
        for j in range(start_idx, end_idx):
            row = (j - start_idx) // tasks_per_row
            col = (j - start_idx) % tasks_per_row
            
            task_x = start_x + col * (task_size + spacing)
            task_y = start_y + row * (task_size + spacing)
            
            task = game.tasks[i][j]
            color = (100, 200, 100) if task["completed"] else CATEGORY_COLORS[i]
            pygame.draw.circle(screen, color, (task_x, task_y), task_size // 2)
            pygame.draw.circle(screen, TEXT_COLOR, (task_x, task_y), task_size // 2, 2)
            
            # Номер задания
            num_text = small_font.render(str(j+1), True, TEXT_COLOR)
            screen.blit(num_text, (task_x - num_text.get_width() // 2, task_y - num_text.get_height() // 2))

def draw_task_window(game):
    if not game.task_window_open:
        return
    
    # Затемнение фона
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    screen.blit(s, (0, 0))
    
    # Окно задания
    window_width = min(800, SCREEN_WIDTH - 100)
    window_height = min(500, SCREEN_HEIGHT - 100)
    window_x = (SCREEN_WIDTH - window_width) // 2
    window_y = (SCREEN_HEIGHT - window_height) // 2
    
    pygame.draw.rect(screen, PANEL_COLOR, (window_x, window_y, window_width, window_height), border_radius=20)
    pygame.draw.rect(screen, TEXT_COLOR, (window_x, window_y, window_width, window_height), 3, border_radius=20)
    
    # Заголовок
    cat_idx = game.selected_category
    task = game.tasks[cat_idx][game.selected_difficulty]
    title = header_font.render(f"Задание: Уровень {task['difficulty']}", True, TEXT_COLOR)
    screen.blit(title, (window_x + window_width // 2 - title.get_width() // 2, window_y + 30))
    
    # Категория
    cat_text = normal_font.render(f"Категория: {game.categories[cat_idx]}", True, CATEGORY_COLORS[cat_idx])
    screen.blit(cat_text, (window_x + 50, window_y + 80))
    
    # Описание задания
    desc_text = normal_font.render("Задание:", True, TEXT_COLOR)
    screen.blit(desc_text, (window_x + 50, window_y + 130))
    
    # Разбиение описания на строки
    description = task["description"]
    words = description.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        if normal_font.size(test_line)[0] < window_width - 100:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    
    for i, line in enumerate(lines):
        line_surf = normal_font.render(line, True, TEXT_COLOR)
        screen.blit(line_surf, (window_x + 70, window_y + 170 + i * 35))
    
    # Показываем ответ только если нажали кнопку "Показать ответ"
    y_pos = window_y + 170 + len(lines) * 35 + 20
    button_width = 180
    button_spacing = 20
    
    if cat_idx == 0:  # Загадки
        if game.show_answer:
            # Показываем ответ
            ans_text = normal_font.render(f"Правильный ответ: {task['answer']}", True, (0, 100, 0))
            screen.blit(ans_text, (window_x + 70, y_pos))
            y_pos += 40
            
            # Кнопки принятия/отклонения
            accept_btn.rect.x = window_x + window_width // 2 - button_width - button_spacing // 2
            accept_btn.rect.y = y_pos
            accept_btn.draw(screen)
            
            reject_btn.rect.x = window_x + window_width // 2 + button_spacing // 2
            reject_btn.rect.y = y_pos
            reject_btn.draw(screen)
        else:
            # Кнопка "Показать ответ"
            show_answer_btn.rect.x = window_x + window_width // 2 - button_width // 2
            show_answer_btn.rect.y = y_pos
            show_answer_btn.draw(screen)
    else:
        # Для остальных категорий сразу показываем кнопки "Принять" и "Отклонить"
        accept_btn.rect.x = window_x + window_width // 2 - button_width - button_spacing // 2
        accept_btn.rect.y = y_pos
        accept_btn.draw(screen)
        
        reject_btn.rect.x = window_x + window_width // 2 + button_spacing // 2
        reject_btn.rect.y = y_pos
        reject_btn.draw(screen)

def draw_intermediate_results(game, continue_btn):
    screen.fill(BACKGROUND_COLOR)
    
    # Заголовок
    title = title_font.render(f"Промежуточные результаты: Раунд {game.round_counter}", True, (220, 20, 60))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    
    # Информация о прогрессе
    progress = game.completed_tasks / game.total_tasks
    progress_text = header_font.render(f"Выполнено заданий: {game.completed_tasks}/{game.total_tasks} ({int(progress*100)}%)", True, TEXT_COLOR)
    screen.blit(progress_text, (SCREEN_WIDTH // 2 - progress_text.get_width() // 2, 120))
    
    # Таблица результатов
    panel_height = min(500, SCREEN_HEIGHT - 280)
    pygame.draw.rect(screen, PANEL_COLOR, (100, 180, SCREEN_WIDTH - 200, panel_height), border_radius=20)
    pygame.draw.rect(screen, TEXT_COLOR, (100, 180, SCREEN_WIDTH - 200, panel_height), 2, border_radius=20)
    
    # Заголовок таблицы
    results_title = header_font.render("Результаты игроков", True, TEXT_COLOR)
    screen.blit(results_title, (SCREEN_WIDTH // 2 - results_title.get_width() // 2, 200))
    
    # Список всех игроков
    sorted_players = sorted(game.players, key=lambda p: p.score, reverse=True)
    for i, player in enumerate(sorted_players):
        if i < 5:  # Показываем только первых 5 игроков
            # Аватар
            screen.blit(player.avatar, (150, 260 + i * 80))
            
            # Имя и очки
            name_text = normal_font.render(f"{i+1}. {player.name}", True, player.color)
            screen.blit(name_text, (250, 270 + i * 80))
            
            score_text = header_font.render(f"{player.score} очков", True, TEXT_COLOR)
            screen.blit(score_text, (SCREEN_WIDTH - 250 - score_text.get_width(), 270 + i * 80))
    
    # Кнопка продолжения
    continue_btn.draw(screen)

def draw_game_over_screen(game, new_game_btn):
    screen.fill(BACKGROUND_COLOR)
    
    # Заголовок
    title = title_font.render("Игра завершена! Финальные результаты", True, (220, 20, 60))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    
    # Информация о количестве раундов
    rounds_text = header_font.render(f"Всего раундов: {game.round_counter}", True, TEXT_COLOR)
    screen.blit(rounds_text, (SCREEN_WIDTH // 2 - rounds_text.get_width() // 2, 120))
    
    # Пьедестал для топ-3
    podium_height = 200
    podium_width = SCREEN_WIDTH - 200
    podium_x = 100
    podium_y = 300
    
    # Основание пьедестала
    pygame.draw.rect(screen, (180, 180, 180), (podium_x, podium_y + podium_height - 20, podium_width, 20))
    
    # Ступени пьедестала
    step_width = podium_width // 3
    step_height = podium_height // 3
    
    # Цвета для пьедестала (однотонные)
    podium_color_1 = (255, 215, 0)  # Золотой
    podium_color_2 = (192, 192, 192)  # Серебряный
    podium_color_3 = (205, 127, 50)   # Бронзовый
    
    # 1 место (золото)
    pygame.draw.rect(screen, podium_color_1, 
                    (podium_x + step_width, podium_y, 
                     step_width, podium_height - step_height))
    
    # 2 место (серебро)
    pygame.draw.rect(screen, podium_color_2, 
                    (podium_x, podium_y + step_height, 
                     step_width, podium_height - step_height))
    
    # 3 место (бронза)
    pygame.draw.rect(screen, podium_color_3, 
                    (podium_x + 2 * step_width, podium_y + step_height, 
                     step_width, podium_height - step_height))
    
    # Список всех игроков
    sorted_players = sorted(game.players, key=lambda p: p.score, reverse=True)
    
    # Отображение топ-3 на пьедестале
    for i, player in enumerate(sorted_players[:3]):
        if i == 0:  # 1 место
            x_pos = podium_x + step_width + step_width // 2
            y_pos = podium_y + 30
            place_color = podium_color_1
        elif i == 1:  # 2 место
            x_pos = podium_x + step_width // 2
            y_pos = podium_y + step_height + 30
            place_color = podium_color_2
        else:  # 3 место
            x_pos = podium_x + 2 * step_width + step_width // 2
            y_pos = podium_y + step_height + 30
            place_color = podium_color_3
        
        # Увеличиваем аватар для топ-3
        avatar = pygame.transform.scale(player.avatar, (120, 120))
        avatar_rect = avatar.get_rect(center=(x_pos, y_pos - 80))
        screen.blit(avatar, avatar_rect)
        
        # Место
        place_text = header_font.render(f"{i+1} МЕСТО", True, place_color)
        screen.blit(place_text, (x_pos - place_text.get_width() // 2, y_pos - 20))
        
        # Имя
        name_text = normal_font.render(player.name, True, player.color)
        screen.blit(name_text, (x_pos - name_text.get_width() // 2, y_pos + 20))
        
        # Очки
        score_text = normal_font.render(f"{player.score} очков", True, TEXT_COLOR)
        screen.blit(score_text, (x_pos - score_text.get_width() // 2, y_pos + 50))
    
    # Таблица для остальных игроков
    if len(sorted_players) > 3:
        other_height = min(200, SCREEN_HEIGHT - podium_y - podium_height - 70)
        pygame.draw.rect(screen, PANEL_COLOR, (100, podium_y + podium_height + 50, SCREEN_WIDTH - 200, other_height), border_radius=20)
        pygame.draw.rect(screen, TEXT_COLOR, (100, podium_y + podium_height + 50, SCREEN_WIDTH - 200, other_height), 2, border_radius=20)
        
        other_title = header_font.render("Остальные участники", True, TEXT_COLOR)
        screen.blit(other_title, (SCREEN_WIDTH // 2 - other_title.get_width() // 2, podium_y + podium_height + 70))
        
        # Отображение остальных игроков
        for i, player in enumerate(sorted_players[3:]):
            if i < 5:  # Показываем только первых 5
                idx = i + 4
                # Аватар
                avatar = pygame.transform.scale(player.avatar, (40, 40))
                screen.blit(avatar, (150, podium_y + podium_height + 120 + i * 40))
                
                # Имя и очки
                player_text = normal_font.render(f"{idx}. {player.name}: {player.score} очков", True, player.color)
                screen.blit(player_text, (200, podium_y + podium_height + 120 + i * 40))
    
    # Кнопка новой игры
    new_game_btn.draw(screen)

# Создание объектов игры и UI
game = Game()

# Кнопки для экрана настройки
start_btn = Button(SCREEN_WIDTH // 2 - 100, 600, 200, 60, "Начать игру")
add_player_btn = Button(SCREEN_WIDTH // 2 - 100, 380, 200, 60, "Добавить игрока")

# Поля ввода
tasks_input = InputBox(600, 250, 200, 40)
player_input = InputBox(600, 320, 200, 40)

# Кнопки для окна задания
show_answer_btn = Button(0, 0, 180, 50, "Показать ответ")
accept_btn = Button(0, 0, 180, 50, "Принять", (144, 238, 144))
reject_btn = Button(0, 0, 180, 50, "Отклонить", (255, 99, 71))

# Кнопки для других экранов
continue_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 60, "Продолжить игру")
new_game_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 60, "Новая игра")

# Главный цикл игры
clock = pygame.time.Clock()
running = True

def handle_mobile_control(direction):
    global mobile_control
    mobile_control = direction

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    # Обработка мобильных контролов
    if mobile_control:
        if game.state == "PLAYING" and not game.task_window_open:
            # Определяем текущую категорию под курсором
            category_width = (SCREEN_WIDTH - 100) // 4 - 10
            for i in range(4):
                cat_x = 50 + i * (category_width + 10)
                cat_rect = pygame.Rect(cat_x, 150, category_width, 600)
                if cat_rect.collidepoint(mouse_pos):
                    max_offset = max(0, (game.tasks_per_category // 5) - 10) * 5
                    if mobile_control == "prev" and game.task_offset[i] > 0:
                        game.task_offset[i] -= 5
                    elif mobile_control == "next" and game.task_offset[i] < max_offset:
                        game.task_offset[i] += 5
                    break
        mobile_control = None
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        
        if game.state == "SETUP":
            # Обработка ввода
            tasks_input.handle_event(event)
            player_input.handle_event(event)
            
            # Обработка кнопок
            if add_player_btn.is_clicked(mouse_pos, event):
                if game.add_player(player_input.text):
                    player_input.text = ""
            
            if start_btn.is_clicked(mouse_pos, event):
                game.tasks_count_input = tasks_input.text
                if game.start_game():
                    pass
        
        elif game.state == "PLAYING":
            if not game.task_window_open:
                # Обработка выбора задания
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    # Проверяем, было ли нажатие на задание
                    category_width = (SCREEN_WIDTH - 100) // 4 - 10
                    tasks_per_row = 5
                    task_size = 30
                    
                    for i in range(4):
                        cat_x = 50 + i * (category_width + 10)
                        
                        # Проверка кнопок листания
                        if game.task_offset[i] > 0:
                            prev_btn = pygame.Rect(cat_x + 10, 600, 30, 30)
                            if prev_btn.collidepoint(event.pos):
                                game.task_offset[i] -= 5
                                continue
                        
                        max_offset = max(0, (game.tasks_per_category // tasks_per_row) - 10) * tasks_per_row
                        if game.task_offset[i] < max_offset:
                            next_btn = pygame.Rect(cat_x + category_width - 40, 600, 30, 30)
                            if next_btn.collidepoint(event.pos):
                                game.task_offset[i] += 5
                                continue
                        
                        # Рассчитаем общую ширину всех кружков в ряду
                        total_width = tasks_per_row * task_size + (tasks_per_row - 1) * 10
                        start_x = cat_x + (category_width - total_width) // 2
                        
                        start_idx = game.task_offset[i]
                        end_idx = min(start_idx + tasks_per_row * 10, game.tasks_per_category)
                        
                        for j in range(start_idx, end_idx):
                            row = (j - start_idx) // tasks_per_row
                            col = (j - start_idx) % tasks_per_row
                            
                            task_x = start_x + col * (task_size + 10)
                            task_y = 230 + row * (task_size + 10)
                            
                            # Проверка расстояния до центра кружка
                            dx = event.pos[0] - task_x
                            dy = event.pos[1] - task_y
                            distance = math.sqrt(dx*dx + dy*dy)
                            
                            if distance <= task_size // 2:
                                game.select_task(i, j)
                                break
            
            else:  # Если открыто окно задания
                # Обработка кнопок
                if show_answer_btn.is_clicked(mouse_pos, event):
                    game.show_answer = True
                
                if accept_btn.is_clicked(mouse_pos, event):
                    game.complete_task(True)
                
                if reject_btn.is_clicked(mouse_pos, event):
                    game.complete_task(False)
        
        elif game.state == "INTERMEDIATE_RESULTS":
            if continue_btn.is_clicked(mouse_pos, event):
                game.state = "PLAYING"
        
        elif game.state == "GAME_OVER":
            if new_game_btn.is_clicked(mouse_pos, event):
                # Перезапуск игры
                game = Game()
                tasks_input.text = str(game.tasks_per_category)
    
    # Обновление состояния кнопок
    start_btn.check_hover(mouse_pos)
    add_player_btn.check_hover(mouse_pos)
    show_answer_btn.check_hover(mouse_pos)
    accept_btn.check_hover(mouse_pos)
    reject_btn.check_hover(mouse_pos)
    continue_btn.check_hover(mouse_pos)
    new_game_btn.check_hover(mouse_pos)
    
    # Отрисовка
    if game.state == "SETUP":
        draw_setup_screen(game, tasks_input, player_input, start_btn, add_player_btn)
    elif game.state == "PLAYING":
        draw_game_screen(game)
        draw_task_window(game)
    elif game.state == "INTERMEDIATE_RESULTS":
        draw_intermediate_results(game, continue_btn)
    elif game.state == "GAME_OVER":
        draw_game_over_screen(game, new_game_btn)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
