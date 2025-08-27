import os
import django
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from asgiref.sync import sync_to_async
from django.conf import settings

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_bot.settings')
django.setup()

from bot.models import Car

# Состояния разговора
CONDITION, COLOR, BODY_TYPE, PRICE_RANGE, RESULTS = range(5)

# Клавиатуры
condition_keyboard = [['Новый', 'Б/У']]
color_keyboard = [['Красный', 'Черный'], ['Синий', 'Зеленый'], ['Желтый']]
body_keyboard = [['Седан', 'Внедорожник'], ['Хэтчбек', 'Купе'], ['Минивэн']]

price_ranges = [
    '5000$ - 10000$',
    '10000$ - 15000$',
    '15000$ - 20000$',
    '20000$ - 30000$',
    '30000$ - 40000$',
    '40000$ - 60000$'
]
price_keyboard = [price_ranges[i:i + 2] for i in range(0, len(price_ranges), 2)]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Добро пожаловать в бот по подбору автомобилей! 🚗\n\n'
        'Я помогу вам найти подходящий автомобиль по вашим предпочтениям.',
        reply_markup=ReplyKeyboardMarkup(condition_keyboard, one_time_keyboard=True)
    )
    return CONDITION


async def condition_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    condition = update.message.text.lower()
    if condition not in ['новый', 'б/у']:
        await update.message.reply_text(
            'Пожалуйста, выберите вариант из клавиатуры.',
            reply_markup=ReplyKeyboardMarkup(condition_keyboard, one_time_keyboard=True)
        )
        return CONDITION

    context.user_data['condition'] = 'new' if condition == 'новый' else 'used'

    await update.message.reply_text(
        'Отлично! Теперь выберите цвет автомобиля:',
        reply_markup=ReplyKeyboardMarkup(color_keyboard, one_time_keyboard=True)
    )
    return COLOR


async def color_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    color_mapping = {
        'красный': 'red',
        'черный': 'black',
        'синий': 'blue',
        'зеленый': 'green',
        'желтый': 'yellow'
    }

    color = update.message.text.lower()
    if color not in color_mapping:
        await update.message.reply_text(
            'Пожалуйста, выберите цвет из клавиатуры.',
            reply_markup=ReplyKeyboardMarkup(color_keyboard, one_time_keyboard=True)
        )
        return COLOR

    context.user_data['color'] = color_mapping[color]

    await update.message.reply_text(
        'Отлично! Теперь выберите тип кузова:',
        reply_markup=ReplyKeyboardMarkup(body_keyboard, one_time_keyboard=True)
    )
    return BODY_TYPE


async def body_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    body_mapping = {
        'седан': 'sedan',
        'внедорожник': 'suv',
        'хэтчбек': 'hatchback',
        'купе': 'coupe',
        'минивэн': 'minivan'
    }

    body_type = update.message.text.lower()
    if body_type not in body_mapping:
        await update.message.reply_text(
            'Пожалуйста, выберите тип кузова из клавиатуры.',
            reply_markup=ReplyKeyboardMarkup(body_keyboard, one_time_keyboard=True)
        )
        return BODY_TYPE

    context.user_data['body_type'] = body_mapping[body_type]

    await update.message.reply_text(
        'Отлично! Теперь выберите ценовой диапазон:',
        reply_markup=ReplyKeyboardMarkup(price_keyboard, one_time_keyboard=True)
    )
    return PRICE_RANGE


async def price_range_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price_range = update.message.text
    if price_range not in price_ranges:
        await update.message.reply_text(
            'Пожалуйста, выберите ценовой диапазон из клавиатуры.',
            reply_markup=ReplyKeyboardMarkup(price_keyboard, one_time_keyboard=True)
        )
        return PRICE_RANGE

    context.user_data['price_range'] = price_range

    # Сначала убираем клавиатуру
    await update.message.reply_text(
        'Ищем подходящие автомобили... 🔍',
        reply_markup=ReplyKeyboardRemove()
    )

    # Поиск подходящих автомобилей
    condition = context.user_data['condition']
    color = context.user_data['color']
    body_type = context.user_data['body_type']

    cars = await sync_to_async(list)(Car.objects.filter(
        condition=condition,
        color=color,
        body_type=body_type,
        price_range=price_range
    ))

    if not cars:
        await update.message.reply_text(
            'К сожалению, по вашим критериям ничего не найдено. 😔\n\n'
            'Попробуйте изменить параметры поиска.\n'
            'Введите /start чтобы начать заново.'
        )
        return ConversationHandler.END

    # Отправляем результаты
    for car in cars:
        message = (
            f'🚗 *{car.name}*\n'
            f'💎 Состояние: {car.get_condition_display()}\n'
            f'🎨 Цвет: {car.get_color_display()}\n'
            f'📦 Кузов: {car.get_body_type_display()}\n'
            f'💰 Цена: {car.price_range}\n'
            f'📝 {car.description}'
        )

        # Если есть фото - отправляем фото с подписью
        if car.image_url:
            await update.message.reply_photo(
                photo=car.image_url,
                caption=message,
                parse_mode='Markdown'
            )
        else:
            # Если фото нет - отправляем только текст
            await update.message.reply_text(message, parse_mode='Markdown')

    await update.message.reply_text(
        'Поиск завершен! 🎉\n'
        'Введите /start чтобы начать новый поиск.'
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Поиск отменен. Если хотите начать заново, введите /start',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def setup_bot():
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CONDITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, condition_handler)],
            COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, color_handler)],
            BODY_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, body_type_handler)],
            PRICE_RANGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price_range_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    return application