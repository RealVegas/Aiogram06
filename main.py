import sqlite3
import random
import asyncio
import requests

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from pyexpat.errors import messages

from loader import bot, dp, logger

button_registry = KeyboardButton(text="Регистрация в телеграм боте")
button_exchange_rates = KeyboardButton(text="Курс валют")
button_tips = KeyboardButton(text="Советы по экономии")
button_finances = KeyboardButton(text="Личные финансы")

keyboards = ReplyKeyboardMarkup(keyboard=[
    [button_registry, button_exchange_rates],
    [button_tips, button_finances]
    ], resize_keyboard=True)

conn = sqlite3.connect('user.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE,
    name TEXT,
    category1 TEXT,
    category2 TEXT,
    category3 TEXT,
    expenses1 REAL,
    expenses2 REAL,
    expenses3 REAL
    )
''')
conn.commit()


class FinancesForm(StatesGroup):
    category1 = State()
    expenses1 = State()
    category2 = State()
    expenses2 = State()
    category3 = State()
    expenses3 = State()


@dp.message(Command('start'))
async def send_start(message: Message):
    await message.answer("Привет! Я ваш личный финансовый помощник. Выберите одну из опций в меню:", reply_markup=keyboards)
    await registration(message=message)


@dp.message(F.text == "Регистрация в телеграм боте")
async def registration(message: Message):
    telegram_id = message.from_user.id
    name = message.from_user.full_name
    cursor.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_id,))
    user = cursor.fetchone()
    if user:
        await message.answer("Вы уже зарегистрированы!")
    else:
        cursor.execute('''INSERT INTO users (telegram_id, name) VALUES (?, ?)''', (telegram_id, name))
        conn.commit()
        await message.answer("Вы успешно зарегистрированы!")


@dp.message(F.text == "Курс валют")
async def exchange_rates(message: Message):
    url = "https://v6.exchangerate-api.com/v6/09edf8b2bb246e1f801cbfba/latest/USD"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            await message.answer("Не удалось получить данные о курсе валют!")
            return
        usd_to_rub = data['conversion_rates']['RUB']
        eur_to_usd = data['conversion_rates']['EUR']

        euro_to_rub = eur_to_usd * usd_to_rub

        await message.answer(f'1$ = {usd_to_rub:.2f} ₽\n'
                             f'1€ = {euro_to_rub:.2f} ₽')

    except Exception as err:
        await message.answer(f'Произошла ошибка {err}')


@dp.message(F.text == 'Советы по экономии')
async def send_tips(message: Message):
    tips = [
        'Составьте бюджет: Начните с составления подробного бюджета, который учитывает все '
        'ваши доходы и расходы. Это поможет вам понять, куда уходят ваши финансы и где можно сократить расходы.',

        'Отслеживайте расходы: Регулярно записывайте все свои расходы, чтобы видеть, на что тратятся ваши'
        'деньги. Это позволит выявить ненужные траты и перенаправить средства на более важные цели или сбережения.',

        'Создайте фонд сбережений: Откладывайте определённую сумму от ваших доходов в фонд сбережений каждый'
        'месяц. Это поможет вам создать финансовую подушку на случай непредвиденных обстоятельств.',

        'Ищите скидки: Перед покупкой товаров или услуг всегда ищите возможные скидки и акции. Это поможет'
        'значительно сократить расходы и сохранить больше средств.',

        'Планируйте крупные покупки: Прежде чем совершать крупные траты, тщательно планируйте и оценивайте их'
        'необходимость. Возможно, стоит подождать сезон распродаж или использовать накопленные сбережения.',

        'Установите финансовые цели: Определите краткосрочные и долгосрочные финансовые цели, такие как покупка'
        'жилья, отпуск или создание пенсионного фонда, и работайте над их достижением.',

        'Создайте резервный фонд: Помимо сбережений, важно иметь резервный фонд, покрывающий хотя бы 3 - 6'
        'месяцев ваших расходов. Это поможет вам чувствовать себя увереннее в случае потери дохода.',

        'Разумно используйте кредиты: Если вам необходимо воспользоваться кредитными продуктами, тщательно'
        'оценивайте свои возможности по их возврату, чтобы избежать непосильной долговой нагрузки.',

        'Пересматривайте свои доходы: Периодически анализируйте источники своих доходов и ищите возможности'
        'их увеличения, будь то повышение на работе или дополнительный заработок.',

        'Обучайтесь финансовой грамотности: Постоянно улучшайте свои знания в области финансов, чтобы принимать'
        'более обоснованные решения и эффективно управлять своим бюджетом.'
    ]

    tip = random.choice(tips)
    await message.answer(tip)


@dp.message(F.text == "Личные финансы")
async def finances(message: Message, state: FSMContext):
    await state.set_state(FinancesForm.category1)
    await message.reply("Введите первую категорию расходов:")


@dp.message(FinancesForm.category1)
async def finances(message: Message, state: FSMContext):
    await state.update_data(category1=message.text)
    await state.set_state(FinancesForm.expenses1)
    await message.reply("Введите расходы для категории 1:")


@dp.message(FinancesForm.expenses1)
async def finances(message: Message, state: FSMContext):
    await state.update_data(expenses1=float(message.text))
    await state.set_state(FinancesForm.category2)
    await message.reply("Введите вторую категорию расходов:")


@dp.message(FinancesForm.category2)
async def finances(message: Message, state: FSMContext):
    await state.update_data(category2=message.text)
    await state.set_state(FinancesForm.expenses2)
    await message.reply("Введите расходы для категории 2:")


@dp.message(FinancesForm.expenses2)
async def finances(message: Message, state: FSMContext):
    await state.update_data(expenses2=float(message.text))
    await state.set_state(FinancesForm.category3)
    await message.reply("Введите третью категорию расходов:")


@dp.message(FinancesForm.category3)
async def finances(message: Message, state: FSMContext):
    await state.update_data(category3=message.text)
    await state.set_state(FinancesForm.expenses3)
    await message.reply("Введите расходы для категории 3:")


@dp.message(FinancesForm.expenses3)
async def finances(message: Message, state: FSMContext):
    data = await state.get_data()
    telegarm_id = message.from_user.id
    cursor.execute('''UPDATE users SET category1 = ?, expenses1 = ?, category2 = ?, expenses2 = ?, category3 = ?, expenses3 = ? WHERE telegram_id = ?''',
                   (data['category1'], data['expenses1'], data['category2'], data['expenses2'], data['category3'], float(message.text), telegarm_id))
    conn.commit()
    await state.clear()

    await message.answer("Категории и расходы сохранены!")


@logger.catch
async def main() -> None:
    logger.info('Бот запущен')
    await dp.start_polling(bot)


async def stop_bot() -> None:
    await bot.session.close()
    logger.info('Бот остановлен')


if __name__ == '__main__':
    if __name__ == '__main__':
        try:
            asyncio.run(main())

        except KeyboardInterrupt:
            asyncio.run(stop_bot())