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
        "parent": "hands"
    },

    "biceps": {
        "text": "Выбери упражнение на бицепс.",
        "buttons": [
            ("Подъем штанги на бицепс", "barbell_biceps"),
            ("Молотки на бицепс", "hammers_biceps"),
        ],
        "parent": "hands"
    },

    "triceps": {
        "text": "Выбери упражнение на трицепс.",
        "buttons": [
            ("Французский жим", "french_press"),
            ("Канат на трицепс", "triceps_rope"),
        ],
        "parent": "hands"
    },

    "legs": {
        "text": "Выбери мышцу ног.",
        "buttons": [
            ("Ягодицы", "buttocks"),
            ("Квадрицепс", "quads"),
            ("Бицепс бедра", "legs_biceps"),
            ("Икры", "calves"),
        ],
        "parent": "legs"
    },

    "buttocks": {
        "text": "Выбери упражнение на ягодицы.",
        "buttons": [
            ("Ягодичный мост", "buttock_bridge"),
            ("Румынская тяга", "romanian_thrust"),
        ],
        "parent": "legs"
    },

    "quads": {
        "text": "Выбери упражнение на квадрицепс.",
        "buttons": [
            ("Присед", "squat"),
            ("Разгибание ног", "leg_extension"),
        ],
        "parent": "legs"
    },

    "legs_biceps": {
        "text": "Выбери упражнение на бицепс ноги.",
        "buttons": [
            ("Румынская тяга", "romanian_thrust"),
            ("Становая тяга", "deadlift_legs"),
        ],
        "parent": "legs"
    },

    "calves": {
        "text": "Выбери упражнение на икры.",
        "buttons": [
            ("Подъёмы на носки стоя", "standing_toe_lifts"),
        ],
        "parent": "legs"
    },

    "torso": {
        "text": "Выбери мышцу туловища.",
        "buttons": [
            ("Грудь", "chest"),
            ("Спина", "back"),
            ("Пресс", "press"),
        ],
        "parent": "torso"
    },

    "chest": {
        "text": "Выбери упражнение на грудь.",
        "buttons": [
            ("Жим штанги лежа", "bench_press"),
            ("Жим штанги на наклонной скамье", "bench_press_bench"),
            ("Жим гантелей", "dumbbell_bench"),
        ],
        "parent": "torso"
    },

    "back": {
        "text": "Выбери упражнение на спину.",
        "buttons": [
            ("Тяга верхнего блока", "upper_block_thrust"),
            ("Тяга штанги в наклоне", "barbell_pull_tilt"),
            ("Становая тяга", "deadlift_back"),
        ],
        "parent": "torso"
    },

    "press": {
        "text": "Выбери упражнение на пресс.",
        "buttons": [
            ("Подъем коленей к груди", "lifting_knees_chest"),
            ("Подъем прямых ног", "lifting_straight_legs"),
        ],
        "parent": "torso"
    },
}

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("Туловище", callback_data="torso"),
            InlineKeyboardButton("Руки", callback_data="hands"),
        ],
        [
            InlineKeyboardButton("Ноги", callback_data="legs"),
        ],
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
            InlineKeyboardButton("Вернуться в меню", callback_data="back_in_menu"),
        ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Туловище", callback_data="torso"),
            InlineKeyboardButton("Руки", callback_data="hands"),
        ],
        [InlineKeyboardButton("Ноги", callback_data="legs")],
    ]

    await update.message.reply_text(
        "Выберите что хотите тренировать.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "back_in_menu":
        context.user_data["current"] = None

        keyboard = [
            [
                InlineKeyboardButton("Туловище", callback_data="torso"),
                InlineKeyboardButton("Руки", callback_data="hands"),
            ],
            [InlineKeyboardButton("Ноги", callback_data="legs")],
        ]

        await query.edit_message_text(
            "Главное меню:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data == "step_back":
        history = context.user_data.get("history", [])

        if not history:
            await query.edit_message_text(
                "Выберите что хотите тренировать.",
                reply_markup=main_menu()
            )
            context.user_data["current"] = None
            return

        previous = history.pop()
        context.user_data["current"] = previous

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

    if data == "back_in_menu":
        context.user_data["history"] = []
        context.user_data["current"] = None

        await query.edit_message_text(
            "Выберите что хотите тренировать.",
            reply_markup=main_menu()
        )
        return

    await query.edit_message_text(
        f"Техника упражнения: {data}"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Напишите /start чтобы открыть упражнения."
    )


def main() -> None:
    TOKEN = os.getenv("TOKEN")

    if not TOKEN:
        raise ValueError("TOKEN variable not found!")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling()


if __name__ == "__main__":
    main()
