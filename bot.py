import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logging.getLogger("httpx").setLevel(logging.WARNING)

MENU = {
    "hands": {
        "text": "Выбери мышцу рук.",
        "buttons": [
            ("Бицепс", "biceps"),
            ("Трицепс", "triceps"),
        ],
        "parent": "root"
    },

    "biceps": {
        "text": "Выбери упражнение на бицепс.",
        "buttons": [
            ("Подъем штанги на бицепс", "barbell_biceps"),
            ("Молотки", "hammers_biceps"),
        ],
        "parent": "hands"
    },

    "barbell_biceps": {
        "text": "Подъем штанги на бицепс",
        "video": "https://www.youtube.com/watch?v=kwG2ipFRgfo",
        "parent": "biceps"
    },

    "hammers_biceps": {
        "text": "Молотки на бицепс",
        "video": "https://www.youtube.com/watch?v=zC3nLlEvin4",
        "parent": "biceps"
    },

    "triceps": {
        "text": "Выбери упражнение на трицепс.",
        "buttons": [
            ("Французский жим", "french_press"),
            ("Канат", "triceps_rope"),
        ],
        "parent": "hands"
    },

    "french_press": {
        "text": "Французский жим",
        "video": "https://www.youtube.com/watch?v=YbX7Wd8jQ-Q",
        "parent": "triceps"
    },

    "triceps_rope": {
        "text": "Канат на трицепс",
        "video": "https://www.youtube.com/watch?v=vB5OHsJ3EME",
        "parent": "triceps"
    },

    "legs": {
        "text": "Выбери мышцу ног.",
        "buttons": [
            ("Ягодицы", "buttocks"),
            ("Квадрицепс", "quads"),
            ("Бицепс бедра", "legs_biceps"),
            ("Икры", "calves"),
        ],
        "parent": "root"
    },

    "buttocks": {
        "text": "Ягодицы",
        "buttons": [
            ("Ягодичный мост", "glute_bridge"),
            ("Румынская тяга", "romanian_deadlift"),
        ],
        "parent": "legs"
    },

    "glute_bridge": {
        "text": "Ягодичный мост",
        "video": "https://www.youtube.com/watch?v=LM8XHLYJoYs",
        "parent": "buttocks"
    },

    "romanian_deadlift": {
        "text": "Румынская тяга",
        "video": "https://www.youtube.com/watch?v=2SHsk9AzdjA",
        "parent": "buttocks"
    },

    "quads": {
        "text": "Квадрицепс",
        "buttons": [
            ("Присед", "squat"),
            ("Разгибание ног", "leg_extension"),
        ],
        "parent": "legs"
    },

    "squat": {
        "text": "Присед со штангой",
        "video": "https://www.youtube.com/watch?v=Dy28eq2PjcM",
        "parent": "quads"
    },

    "leg_extension": {
        "text": "Разгибание ног",
        "video": "https://www.youtube.com/watch?v=YyvSfVjQeL0",
        "parent": "quads"
    },

    "legs_biceps": {
        "text": "Бицепс бедра",
        "buttons": [
            ("Становая тяга", "deadlift"),
        ],
        "parent": "legs"
    },

    "deadlift": {
        "text": "Становая тяга",
        "video": "https://www.youtube.com/watch?v=ytGaGIn3SjE",
        "parent": "legs_biceps"
    },

    "calves": {
        "text": "Икры",
        "buttons": [
            ("Подъёмы на носки", "calf_raises"),
        ],
        "parent": "legs"
    },

    "calf_raises": {
        "text": "Подъёмы на носки",
        "video": "https://www.youtube.com/watch?v=-M4-G8p8fmc",
        "parent": "calves"
    },

    "torso": {
        "text": "Туловище",
        "buttons": [
            ("Грудь", "chest"),
            ("Спина", "back"),
            ("Пресс", "press"),
        ],
        "parent": "root"
    },

    "chest": {
        "text": "Грудь",
        "buttons": [
            ("Жим лёжа", "bench_press"),
            ("Жим гантелей", "dumbbell_press"),
        ],
        "parent": "torso"
    },

    "bench_press": {
        "text": "Жим штанги лёжа",
        "video": "https://www.youtube.com/watch?v=gRVjAtPip0Y",
        "parent": "chest"
    },

    "dumbbell_press": {
        "text": "Жим гантелей",
        "video": "https://www.youtube.com/watch?v=VmB1G1K7v94",
        "parent": "chest"
    },

    "back": {
        "text": "Спина",
        "buttons": [
            ("Тяга верхнего блока", "lat_pulldown"),
            ("Тяга штанги", "barbell_row"),
        ],
        "parent": "torso"
    },

    "lat_pulldown": {
        "text": "Тяга верхнего блока",
        "video": "https://www.youtube.com/watch?v=CAwf7n6Luuc",
        "parent": "back"
    },

    "barbell_row": {
        "text": "Тяга штанги в наклоне",
        "video": "https://www.youtube.com/watch?v=vT2GjY_Umpw",
        "parent": "back"
    },

    "press": {
        "text": "Пресс",
        "buttons": [
            ("Подъем коленей", "knee_raise"),
            ("Подъем ног", "leg_raise"),
        ],
        "parent": "torso"
    },

    "knee_raise": {
        "text": "Подъем коленей",
        "video": "https://www.youtube.com/watch?v=JB2oyawG9KI",
        "parent": "press"
    },

    "leg_raise": {
        "text": "Подъем ног",
        "video": "https://www.youtube.com/watch?v=l4kQd9eWclE",
        "parent": "press"
    },
}

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("Туловище", callback_data="torso"),
            InlineKeyboardButton("Руки", callback_data="hands"),
        ],
        [InlineKeyboardButton("Ноги", callback_data="legs")],
    ]

    return InlineKeyboardMarkup(keyboard)


def build_keyboard(key: str):
    buttons = MENU[key]["buttons"]

    keyboard = [
        [InlineKeyboardButton(text, callback_data=data)]
        for text, data in buttons
    ]

    keyboard.append([
        InlineKeyboardButton("Назад", callback_data="step_back"),
        InlineKeyboardButton("В меню", callback_data="back_in_menu"),
    ])

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Выберите что хотите тренировать.",
        reply_markup=main_menu(),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "back_in_menu":
        context.user_data["history"] = []
        context.user_data["current"] = None

        await query.edit_message_text(
            "Выберите часть тела которую хотите тренировать.",
            reply_markup=main_menu()
        )
        return

    if data == "step_back":
        history = context.user_data.get("history", [])

        if not history:
            await query.edit_message_text(
                "Выберите часть тела которую хотите тренировать.",
                reply_markup=main_menu()
            )
            return

        previous = history.pop()
        context.user_data["current"] = previous
        context.user_data["history"] = history

        await query.edit_message_text(
            MENU[previous]["text"],
            reply_markup=build_keyboard(previous)
        )
        return

    if data in MENU:
        history = context.user_data.setdefault("history", [])

        current = context.user_data.get("current")
        if current:
            history.append(current)

        context.user_data["current"] = data

        await query.edit_message_text(
            MENU[data]["text"],
            reply_markup=build_keyboard(data)
        )
        return

    exercise = MENU.get(data)

    if exercise:
        text = exercise.get("text", data)
        video = exercise.get("video")

        message = f"🏋️ {text}\n\n🎥 Видео техника:\n{video if video else 'Видео отсутствует'}"
    else:
        message = f"Техника упражнения: {data}"

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Главное меню", callback_data="back_in_menu")]
        ])
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Напишите /start чтобы открыть меню.")


def main() -> None:
    TOKEN = os.getenv("TOKEN")

    if not TOKEN:
        raise ValueError("TOKEN variable not found!")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()


if __name__ == "__main__":
    main()
