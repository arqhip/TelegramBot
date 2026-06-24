#!/usr/bin/env python

import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# Логи
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

MENU = {
    "hands": {
        "text": "Выбери мышцу рук",
        "buttons": [
            ("Бицепс", "biceps"),
            ("Трицепс", "triceps"),
        ]
    },

    "biceps": {
        "text": "Выбери упражнение на бицепс",
        "buttons": [
            ("Подъем штанги на бицепс", "barbell_biceps"),
            ("Молотки на бицепс", "hammers_biceps"),
        ]
    },

    "triceps": {
        "text": "Выбери упражнение на трицепс",
        "buttons": [
            ("Французский жим", "french_press"),
            ("Канат на трицепс", "triceps_rope"),
        ]
    },


    "legs": {
        "text": "Выбери мышцу ног",
        "buttons": [
            ("Ягодицы", "buttocks"),
            ("Квадрицепс", "quads"),
            ("Бицепс бедра", "legs_biceps"),
            ("Икры", "calves"),
        ]
    },

    "buttocks": {
        "text": "Выбери упражнение на ягодицы",
        "buttons": [
            ("Ягодичный мост", "buttock_bridge"),
            ("Румынская тяга", "romanian_thrust"),
        ]
    },

    "quads": {
        "text": "Выбери упражнение на квадрицепс",
        "buttons": [
            ("Присед", "squat"),
            ("Разгибание ног", "leg_extension"),
        ]
    },

    "legs_biceps": {
        "text": "Выбери упражнение на бицепс ноги",
        "buttons": [
            ("Румынская тяга", "romanian_thrust"),
            ("Становая тяга", "deadlift_legs"),
        ]
    },

    "calves": {
        "text": "Выбери упражнение на икры",
        "buttons": [
            ("Подъёмы на носки стоя", "standing_toe_lifts"),
        ]
    },

    "torso": {
        "text": "Выбери мышцу туловища",
        "buttons": [
            ("Грудь", "chest"),
            ("Спина", "back"),
            ("Пресс", "press"),
        ]
    },

    "chest": {
        "text": "Выбери упражнение на грудь",
        "buttons": [
            ("Жим штанги лежа", "bench_press"),
            ("Жим штанги на наклонной скамье", "bench_press_bench"),
            ("Жим гантелей на скамье 30 градусов", "dumbbell_bench"),
        ]
    },

    "back": {
        "text": "Выбери упражнение на спину",
        "buttons": [
            ("Тяга верхнего блока", "upper_block_thrust"),
            ("Тяга штанги в наклоне", "barbell_pull_tilt"),
            ("Становая тяга", "deadlift_back"),
        ]
    },

    "press": {
        "text": "Выбери упражнение на пресс",
        "buttons": [
            ("Подъем коленей к груди", "lifting_knees_chest"),
            ("Подъем прямых ног до параллели", "lifting_straight_legs"),
        ]
    },
}

def build_keyboard(key: str):
    buttons = MENU[key]["buttons"]

    keyboard = [
        [InlineKeyboardButton(text, callback_data=data)]
        for text, data in buttons
    ]

    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Туловище", callback_data="torso"),
            InlineKeyboardButton("Руки", callback_data="hands"),
        ],
        [InlineKeyboardButton("Ноги", callback_data="legs")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Please choose:",
        reply_markup=reply_markup,
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    # если есть такой экран в MENU
    if data in MENU:
        await query.edit_message_text(
            MENU[data]["text"],
            reply_markup=build_keyboard(data)
        )
        return

    # если это упражнение (конечный уровень)
    await query.edit_message_text(
        f"💪 Упражнение: {data}"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Use /start to test this bot."
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
