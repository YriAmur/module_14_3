from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio


api = ""
bot = Bot(token = api)
dp = Dispatcher(bot, storage = MemoryStorage())


# Определение состояний
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Рассчитать'),
            KeyboardButton(text='Информация')
        ]
    ], resize_keyboard=True
)

kb_inl = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories'),
            InlineKeyboardButton('Формулы расчёта', callback_data='formulas')
        ]
    ], resize_keyboard=True
)

# Функция /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)

# Функция для обработки нажатия кнопки 'Рассчитать'
@dp.message_handler(text=['Рассчитать'])
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=kb_inl)

# Функция для обработки нажатия кнопки 'Информация'
@dp.message_handler(text=['Информация'])
async def info(message: types.Message):
    await message.answer('Данный бот рассчитает суточную норму потребления калорий')

# Функция для получения формул
@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    formula_text = ("Формула Миффлина-Сан Жеора:\n"
                    "Для мужчин:\n"
                    "BMR = 10 * вес + 6.25 * рост - 5 * возраст + 5\n"
                    "Для женщин:\n"
                    "BMR = 10 * вес + 6.25 * рост - 5 * возраст - 161")
    await call.message.answer(formula_text)
    await call.answer()

# Функция для установки возраста по нажатой Inline кнопке
@dp.callback_query_handler(lambda call: call.data == 'calories')
async def set_age(call: types.CallbackQuery):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()  # Переход к состоянию

# Функция для установки роста
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)  # Сохранение возраста
    await message.answer('Введите свой рост:')
    await UserState.growth.set()  # Переход к состоянию growth

# Функция для установки веса
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)  # Сохранение роста
    await message.answer('Введите свой вес:')
    await UserState.weight.set()  # Переход к состоянию weight


# Функция для отправки калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)  # Сохранение веса



    data = await state.get_data()  # Получение всех введенных данных
    age = int(data.get('age'))
    growth = int(data.get('growth'))
    weight = int(data.get('weight'))

    # Формула Миффлина - Сан Жеора (для мужчин)
    # BMR = 10 * weight + 6.25 * height - 5 * age + 5
    bmr = 10 * weight + 6.25 * growth - 5 * age + 5
    await message.answer(f'Ваша норма калорий: {bmr} калорий.')

    await state.finish()  # Завершение состояний

@dp.message_handler()
async def all_message(message: types.Message):
    await message.answer('Введите команду /start, чтобы начать общение')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)