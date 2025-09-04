import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from datetime import datetime, date, time, timedelta

#  токен від BotFather
API_TOKEN = "8161794118:AAF1R1L-ugLfiYANK-iuiROwyGHx3sfxpYs"

# Ініціалізація бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Список чатів, де бот активний
active_chats = set()

# Розклад для двох тижнів
schedule_week1 = {
    "Пн": {
        1: "Правознавство (lec., Zoom)",
        2: "Комп'ютерна оптимізація процесів і систем (prc., Zoom)",
        4: "Правознавство (prc., Zoom)"
    },
    "Вт": {
        2: "Теорія автоматичного керування. Ч.1 (prc., офлайн, 283-1)",
        3: "Основи цифрової схемотехніки (lab., офлайн, 287а-1)"
    },
    "Ср": {
        2: "Основи цифрової схемотехніки (lec., Zoom)",
        3: "Практичний курс іноземної мови (prc., Zoom)",
        5: "Біоконструкційні матеріали (prc., Zoom)"
    },
    "Чт": {
        2: "Теорія автоматичного керування. Ч.1 (lec., Zoom)",
        4: "Технології складання в автоматизованому виробництві (lec., Zoom)"
    },
    "Пт": {
        2: "Технології складання в автоматизованому виробництві (prc., офлайн, 293-1)",
        5: "Біонічний дизайн (prc., Zoom)",
        6: "Біонічний дизайн (lec., Zoom)"
    },
    "Сб": {}
}

schedule_week2 = {
    "Пн": {
        2: "Теорія автоматичного керування. Частина 1. Теорія лінійних систем автоматичного управління (lab., Zoom)",
        4: "Біоконструкційні матеріали (lec., Zoom)",
        5: "Комп’ютерна оптимізація процесів і систем (lec., Zoom)"
    },
    "Вт": {
        3: "Основи цифрової схемотехніки (lab., офлайн, 287а-1)",
        5: "Основи цифрової схемотехніки (prc., офлайн, 287а-1)"
    },
    "Ср": {
        3: "Практичний курс іноземної мови (prc., Zoom)",
        4: "Комп’ютерна оптимізація процесів і систем (lec., Zoom)Комп’ютерна оптимізація процесів і систем (prc., Zoom)",
        5: "Біоконструкційні матеріали (prc., Zoom)"
    },
    "Чт": {
        2: "Теорія автоматичного керування. Ч.1 (lec., Zoom)",
        3: "Теорія автоматичного керування. Ч.1 (lec., Zoom)",
        4: "Технології складання в автоматизованому виробництві (lec., Zoom)"
    },
    "Пт": {
        3: "Технології складання в автоматизованому виробництві (prc., офлайн, 293-1)",
        5: "Біонічний дизайн (prc., Zoom)",
        6: "Біонічний дизайн (lec., Zoom)"
    },
    "Сб": {}
}
# schedule_week2 = schedule_week1  # щоб не дублювати, поки що залишаю той самий

# Часи початку пар
lesson_times = {
    1: time(8, 30),
    2: time(10, 25),
    3: time(12, 20),
    4: time(14, 15),
    5: time(16, 10),
    6: time(18, 30)
}

# Початок навчального року (перший тиждень) - виправлено на понеділок 2 вересня 2024
START_WEEK = date(2024, 9, 2)


# Визначення номера тижня (1 або 2)
def get_week_number():
    today = date.today()
    weeks_passed = (today - START_WEEK).days // 7
    return 1 if weeks_passed % 2 == 0 else 2


# Вибір розкладу залежно від тижня
def get_current_schedule():
    return schedule_week1 if get_week_number() == 1 else schedule_week2


# /start
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    chat_id = message.chat.id
    active_chats.add(chat_id)
    await message.answer("✅ Бот активований у цьому чаті. Тепер я буду надсилати розклад та нагадування.")


# /today
@dp.message(Command("today"))
async def today_schedule(message: types.Message):
    await message.answer(get_schedule_for_day(datetime.today().weekday()))


# /tomorrow
@dp.message(Command("tomorrow"))
async def tomorrow_schedule(message: types.Message):
    tomorrow_weekday = (datetime.today().weekday() + 1) % 7
    await message.answer(get_schedule_for_day(tomorrow_weekday))


# /week
@dp.message(Command("week"))
async def week_schedule(message: types.Message):
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]
    schedule = get_current_schedule()
    week_num = get_week_number()
    text = f"📅 Розклад на {week_num}-й тиждень:\n\n"
    for day in weekdays:
        text += f"{day}:\n"
        if day in schedule and schedule[day]:
            for para, subj in sorted(schedule[day].items()):
                start_time = lesson_times[para].strftime('%H:%M')
                text += f"  {para} пара ({start_time}): {subj}\n"
        else:
            text += "  Пар немає ✅\n"
        text += "\n"
    await message.answer(text)


# /whichweek
@dp.message(Command("whichweek"))
async def which_week(message: types.Message):
    week_num = get_week_number()
    await message.answer(f"ℹ️ Зараз {week_num}-й тиждень розкладу")


# /test_daily - для тестування щоденної розсилки
@dp.message(Command("test_daily"))
async def test_daily_schedule(message: types.Message):
    if message.chat.id in active_chats:
        await send_daily_schedule()
        await message.answer("✅ Тестова щоденна розсилка надіслана!")
    else:
        await message.answer("⚠️ Спершу активуйте бота командою /start")


@dp.message(Command("next"))
async def next_lesson(message: types.Message):
    now = datetime.now().time()
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
    today_index = datetime.today().weekday()
    today = weekdays[today_index]
    schedule = get_current_schedule()

    # Перевіряємо чи є пари сьогодні
    if today not in schedule or not schedule[today]:
        # Шукаємо наступну пару в наступні дні
        for i in range(1, 7):  # перевіряємо наступні 6 днів
            next_day_index = (today_index + i) % 7
            next_day = weekdays[next_day_index]
            if next_day in schedule and schedule[next_day]:
                next_para = min(schedule[next_day].keys())
                next_time = lesson_times[next_para]
                days_ahead = "завтра" if i == 1 else f"у {next_day}"
                await message.answer(
                    f"📌 Сьогодні пар немає. Наступна пара {days_ahead}: {next_para} пара о {next_time.strftime('%H:%M')} — {schedule[next_day][next_para]}")
                return
        await message.answer("📌 Пар немає на найближчий тиждень ✅")
        return

    # Шукаємо наступну пару сьогодні
    for para in sorted(schedule[today].keys()):
        start_time = lesson_times[para]
        if now < start_time:
            subj = schedule[today][para]
            await message.answer(f"👉 Наступна пара сьогодні: {para} пара о {start_time.strftime('%H:%M')} — {subj}")
            return

    # Якщо пари сьогодні вже закінчилися, шукаємо завтра
    for i in range(1, 7):
        next_day_index = (today_index + i) % 7
        next_day = weekdays[next_day_index]
        if next_day in schedule and schedule[next_day]:
            next_para = min(schedule[next_day].keys())
            next_time = lesson_times[next_para]
            days_ahead = "завтра" if i == 1 else f"у {next_day}"
            await message.answer(
                f"📌 На сьогодні пари вже закінчилися. Наступна пара {days_ahead}: {next_para} пара о {next_time.strftime('%H:%M')} — {schedule[next_day][next_para]}")
            return

    await message.answer("📌 Пар немає на найближчий тиждень ✅")


# --- допоміжні функції ---

def get_schedule_for_day(day_index):
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
    day = weekdays[day_index]
    schedule = get_current_schedule()

    if day in schedule and schedule[day]:
        text = f"📅 Розклад на {day}:\n"
        for para in sorted(schedule[day].keys()):
            subj = schedule[day][para]
            start_time = lesson_times[para].strftime('%H:%M')
            text += f"{para} пара ({start_time}): {subj}\n"
    else:
        text = f"📅 {day}: пар немає ✅"
    return text


async def send_daily_schedule():
    """Надсилає розклад на сьогодні о 7:00 ранку"""
    text = get_schedule_for_day(datetime.today().weekday())
    for chat_id in list(active_chats):  # створюємо копію для безпечної ітерації
        try:
            await bot.send_message(chat_id, text)
        except Exception as e:
            print(f"Помилка при надсиланні повідомлення до чату {chat_id}: {e}")
            # Видаляємо неактивні чати
            active_chats.discard(chat_id)


async def check_lessons():
    """Перевіряє чи потрібно надсилати нагадування про пару за 15 хвилин"""
    now = datetime.now()
    current_time = now.time()
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
    today = weekdays[now.weekday()]
    schedule = get_current_schedule()

    if today in schedule and schedule[today]:
        for para, start_time in lesson_times.items():
            if para in schedule[today]:
                # Обчислюємо час нагадування (за 15 хвилин до пари)
                reminder_datetime = datetime.combine(now.date(), start_time) - timedelta(minutes=15)
                reminder_time = reminder_datetime.time()

                # Перевіряємо чи потрібно надсилати нагадування зараз (з точністю до хвилини)
                if (current_time.hour == reminder_time.hour and
                        current_time.minute == reminder_time.minute):

                    subj = schedule[today][para]
                    message_text = f"⏰ Через 15 хв починається {para} пара: {subj}"

                    print(f"Надсилаємо нагадування: {message_text}")

                    for chat_id in list(active_chats):
                        try:
                            await bot.send_message(chat_id, message_text)
                        except Exception as e:
                            print(f"Помилка при надсиланні нагадування до чату {chat_id}: {e}")
                            active_chats.discard(chat_id)


# --- планувальник ---

# Налаштування часу для щоденної розсилки
DAILY_SCHEDULE_TIME = time(8, 20)  # 8:20


async def scheduler():
    """Планувальник задач"""
    last_daily_send = None  # останній день коли відправляли щоденний розклад

    while True:
        now = datetime.now()
        current_time = now.time()
        current_date = now.date()

        # Перевіряємо чи потрібно надсилати щоденний розклад
        if (current_time.hour == DAILY_SCHEDULE_TIME.hour and
                current_time.minute == DAILY_SCHEDULE_TIME.minute and
                last_daily_send != current_date):
            print(f"Надсилаємо щоденний розклад о {current_time.strftime('%H:%M')}")
            await send_daily_schedule()
            last_daily_send = current_date

        # Перевіряємо нагадування про пари
        await check_lessons()

        # Чекаємо 30 секунд перед наступною перевіркою
        await asyncio.sleep(30)


# --- старт ---

async def main():
    print("Бот запускається...")
    print(f"Щоденна розсилка налаштована на {DAILY_SCHEDULE_TIME.strftime('%H:%M')}")

    # Запускаємо планувальник як фонову задачу
    scheduler_task = asyncio.create_task(scheduler())

    try:
        # Запускаємо polling
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("Бот зупиняється...")
    finally:
        # Зупиняємо планувальник при завершенні
        scheduler_task.cancel()
        await bot.session.close()
        print("Бот зупинено.")


if __name__ == "__main__":
    asyncio.run(main())