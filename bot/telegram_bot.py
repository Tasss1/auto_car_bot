import os
import django
from telegram import (
    Update, ReplyKeyboardMarkup, ReplyKeyboardRemove,
    InputMediaPhoto, InputFile
)
from asgiref.sync import sync_to_async
from telegram.ext import (
    Application, CommandHandler, ConversationHandler,
    MessageHandler, filters, ContextTypes
)
from django.conf import settings

# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "car_bot.settings")
django.setup()

from bot.models import Car

# Состояния
CONDITION, COLOR, BODY_TYPE, PRICE_RANGE = range(4)

# Диапазоны цен
PRICE_RANGES = [
    (5000, 10000),
    (10000, 15000),
    (15000, 20000),
    (20000, 30000),
    (30000, 40000),
    (40000, 60000),
]


def chunk(lst, n):
    """Разбить список на строки по n элементов для клавиатуры."""
    return [lst[i:i + n] for i in range(0, len(lst), n)]


# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Новый"], ["Б/У"]]
    await update.message.reply_text(
        "Добро пожаловать в бот по подбору автомобилей! 🚗\n\n"
        "Выберите состояние автомобиля:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CONDITION


# ===== CONDITION HANDLER =====
async def condition_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip().lower()
    if text not in ["новый", "б/у"]:
        await update.message.reply_text("Пожалуйста, выберите один из вариантов кнопками.")
        return CONDITION

    context.user_data["condition"] = "new" if text == "новый" else "used"

    color_buttons = chunk([v for _, v in Car.COLOR_CHOICES], 2)
    await update.message.reply_text(
        "🎨 Выберите цвет:",
        reply_markup=ReplyKeyboardMarkup(color_buttons, one_time_keyboard=True, resize_keyboard=True)
    )
    return COLOR


# ===== COLOR HANDLER =====
async def color_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    color_text = (update.message.text or "").strip().lower()
    reverse_colors = {v.lower(): k for k, v in Car.COLOR_CHOICES}

    if color_text not in reverse_colors:
        color_buttons = chunk([v for _, v in Car.COLOR_CHOICES], 2)
        await update.message.reply_text(
            "Пожалуйста, выберите цвет кнопкой 👇",
            reply_markup=ReplyKeyboardMarkup(color_buttons, one_time_keyboard=True, resize_keyboard=True)
        )
        return COLOR

    context.user_data["color"] = reverse_colors[color_text]

    body_buttons = chunk([v for _, v in Car.BODY_TYPE_CHOICES], 2)
    await update.message.reply_text(
        "📦 Выберите тип кузова:",
        reply_markup=ReplyKeyboardMarkup(body_buttons, one_time_keyboard=True, resize_keyboard=True)
    )
    return BODY_TYPE


# ===== BODY_TYPE HANDLER =====
async def body_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    body_text = (update.message.text or "").strip().lower()
    reverse_bodies = {v.lower(): k for k, v in Car.BODY_TYPE_CHOICES}

    if body_text not in reverse_bodies:
        body_buttons = chunk([v for _, v in Car.BODY_TYPE_CHOICES], 2)
        await update.message.reply_text(
            "Пожалуйста, выберите тип кузова кнопкой 👇",
            reply_markup=ReplyKeyboardMarkup(body_buttons, one_time_keyboard=True, resize_keyboard=True)
        )
        return BODY_TYPE

    context.user_data["body_type"] = reverse_bodies[body_text]

    price_buttons = [[f"{low}-{high}$"] for low, high in PRICE_RANGES]
    await update.message.reply_text(
        "💰 Выберите диапазон цен:",
        reply_markup=ReplyKeyboardMarkup(price_buttons, one_time_keyboard=True, resize_keyboard=True)
    )
    return PRICE_RANGE


# ===== PRICE_RANGE HANDLER =====
async def price_range_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = (update.message.text or "").strip()
    try:
        clean = raw.replace("$", "").replace(" ", "")
        low_s, high_s = clean.split("-")
        low, high = int(low_s), int(high_s)
    except Exception:
        await update.message.reply_text("Введите корректный диапазон (например: 20000-30000$)")
        return PRICE_RANGE

    cars = await sync_to_async(list)(
        Car.objects.filter(
            condition=context.user_data["condition"],
            color=context.user_data["color"],
            body_type=context.user_data["body_type"],
            price__gte=low,
            price__lte=high
        )
    )

    if not cars:
        await update.message.reply_text(
            "К сожалению, по вашим критериям ничего не найдено 😔\n\n"
            "Введите /start, чтобы попробовать снова.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    for car in cars:
        msg = (
            f"🚗 *{car.name}*\n"
            f"💎 Состояние: {car.get_condition_display()}\n"
            f"🎨 Цвет: {car.get_color_display()}\n"
            f"📦 Кузов: {car.get_body_type_display()}\n"
            f"💰 Цена: {car.price}$\n"
            f"📝 {car.description}"
        )

        images = car.get_all_images()  # должен возвращать пути или URL
        media_group = []

        for i, img_path in enumerate(images):
            # Если путь локальный
            full_path = os.path.join(settings.BASE_DIR, img_path)
            if os.path.exists(full_path):
                if i == 0:
                    media_group.append(InputMediaPhoto(InputFile(full_path), caption=msg, parse_mode="Markdown"))
                else:
                    media_group.append(InputMediaPhoto(InputFile(full_path)))
            # Если это прямой URL (например через MEDIA_URL)
            else:
                if i == 0:
                    media_group.append(InputMediaPhoto(img_path, caption=msg, parse_mode="Markdown"))
                else:
                    media_group.append(InputMediaPhoto(img_path))

        if media_group:
            await update.message.reply_media_group(media=media_group)
        else:
            await update.message.reply_text(msg, parse_mode="Markdown")

        # Видео
        if car.video_url:
            video_path = os.path.join(settings.BASE_DIR, car.video_url)
            if os.path.exists(video_path):
                await update.message.reply_video(video=InputFile(video_path), caption="🎥 Видео автомобиля")
            else:
                # Если видео URL
                await update.message.reply_video(video=car.video_url, caption="🎥 Видео автомобиля")

    await update.message.reply_text(
        "Поиск завершен 🎉\nВведите /start для нового поиска.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# ===== CANCEL =====
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Поиск отменён. Введите /start для новой попытки.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# ===== SETUP BOT =====
def setup_bot():
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CONDITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, condition_handler)],
            COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, color_handler)],
            BODY_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, body_type_handler)],
            PRICE_RANGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price_range_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    return application
